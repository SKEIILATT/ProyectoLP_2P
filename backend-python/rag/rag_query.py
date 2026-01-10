'''
Script de Consulta RAG
Permite hacer preguntas sobre los documentos PDF Procesados
'''
import argparse
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.documents import Document
import pandas as pd
import re
import os

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

def consultar(query, vector, modelo_ollama="mistral"):
    """
    Realiza la consulta RAG sobre los documentos que se han analizado

    Args:
        query: La consulta que se desea hacer sobre los documentos
        vector: El vector de ChromaDB que se ha creado para los documentos
        modelo_ollama: El modelo ollama que se ha utilizado para la consulta

    Returns:
        dict con keys: result, sources, metadata
    """
    print(f"Generando respuesta con modelo {modelo_ollama}")

    # Aquí inicializo el modelo de IA que se va a utilizar para las consultas
    # El parámetro temperature=0.0 es para que la respuesta sea más precisa
    llm = ChatOllama(model=modelo_ollama, temperature=0.0)

    # Configuramos el retriever para obtener un conjunto amplio de documentos
    retriever = vector.as_retriever(search_kwargs={"k": 30})

    # Obtener documentos relevantes — pedimos más resultados para luego priorizar CSVs
    docs = []
    try:
        # Pedimos más documentos (k=30) y luego priorizamos CSVs en el ordering
        docs = vector.similarity_search(query, k=30)
    except Exception as e:
        print(f"  similarity_search falló: {e}")

    # Fallback: búsqueda explícita por metadatas (filenames con palabras clave)
    if not docs or len(docs) < 5:
        print(f"  Solo {len(docs) if docs else 0} docs encontrados, buscando por metadatas...")
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
                    for i in matched_indices[:20]:  # Limitar a 20
                        docs.append(Document(page_content=documents[i], metadata=metadatas[i]))
        except Exception as e:
            print(f"  Metadata search falló: {e}")

    if not docs:
        return {
            "result": "No tengo suficiente información.",
            "sources": [],
            "metadata": {"docs_found": 0}
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

    # Construir lista priorizada: CSVs primero, luego otros (limitar a 10-15 para prompt)
    docs = (csv_docs + other_docs)[:15]

    # FILTRAR documentos: priorizar los que contienen palabras clave
    palabras_clave = ['desercion', 'abandono', 'tasa', 'estudiantes', 'matriculados']
    docs_relevantes = []
    for doc in docs:
        content_lower = getattr(doc, 'page_content', '').lower()
        coincidencias = sum(1 for kw in palabras_clave if kw in content_lower)
        if coincidencias >= 1:
            docs_relevantes.append((doc, coincidencias))

    # Si hay docs con coincidencias, ordenar por coincidencias y tomar top 5
    if docs_relevantes:
        docs_relevantes.sort(key=lambda x: x[1], reverse=True)
        docs_final = [doc for doc, _ in docs_relevantes[:5]]
    else:
        # fallback: tomar primeros 5 priorizados
        docs_final = docs[:5]

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

    # Combinamos el contexto de los documentos (seguro ante diferentes shapes)
    context = "\n\n".join([getattr(doc, 'page_content', str(doc)) for doc in docs_final])[:3000]

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

    # Si el LLM indica que no tiene suficiente información, usar el fallback determinista sobre CSVs
    if isinstance(answer, str) and (
        "no tengo suficiente información" in answer.lower() or
        "no tengo suficiente" in answer.lower() or
        "no tengo" in answer.lower() or
        answer.strip() == ""
    ):
        csv_ans = answer_from_csvs(query)
        if csv_ans:
            return {
                "result": csv_ans,
                "sources": ["resumen_general_desercion_2022.csv", "desercion_por_sexo.csv", "desercion_por_tipo_institucion.csv"],
                "metadata": {"fallback": True, "docs_found": len(docs_final)}
            }

    return {
        "result": answer,
        "sources": sources,
        "metadata": {
            "docs_found": len(docs_final),
            "csv_docs": len([d for d in docs_final if any(x in str(getattr(d, 'metadata', {}).get('source', '')).lower() for x in ['.csv'])]),
            "other_docs": len([d for d in docs_final if not any(x in str(getattr(d, 'metadata', {}).get('source', '')).lower() for x in ['.csv'])])
        }
    }

def generar_insights(vector, modelo_ollama="mistral"):
    """
    Genera insights automáticos analizando todos los datos disponibles en el RAG

    Args:
        vector: El vector de ChromaDB con los documentos
        modelo_ollama: El modelo ollama a utilizar

    Returns:
        dict con insights encontrados
    """
    print("Generando insights automáticos...")

    llm = ChatOllama(model=modelo_ollama, temperature=0.2)

    # Obtener documentos clave
    try:
        docs = vector.similarity_search("estadísticas abandono deserción factores riesgo becas rendimiento", k=10)
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
    """Intentar responder consultas frecuentes directamente desde los CSVs procesados.
    Maneja preguntas como: total abandonaron, por sexo, tasa de deserción, por tipo de institución.
    """
    base = "../data/processed/estadisticas_ecuador"
    try:
        resumen_path = os.path.join(base, "resumen_general_desercion_2022.csv")
        sexo_path = os.path.join(base, "desercion_por_sexo.csv")
        tipo_path = os.path.join(base, "desercion_por_tipo_institucion.csv")

        q = query.lower()

        # Total abandonaron
        if re.search(r"cuant[oa]|cuánt[oa]|numero|número", q) and re.search(r"abandon|desercion", q):
            if os.path.exists(resumen_path):
                df = pd.read_csv(resumen_path)
                # Buscar la fila 'Total Estudiantes que Abandonaron' o columna equivalente
                if 'Indicador' in df.columns and 'Valor' in df.columns:
                    row = df[df['Indicador'].str.contains('Total Estudiantes que Abandonaron', case=False, na=False)]
                    if not row.empty:
                        val = int(row['Valor'].iloc[0])
                        return f"En 2022 abandonaron {val} estudiantes (según resumen_general_desercion_2022.csv)."
                # fallback: sumar si hay columna
                return "No pude leer el resumen de abandono correctamente."

        # Desercion por sexo
        if 'sexo' in q or 'mujer' in q or 'hombre' in q:
            if os.path.exists(sexo_path):
                df = pd.read_csv(sexo_path)
                # Normalizar columnas
                cols = [c.lower() for c in df.columns]
                # Buscar filas por sexo
                lines = []
                for _, r in df.iterrows():
                    s = r.iloc[0]
                    aban = r.iloc[1]
                    total = r.iloc[2] if len(r) > 2 else None
                    lines.append(f"{s}: {int(aban)} abandonaron de {int(total)} matriculados (tasa: {r.iloc[3]}%)")
                return "; ".join(lines)

        # Desercion por tipo de institucion
        if 'tipo' in q or 'institucion' in q:
            if os.path.exists(tipo_path):
                df = pd.read_csv(tipo_path)
                # convertir a texto simple
                items = []
                for _, r in df.iterrows():
                    items.append(" - ".join([str(x) for x in r.values]))
                return "\n".join(items[:20])

    except Exception as e:
        return f"Error leyendo CSVs: {e}"

    return None

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
        default="mistral",
        help="Modelo de Ollama a usar (default: mistral). Ejemplos: llama3, llama3.1, mistral, etc."
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
