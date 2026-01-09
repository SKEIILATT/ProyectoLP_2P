from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

CHROMA_PATH = "../documents/processed/chroma_db"

def main():
    print("Cargando ChromaDB...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vector = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

    query = input("Consulta de prueba: ")
    
    docs = []
    
    # Intento 1: retriever con k grande
    print("\nIntentando retriever.get_relevant_documents(k=10)...")
    try:
        retriever = vector.as_retriever(search_kwargs={"k": 10})
        docs = retriever.get_relevant_documents(query)
        if docs:
            print(f"✓ Encontrados {len(docs)} con retriever")
    except Exception as e:
        print(f"✗ Retriever falló: {e}")
    
    # Intento 2: similarity_search directo
    if not docs:
        print("Intentando vector.similarity_search(k=10)...")
        try:
            docs = vector.similarity_search(query, k=10)
            if docs:
                print(f"✓ Encontrados {len(docs)} con similarity_search")
        except Exception as e:
            print(f"✗ similarity_search falló: {e}")
    
    # Intento 3: Búsqueda por metadatas (filename matching)
    if not docs:
        print("Intentando búsqueda por metadatas...")
        try:
            collection = getattr(vector, '_collection', None)
            if collection:
                data = collection.get(include=['metadatas', 'documents'])
                metadatas = data.get('metadatas', [])
                documents = data.get('documents', [])
                
                # Buscar por palabras clave
                keywords = ['desercion', 'sexo', '2022', 'estadistica']
                matched_indices = []
                for i, m in enumerate(metadatas):
                    if isinstance(m, dict):
                        source = str(m.get('source', '')).lower()
                        for kw in keywords:
                            if kw in source:
                                matched_indices.append(i)
                                break
                
                if matched_indices:
                    from langchain_core.documents import Document
                    docs = [Document(page_content=documents[i], metadata=metadatas[i]) for i in matched_indices[:10]]
                    print(f"✓ Encontrados {len(docs)} por metadata matching")
        except Exception as e:
            print(f"✗ Metadata matching falló: {e}")

    if not docs:
        print("❌ No se encontraron documentos relevantes.")
        return

    print(f"\n✅ Encontrados {len(docs)} documentos. Mostrando snippets:\n")
    for i, d in enumerate(docs, 1):
        content = getattr(d, 'page_content', str(d))
        meta = getattr(d, 'metadata', {})
        print(f"--- Documento {i} ---")
        print(f"Metadata: {meta}")
        print(content[:800])
        print("\n")

if __name__ == '__main__':
    main()
