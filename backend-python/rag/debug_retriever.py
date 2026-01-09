from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

CHROMA_PATH = "../documents/processed/chroma_db"

def main():
    print("Cargando ChromaDB...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vector = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

    retriever = vector.as_retriever(search_kwargs={"k": 5})

    query = input("Consulta de prueba: ")
    try:
        docs = retriever.get_relevant_documents(query)
    except Exception:
        try:
            docs = retriever.retrieve(query)
        except Exception:
            try:
                docs = retriever(query) if callable(retriever) else []
            except Exception:
                docs = []

    if not docs:
        print("No se encontraron documentos relevantes.")
        return

    print(f"Encontrados {len(docs)} documentos. Mostrando snippets:\n")
    for i, d in enumerate(docs, 1):
        content = getattr(d, 'page_content', str(d))
        meta = getattr(d, 'metadata', {})
        print(f"--- Documento {i} ---")
        print(f"Metadata: {meta}")
        print(content[:1000])
        print("\n")

if __name__ == '__main__':
    main()
