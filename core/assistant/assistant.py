from typing import Optional, List, Tuple

import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
import faiss
from pinecone import Pinecone
import json
import os

from core.base.config import config
from core.base.conversation import Conversation

# Set OpenMP environment variable to ignore duplicate library error
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'


class QuantumAssistantConversation(Conversation):
    response_tags = [
        "concept_explanation",
        "insufficient_data",
        "unclear_notation",
        "image_reference",
        "encourage_self_learning"
    ]

    def __init__(self, conversation_id: Optional[str] = None):
        super().__init__(conversation_id)
        self.tokenizer = AutoTokenizer.from_pretrained(config["model_name"])
        self.model = AutoModel.from_pretrained(config["model_name"])
        self.index = self._initialize_database()
        self.chunks = self._load_chunks()

    def _initialize_database(self):
        if config["database"] == "pinecone":
            pc = Pinecone(api_key=config["pinecone_api_key"])
            index = pc.Index(config["pinecone_index_name"])
            print(f"Connected to Pinecone index: {config['pinecone_index_name']}")
            return index
        elif config["database"] == "faiss":
            if os.path.exists(config["faiss_index_file"]):
                index = faiss.read_index(config["faiss_index_file"])
                print(f"Loaded FAISS index from file: {config['faiss_index_file']}")
                return index
            else:
                raise FileNotFoundError("FAISS index file not found. Please run the indexing process first.")
        else:
            raise ValueError("Invalid database choice. Use 'pinecone' or 'faiss'.")

    def _load_chunks(self):
        if os.path.exists(config["chunks_file"]):
            with open(config["chunks_file"], "r") as f:
                chunks = json.load(f)
            print(f"Loaded {len(chunks)} chunks from file.")
            return chunks
        else:
            raise FileNotFoundError("Chunks file not found. Please run the indexing process first.")

    def create_embedding(self, text: str) -> np.ndarray:
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

    def search_similar_chunks(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        if config["database"] == "pinecone":
            results = self.index.query(vector=query_embedding.tolist(), top_k=top_k, include_metadata=True)
            return [(match['metadata']['text'], float(match['score'])) for match in results['matches']]
        elif config["database"] == "faiss":
            distances, indices = self.index.search(np.array([query_embedding]), top_k)
            return [(self.chunks[int(i)], float(d)) for i, d in zip(indices[0], distances[0])]

    def process_query(self, user_query: str) -> str:
        iterations = config['max_follow_up_limit']
        response = None

        extracted_content = config["top_k"]
        internal_query = user_query
        while iterations:
            print(f"<<<<<<<<<<<<<<<<<<<<<<<<<< ITERATION {iterations} >>>>>>>>>>>>>>>>>>>>>>>>")
            # Increase extracted content in followup questions
            extracted_content += ((config['max_follow_up_limit'] - iterations) * 5)
            query_embedding = self.create_embedding(internal_query)
            relevant_chunks = self.search_similar_chunks(query_embedding, extracted_content)
            system_prompt, context = self.prepare_system_prompt(internal_query, relevant_chunks)
            internal_query = self.prepare_user_prompt(query=user_query, context=context,
                                                      follow_up_limit_remaining=iterations)

            print(system_prompt)
            print('\n\n')
            print(internal_query)

            self.add_message("user", internal_query)

            response, tags = self.send_to_claude_api(system_prompt)

            self.add_message("assistant", response)

            if tags.get('insufficient_data'):
                print("!!!!!! Insufficient Data")
                internal_query = user_query + ' \n ' + tags.get('insufficient_data')
            else:
                break

            iterations -= 1
        return response

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
                {kwargs.get('follow_up_limit_remaining')-0}
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
        7. Max followup questions limit is {config['max_follow_up_limit']}. When this limit is reached, answer the query anyway by combining the data provided in all the iterations and data from external sources as well. If external sources are used, cite link/name of those sources in response (This is very important).

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

    def save_to_db(self):
        # Placeholder for database save operation
        print(f"Saving conversation {self.conversation_id} to database")
        # Implement your database save logic here
        # Make sure to save self.messages along with other conversation data
        pass

    @classmethod
    def load_from_db(cls, conversation_id: str):
        # Placeholder for database load operation
        print(f"Loading conversation {conversation_id} from database")
        # Implement your database load logic here
        conversation = cls(conversation_id)
        # Load messages and other data into the conversation object
        # Make sure to populate conversation.messages with the loaded data
        return conversation


def main():
    conversation = QuantumAssistantConversation()
    while True:
        user_query = input("Enter your query (or 'quit' to exit): ")
        if user_query.lower() == 'quit':
            break

        if not user_query:
            print('Invalid Query')
            continue
        
        response = conversation.process_query(user_query)
        print("\n\nAssistant:", response)

    conversation.save_to_db()


if __name__ == '__main__':
    main()
