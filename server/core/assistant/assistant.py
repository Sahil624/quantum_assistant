from django.conf import settings
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
import logging
import json
import os
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
import faiss
from pinecone import Pinecone
from typing import List, Tuple, Optional
from ..base.conversation import Conversation as BaseConversation

from ..models import Conversation, Message, AIResponse, PerformanceMetric, SystemPrompt


logger = logging.getLogger(__name__)

# Set OpenMP environment variable to ignore duplicate library error
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ["TOKENIZERS_PARALLELISM"] = "false"

class QuantumAssistantConversation(BaseConversation):
    response_tags = [
        "concept_explanation",
        "insufficient_data",
        "unclear_notation",
        "image_reference",
        "encourage_self_learning"
    ]

    def __init__(self, user: type[AbstractUser], conversation_id: Optional[str] = None):
        super().__init__(conversation_id)
        self.user = user
        self.conversation_obj = self._get_or_create_conversation(conversation_id)
        self.tokenizer = AutoTokenizer.from_pretrained(settings.MODEL_NAME)
        self.model = AutoModel.from_pretrained(settings.MODEL_NAME)
        self.index = self._initialize_database()
        self.chunks = self._load_chunks()

    def _get_or_create_conversation(self, conversation_id):
        if conversation_id:
            conv_obj = Conversation.objects.get(id=conversation_id, user=self.user)
            # Update conversation here.
            conv_obj.messages.values_list('content', 'message_type')
            return conv_obj 
        else:
            system_prompt = SystemPrompt.objects.filter(is_active=True, assistant_type='STUDY').first()
            return Conversation.objects.create(system_prompt=system_prompt, user=self.user)

    def _initialize_database(self):
        if settings.DATABASE == "pinecone":
            pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            index = pc.Index(settings.PINECONE_INDEX_NAME)
            logger.info(f"Connected to Pinecone index: {settings.PINECONE_INDEX_NAME}")
            return index
        elif settings.DATABASE == "faiss":
            if os.path.exists(settings.FAISS_INDEX_FILE):
                index = faiss.read_index(settings.FAISS_INDEX_FILE)
                logger.info(f"Loaded FAISS index from file: {settings.FAISS_INDEX_FILE}")
                return index
            else:
                logger.error("FAISS index file not found. Please run the indexing process first.")
                raise FileNotFoundError("FAISS index file not found. Please run the indexing process first.")
        else:
            logger.error("Invalid database choice. Use 'pinecone' or 'faiss'.")
            raise ValueError("Invalid database choice. Use 'pinecone' or 'faiss'.")

    def _load_chunks(self):
        if os.path.exists(settings.CHUNKS_FILE):
            with open(settings.CHUNKS_FILE, "r") as f:
                chunks = json.load(f)
            logger.info(f"Loaded {len(chunks)} chunks from file.")
            return chunks
        else:
            logger.error("Chunks file not found. Please run the indexing process first.")
            raise FileNotFoundError("Chunks file not found. Please run the indexing process first.")

    def create_embedding(self, text: str) -> np.ndarray:
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

    def search_similar_chunks(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        if settings.DATABASE == "pinecone":
            results = self.index.query(vector=query_embedding.tolist(), top_k=top_k, include_metadata=True)
            return [(match['metadata']['text'], float(match['score'])) for match in results['matches']]
        elif settings.DATABASE == "faiss":
            distances, indices = self.index.search(np.array([query_embedding]), top_k)
            return [(self.chunks[int(i)], float(d)) for i, d in zip(indices[0], distances[0])]

    @transaction.atomic
    def process_query(self, user_query: str) -> str:
        iterations = settings.MAX_FOLLOW_UP_LIMIT
        response = None

        extracted_content = settings.TOP_K
        internal_query = user_query
        while iterations:
            logger.info(f"Processing iteration {iterations}")
            extracted_content += ((settings.MAX_FOLLOW_UP_LIMIT - iterations) * 5)
            query_embedding = self.create_embedding(internal_query)
            relevant_chunks = self.search_similar_chunks(query_embedding, extracted_content)
            system_prompt, context = self.prepare_system_prompt(internal_query, relevant_chunks)
            internal_query = self.prepare_user_prompt(query=user_query, context=context,
                                                      follow_up_limit_remaining=iterations)

            logger.debug(f"System prompt: {system_prompt}")
            logger.debug(f"Internal query: {internal_query}")

            self.add_message("user", internal_query)

            response, tags = self.send_to_claude_api(system_prompt)

            assistant_message = self.add_message("assistant", response)

            if tags.get('insufficient_data'):
                logger.info("Insufficient data detected")
                internal_query = user_query + ' \n ' + tags.get('insufficient_data')
            else:
                assistant_message.is_answer = True
                assistant_message.save()
                break

            iterations -= 1

        # Save performance metrics
        PerformanceMetric.objects.create(
            conversation=self.conversation_obj,
            metric_name="iterations",
            metric_value=settings.MAX_FOLLOW_UP_LIMIT - iterations
        )

        return tags

    def prepare_user_prompt(self, query: str, context: str, **kwargs) -> str:
        return f'''                
            <input>
            <user_query>
                {query}
            </user_query>
            
            <context>
                {context}
            </context>
            
            <follow_up_limit_remaining>
                {kwargs.get('follow_up_limit_remaining')-1}
            </follow_up_limit_remaining>
            </input>
        '''

    def prepare_system_prompt(self, query: str, relevant_chunks: List[Tuple[str, float]]) -> Tuple[str, str]:
        context = "\n".join([f"- {chunk}" for chunk, _ in relevant_chunks])

        system_prompt = f"""
        <system>
        You are a student assistant AI specializing in quantum computing and cryptography. Your primary role is to explain concepts based on the information provided in the context below. This context is extracted from a larger dataset based on relevance to the user's query, so it may contain fragments from different sources.

        Guidelines for your responses:
        1. Explain concepts using ONLY the information provided in the context.
        2. If the information is insufficient, respond with <INSUFFICIENT_DATA> tag and suggest what additional query parameters might help retrieve more relevant information.
        3. When using specific parts of the context, indicate which part you're referencing (e.g., "According to the learning objective mentioned...").
        4. For unclear mathematical notations or image references, respond with <NOTATION_UNCLEAR> or <IMAGE_REFERENCE> tag respectively, and explain what information is missing or unclear.
        5. Focus on explaining concepts rather than providing direct answers. If a user asks for an answer, respond with:
           "As a learning assistant, I believe it would be more beneficial for you to work through this problem yourself. Would you like me to explain the relevant concepts to help you arrive at the answer on your own?"
           Only if the user insists after this explanation should you provide a direct answer based on the context.
        6. Do not expand on concepts beyond what's directly stated in the context.
        7. Max followup questions limit is {settings.MAX_FOLLOW_UP_LIMIT}. When this limit is reached, answer the query anyway by combining the data provided in all the iterations and data from external sources (like articles, blogs, research papers etc.) as well. If external sources are used, cite link/name of those sources in response (This is very important).
        8. If query is answered from context, do tell the user about it (Where you concluded the response from) in a short summary.

        <output>
        <concept_explanation>
        [Explanation of concept based on the context]. Only send when either course is explained from provided data or max followup limit is reached. Do not mention about context. User does not know about context, it is sent by server. Instead use the term "Curriculum"
        </concept_explanation>

        <insufficient_data>
        To provide a more complete explanation, we might need additional information about [suggested query parameters]. Give me required information in form of followup questions, I will index those question in database and send updated info.Only send this tag when some extra data is needed. Only send list of question nothing else.
        Example:-
        - Follow up question1?
        - Follow up question2?
        - Follow up question3?
        </insufficient_data>

        <unclear_notation>
        [NOTATION_UNCLEAR] The mathematical notation in the context is not properly formatted. The unclear part is [specify the unclear notation]. To explain this concept accurately, we would need a clearer representation of the mathematical expressions.
        </unclear_notation>

        <image_reference>
        [IMAGE_REFERENCE] The context refers to an image (!imagesnanomod18fig2.png) which I cannot display or describe. This image seems to be related to [mention the topic based on surrounding text]. To fully explain this concept, we would need a description of the image contents.
        </image_reference>

        <encourage_self_learning>
        As a learning assistant, I believe it would be more beneficial for you to work through this problem yourself. Would you like me to explain the relevant concepts to help you arrive at the answer on your own?
        </encourage_self_learning>
        </output>

        Remember, your goal is to assist students in understanding quantum computing concepts by explaining information from the given context, not to demonstrate broader knowledge of the field.
        </system>
        """
        return system_prompt, context

    def add_message(self, role: str, content: str) -> Message:
        super().add_message(role, content)
        return Message.objects.create(
            conversation=self.conversation_obj,
            content=content,
            message_type=role.upper()
        )

    def send_to_claude_api(self, system_prompt) -> Tuple[str, dict]:
        response, tags = super().send_to_claude_api(system_prompt)    
        
        # Save the AI response
        AIResponse.objects.create(
            message=self.conversation_obj.messages.last(),
            ai_type='CLAUDE',
            attempt_number=1,
            response_content=response,
            is_final_answer=True
        )
        
        return response, tags

    @classmethod
    def load_from_db(cls, conversation_id: str):
        return cls(conversation_id)

def main():
    conversation = QuantumAssistantConversation()
    while True:
        user_query = input("Enter your query (or 'quit' to exit): ")
        if user_query.lower() == 'quit':
            break

        if not user_query:
            logger.warning('Invalid Query')
            continue
        
        response = conversation.process_query(user_query)
        print("\n\nAssistant:", response)

if __name__ == '__main__':
    main()