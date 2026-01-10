import { useState } from 'react';
import Navigation from './components/Navigation';
import AbandonoDashboard from './components/AbandonoDashboard';
import ChatBot from './components/ChatBot';

function App() {
  const [currentView, setCurrentView] = useState<'dashboard' | 'chat'>('dashboard');

  return (
    <div className="min-h-screen bg-gray-100">
      <Navigation currentView={currentView} onViewChange={setCurrentView} />
      {currentView === 'dashboard' ? <AbandonoDashboard /> : <ChatBot />}
    </div>
  );
}

export default App;
