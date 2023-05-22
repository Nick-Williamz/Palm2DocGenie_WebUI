import pandas as pd
import numpy as np
import google.generativeai as palm
import chromadb
from chromadb.api.types import Documents, Embeddings

def configure_palm(api_key):
    palm.configure(api_key=api_key)

def get_text_model():
    models = [m for m in palm.list_models() if 'embedText' in m.supported_generation_methods]
    if not models:
        raise ValueError("No models found that support 'embedText' generation method.")
    return models[0]

def embed_function(texts: Documents, text_model) -> Embeddings:
    return [palm.generate_embeddings(model=text_model, text=text)['embedding'] for text in texts]

def create_chroma_db(documents, name, text_model):
    chroma_client = chromadb.Client()
    db = chroma_client.create_collection(name=name, embedding_function=lambda texts: embed_function(texts, text_model))
    for i, d in enumerate(documents):
        db.add(documents=d, ids=str(i))
    return db

def generate_embeddings_df(documents, text_model):
    # Set up the ChromaDB database
    db = create_chroma_db(documents, "embeddings_db", text_model)

    # Retrieve the embeddings and metadata from the database
    embeddings_data = db.peek(len(documents))
    
    # Create a DataFrame from the embeddings data
    df = pd.DataFrame(embeddings_data)
    df.columns = ['Text', 'Embeddings', 'Document_ID', 'Embedding_ID']
    df['Embeddings'] = df['Embeddings'].apply(np.array)

    return df