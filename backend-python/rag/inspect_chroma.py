from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

CHROMA_PATH = "../documents/processed/chroma_db"


def main():
    print("Cargando ChromaDB para inspección...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vector = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

    # Intentos para acceder a los documentos/metadata de la colección
    collection = getattr(vector, '_collection', None)
    if collection is None:
        print("No pude acceder a la colección interna del vectorstore.")
        return

    print("Colección encontrada. Intentando obtener metadatos y documentos...")
    try:
        data = collection.get(include=['metadatas', 'documents'])
        metadatas = data.get('metadatas', [])
        documents = data.get('documents', [])
        print(f"Total metadatas: {len(metadatas)}")
        print(f"Total documents: {len(documents)}")

        # Mostrar algunos ejemplos
        for i in range(min(10, len(documents))):
            print("--- Documento #{} ---".format(i+1))
            print("Metadata:", metadatas[i])
            print("Contenido (primeros 800 chars):")
            print(documents[i][:800])
            print("\n")

        # Mostrar fuentes únicas si existen
        sources = set()
        for m in metadatas:
            if isinstance(m, dict) and 'source' in m:
                sources.add(m['source'])
        if sources:
            print("Fuentes detectadas:")
            for s in list(sources)[:30]:
                print(" -", s)
        else:
            print("No se detectaron campos 'source' en metadatas.")

    except Exception as e:
        print("Error al obtener datos de la colección:", e)

if __name__ == '__main__':
    main()
