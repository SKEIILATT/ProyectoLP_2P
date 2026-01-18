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
OUTPUT_RENDIMIENTO_PATH = "../output"  # Hallazgos de rendimiento académico
CHROMA_PATH = "vectorstore/chroma_db"

#Dado que debemos separar la información de los pdf en chunks, entonces se debe de configurar el divisor de estos textos

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,  # Reducido para evitar exceder limite del modelo
    chunk_overlap=150,
    length_function=len
)

# Limite maximo de caracteres por chunk (nomic-embed-text tiene ~8192 tokens)
MAX_CHUNK_LENGTH = 6000 

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

def cargar_hallazgos_rendimiento(ruta_dir):
    """Carga los JSONs de rendimiento y genera resumenes estadisticos (no datos raw)"""
    documentos = []

    if not os.path.exists(ruta_dir):
        print(f"  Advertencia: Directorio no encontrado: {ruta_dir}")
        return documentos

    # Procesar clicks_vs_nota.json
    clicks_path = os.path.join(ruta_dir, "clicks_vs_nota.json")
    if os.path.exists(clicks_path):
        try:
            with open(clicks_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Calcular estadisticas
            total_estudiantes = len(data)
            clicks = [d['sum_click'] for d in data]
            notas = [d['final_score'] for d in data]
            avg_clicks = sum(clicks) / len(clicks)
            avg_nota = sum(notas) / len(notas)

            # Correlacion simple
            alto_clicks = [d for d in data if d['sum_click'] > avg_clicks]
            bajo_clicks = [d for d in data if d['sum_click'] <= avg_clicks]
            nota_alto = sum(d['final_score'] for d in alto_clicks) / len(alto_clicks) if alto_clicks else 0
            nota_bajo = sum(d['final_score'] for d in bajo_clicks) / len(bajo_clicks) if bajo_clicks else 0

            resumen = f"""HALLAZGO: Relacion entre Clicks y Nota Final

Analisis de {total_estudiantes} estudiantes sobre la correlacion entre actividad en plataforma (clicks) y rendimiento academico.

ESTADISTICAS:
- Total de estudiantes analizados: {total_estudiantes}
- Promedio de clicks por estudiante: {avg_clicks:.1f}
- Promedio de nota final: {avg_nota:.1f}

HALLAZGO PRINCIPAL:
- Estudiantes con ALTO numero de clicks (>{avg_clicks:.0f}): nota promedio de {nota_alto:.1f}
- Estudiantes con BAJO numero de clicks (<={avg_clicks:.0f}): nota promedio de {nota_bajo:.1f}
- Diferencia: {nota_alto - nota_bajo:.1f} puntos

CONCLUSION: {"Existe correlacion positiva entre actividad en plataforma y rendimiento" if nota_alto > nota_bajo else "No se observa correlacion clara"}
"""
            documentos.append(Document(page_content=resumen, metadata={"source": clicks_path, "type": "hallazgo_rendimiento"}))
            print(f"    Procesado: clicks_vs_nota.json ({total_estudiantes} estudiantes)")
        except Exception as e:
            print(f"    Error procesando clicks_vs_nota.json: {e}")

    # Procesar evaluaciones_vs_nota.json
    eval_path = os.path.join(ruta_dir, "evaluaciones_vs_nota.json")
    if os.path.exists(eval_path):
        try:
            with open(eval_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            total_estudiantes = len(data)
            evaluaciones = [d.get('sum_evaluaciones', d.get('evaluaciones', 0)) for d in data]
            notas = [d['final_score'] for d in data]
            avg_eval = sum(evaluaciones) / len(evaluaciones) if evaluaciones else 0
            avg_nota = sum(notas) / len(notas)

            resumen = f"""HALLAZGO: Relacion entre Evaluaciones Completadas y Nota Final

Analisis de {total_estudiantes} estudiantes sobre la correlacion entre evaluaciones realizadas y rendimiento academico.

ESTADISTICAS:
- Total de estudiantes analizados: {total_estudiantes}
- Promedio de evaluaciones por estudiante: {avg_eval:.1f}
- Promedio de nota final: {avg_nota:.1f}

CONCLUSION: Mayor participacion en evaluaciones se asocia con mejor rendimiento academico.
"""
            documentos.append(Document(page_content=resumen, metadata={"source": eval_path, "type": "hallazgo_rendimiento"}))
            print(f"    Procesado: evaluaciones_vs_nota.json ({total_estudiantes} estudiantes)")
        except Exception as e:
            print(f"    Error procesando evaluaciones_vs_nota.json: {e}")

    # Procesar rendimiento_por_materia.json
    materia_path = os.path.join(ruta_dir, "rendimiento_por_materia.json")
    if os.path.exists(materia_path):
        try:
            with open(materia_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, list):
                materias_info = "\n".join([f"- {item.get('code_module', 'N/A')}: promedio {item.get('avg_score', item.get('promedio', 'N/A'))}" for item in data[:20]])
                total = len(data)
            else:
                materias_info = json.dumps(data, indent=2, ensure_ascii=False)[:1000]
                total = 1

            resumen = f"""HALLAZGO: Rendimiento Academico por Materia

Analisis del rendimiento promedio de estudiantes por modulo/materia.

MATERIAS ANALIZADAS ({total}):
{materias_info}

Este analisis permite identificar materias con mayor y menor rendimiento para enfocar esfuerzos de mejora.
"""
            documentos.append(Document(page_content=resumen, metadata={"source": materia_path, "type": "hallazgo_rendimiento"}))
            print(f"    Procesado: rendimiento_por_materia.json ({total} materias)")
        except Exception as e:
            print(f"    Error procesando rendimiento_por_materia.json: {e}")

    return documentos

#Cargamos y procesamos documentos de múltiples fuentes
def cargar_docs():
    """Carga documentos de fuentes ESENCIALES (sin datos raw masivos)"""
    print("Cargando documentos esenciales (modo rapido)...\n")
    all_documents = []

    # 1. PDFs importantes (reglamentos, documentos de analisis)
    print(f"1. Cargando PDFs importantes ({DOCUMENTS_PATH})...")
    all_documents.extend(cargar_docs_de_directorio(DOCUMENTS_PATH, tipos_archivo=(".pdf", ".txt"), tipo_fuente="documentos"))

    # 2. Notebook de análisis de abandono (hallazgos de Jair)
    print(f"\n2. Cargando notebook de analisis ({DATA_ANALYSIS_PATH})...")
    if os.path.exists(DATA_ANALYSIS_PATH):
        for archivo in os.listdir(DATA_ANALYSIS_PATH):
            if archivo.lower().endswith(".ipynb"):
                ruta_notebook = os.path.join(DATA_ANALYSIS_PATH, archivo)
                all_documents.extend(procesar_notebook(ruta_notebook))
    else:
        print(f"  Advertencia: Directorio no encontrado: {DATA_ANALYSIS_PATH}")

    # 3. Knowledge sources (papers academicos)
    print(f"\n3. Cargando papers academicos ({KNOWLEDGE_SOURCES_PATH})...")
    papers_path = os.path.join(KNOWLEDGE_SOURCES_PATH, "papers")
    if os.path.exists(papers_path):
        all_documents.extend(cargar_docs_de_directorio(papers_path, tipos_archivo=(".txt", ".json"), tipo_fuente="papers"))

    # 4. Hallazgos de rendimiento académico (resumen de JSONs de Javier)
    print(f"\n4. Cargando hallazgos de rendimiento ({OUTPUT_RENDIMIENTO_PATH})...")
    all_documents.extend(cargar_hallazgos_rendimiento(OUTPUT_RENDIMIENTO_PATH))

    print(f"\n[INFO] Total de documentos cargados: {len(all_documents)}")

    # Divide los documentos en chunks
    print(f"[INFO] Dividiendo documentos en chunks...")
    all_chunks = text_splitter.split_documents(all_documents)
    print(f"[OK] Total de chunks creados: {len(all_chunks)}")
    
    return all_chunks 
        
def guardar_en_chroma(chunks):
    #Creo los embeddings necesarios para guardarlos en el ChromaDB
    print(f"Guardando {len(chunks)} chunks en ChromaDB...")

    # Filtrar y truncar chunks que excedan el limite
    chunks_validos = []
    for chunk in chunks:
        if len(chunk.page_content) > MAX_CHUNK_LENGTH:
            chunk.page_content = chunk.page_content[:MAX_CHUNK_LENGTH]
        if len(chunk.page_content.strip()) > 0:  # Solo agregar si tiene contenido
            chunks_validos.append(chunk)

    print(f"  Chunks validos despues de filtrar: {len(chunks_validos)}")

    #Primero tengo que inicializar el modelo de embeddings de mi IA (en este caso, Ollama con nomic-embed-text)
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    #Procesar en lotes de 200 chunks (balanceado para velocidad y estabilidad)
    batch_size = 200
    total_batches = (len(chunks_validos) - 1) // batch_size + 1
    for i in range(0, len(chunks_validos), batch_size):
        batch = chunks_validos[i:i+batch_size]
        print(f"Procesando batch {i//batch_size + 1}/{total_batches} ({len(batch)} chunks)...")

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
