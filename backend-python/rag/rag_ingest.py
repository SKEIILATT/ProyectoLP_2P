import os
import json
import nbformat
from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

DOCUMENTS_PATH = "documents_raw"
DATA_RAW_PATH = "../data/raw"
DATA_PROCESSED_PATH = "../data/processed/estadisticas_ecuador"
DATA_ANALYSIS_PATH = "../data/analysis"
DATA_ROOT_PATH = "../data"
KNOWLEDGE_SOURCES_PATH = "knowledge_sources"
OUTPUT_RENDIMIENTO_PATH = "../output"
CHROMA_PATH = "vectorstore/chroma_db"

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=150,
    length_function=len
)

MAX_CHUNK_LENGTH = 6000

def procesar_notebook(ruta_notebook):
    """Extrae el contenido de un notebook Jupyter y lo convierte en documentos"""
    try:
        with open(ruta_notebook, 'r', encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=4)

        contenido = []
        for i, celda in enumerate(notebook.cells):
            if celda.cell_type == 'markdown':
                contenido.append(f"# Markdown (Celda {i})\n{celda.source}")
            elif celda.cell_type == 'code':
                contenido.append(f"# Código (Celda {i})\n{celda.source}")

            if hasattr(celda, 'outputs') and celda.outputs:
                for output in celda.outputs:
                    if hasattr(output, 'text'):
                        contenido.append(f"# Output (Celda {i})\n{output.text}")

        contenido_completo = "\n\n".join(contenido)
        return [Document(page_content=contenido_completo, metadata={"source": ruta_notebook, "type": "notebook"})]
    except Exception:
        return []

def cargar_docs_de_directorio(ruta_dir, tipos_archivo=(".pdf", ".txt", ".csv"), tipo_fuente="documento"):
    """Carga documentos de un directorio específico (recursivo)."""
    documentos = []

    if not os.path.exists(ruta_dir):
        return documentos

    found_files = []
    for root, _, files in os.walk(ruta_dir):
        for f in files:
            if f.lower().endswith(tipos_archivo):
                found_files.append(os.path.join(root, f))

    for ruta in found_files:
        try:
            if ruta.lower().endswith(".pdf"):
                loader = PyPDFLoader(ruta)
                documentos.extend(loader.load())
            elif ruta.lower().endswith(".txt"):
                loader = TextLoader(ruta, encoding='utf-8')
                documentos.extend(loader.load())
            elif ruta.lower().endswith(".csv"):
                try:
                    with open(ruta, 'r', encoding='utf-8') as f:
                        contenido_csv = f.read()
                    nombre_archivo = os.path.basename(ruta)
                    contenido_con_titulo = f"Archivo: {nombre_archivo}\n\nDatos:\n{contenido_csv}"
                    documentos.append(Document(
                        page_content=contenido_con_titulo,
                        metadata={"source": ruta, "type": "csv", "filename": nombre_archivo}
                    ))
                except Exception:
                    loader = CSVLoader(ruta)
                    documentos.extend(loader.load())
            elif ruta.lower().endswith(".json"):
                try:
                    with open(ruta, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    nombre_archivo = os.path.basename(ruta)
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
                except Exception:
                    pass
        except Exception:
            continue

    return documentos

def cargar_hallazgos_rendimiento(ruta_dir):
    """Carga los JSONs de rendimiento y genera resúmenes estadísticos"""
    documentos = []

    if not os.path.exists(ruta_dir):
        return documentos

    clicks_path = os.path.join(ruta_dir, "clicks_vs_nota.json")
    if os.path.exists(clicks_path):
        try:
            with open(clicks_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            total_estudiantes = len(data)
            clicks = [d['sum_click'] for d in data]
            notas = [d['final_score'] for d in data]
            avg_clicks = sum(clicks) / len(clicks)
            avg_nota = sum(notas) / len(notas)

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
        except Exception:
            pass

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
        except Exception:
            pass

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
        except Exception:
            pass

    return documentos

def cargar_docs():
    """Carga TODOS los documentos importantes del proyecto"""
    all_documents = []

    all_documents.extend(cargar_docs_de_directorio(DOCUMENTS_PATH, tipos_archivo=(".pdf", ".txt"), tipo_fuente="documentos"))

    if os.path.exists(DATA_ANALYSIS_PATH):
        for archivo in os.listdir(DATA_ANALYSIS_PATH):
            if archivo.lower().endswith(".ipynb"):
                ruta_notebook = os.path.join(DATA_ANALYSIS_PATH, archivo)
                all_documents.extend(procesar_notebook(ruta_notebook))

    if os.path.exists(KNOWLEDGE_SOURCES_PATH):
        all_documents.extend(cargar_docs_de_directorio(KNOWLEDGE_SOURCES_PATH, tipos_archivo=(".txt", ".json", ".pdf"), tipo_fuente="knowledge"))

    all_documents.extend(cargar_hallazgos_rendimiento(OUTPUT_RENDIMIENTO_PATH))

    if os.path.exists(DATA_PROCESSED_PATH):
        for archivo in os.listdir(DATA_PROCESSED_PATH):
            if archivo.lower().endswith(".csv"):
                ruta_csv = os.path.join(DATA_PROCESSED_PATH, archivo)
                try:
                    with open(ruta_csv, 'r', encoding='utf-8') as f:
                        contenido = f.read()
                    doc = Document(
                        page_content=f"ESTADISTICAS ECUADOR 2022 - {archivo}\n\n{contenido}",
                        metadata={"source": ruta_csv, "type": "estadisticas_ecuador", "filename": archivo}
                    )
                    all_documents.append(doc)
                except Exception:
                    pass

    csvs_principales = ["studentInfo.csv", "assessments.csv", "studentAssessment.csv", "vle.csv"]
    for csv_name in csvs_principales:
        ruta_csv = os.path.join(DATA_ROOT_PATH, csv_name)
        if os.path.exists(ruta_csv):
            try:
                import pandas as pd
                df = pd.read_csv(ruta_csv, nrows=100)

                resumen = f"DATASET: {csv_name}\n\n"
                resumen += f"Columnas: {', '.join(df.columns.tolist())}\n\n"
                resumen += f"Primeras filas de ejemplo:\n{df.head(10).to_string()}\n\n"
                resumen += f"Estadísticas descriptivas:\n{df.describe().to_string()}\n"

                doc = Document(
                    page_content=resumen,
                    metadata={"source": ruta_csv, "type": "dataset", "filename": csv_name}
                )
                all_documents.append(doc)
            except Exception:
                pass

    uci_path = os.path.join(DATA_RAW_PATH, "dataset_uci.csv")
    if os.path.exists(uci_path):
        try:
            import pandas as pd
            df = pd.read_csv(uci_path, nrows=50)
            resumen = f"DATASET UCI - Datos de desercion universitaria\n\n"
            resumen += f"Columnas: {', '.join(df.columns.tolist())}\n\n"
            resumen += f"Primeras filas:\n{df.head(10).to_string()}\n\n"
            resumen += f"Estadísticas:\n{df.describe().to_string()}\n"

            doc = Document(
                page_content=resumen,
                metadata={"source": uci_path, "type": "dataset_uci", "filename": "dataset_uci.csv"}
            )
            all_documents.append(doc)
        except Exception:
            pass

    all_chunks = text_splitter.split_documents(all_documents)
    return all_chunks

def guardar_en_chroma(chunks):
    """Guarda los chunks en ChromaDB"""
    chunks_validos = []
    for chunk in chunks:
        if len(chunk.page_content) > MAX_CHUNK_LENGTH:
            chunk.page_content = chunk.page_content[:MAX_CHUNK_LENGTH]
        if len(chunk.page_content.strip()) > 0:
            chunks_validos.append(chunk)

    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    batch_size = 200
    for i in range(0, len(chunks_validos), batch_size):
        batch = chunks_validos[i:i+batch_size]

        if i == 0:
            vectorstore = Chroma.from_documents(
                documents=batch,
                embedding=embeddings,
                persist_directory=CHROMA_PATH
            )
        else:
            vectorstore = Chroma(
                persist_directory=CHROMA_PATH,
                embedding_function=embeddings
            )
            vectorstore.add_documents(batch)

    print(f"Base de datos guardada en {CHROMA_PATH}")

if __name__ == "__main__":
    chunks = cargar_docs()
    print(f"Total de chunks: {len(chunks)}")
    guardar_en_chroma(chunks)
    print("Proceso completado.")
