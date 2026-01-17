import { useEffect, useState, useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ScatterChart,
  Scatter,
  ResponsiveContainer
} from 'recharts';

interface RendimientoPorMateria {
  code_module: string;
  average_score?: number;
}

interface ClicksVsNota {
  id_student: number;
  sum_click?: number;
  final_score?: number;
}

interface EvaluacionesVsNota {
  id_student: number;
  num_assessments?: number;
  final_score?: number;
}

interface RendimientoGeneral {
  rendimiento_por_materia: RendimientoPorMateria[];
  clicks_vs_nota: ClicksVsNota[];
  evaluaciones_vs_nota: EvaluacionesVsNota[];
}

export default function RendimientoDashboard() {
  const [data, setData] = useState<RendimientoGeneral | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8000/api/rendimiento/general');
        if (!response.ok) throw new Error('Error en la respuesta del servidor');
        const result = await response.json();
        setData(result.data);
        setError(null);
      } catch (err) {
        setError('Error al cargar los datos. Verifica que el servidor esté corriendo.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Optimización 1: Usar useMemo para cálculos pesados
  const kpis = useMemo(() => {
    if (!data) return { totalMaterias: 0, promedioGeneral: 0, totalEstudiantes: 0 };
    
    const totalMaterias = data.rendimiento_por_materia.length;
    const promedioGeneral = data.rendimiento_por_materia.reduce(
      (acc, m) => acc + (m.average_score || 0), 
      0
    ) / (totalMaterias || 1);
    const totalEstudiantes = data.clicks_vs_nota.length;

    return { totalMaterias, promedioGeneral, totalEstudiantes };
  }, [data]);

  // Optimización 2: Samplear datos para scatter plots (muestra representativa)
  const evaluacionesScatterData = useMemo(() => {
    if (!data) return [];
    
    const filtered = data.evaluaciones_vs_nota
      .filter(item => item.num_assessments != null && item.final_score != null)
      .map(item => ({
        x: item.num_assessments,
        y: item.final_score,
        id_student: item.id_student
      }));

    // Si hay más de 500 puntos, tomar una muestra representativa
    if (filtered.length > 500) {
      const step = Math.ceil(filtered.length / 500);
      return filtered.filter((_, index) => index % step === 0);
    }
    
    return filtered;
  }, [data]);

  const clicksScatterData = useMemo(() => {
    if (!data) return [];
    
    const filtered = data.clicks_vs_nota
      .filter(item => item.sum_click != null && item.final_score != null)
      .map(item => ({
        x: item.sum_click,
        y: item.final_score,
        id_student: item.id_student
      }));

    // Si hay más de 500 puntos, tomar una muestra representativa
    if (filtered.length > 500) {
      const step = Math.ceil(filtered.length / 500);
      return filtered.filter((_, index) => index % step === 0);
    }
    
    return filtered;
  }, [data]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 text-lg">Cargando datos...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="bg-red-50 border-l-4 border-red-500 p-6 rounded-lg shadow-md max-w-md">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-red-800 font-medium">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Dashboard de Rendimiento</h1>
          <p className="text-gray-600">Análisis y visualización de desempeño estudiantil</p>
        </div>

        {/* KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-blue-500 hover:shadow-lg transition-shadow">
            <p className="text-sm font-medium text-gray-600 uppercase tracking-wide">Total Materias</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{kpis.totalMaterias}</p>
          </div>
          <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-green-500 hover:shadow-lg transition-shadow">
            <p className="text-sm font-medium text-gray-600 uppercase tracking-wide">Promedio General</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{kpis.promedioGeneral.toFixed(2)}</p>
          </div>
          <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-purple-500 hover:shadow-lg transition-shadow">
            <p className="text-sm font-medium text-gray-600 uppercase tracking-wide">Total Estudiantes</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{kpis.totalEstudiantes}</p>
          </div>
        </div>

        {/* Gráfico de Barras - Promedio por Materia */}
        <div className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Promedio de notas por materia</h2>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={data.rendimiento_por_materia}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="code_module"
                tick={{ fontSize: 14 }}
                label={{ value: 'Materia', position: 'insideBottom', offset: -5, style: { fontWeight: 600 } }}
              />
              <YAxis 
                label={{ value: 'Promedio de notas', angle: -90, position: 'insideLeft', style: { fontWeight: 600 } }}
              />
              <Tooltip 
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                formatter={(value: any) => [value.toFixed(2), 'Promedio']}
              />
              <Bar dataKey="average_score" fill="#1e88e5" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Gráficos de Dispersión */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Evaluaciones vs Nota Final */}
          <div className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Relación entre evaluaciones rendidas y nota final</h2>
            {evaluacionesScatterData.length < data.evaluaciones_vs_nota.length && (
              <p className="text-xs text-gray-500 mb-2">
                Mostrando muestra representativa de {evaluacionesScatterData.length} de {data.evaluaciones_vs_nota.length} estudiantes
              </p>
            )}
            <ResponsiveContainer width="100%" height={400}>
              <ScatterChart margin={{ top: 20, right: 20, bottom: 40, left: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis
                  type="number"
                  dataKey="x"
                  name="Evaluaciones"
                  domain={[0, 'auto']}
                  label={{ value: 'Número de evaluaciones rendidas', position: 'insideBottom', offset: -15, style: { fontWeight: 600, fontSize: 12 } }}
                />
                <YAxis
                  type="number"
                  dataKey="y"
                  name="Nota"
                  domain={[0, 100]}
                  label={{ value: 'Nota final', angle: -90, position: 'insideLeft', style: { fontWeight: 600, fontSize: 12 } }}
                />
                <Tooltip
                  cursor={{ strokeDasharray: '3 3' }}
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '10px' }}
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      return (
                        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-md">
                          <p className="font-semibold text-gray-900">Est. #{payload[0].payload.id_student}</p>
                          <p className="text-sm text-gray-600">Evaluaciones: {payload[0].payload.x}</p>
                          <p className="text-sm text-gray-600">Nota: {payload[0].payload.y}</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Scatter
                  data={evaluacionesScatterData}
                  fill="#1e88e5"
                  fillOpacity={0.6}
                  isAnimationActive={false}
                />
              </ScatterChart>
            </ResponsiveContainer>
          </div>

          {/* Clicks vs Nota Final */}
          <div className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Relación entre interacción en plataforma y nota final</h2>
            {clicksScatterData.length < data.clicks_vs_nota.length && (
              <p className="text-xs text-gray-500 mb-2">
                Mostrando muestra representativa de {clicksScatterData.length} de {data.clicks_vs_nota.length} estudiantes
              </p>
            )}
            <ResponsiveContainer width="100%" height={400}>
              <ScatterChart margin={{ top: 20, right: 20, bottom: 40, left: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis
                  type="number"
                  dataKey="x"
                  name="Clicks"
                  domain={[0, 'auto']}
                  label={{ value: 'Total de clicks en la plataforma', position: 'insideBottom', offset: -15, style: { fontWeight: 600, fontSize: 12 } }}
                />
                <YAxis
                  type="number"
                  dataKey="y"
                  name="Nota"
                  domain={[0, 100]}
                  label={{ value: 'Nota final', angle: -90, position: 'insideLeft', style: { fontWeight: 600, fontSize: 12 } }}
                />
                <Tooltip
                  cursor={{ strokeDasharray: '3 3' }}
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '10px' }}
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      return (
                        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-md">
                          <p className="font-semibold text-gray-900">Est. #{payload[0].payload.id_student}</p>
                          <p className="text-sm text-gray-600">Clicks: {payload[0].payload.x}</p>
                          <p className="text-sm text-gray-600">Nota: {payload[0].payload.y}</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Scatter
                  data={clicksScatterData}
                  fill="#1e88e5"
                  fillOpacity={0.6}
                  isAnimationActive={false}
                />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}