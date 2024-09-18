import os
import dotenv


dotenv.load_dotenv('.env')


config = {
    "database": os.getenv('database'),  # Options: "faiss" or "pinecone"
    "model_name": "sentence-transformers/all-MiniLM-L6-v2",
    "dimension": 384,  # Dimension of the chosen model
    "top_k": 5,
    "pinecone_api_key": os.getenv('pinecone_api_key'),
    "pinecone_environment": "your-pinecone-environment",
    "pinecone_index_name": "textbook-chunks",
    "faiss_index_file": "faiss_index.bin",
    "chunks_file": "text_chunks.json",
    "notebook_directory": os.getenv('notebook_directory'),
    "chunk_size": 3,  # Number of sentences per chunk
    "anthropic_api_key": os.getenv('anthropic_key'),
    "anthropic_model": os.getenv('anthropic_model'),
    "max_follow_up_limit": os.getenv("max_follow_up_questions", 3),
    'notebook_json_path': os.getenv('notebook_json_path'),
    'cell_json_path': os.getenv('cell_json_path')
}
