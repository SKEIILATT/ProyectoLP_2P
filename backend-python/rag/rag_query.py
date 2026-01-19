'''
Script de Consulta RAG
Permite hacer preguntas sobre los documentos PDF Procesados
Usa Groq para inferencia rápida en la nube
'''
import argparse
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_groq import ChatGroq
from langchain_core.documents import Document
import pandas as pd
import re
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

CHROMA_PATH = "vectorstore/chroma_db"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Modelos disponibles en Groq (actualizados 2025)
GROQ_MODELS = {
    "llama3": "llama-3.1-8b-instant",
    "llama3-70b": "llama-3.3-70b-versatile",
    "mixtral": "mistral-saba-24b",
    "gemma": "gemma2-9b-it"
}

def cargar_rag():
    """Carga el sistema RAG desde ChromaDB"""
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vector = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )
    return vector

def obtener_estadisticas_rag(vector):
    """
    Obtiene estadísticas sobre el conocimiento almacenado en el RAG

    Args:
        vector: El vector de ChromaDB

    Returns:
        dict con estadísticas del RAG
    """
    try:
        collection = getattr(vector, '_collection', None)
        if collection is None:
            return {"error": "No se pudo acceder a la colección"}

        data = collection.get(include=['metadatas', 'documents'])
        metadatas = data.get('metadatas', [])
        documents = data.get('documents', [])

        # Contar documentos por tipo
        fuentes = {}
        total_chunks = len(documents)

        for meta in metadatas:
            if isinstance(meta, dict):
                source = meta.get('source', 'Desconocido')
                filename = source.split('/')[-1].split('\\')[-1]

                if filename not in fuentes:
                    fuentes[filename] = {
                        'nombre': filename,
                        'chunks': 0,
                        'tipo': 'CSV' if filename.endswith('.csv') else 'Jupyter' if filename.endswith('.ipynb') else 'PDF' if filename.endswith('.pdf') else 'Otro'
                    }
                fuentes[filename]['chunks'] += 1

        # Ordenar por número de chunks
        fuentes_list = sorted(fuentes.values(), key=lambda x: x['chunks'], reverse=True)

        return {
            "total_documentos": len(fuentes),
            "total_chunks": total_chunks,
            "fuentes": fuentes_list,
            "tipos": {
                "csv": len([f for f in fuentes_list if f['tipo'] == 'CSV']),
                "jupyter": len([f for f in fuentes_list if f['tipo'] == 'Jupyter']),
                "pdf": len([f for f in fuentes_list if f['tipo'] == 'PDF']),
                "otros": len([f for f in fuentes_list if f['tipo'] == 'Otro'])
            }
        }
    except Exception as e:
        return {"error": str(e)}

def consultar(query, vector, modelo="llama3"):
    """
    Realiza la consulta RAG sobre los documentos que se han analizado

    Args:
        query: La consulta que se desea hacer sobre los documentos
        vector: El vector de ChromaDB que se ha creado para los documentos
        modelo: El modelo de Groq a utilizar (llama3, llama3-70b, mixtral, gemma)

    Returns:
        dict con keys: result, sources, metadata
    """
    modelo_groq = GROQ_MODELS.get(modelo, "llama-3.1-8b-instant")

    # Inicializar el modelo de Groq (inferencia rápida en la nube)
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model_name=modelo_groq,
        temperature=0.0
    )

    query_lower = query.lower()

    # DETECCION TEMPRANA: Si pregunta sobre Ecuador, estadísticas, tasa, deserción - usar CSVs directamente
    es_pregunta_estadisticas = any(kw in query_lower for kw in [
        'ecuador', '2022', 'tasa', 'desercion', 'deserción',
        'abandonaron', 'matriculados', 'cuantos', 'cuántos',
        'estadistica', 'estadística', 'porcentaje'
    ])

    if es_pregunta_estadisticas:
        csv_answer = answer_from_csvs(query)
        if csv_answer and not csv_answer.startswith("Error"):
            return {
                "result": csv_answer,
                "sources": ["resumen_general_desercion_2022.csv", "desercion_por_sexo.csv", "desercion_por_tipo_institucion.csv"],
                "metadata": {"docs_found": 1, "used_rag_context": True, "csv_direct": True}
            }

    # Configuramos el retriever para obtener documentos relevantes
    retriever = vector.as_retriever(search_kwargs={"k": 5})

    # Obtener documentos relevantes
    docs = []
    try:
        # Si es pregunta de estadísticas, buscar con términos específicos
        if es_pregunta_estadisticas:
            docs = vector.similarity_search("ESTADISTICAS ECUADOR 2022 desercion abandono tasa estudiantes", k=10)
        else:
            docs = vector.similarity_search(query, k=5)
    except Exception:
        pass

    if not docs or len(docs) < 5:
        try:
            collection = getattr(vector, '_collection', None)
            if collection is not None:
                data = collection.get(include=['metadatas', 'documents'])
                metadatas = data.get('metadatas', [])
                documents = data.get('documents', [])

                # Palabras clave para buscar en filenames
                keywords = ['desercion', 'estadistica', 'sexo', '2022']
                matched_indices = []
                for i, m in enumerate(metadatas):
                    if isinstance(m, dict):
                        source = str(m.get('source', '')).lower().replace('ñ', 'n')
                        if any(kw in source for kw in keywords):
                            matched_indices.append(i)

                # Agregar docs encontrados por metadata
                if matched_indices:
                    for i in matched_indices[:20]:
                        docs.append(Document(page_content=documents[i], metadata=metadatas[i]))
        except Exception:
            pass

    if not docs:
        llm_fallback = ChatGroq(
            api_key=GROQ_API_KEY,
            model_name=GROQ_MODELS.get(modelo, "llama-3.1-8b-instant"),
            temperature=0.3
        )
        prompt_general = (
            "Eres un asistente experto en educación y abandono estudiantil. "
            "Responde la siguiente pregunta con tu conocimiento general. "
            "Si la pregunta no está relacionada con educación, responde de manera útil y amigable.\n\n"
            f"Pregunta: {query}\n\n"
            "Respuesta:"
        )
        try:
            resp = llm_fallback.invoke(prompt_general)
            answer = getattr(resp, 'content', str(resp))
        except Exception as e:
            answer = f"Error al procesar: {e}"

        return {
            "result": answer,
            "sources": [],
            "metadata": {"docs_found": 0, "used_rag_context": False, "knowledge_type": "general"}
        }

    # PRIORIZAR CSVs: separar docs CSV y otros, luego ordenar dando preferencia a CSVs
    csv_docs = []
    other_docs = []
    for doc in docs:
        meta = getattr(doc, 'metadata', None) or {}
        source = str(meta.get('source', '')).lower() if isinstance(meta, dict) else ''
        filename = source.split('/')[-1] if source else ''
        is_csv = False
        if isinstance(meta, dict) and str(meta.get('type', '')).lower() == 'csv':
            is_csv = True
        if filename.endswith('.csv') or source.endswith('.csv'):
            is_csv = True
        # También detectar si el contenido empieza con un header tipo 'Archivo: <name>.csv'
        try:
            pc = getattr(doc, 'page_content', '')
            if not is_csv and isinstance(pc, str):
                head = pc.strip()[:200].lower()
                if head.startswith('archivo:') and '.csv' in head:
                    is_csv = True
        except Exception:
            pass

        if is_csv:
            csv_docs.append(doc)
        else:
            other_docs.append(doc)

    # Construir lista priorizada: CSVs primero, luego otros (limitar a 3 para tinyllama)
    docs = (csv_docs + other_docs)[:3]

    # FILTRAR documentos: priorizar los que contienen palabras clave
    palabras_clave = ['desercion', 'abandono', 'tasa', 'estudiantes', 'matriculados']
    docs_relevantes = []
    for doc in docs:
        content_lower = getattr(doc, 'page_content', '').lower()
        coincidencias = sum(1 for kw in palabras_clave if kw in content_lower)
        if coincidencias >= 1:
            docs_relevantes.append((doc, coincidencias))

    # Si hay docs con coincidencias, ordenar por coincidencias y tomar top 3
    if docs_relevantes:
        docs_relevantes.sort(key=lambda x: x[1], reverse=True)
        docs_final = [doc for doc, _ in docs_relevantes[:3]]
    else:
        # fallback: tomar primeros 3 priorizados
        docs_final = docs[:3]

    # Extraer fuentes únicas de los documentos utilizados
    sources = []
    for doc in docs_final:
        meta = getattr(doc, 'metadata', {}) or {}
        if isinstance(meta, dict):
            source = meta.get('source', '')
            if source:
                # Extraer solo el nombre del archivo
                filename = source.split('/')[-1].split('\\')[-1]
                if filename not in sources:
                    sources.append(filename)

    # Combinamos el contexto de los documentos (limitado para tinyllama)
    context = "\n\n".join([getattr(doc, 'page_content', str(doc)) for doc in docs_final])[:1500]

    # Creamos el prompt completo - Permite respuesta híbrida RAG + conocimiento general
    prompt_text = (
        "Eres un asistente experto en educación y abandono estudiantil. "
        "Usa PRIMERO la información del contexto proporcionado para responder. "
        "Si el contexto tiene información relevante, basa tu respuesta en él. "
        "Si el contexto NO tiene suficiente información, puedes complementar con tu conocimiento general, "
        "pero indica claramente qué parte viene de los datos y qué parte es conocimiento general.\n\n"
        "Contexto de documentos:\n"
        f"{context}\n\n"
        f"Pregunta: {query}\n\n"
        "Respuesta:"
    )

    # Ejecutamos la consulta con el LLM
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

    # Solo usar fallback de CSVs si la respuesta está completamente vacía
    if isinstance(answer, str) and answer.strip() == "":
        csv_ans = answer_from_csvs(query)
        if csv_ans:
            return {
                "result": csv_ans,
                "sources": ["resumen_general_desercion_2022.csv", "desercion_por_sexo.csv", "desercion_por_tipo_institucion.csv"],
                "metadata": {"fallback": True, "docs_found": len(docs_final)}
            }

    # Determinar si la respuesta usó contexto RAG o conocimiento general
    used_rag_context = len(docs_final) > 0 and len(context.strip()) > 100

    return {
        "result": answer,
        "sources": sources,
        "metadata": {
            "docs_found": len(docs_final),
            "used_rag_context": used_rag_context,
            "csv_docs": len([d for d in docs_final if any(x in str(getattr(d, 'metadata', {}).get('source', '')).lower() for x in ['.csv'])]),
            "other_docs": len([d for d in docs_final if not any(x in str(getattr(d, 'metadata', {}).get('source', '')).lower() for x in ['.csv'])])
        }
    }

def generar_insights(vector, modelo="llama3"):
    """
    Genera insights automáticos analizando todos los datos disponibles en el RAG
    """

    modelo_groq = GROQ_MODELS.get(modelo, "llama-3.1-8b-instant")
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model_name=modelo_groq,
        temperature=0.2
    )

    # Obtener documentos globales del RAG (no dependiente de query)
    try:
        collection = getattr(vector, "_collection", None)
        if collection is None:
            docs = []
        else:
            data = collection.get(include=["documents", "metadatas"])
            raw_docs = zip(
            data.get("documents", []),
            data.get("metadatas", [])
        )

        docs = []
        seen_sources = set()

        for doc, meta in raw_docs:
            source = meta.get("source") if meta else None

            if source and source not in seen_sources:
                docs.append(Document(page_content=doc, metadata=meta))
                seen_sources.add(source)

            if len(docs) >= 5:  # 1 PDF ≈ 1 aporte
                break

    except Exception:
        docs = []


    if not docs:
        return {
            "success": False,
            "insights": [],
            "error": "No hay suficientes datos para generar insights"
        }

    # Combinar contexto
    context = "\n\n".join([getattr(doc, 'page_content', str(doc)) for doc in docs])[:4000]

    prompt = f"""Analiza los siguientes datos sobre abandono estudiantil y encuentra los 3 hallazgos más importantes y sorprendentes.

Contexto:
{context}

Instrucciones:
- Identifica patrones, correlaciones o hallazgos clave
- Presenta cada hallazgo en una oración clara y concisa
- Enfócate en información cuantitativa y específica
- Evita generalidades, proporciona números exactos cuando sea posible

Responde con exactamente 3 hallazgos, uno por línea, numerados 1., 2., 3.

Hallazgos:"""

    try:
        resp = llm.invoke(prompt)
        answer = getattr(resp, 'content', str(resp))

        # Parsear insights
        lines = [l.strip() for l in answer.split('\n') if l.strip()]
        insights = []
        for line in lines:
            # Remover numeración si existe
            clean = re.sub(r'^\d+[\.\)]\s*', '', line)
            if clean and len(clean) > 20:
                insights.append(clean)

        return {
            "success": True,
            "insights": insights[:3],
            "sources": list(set([getattr(doc, 'metadata', {}).get('source', '').split('/')[-1] for doc in docs if getattr(doc, 'metadata', {}).get('source')]))
        }
    except Exception as e:
        return {
            "success": False,
            "insights": [],
            "error": str(e)
        }

def answer_from_csvs(query):
    """Responde consultas sobre estadísticas de Ecuador directamente desde los CSVs procesados."""
    base = "../data/processed/estadisticas_ecuador"
    try:
        resumen_path = os.path.join(base, "resumen_general_desercion_2022.csv")
        sexo_path = os.path.join(base, "desercion_por_sexo.csv")
        tipo_path = os.path.join(base, "desercion_por_tipo_institucion.csv")

        q = query.lower()

        # Tasa de deserción general
        if re.search(r"tasa|porcentaje", q) and re.search(r"desercion|deserción|abandon", q):
            if os.path.exists(resumen_path):
                df = pd.read_csv(resumen_path)
                if 'Indicador' in df.columns and 'Valor' in df.columns:
                    # Buscar tasa de deserción
                    row_tasa = df[df['Indicador'].str.contains('Tasa de Deserción', case=False, na=False)]
                    row_total = df[df['Indicador'].str.contains('Total Estudiantes Matriculados', case=False, na=False)]
                    row_abandon = df[df['Indicador'].str.contains('Total Estudiantes que Abandonaron', case=False, na=False)]

                    respuesta = "Según los datos de Ecuador 2022:\n"
                    if not row_tasa.empty:
                        respuesta += f"- Tasa de Deserción: {row_tasa['Valor'].iloc[0]}%\n"
                    if not row_total.empty:
                        respuesta += f"- Total Estudiantes Matriculados: {int(row_total['Valor'].iloc[0]):,}\n"
                    if not row_abandon.empty:
                        respuesta += f"- Total Estudiantes que Abandonaron: {int(row_abandon['Valor'].iloc[0]):,}\n"

                    row_ret = df[df['Indicador'].str.contains('Tasa de Retención', case=False, na=False)]
                    if not row_ret.empty:
                        respuesta += f"- Tasa de Retención: {row_ret['Valor'].iloc[0]}%"

                    return respuesta

        # Total abandonaron
        if re.search(r"cuant[oa]|cuánt[oa]|numero|número|total", q) and re.search(r"abandon|desercion|deserción", q):
            if os.path.exists(resumen_path):
                df = pd.read_csv(resumen_path)
                if 'Indicador' in df.columns and 'Valor' in df.columns:
                    row = df[df['Indicador'].str.contains('Total Estudiantes que Abandonaron', case=False, na=False)]
                    if not row.empty:
                        val = int(row['Valor'].iloc[0])
                        row_total = df[df['Indicador'].str.contains('Total Estudiantes Matriculados', case=False, na=False)]
                        total = int(row_total['Valor'].iloc[0]) if not row_total.empty else None
                        if total:
                            return f"En Ecuador 2022, abandonaron {val:,} estudiantes de un total de {total:,} matriculados."
                        return f"En Ecuador 2022, abandonaron {val:,} estudiantes."
                return "No pude leer el resumen de abandono correctamente."

        # Desercion por sexo
        if 'sexo' in q or 'mujer' in q or 'hombre' in q or 'genero' in q or 'género' in q:
            if os.path.exists(sexo_path):
                df = pd.read_csv(sexo_path)
                lines = ["Deserción por sexo en Ecuador 2022:"]
                for _, r in df.iterrows():
                    s = r.iloc[0]
                    aban = r.iloc[1]
                    total = r.iloc[2] if len(r) > 2 else None
                    tasa = r.iloc[3] if len(r) > 3 else None
                    if tasa:
                        lines.append(f"- {s}: {int(aban):,} abandonaron de {int(total):,} matriculados (tasa: {tasa}%)")
                    else:
                        lines.append(f"- {s}: {int(aban):,} abandonaron")
                return "\n".join(lines)

        # Desercion por tipo de institucion
        if 'tipo' in q or 'institucion' in q or 'institución' in q:
            if os.path.exists(tipo_path):
                df = pd.read_csv(tipo_path)
                lines = ["Deserción por tipo de institución en Ecuador 2022:"]
                for _, r in df.iterrows():
                    lines.append("- " + " - ".join([str(x) for x in r.values]))
                return "\n".join(lines[:20])

        # Pregunta general sobre estadísticas Ecuador
        if 'ecuador' in q or '2022' in q:
            if os.path.exists(resumen_path):
                df = pd.read_csv(resumen_path)
                if 'Indicador' in df.columns and 'Valor' in df.columns:
                    respuesta = "Resumen de deserción estudiantil en Ecuador 2022:\n"
                    for _, row in df.iterrows():
                        indicador = row['Indicador']
                        valor = row['Valor']
                        if pd.notna(valor):
                            if 'Tasa' in indicador or '%' in str(indicador):
                                respuesta += f"- {indicador}: {valor}%\n"
                            else:
                                try:
                                    respuesta += f"- {indicador}: {int(valor):,}\n"
                                except ValueError:
                                    respuesta += f"- {indicador}: {valor}\n"
                    return respuesta.strip()

    except Exception as e:
        return f"Error leyendo CSVs: {e}"

    return None

def main():
    """Función principal para ejecución CLI"""
    parser = argparse.ArgumentParser(description="Consulta documentos procesados usando RAG")
    parser.add_argument("pregunta", type=str, help="La pregunta sobre los documentos")
    parser.add_argument("--modelo", type=str, default="llama3", help="Modelo a usar")

    args = parser.parse_args()
    vectorstore = cargar_rag()

    try:
        resultado = consultar(args.pregunta, vectorstore, args.modelo)
        print(resultado["result"])
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
