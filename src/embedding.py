import chromadb
import chromadb.utils.embedding_functions as embedding_functions
import uuid

def record_documents(client: chromadb.Client, ef: embedding_functions.GoogleGeminiEmbeddingFunction, collection_name: str, chunks: list[str]):
    collection = client.get_or_create_collection(name= collection_name,
                                                 embedding_function= ef)

    collection.upsert(
        documents= chunks,
        ids=[str(uuid.uuid4()) for _ in range(len(chunks))]
    )

def query(client: chromadb.Client, ef: embedding_functions.GoogleGeminiEmbeddingFunction, collection_name: str, queries:list[str], n_results: int = 5):
    try:
        collection = client.get_collection(name= collection_name,
                                           embedding_function = ef)
        
        results = collection.query(
            query_texts= queries,
            n_results=n_results
        )

        return results["documents"]
    
    except Exception as e:
        print(f"Error: {e}")