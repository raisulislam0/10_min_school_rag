import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

# Check if ChromaDB directory exists
if os.path.exists("./chroma_bn"):
    print("ChromaDB directory exists. Connecting to existing database...")
    chroma_client = chromadb.PersistentClient(path="./chroma_bn")
    collection = chroma_client.get_or_create_collection(
        name="bn_knowledge",
        configuration={
          "embedding_function": SentenceTransformerEmbeddingFunction(
          model_name="nomic-ai/nomic-embed-text-v2-moe",
          trust_remote_code=True),
          "hnsw": {"space": "l2"}
        }
    )
    print(f"Connected to existing collection with {collection.count()} documents")
else:
    print("ChromaDB directory doesn't exist. Creating and embedding documents...")
    chroma_client = chromadb.PersistentClient(path="./chroma_bn")
    collection = chroma_client.get_or_create_collection(
        name="bn_knowledge",
        configuration={
          "embedding_function": SentenceTransformerEmbeddingFunction(
          model_name="nomic-ai/nomic-embed-text-v2-moe",
          trust_remote_code=True),
          "hnsw": {"space": "l2"}
        }
    )
    
    chunks = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators= ["\n\n", "\n", ".", "।", "!", "?"]
    )

    # Load corpus
    with open("cleaned_output.txt", "r", encoding="utf-8") as f:
        sentences = f.read()
        chunks = text_splitter.split_text(sentences)

    # Populate ChromaDB
    for i, sentence in enumerate(chunks):
        collection.add(
            documents=[sentence],
            ids=[f"id_{i}"]
        )
    print(f"Added {len(chunks)} documents to collection")
