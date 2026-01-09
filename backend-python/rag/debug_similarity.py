from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

CHROMA_PATH = "../documents/processed/chroma_db"

def main():
    print("Cargando ChromaDB...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vector = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

    query = "¿Cuál es la deserción por sexo en 2022?"
    
    print(f"\nBuscando documentos para: '{query}'\n")
    
    # similarity_search
    print("1. Intentando similarity_search(k=15)...")
    docs = vector.similarity_search(query, k=15)
    
    print(f"   Encontrados: {len(docs)} documentos\n")
    
    for i, doc in enumerate(docs, 1):
        content = doc.page_content[:500]
        source = doc.metadata.get('source', 'sin fuente')
        doc_type = doc.metadata.get('type', 'unknown')
        
        print(f"--- Doc {i} ---")
        print(f"Source: {source}")
        print(f"Type: {doc_type}")
        print(f"Content (primeros 500 chars):\n{content}\n")
        
        # Marcar si contiene datos de deserción
        if 'desercion' in content.lower() or 'abandono' in content.lower():
            print("✓ CONTIENE DESERCIÓN/ABANDONO\n")
        else:
            print("✗ NO CONTIENE DESERCIÓN/ABANDONO\n")

if __name__ == '__main__':
    main()
