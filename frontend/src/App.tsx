import { useState } from 'react';
import Navigation from './components/Navigation';
import AbandonoDashboard from './components/AbandonoDashboard';
import RendimientoDashboard from './components/RendimientoDashboard'; 
import ChatBot from './components/ChatBot';
import RagKnowledgeBase from './components/RagKnowledgeBase';

function App() {
  const [currentView, setCurrentView] = useState<'abandono' | 'rendimiento' | 'chat' | 'knowledge'>('abandono');

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Barra de navegación */}
      <Navigation currentView={currentView} onViewChange={setCurrentView} />

      {/* Contenido dinámico según el botón seleccionado */}
      {currentView === 'abandono' && <AbandonoDashboard />}
      {currentView === 'rendimiento' && <RendimientoDashboard />}
      {currentView === 'chat' && <ChatBot />}
      {currentView === 'knowledge' && <RagKnowledgeBase />}
    </div>
  );
}

export default App;
