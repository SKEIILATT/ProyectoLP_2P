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

export default function RagKnowledgeBase() {
  const [stats, setStats] = useState<RagStats | null>(null);
  const [loading, setLoading] = useState(true);
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

        {/* Información adicional */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
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
