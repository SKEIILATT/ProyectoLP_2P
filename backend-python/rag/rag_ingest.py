import os
import json
import nbformat
from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

# Rutas de diferentes fuentes de datos (estructura unificada)
DOCUMENTS_PATH = "documents_raw"
DATA_RAW_PATH = "../data/raw"
DATA_PROCESSED_PATH = "../data/processed/estadisticas_ecuador"
DATA_ANALYSIS_PATH = "../data/analysis"
KNOWLEDGE_SOURCES_PATH = "knowledge_sources"
CHROMA_PATH = "vectorstore/chroma_db"

#Dado que debemos separar la información de los pdf en chunks, entonces se debe de configurar el divisor de estos textos

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=200,
    length_function=len
) 

# Función para extraer contenido de notebooks Jupyter
def procesar_notebook(ruta_notebook):
    """Extrae el contenido de un notebook Jupyter y lo convierte en documentos"""
    print(f"  Extrayendo contenido del notebook: {ruta_notebook}")
    try:
        with open(ruta_notebook, 'r', encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=4)
        
        contenido = []
        for i, celda in enumerate(notebook.cells):
            if celda.cell_type == 'markdown':
                contenido.append(f"# Markdown (Celda {i})\n{celda.source}")
            elif celda.cell_type == 'code':
                contenido.append(f"# Código (Celda {i})\n{celda.source}")
            
            # Agregar outputs si existen
            if hasattr(celda, 'outputs') and celda.outputs:
                for output in celda.outputs:
                    if hasattr(output, 'text'):
                        contenido.append(f"# Output (Celda {i})\n{output.text}")
        
        contenido_completo = "\n\n".join(contenido)
        return [Document(page_content=contenido_completo, metadata={"source": ruta_notebook, "type": "notebook"})]
    except Exception as e:
        print(f"  Error procesando notebook: {e}")
        return []

def cargar_docs_de_directorio(ruta_dir, tipos_archivo=(".pdf", ".txt", ".csv"), tipo_fuente="documento"):
    """Carga documentos de un directorio específico (recursivo)."""
    documentos = []

    if not os.path.exists(ruta_dir):
        print(f"  Advertencia: Directorio no encontrado: {ruta_dir}")
        return documentos

    found_files = []
    for root, _, files in os.walk(ruta_dir):
        for f in files:
            if f.lower().endswith(tipos_archivo):
                found_files.append(os.path.join(root, f))

    if not found_files:
        print(f"  No se encontraron archivos en {ruta_dir}")
        return documentos

    print(f"  Encontrados {len(found_files)} archivos en {ruta_dir} (recursivo)")

    for ruta in found_files:
        archivo = os.path.basename(ruta)
        print(f"    Procesando {os.path.relpath(ruta)}...")

        try:
            if ruta.lower().endswith(".pdf"):
                loader = PyPDFLoader(ruta)
                documentos.extend(loader.load())
            elif ruta.lower().endswith(".txt"):
                loader = TextLoader(ruta, encoding='utf-8')
                documentos.extend(loader.load())
            elif ruta.lower().endswith(".csv"):
                # Leer CSV como texto completo para mejor búsqueda semántica
                try:
                    with open(ruta, 'r', encoding='utf-8') as f:
                        contenido_csv = f.read()
                    # Agregar nombre del archivo al contenido para mejorar búsqueda
                    nombre_archivo = os.path.basename(ruta)
                    contenido_con_titulo = f"Archivo: {nombre_archivo}\n\nDatos:\n{contenido_csv}"
                    documentos.append(Document(
                        page_content=contenido_con_titulo,
                        metadata={"source": ruta, "type": "csv", "filename": nombre_archivo}
                    ))
                except Exception:
                    # Fallback a CSVLoader si falla lectura de texto
                    loader = CSVLoader(ruta)
                    documentos.extend(loader.load())
            elif ruta.lower().endswith(".json"):
                # Cargar archivos JSON (papers scraped, etc.)
                try:
                    with open(ruta, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    nombre_archivo = os.path.basename(ruta)
                    # Si es una lista de papers
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                contenido = "\n".join([f"{k}: {v}" for k, v in item.items()])
                                documentos.append(Document(
                                    page_content=contenido,
                                    metadata={"source": ruta, "type": "json", "filename": nombre_archivo}
                                ))
                    else:
                        contenido = json.dumps(data, indent=2, ensure_ascii=False)
                        documentos.append(Document(
                            page_content=contenido,
                            metadata={"source": ruta, "type": "json", "filename": nombre_archivo}
                        ))
                except Exception as e:
                    print(f"    Error procesando JSON {ruta}: {e}")
        except Exception as e:
            print(f"    Error procesando {ruta}: {e}")
            continue

    return documentos

#Cargamos y procesamos documentos de múltiples fuentes
def cargar_docs():
    """Carga documentos de todas las fuentes de datos disponibles"""
    print("Cargando documentos de múltiples fuentes...\n")
    all_documents = []
    
    # 1. Documentos raw
    print(f"1. Cargando documentos RAW ({DOCUMENTS_PATH})...")
    all_documents.extend(cargar_docs_de_directorio(DOCUMENTS_PATH))
    
    # 1b. Documentos en data/raw (si existen)
    print(f"\n1.b Cargando documentos RAW adicionales ({DATA_RAW_PATH})...")
    all_documents.extend(cargar_docs_de_directorio(DATA_RAW_PATH))
    
    # 2. Estadísticas procesadas (CSVs)
    print(f"\n2. Cargando estadísticas procesadas ({DATA_PROCESSED_PATH})...")
    all_documents.extend(cargar_docs_de_directorio(DATA_PROCESSED_PATH, tipos_archivo=(".csv",), tipo_fuente="estadísticas"))
    
    # 3. Análisis del notebook
    print(f"\n3. Cargando análisis desde notebook ({DATA_ANALYSIS_PATH})...")
    if os.path.exists(DATA_ANALYSIS_PATH):
        for archivo in os.listdir(DATA_ANALYSIS_PATH):
            if archivo.lower().endswith(".ipynb"):
                ruta_notebook = os.path.join(DATA_ANALYSIS_PATH, archivo)
                all_documents.extend(procesar_notebook(ruta_notebook))
    else:
        print(f"  Advertencia: Directorio no encontrado: {DATA_ANALYSIS_PATH}")

    # 4. Knowledge sources (papers y recursos scraped)
    print(f"\n4. Cargando knowledge sources ({KNOWLEDGE_SOURCES_PATH})...")
    papers_path = os.path.join(KNOWLEDGE_SOURCES_PATH, "papers")
    resources_path = os.path.join(KNOWLEDGE_SOURCES_PATH, "resources")

    # Cargar papers (JSON y TXT)
    if os.path.exists(papers_path):
        all_documents.extend(cargar_docs_de_directorio(papers_path, tipos_archivo=(".txt", ".json"), tipo_fuente="papers"))

    # Cargar resources
    if os.path.exists(resources_path):
        all_documents.extend(cargar_docs_de_directorio(resources_path, tipos_archivo=(".txt", ".json"), tipo_fuente="resources"))

    print(f"\n📊 Total de documentos cargados: {len(all_documents)}")
    
    # Divide los documentos en chunks
    print(f"🔪 Dividiendo documentos en chunks...")
    all_chunks = text_splitter.split_documents(all_documents)
    print(f"✅ Total de chunks creados: {len(all_chunks)}")
    
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
