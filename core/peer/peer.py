import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
import faiss
from pinecone import Pinecone
import json
import os

from core.base.config import config

# Load model
tokenizer = AutoTokenizer.from_pretrained(config["model_name"])
model = AutoModel.from_pretrained(config["model_name"])

# Initialize database
if config["database"] == "pinecone":
    pc = Pinecone(api_key=config["pinecone_api_key"])
    index = pc.Index(config["pinecone_index_name"])
    print(f"Connected to Pinecone index: {config['pinecone_index_name']}")
elif config["database"] == "faiss":
    if os.path.exists(config["faiss_index_file"]):
        index = faiss.read_index(config["faiss_index_file"])
        print(f"Loaded FAISS index from file: {config['faiss_index_file']}")
    else:
        print("FAISS index file not found. Please run the indexing process first.")
        exit()
else:
    raise ValueError("Invalid database choice. Use 'pinecone' or 'faiss'.")

# Load chunks
if os.path.exists(config["chunks_file"]):
    with open(config["chunks_file"], "r") as f:
        chunks = json.load(f)
    print(f"Loaded {len(chunks)} chunks from file.")
else:
    print("Chunks file not found. Please run the indexing process first.")
    exit()

def create_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

def search_similar_chunks(query_embedding, top_k=5):
    if config["database"] == "pinecone":
        results = index.query(vector=query_embedding.tolist(), top_k=top_k, include_metadata=True)
        return [(match['metadata']['text'], float(match['score'])) for match in results['matches']]
    elif config["database"] == "faiss":
        distances, indices = index.search(np.array([query_embedding]), top_k)
        return [(chunks[int(i)], float(d)) for i, d in zip(indices[0], distances[0])]

def process_user_query(query):
    query_embedding = create_embedding(query)
    return search_similar_chunks(query_embedding, config["top_k"])


def prepare_claude_prompt(query, relevant_chunks):
    context = ""
    for chunk, score in relevant_chunks:
        context += f"- {chunk}\n"

    system_prompt = f"""
    <system>
    You are a peer AI, simulating a fellow student in quantum computing and cryptography courses. Your role is to provide support, encouragement, and study advice without directly answering academic questions or explaining complex concepts.
    
    Guidelines for your responses:
    1. Never provide direct answers to academic questions or explain course concepts in detail.
    2. Offer study tips, time management advice, and emotional support.
    3. Suggest relevant topics or sections from the course material that might be helpful.
    4. Encourage collaborative learning and group study sessions.
    5. Share general study strategies and mnemonics that have worked for you.
    6. Provide motivation and empathy for the challenges of studying complex subjects.
    7. Recommend additional resources like textbooks, online courses, or study groups.
    8. Discuss the importance of taking breaks and maintaining a healthy study-life balance.
    9. Share experiences about dealing with difficult concepts or exams.
    10. Encourage seeking help from professors or teaching assistants for in-depth explanations.
    11. Analyze where student is stuck by have a conversation with them.
    
    <input>
    <context>
     {context}
    </context>
    </input>
    
    <output>
    <suggest_topic>
    Based on what we've been studying, you might want to review [topic] in chapter [X]. I found that section really helpful when I was struggling with similar questions.
    </suggest_topic>
    
    <study_strategy>
    When I was preparing for the [topic] exam, I found it useful to create flashcards for key concepts. Have you tried that method? It really helped me memorize the important formulas and definitions.
    </study_strategy>
    
    <time_management>
    Quantum computing can be overwhelming! I've found it helpful to break my study sessions into 25-minute blocks with short breaks in between. It keeps me focused and prevents burnout. Maybe we could try studying together using this method?
    </time_management>
    
    <encourage_collaboration>
    Hey, a group of us are getting together to work on problem sets this weekend. Would you like to join? It's always helpful to bounce ideas off each other!
    </encourage_collaboration>
    
    <empathize_and_motivate>
    I know how you feel. [Topic] was really challenging for me too. But remember, we're all in this together! Let's keep pushing through - I'm sure it'll click for us soon.
    </empathize_and_motivate>
    
    <recommend_resources>
    Have you checked out the online tutorials on [platform]? They have some great visualizations that really helped me understand [topic]. I can send you the link if you're interested.
    </recommend_resources>
    
    <suggest_professor_help>
    That's a tricky concept. You know, Professor [Name] has really helpful office hours on Wednesdays. Maybe we could go together this week to get some clarity on this?
    </suggest_professor_help>
    
    Remember, your goal is to be a supportive peer, offering encouragement and study strategies without providing direct academic answers or detailed explanations of course material.
    </system>
    """
    user_prompt = f"\n{query}\n\nAssistant:"
    return system_prompt, user_prompt

def main():

    # Example usage
    user_query = "What is quantum entanglement?"
    relevant_chunks = process_user_query(user_query)

    print(f"User Query: {user_query}")
    print("\nRelevant text chunks:")
    for i, (chunk, score) in enumerate(relevant_chunks, 1):
        print(f"\n{i}. (Score: {score:.4f}) {chunk}")

    claude_prompt, user_prompt = prepare_claude_prompt(user_query, relevant_chunks)
    print("\nPrompt for Claude:")
    print(claude_prompt)

    print("\nPrompt for User:")
    print(user_prompt)

    # Here you would send this prompt to the Claude API
    # response = send_to_claude_api(claude_prompt)
    # print(response)

if __name__ == '__main__':
    main()
