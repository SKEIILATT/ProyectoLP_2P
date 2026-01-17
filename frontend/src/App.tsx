import { useState } from 'react';
import Navigation from './components/Navigation';
import LandingPage from './components/LandingPage';
import AbandonoDashboard from './components/AbandonoDashboard';
import RendimientoDashboard from './components/RendimientoDashboard';
import ChatBot from './components/ChatBot';
import RagKnowledgeBase from './components/RagKnowledgeBase';

type ViewType = 'home' | 'abandono' | 'rendimiento' | 'chat' | 'knowledge';

function App() {
  const [currentView, setCurrentView] = useState<ViewType>('home');

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Landing page sin navegación */}
      {currentView === 'home' ? (
        <LandingPage onNavigate={setCurrentView} />
      ) : (
        <>
          {/* Barra de navegación */}
          <Navigation currentView={currentView} onViewChange={setCurrentView} />

          {/* Contenido dinámico según el botón seleccionado */}
          {currentView === 'abandono' && <AbandonoDashboard />}
          {currentView === 'rendimiento' && <RendimientoDashboard />}
          {currentView === 'chat' && <ChatBot />}
          {currentView === 'knowledge' && <RagKnowledgeBase />}
        </>
      )}
    </div>
  );
}

export default App;
