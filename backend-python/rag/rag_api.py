"""
API REST para el Sistema RAG
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from rag_query import cargar_rag, consultar, generar_insights, obtener_estadisticas_rag

app = Flask(__name__)
CORS(app)

vectorstore = None

try:
    vectorstore = cargar_rag()
except Exception:
    pass

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
    """Endpoint principal para realizar consultas al RAG"""
    try:
        if vectorstore is None:
            return jsonify({
                'success': False,
                'error': 'Sistema RAG no inicializado. Verifica que ChromaDB existe.'
            }), 503

        data = request.get_json()

        if not data or 'pregunta' not in data:
            return jsonify({
                'success': False,
                'error': 'El campo "pregunta" es requerido'
            }), 400

        pregunta = data['pregunta']
        modelo = data.get('modelo', 'llama3')

        if not pregunta.strip():
            return jsonify({
                'success': False,
                'error': 'La pregunta no puede estar vacía'
            }), 400

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
    """Devuelve la lista de modelos disponibles en Groq"""
    return jsonify({
        'models': [
            {'id': 'llama3', 'name': 'Llama 3.1 (8B)', 'description': 'Modelo rápido y eficiente'},
            {'id': 'llama3-70b', 'name': 'Llama 3.3 (70B)', 'description': 'Modelo más potente'},
            {'id': 'mixtral', 'name': 'Mistral Saba 24B', 'description': 'Modelo de Mistral AI'},
            {'id': 'gemma', 'name': 'Gemma 2 (9B)', 'description': 'Modelo de Google'}
        ]
    })

@app.route('/api/rag/insights', methods=['POST'])
def insights():
    """Genera insights automáticos analizando todos los datos del RAG"""
    try:
        if vectorstore is None:
            return jsonify({
                'success': False,
                'error': 'Sistema RAG no inicializado'
            }), 503

        data = request.get_json() or {}
        modelo = data.get('modelo', 'llama3')

        resultado = generar_insights(vectorstore, modelo)

        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/rag/stats', methods=['GET'])
def stats():
    """Obtiene estadísticas sobre el conocimiento almacenado en el RAG"""
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
    app.run(host='0.0.0.0', port=5000, debug=True)
