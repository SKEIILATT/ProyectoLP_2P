import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

DOCUMENTS_PATH = "./documents/raw"
CHROMA_PATH = "./documents/processed/chroma_db"

#Dado que debemos separar la información de los pdf en chunks, entonces se debe de configurar el divisor de estos textos

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=len
) 

#Cargamos y procesamos los pdf
def cargar_docs():
    #Esta función nos permite cargar los pdf de la carpeta raw y dividirlos en chunks
    print("Cargando documentos pdf")
    all_chunks=[]
    pdf_files = []
    for f in os.listdir(DOCUMENTS_PATH):
        if f.endswith(".pdf"):
            pdf_files.append(f)
    print(f"Encontrados {len(pdf_files)} archivos")

    #Procesamos cada PDF
    for pdf_file in pdf_files:
        pdf_path = os.path.join(DOCUMENTS_PATH, pdf_file)
        print("Procesando PDF")
        #Cargo el PDF
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        #Divido en chunks
        chunks = text_splitter.split_documents(documents)
        
        #Agrego a la lista
        all_chunks.extend(chunks)
        print(f"{len(chunks)} chunks creados")

    print(f"Total de chunks: {len(all_chunks)}")
    return all_chunks 
        
def guardar_en_chroma(chunks):
    #Creo los embeddings necesarios para guardarlos en el ChromaDB
    print(f"Guardando {len(chunks)} chunks en ChromaDB...")

    #Primero tengo que inicializar el modelo de embeddings de mi IA (en este caso, Ollama con nomic-embed-text)
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    #Procesar en lotes de 100 chunks para evitar timeouts
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        print(f"Procesando batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1} ({len(batch)} chunks)...")

        if i == 0:
            # Primer batch: crear la base de datos
            vectorstore = Chroma.from_documents(
                documents=batch,
                embedding=embeddings,
                persist_directory=CHROMA_PATH
            )
        else:
            # Batches siguientes: agregar a la base existente
            vectorstore = Chroma(
                persist_directory=CHROMA_PATH,
                embedding_function=embeddings
            )
            vectorstore.add_documents(batch)

    print(f"Base de datos guardada en {CHROMA_PATH}")

if __name__ == "__main__":
    print("Iniciando proceso de ingesta de documentos...\n")
    chunks = cargar_docs()
    guardar_en_chroma(chunks)
    print("Proceso completado. Base de datos lista.")
