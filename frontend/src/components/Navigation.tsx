type ViewType = 'home' | 'abandono' | 'rendimiento' | 'chat' | 'knowledge';

interface NavigationProps {
  currentView: ViewType;
  onViewChange: (view: ViewType) => void;
}

export default function Navigation({ currentView, onViewChange }: NavigationProps) {
  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <button
            onClick={() => onViewChange('home')}
            className="flex items-center space-x-3 hover:opacity-80 transition-opacity"
          >
            <div className="bg-purple-600 rounded-lg p-2">
              <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <div className="text-left">
              <h1 className="text-xl font-bold text-gray-900">RAG-EDU</h1>
              <p className="text-xs text-gray-600">Sistema de Análisis Educativo con IA</p>
            </div>
          </button>

          <div className="flex space-x-2">
            {/* Botón Abandono */}
            <button
              onClick={() => onViewChange('abandono')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                currentView === 'abandono'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <div className="flex items-center space-x-2">
                <span>Abandono</span>
              </div>
            </button>

            {/* Botón Rendimiento */}
            <button
              onClick={() => onViewChange('rendimiento')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                currentView === 'rendimiento'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <div className="flex items-center space-x-2">
                <span>Rendimiento</span>
              </div>
            </button>

            {/* Botón Chat IA */}
            <button
              onClick={() => onViewChange('chat')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                currentView === 'chat'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <div className="flex items-center space-x-2">
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
                <span>Chat IA</span>
              </div>
            </button>

            <button
              onClick={() => onViewChange('knowledge')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                currentView === 'knowledge'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <div className="flex items-center space-x-2">
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                </svg>
                <span>Base de Conocimiento</span>
              </div>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
