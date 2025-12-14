import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

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

    #Primero tengo que inicializar el modelo de embeddings de mi IA (en este caso, Ollama, pero podría ser cualquier IA si es que se tiene una API KEY)
    embeddings = OllamaEmbeddings(model="mistral")

    #Creo la base de datos vectorial (ChromaDB)
    Chroma.from_documents(
        documents = chunks,
        embedding = embeddings,
        persist_directory = CHROMA_PATH
    )
    print(f"Base de datos guardadas en {CHROMA_PATH}")

if __name__ == "__main__":
    print("Iniciando proceso de ingesta de documentos...\n")
    chunks = cargar_docs()
    guardar_en_chroma(chunks)
    print("Proceso completado. Base de datos lista.")
