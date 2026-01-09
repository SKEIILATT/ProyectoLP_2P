'''
Script de Consulta RAG
Permite hacer preguntas sobre los documentos PDF Procesados
'''
import argparse
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.documents import Document

CHROMA_PATH = "../documents/processed/chroma_db"

def cargar_rag():
    """Carga el sistema RAG desde ChromaDB"""
    print("Cargando sistema RAG")
    # Me permite cargar el modelo de embeddings de mi IA (En este caso, Ollama con nomic-embed-text)
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    # Cargamos el vector de ChromaDB
    vector = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )
    print("Vector y sistema RAG cargado correctamente")
    return vector

def consultar(query, vector, modelo_ollama="llama3"):
    """
    Realiza la consulta RAG sobre los documentos que se han analizado
    
    Args:
        query: La consulta que se desea hacer sobre los documentos
        vector: El vector de ChromaDB que se ha creado para los documentos
        modelo_ollama: El modelo ollama que se ha utilizado para la consulta
    """
    print(f"Generando respuesta con modelo {modelo_ollama}")

    # Aquí inicializo el modelo de IA que se va a utilizar para las consultas
    # El parámetro temperature=0.0 es para que la respuesta sea más precisa
    llm = ChatOllama(model=modelo_ollama, temperature=0.0)

    # Configuramos el retriever para obtener los documentos relevantes
    retriever = vector.as_retriever(search_kwargs={"k": 3})

    # Obtener documentos relevantes con varios fallbacks según la versión
    try:
        docs = retriever.get_relevant_documents(query)
    except Exception:
        try:
            docs = retriever.retrieve(query)
        except Exception:
            # Algunos retrievers son callables
            try:
                docs = retriever(query) if callable(retriever) else []
            except Exception:
                docs = []

    # Fallback: intentar similarity_search directamente en el vectorstore
    if not docs:
        try:
            docs = vector.similarity_search(query, k=5)
        except Exception:
            docs = docs or []

    # Si aún no hay docs, intentar búsqueda por metadatas (por ejemplo filenames)
    if not docs:
        try:
            collection = getattr(vector, '_collection', None)
            if collection is not None:
                data = collection.get(include=['metadatas', 'documents'])
                metadatas = data.get('metadatas', [])
                documents = data.get('documents', [])
                # buscar fuentes que contengan palabras clave de la pregunta
                keywords = [w.lower().strip() for w in query.replace('ñ','n').split() if len(w) > 3]
                matched = []
                for i, m in enumerate(metadatas):
                    src = ''
                    if isinstance(m, dict):
                        src = str(m.get('source', '')).lower()
                    if any(kw in src for kw in keywords):
                        matched.append(i)
                if matched:
                    docs = []
                    for i in matched:
                        docs.append(Document(page_content=documents[i], metadata=metadatas[i]))
        except Exception:
            pass

    if not docs:
        return {"result": "No tengo suficiente información."}

    # Combinamos el contexto de los documentos (seguro ante diferentes shapes)
    context = "\n\n".join([getattr(doc, 'page_content', str(doc)) for doc in docs])[:1800]

    # Creamos el prompt completo
    prompt_text = (
        "Responde SOLAMENTE usando la información del contexto. "
        "Si no encuentras la respuesta, contesta: 'No tengo suficiente información.'\n\n"
        "Contexto:\n"
        f"{context}\n\n"
        f"Pregunta: {query}\n\n"
        "Respuesta:"
    )

    print(f"\nPregunta: {query}\n")

    # Ejecutamos la consulta con el LLM de forma robusta
    answer = None
    try:
        resp = llm(prompt_text)
        if isinstance(resp, str):
            answer = resp
        else:
            answer = getattr(resp, 'content', str(resp))
    except Exception:
        try:
            resp = llm.invoke(prompt_text)
            answer = getattr(resp, 'content', str(resp))
        except Exception as e:
            answer = f"Error al invocar el modelo: {e}"

    return {"result": answer}

def main():
    """Función principal del script"""
    # Configuramos el parser de argumentos CLI
    parser = argparse.ArgumentParser(
        description="Consulta documentos procesados usando RAG",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python rag_query.py "¿Cuál es el proceso para obtener una beca?"
  python rag_query.py "¿Qué dice el reglamento sobre el control de asistencia?" --modelo llama3.1
        """
    )
    
    parser.add_argument(
        "pregunta",
        type=str,
        help="La pregunta que quieres hacer sobre los documentos"
    )
    
    parser.add_argument(
        "--modelo",
        type=str,
        default="llama3",
        help="Modelo de Ollama a usar (default: llama3). Ejemplos: llama3, llama3.1, mistral, etc."
    )
    
    args = parser.parse_args()
    
    # Cargamos el sistema RAG
    vectorstore = cargar_rag()
    
    # Realizamos la consulta
    try:
        resultado = consultar(args.pregunta, vectorstore, args.modelo)
        
        # Mostramos la respuesta
        print("\n" + "="*80)
        print("RESPUESTA:")
        print("="*80)
        print(resultado["result"])
        
    except Exception as e:
        print(f"\n Error al procesar la consulta: {str(e)}")
        print("\nAsegúrate de que:")
        print("  1. Ollama está corriendo (ollama serve)")
        print("  2. El modelo especificado está disponible (ollama pull llama3)")
        print("  3. La base de datos ChromaDB existe y fue creada con rag_ingest.py")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
