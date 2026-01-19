import { useState, useEffect } from 'react';
import axios from 'axios';

interface Fuente {
  nombre: string;
  chunks: number;
  tipo: string;
}

interface RagStats {
  total_documentos: number;
  total_chunks: number;
  fuentes: Fuente[];
  tipos: {
    csv: number;
    jupyter: number;
    pdf: number;
    otros: number;
  };
}

interface InsightsData {
  insights: string[];
  sources: string[];
}


export default function RagKnowledgeBase() {
  const [stats, setStats] = useState<RagStats | null>(null);
  const [insights, setInsights] = useState<InsightsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [insightsLoading, setInsightsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/api/rag/stats');

      if (response.data.error) {
        setError(response.data.error);
      } else {
        setStats(response.data);
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Error al cargar estadísticas del RAG');
    } finally {
      setLoading(false);
    }
  };

  const fetchInsights = async () => {
    try {
      setInsightsLoading(true);
      const response = await axios.post('http://localhost:5000/api/rag/insights', {
        modelo: 'mistral'
      });

      if (response.data.error) {
        console.error('Error en insights:', response.data.error);
      } else {
        setInsights(response.data);
      }
    } catch (err: any) {
      console.error('Error al generar insights:', err);
    } finally {
      setInsightsLoading(false);
    }
  };

  const getTipoColor = (tipo: string) => {
    switch (tipo) {
      case 'CSV':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'Jupyter':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'PDF':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 py-8 px-4 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando base de conocimiento...</p>
        </div>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="min-h-screen bg-gray-100 py-8 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h2 className="text-xl font-bold text-red-800 mb-2">Error al cargar datos</h2>
            <p className="text-red-600">{error || 'No se pudo conectar con el servicio RAG'}</p>
            <button
              onClick={fetchStats}
              className="mt-4 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
            >
              Reintentar
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Base de Conocimiento RAG</h1>
          <p className="text-gray-600">Documentos y datos indexados para consultas con IA</p>
        </div>

        {/* KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-blue-500">
            <p className="text-sm font-medium text-gray-600">Total Documentos</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total_documentos}</p>
            <p className="text-sm text-gray-500 mt-1">Archivos únicos</p>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-purple-500">
            <p className="text-sm font-medium text-gray-600">Total Fragmentos</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total_chunks.toLocaleString()}</p>
            <p className="text-sm text-gray-500 mt-1">Chunks vectorizados</p>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-green-500">
            <p className="text-sm font-medium text-gray-600">Promedio por Documento</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">
              {Math.round(stats.total_chunks / stats.total_documentos)}
            </p>
            <p className="text-sm text-gray-500 mt-1">Chunks promedio</p>
          </div>
        </div>

        {/* Distribución por tipo */}
        <div className="bg-white rounded-xl shadow-md p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Distribución por Tipo de Documento</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
              <p className="text-sm font-medium text-green-700">CSV</p>
              <p className="text-2xl font-bold text-green-900 mt-1">{stats.tipos.csv}</p>
            </div>
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 text-center">
              <p className="text-sm font-medium text-orange-700">Jupyter Notebooks</p>
              <p className="text-2xl font-bold text-orange-900 mt-1">{stats.tipos.jupyter}</p>
            </div>
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
              <p className="text-sm font-medium text-red-700">PDF</p>
              <p className="text-2xl font-bold text-red-900 mt-1">{stats.tipos.pdf}</p>
            </div>
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
              <p className="text-sm font-medium text-gray-700">Otros</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{stats.tipos.otros}</p>
            </div>
          </div>
        </div>

        {/* Lista de fuentes */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Fuentes de Datos Disponibles</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Documento
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Tipo
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Fragmentos
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Porcentaje
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {stats.fuentes.map((fuente, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{fuente.nombre}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full border ${getTipoColor(fuente.tipo)}`}>
                        {fuente.tipo}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{fuente.chunks.toLocaleString()}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-32 bg-gray-200 rounded-full h-2 mr-2">
                          <div
                            className="bg-purple-600 h-2 rounded-full"
                            style={{ width: `${(fuente.chunks / stats.total_chunks) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-600">
                          {((fuente.chunks / stats.total_chunks) * 100).toFixed(1)}%
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Sección de Insights/Hallazgos */}
        <div className="bg-white rounded-xl shadow-md p-6 mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-gray-900">Hallazgos e Insights</h2>
              <p className="text-gray-600 text-sm mt-1">
                Análisis automático generado por IA sobre los datos indexados
              </p>
            </div>
            <button
              onClick={fetchInsights}
              disabled={insightsLoading}
              className={`px-6 py-3 rounded-lg font-medium transition-all flex items-center space-x-2 ${
                insightsLoading
                  ? 'bg-gray-300 cursor-not-allowed'
                  : 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700 shadow-md hover:shadow-lg'
              }`}
            >
              {insightsLoading ? (
                <>
                  <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Generando...</span>
                </>
              ) : (
                <>
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  <span>Generar Insights</span>
                </>
              )}
            </button>
          </div>

          {!insights && !insightsLoading && (
            <div className="text-center py-12 bg-gray-50 rounded-xl border-2 border-dashed border-gray-200">
              <svg className="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Sin insights generados</h3>
              <p className="text-gray-500 max-w-md mx-auto">
                Haz clic en "Generar Insights" para que la IA analice los documentos indexados y extraiga los hallazgos más relevantes.
              </p>
            </div>
          )}

          {insights && insights.insights.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center space-x-2 text-sm text-gray-500 mb-4">
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span>Basado en {insights.sources.length} fuentes analizadas</span>
              </div>

              {insights.insights.map((insight, index) => (
                <div
                  key={index}
                  className="bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-100 rounded-xl p-5 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0">
                      <div className="w-10 h-10 bg-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                        {index + 1}
                      </div>
                    </div>
                    <div className="flex-1">
                      <p className="text-gray-800 leading-relaxed">{insight}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Información adicional */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">Acerca de esta base de conocimiento</h3>
          <p className="text-blue-800 text-sm leading-relaxed">
            Este sistema RAG utiliza ChromaDB para almacenar y recuperar información vectorizada. Cada documento se divide en fragmentos (chunks)
            que son convertidos a embeddings utilizando el modelo nomic-embed-text. Cuando realizas una consulta, el sistema busca los fragmentos
            más relevantes y los utiliza como contexto para que el modelo de lenguaje (Mistral) genere respuestas precisas basadas en tus datos.
          </p>
        </div>
      </div>
    </div>
  );
}
