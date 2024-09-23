import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
from pinecone import Pinecone
import faiss
import json
import os
import nbformat
import re

from core.base.config import config
from core.pre_processor.common import get_nb_files_path

# Load model
tokenizer = AutoTokenizer.from_pretrained(config["model_name"])
model = AutoModel.from_pretrained(config["model_name"])

# Initialize database
if config["database"] == "pinecone":
    pc = Pinecone(api_key=config["pinecone_api_key"])
    if config["pinecone_index_name"] not in pc.list_indexes().names():
        pc.create_index(
            name=config["pinecone_index_name"],
            dimension=config["dimension"],
            metric='cosine'
        )
    index = pc.Index(config["pinecone_index_name"])
elif config["database"] == "faiss":
    if os.path.exists(config["faiss_index_file"]):
        index = faiss.read_index(config["faiss_index_file"])
    else:
        index = faiss.IndexFlatL2(config["dimension"])
else:
    raise ValueError("Invalid database choice. Use 'pinecone' or 'faiss'.")

# Load or initialize chunks
if os.path.exists(config["chunks_file"]):
    with open(config["chunks_file"], "r") as f:
        chunks = json.load(f)
else:
    chunks = []


def create_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()


def index_chunks(new_chunks):
    global chunks
    if not new_chunks:
        print("No new chunks to index.")
        return

    chunks.extend(new_chunks)
    embeddings = [create_embedding(chunk) for chunk in new_chunks]

    if config["database"] == "pinecone":
        to_upsert = [(str(i + len(chunks) - len(new_chunks)), emb.tolist(), {"text": chunk})
                     for i, (emb, chunk) in enumerate(zip(embeddings, new_chunks))]
        index.upsert(vectors=to_upsert)
    elif config["database"] == "faiss":
        index.add(np.array(embeddings))

    # Save chunks
    with open(config["chunks_file"], "w") as f:
        json.dump(chunks, f)

    # Save Faiss index if using Faiss
    if config["database"] == "faiss":
        faiss.write_index(index, config["faiss_index_file"])


def extract_text_from_notebook(notebook_path):
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)

        text = ""
        for cell in nb.cells:
            if cell.cell_type == 'markdown':
                text += cell.source + "\n\n"
            elif cell.cell_type == 'code':
                # Uncomment the next line if you want to include code cells
                # text += cell.source + "\n\n"
                pass

        return text
    except Exception as e:
        print(f"Error processing notebook {notebook_path}: {str(e)}")
        return ""


def clean_text(text):
    # Remove special characters and extra whitespace
    text = re.sub(r'[^\w\s.,?!]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def chunk_text(text, chunk_size=3):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = [' '.join(sentences[i:i + chunk_size]) for i in range(0, len(sentences), chunk_size)]
    return [chunk for chunk in chunks if chunk.strip()]  # Remove empty chunks


def process_notebooks(directory):
    notebook_files = get_nb_files_path(directory)
    all_chunks = []
    for notebook_file in notebook_files:
        print(f"Processing notebook: {notebook_file}")
        text = extract_text_from_notebook(notebook_file)
        if text:
            clean_text_content = clean_text(text)
            chunks = chunk_text(clean_text_content, config["chunk_size"])
            all_chunks.extend(chunks)

    print(f"Total chunks extracted: {len(all_chunks)}")
    return all_chunks


def main():
    # Main processing
    if not chunks:
        print("Processing notebooks...")
        new_chunks = process_notebooks(config["notebook_directory"])
        if new_chunks:
            index_chunks(new_chunks)
            print("Notebook processing and indexing complete.")
        else:
            print("No valid chunks found in notebooks. Please check your notebook content and directory path.")


if __name__ == '__main__':
    main()
