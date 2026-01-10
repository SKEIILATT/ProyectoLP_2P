"""
API REST para el Sistema RAG
Expone el sistema de consultas RAG como servicio HTTP
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from rag_query import cargar_rag, consultar, generar_insights, obtener_estadisticas_rag
import os

app = Flask(__name__)
CORS(app)  # Permitir CORS para que React y Laravel puedan consumir la API

# Cargar el sistema RAG al iniciar la aplicación
print("Inicializando sistema RAG...")
vectorstore = None

try:
    vectorstore = cargar_rag()
    print("Sistema RAG cargado exitosamente")
except Exception as e:
    print(f"Error al cargar RAG: {e}")

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de salud para verificar que el servicio está activo"""
    return jsonify({
        'status': 'ok',
        'rag_loaded': vectorstore is not None,
        'service': 'RAG-EDU API'
    })

@app.route('/api/rag/query', methods=['POST'])
def query():
    """
    Endpoint principal para realizar consultas al RAG

    Request body:
    {
        "pregunta": "¿Cuántos estudiantes abandonaron en 2022?",
        "modelo": "mistral" (opcional, default: mistral)
    }

    Response:
    {
        "pregunta": "...",
        "respuesta": "...",
        "modelo": "mistral",
        "success": true
    }
    """
    try:
        # Validar que el RAG esté cargado
        if vectorstore is None:
            return jsonify({
                'success': False,
                'error': 'Sistema RAG no inicializado. Verifica que ChromaDB existe.'
            }), 503

        # Obtener datos del request
        data = request.get_json()

        if not data or 'pregunta' not in data:
            return jsonify({
                'success': False,
                'error': 'El campo "pregunta" es requerido'
            }), 400

        pregunta = data['pregunta']
        modelo = data.get('modelo', 'mistral')

        # Validar que la pregunta no esté vacía
        if not pregunta.strip():
            return jsonify({
                'success': False,
                'error': 'La pregunta no puede estar vacía'
            }), 400

        # Realizar la consulta
        resultado = consultar(pregunta, vectorstore, modelo)

        return jsonify({
            'success': True,
            'pregunta': pregunta,
            'respuesta': resultado['result'],
            'sources': resultado.get('sources', []),
            'metadata': resultado.get('metadata', {}),
            'modelo': modelo
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al procesar la consulta: {str(e)}'
        }), 500

@app.route('/api/rag/models', methods=['GET'])
def models():
    """Devuelve la lista de modelos disponibles en Ollama"""
    return jsonify({
        'models': [
            {'id': 'mistral', 'name': 'Mistral', 'description': 'Modelo rápido y preciso'},
            {'id': 'llama3', 'name': 'Llama 3', 'description': 'Modelo de Meta AI'},
            {'id': 'llama3.1', 'name': 'Llama 3.1', 'description': 'Versión mejorada de Llama 3'}
        ]
    })

@app.route('/api/rag/insights', methods=['POST'])
def insights():
    """
    Genera insights automáticos analizando todos los datos del RAG

    Request body:
    {
        "modelo": "mistral" (opcional)
    }

    Response:
    {
        "success": true,
        "insights": ["hallazgo 1", "hallazgo 2", "hallazgo 3"],
        "sources": ["archivo1.csv", "archivo2.ipynb"]
    }
    """
    try:
        if vectorstore is None:
            return jsonify({
                'success': False,
                'error': 'Sistema RAG no inicializado'
            }), 503

        data = request.get_json() or {}
        modelo = data.get('modelo', 'mistral')

        resultado = generar_insights(vectorstore, modelo)

        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/rag/stats', methods=['GET'])
def stats():
    """
    Obtiene estadísticas sobre el conocimiento almacenado en el RAG

    Response:
    {
        "total_documentos": 10,
        "total_chunks": 245,
        "fuentes": [{nombre, chunks, tipo}],
        "tipos": {csv: 5, jupyter: 2, pdf: 3}
    }
    """
    try:
        if vectorstore is None:
            return jsonify({
                'error': 'Sistema RAG no inicializado'
            }), 503

        estadisticas = obtener_estadisticas_rag(vectorstore)

        return jsonify(estadisticas)

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("="*80)
    print("RAG-EDU API Server")
    print("="*80)
    print("Endpoints disponibles:")
    print("  GET  /health              - Estado del servicio")
    print("  POST /api/rag/query       - Consultar al RAG")
    print("  POST /api/rag/insights    - Generar insights automáticos")
    print("  GET  /api/rag/stats       - Estadísticas del conocimiento")
    print("  GET  /api/rag/models      - Modelos disponibles")
    print("="*80)
    print("\nIniciando servidor en http://localhost:5000")
    print("Presiona Ctrl+C para detener\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
