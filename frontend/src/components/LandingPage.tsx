interface LandingPageProps {
  onNavigate: (view: 'abandono' | 'rendimiento' | 'chat' | 'knowledge') => void;
}

export default function LandingPage({ onNavigate }: LandingPageProps) {
  const features = [
    {
      id: 'abandono',
      title: 'Dashboard de Abandono',
      description: 'Visualiza estadísticas de deserción estudiantil en Ecuador. Analiza datos por sexo, tipo de institución y tendencias históricas.',
      icon: (
        <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      color: 'blue',
      bgGradient: 'from-blue-500 to-blue-600',
    },
    {
      id: 'rendimiento',
      title: 'Dashboard de Rendimiento',
      description: 'Explora el rendimiento académico estudiantil. Correlaciona clicks en plataforma, evaluaciones rendidas y notas finales.',
      icon: (
        <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
      ),
      color: 'green',
      bgGradient: 'from-green-500 to-green-600',
    },
    {
      id: 'chat',
      title: 'Chat con IA',
      description: 'Realiza consultas en lenguaje natural sobre los datos educativos. Nuestro sistema RAG responde con información contextualizada.',
      icon: (
        <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
      ),
      color: 'purple',
      bgGradient: 'from-purple-500 to-purple-600',
    },
    {
      id: 'knowledge',
      title: 'Base de Conocimiento',
      description: 'Explora los documentos y hallazgos indexados en el sistema. Visualiza insights generados automáticamente por IA.',
      icon: (
        <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      ),
      color: 'orange',
      bgGradient: 'from-orange-500 to-orange-600',
    },
  ];

  const technologies = [
    { name: 'React', icon: '⚛️' },
    { name: 'Laravel', icon: '🔧' },
    { name: 'Python', icon: '🐍' },
    { name: 'LangChain', icon: '🔗' },
    { name: 'ChromaDB', icon: '💾' },
    { name: 'Ollama', icon: '🤖' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-indigo-700"></div>
        <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2260%22%20height%3D%2260%22%20viewBox%3D%220%200%2060%2060%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cg%20fill%3D%22%23ffffff%22%20fill-opacity%3D%220.05%22%3E%3Cpath%20d%3D%22M36%2034v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6%2034v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6%204V0H4v4H0v2h4v4h2V6h4V4H6z%22%2F%3E%3C%2Fg%3E%3C%2Fg%3E%3C%2Fsvg%3E')] opacity-30"></div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
          <div className="text-center">
            {/* Logo */}
            <div className="flex justify-center mb-8">
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 border border-white/20">
                <svg className="h-16 w-16 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
            </div>

            <h1 className="text-5xl lg:text-6xl font-bold text-white mb-6">
              RAG-EDU
            </h1>
            <p className="text-xl lg:text-2xl text-purple-100 mb-4 font-light">
              Sistema de Análisis Educativo con Inteligencia Artificial
            </p>
            <p className="text-lg text-purple-200 max-w-3xl mx-auto mb-10">
              Plataforma integral para el análisis de deserción estudiantil y rendimiento académico
              en Ecuador, potenciada por un sistema RAG (Retrieval-Augmented Generation) que permite
              consultas en lenguaje natural sobre datos educativos.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={() => onNavigate('chat')}
                className="px-8 py-4 bg-white text-purple-700 font-semibold rounded-xl shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200"
              >
                Comenzar a Explorar
              </button>
              <button
                onClick={() => onNavigate('abandono')}
                className="px-8 py-4 bg-purple-500/30 text-white font-semibold rounded-xl border border-white/30 hover:bg-purple-500/50 transition-all duration-200"
              >
                Ver Dashboards
              </button>
            </div>
          </div>
        </div>

        {/* Wave separator */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg className="w-full h-16 fill-gray-50" viewBox="0 0 1440 54" preserveAspectRatio="none">
            <path d="M0 22L60 16.7C120 11 240 1.00001 360 0.700012C480 1.00001 600 11 720 16.7C840 22 960 22 1080 19.3C1200 16.7 1320 11 1380 8.30001L1440 5.70001V54H1380C1320 54 1200 54 1080 54C960 54 840 54 720 54C600 54 480 54 360 54C240 54 120 54 60 54H0V22Z" />
          </svg>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
              Explora Nuestras Herramientas
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Accede a dashboards interactivos, consulta datos con IA y descubre insights sobre la educación en Ecuador.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {features.map((feature) => (
              <button
                key={feature.id}
                onClick={() => onNavigate(feature.id as 'abandono' | 'rendimiento' | 'chat' | 'knowledge')}
                className="group bg-white rounded-2xl shadow-md hover:shadow-xl p-8 text-left transition-all duration-300 transform hover:-translate-y-1 border border-gray-100"
              >
                <div className={`inline-flex p-4 rounded-xl bg-gradient-to-r ${feature.bgGradient} text-white mb-6 group-hover:scale-110 transition-transform duration-300`}>
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3 group-hover:text-purple-600 transition-colors">
                  {feature.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
                <div className="mt-6 flex items-center text-purple-600 font-medium">
                  <span>Explorar</span>
                  <svg className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </div>
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* About Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-6">
                Sobre el Proyecto
              </h2>
              <div className="space-y-4 text-gray-600">
                <p>
                  <strong className="text-gray-900">RAG-EDU</strong> es un proyecto académico que combina
                  análisis de datos educativos con inteligencia artificial para proporcionar insights
                  sobre la deserción estudiantil y el rendimiento académico.
                </p>
                <p>
                  Utilizamos datos reales del sistema educativo ecuatoriano y el dataset Open University
                  Learning Analytics para crear visualizaciones interactivas y un sistema de consultas
                  basado en RAG (Retrieval-Augmented Generation).
                </p>
                <p>
                  El sistema permite realizar preguntas en lenguaje natural sobre los datos,
                  generando respuestas contextualizadas basadas en documentos, estadísticas y
                  análisis previos indexados en nuestra base de conocimiento.
                </p>
              </div>

              {/* Key Stats */}
              <div className="grid grid-cols-3 gap-4 mt-8">
                <div className="text-center p-4 bg-purple-50 rounded-xl">
                  <p className="text-2xl font-bold text-purple-600">159K+</p>
                  <p className="text-sm text-gray-600">Estudiantes analizados</p>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded-xl">
                  <p className="text-2xl font-bold text-blue-600">7</p>
                  <p className="text-sm text-gray-600">Materias</p>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-xl">
                  <p className="text-2xl font-bold text-green-600">2022</p>
                  <p className="text-sm text-gray-600">Datos Ecuador</p>
                </div>
              </div>
            </div>

            {/* Tech Stack */}
            <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-2xl p-8">
              <h3 className="text-xl font-bold text-gray-900 mb-6">Stack Tecnológico</h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                {technologies.map((tech) => (
                  <div
                    key={tech.name}
                    className="flex items-center space-x-3 bg-white rounded-xl p-4 shadow-sm"
                  >
                    <span className="text-2xl">{tech.icon}</span>
                    <span className="font-medium text-gray-700">{tech.name}</span>
                  </div>
                ))}
              </div>

              <div className="mt-8 p-4 bg-purple-100 rounded-xl">
                <h4 className="font-semibold text-purple-900 mb-2">Sistema RAG</h4>
                <p className="text-sm text-purple-700">
                  Retrieval-Augmented Generation permite consultar documentos indexados
                  usando embeddings vectoriales y modelos de lenguaje locales (Ollama/Mistral).
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <div className="flex justify-center items-center space-x-3 mb-4">
            <div className="bg-purple-600 rounded-lg p-2">
              <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <span className="text-xl font-bold text-white">RAG-EDU</span>
          </div>
          <p className="text-sm">
            Proyecto académico - Sistema de Análisis Educativo con IA
          </p>
          <p className="text-sm mt-2">
            Desarrollado con React, Laravel, Python y LangChain
          </p>
        </div>
      </footer>
    </div>
  );
}
