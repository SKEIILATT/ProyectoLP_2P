import { useState } from 'react';
import Navigation from './components/Navigation';
import AbandonoDashboard from './components/AbandonoDashboard';
import ChatBot from './components/ChatBot';
import RagKnowledgeBase from './components/RagKnowledgeBase';

function App() {
  const [currentView, setCurrentView] = useState<'dashboard' | 'chat' | 'knowledge'>('dashboard');

  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <AbandonoDashboard />;
      case 'chat':
        return <ChatBot />;
      case 'knowledge':
        return <RagKnowledgeBase />;
      default:
        return <AbandonoDashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Navigation currentView={currentView} onViewChange={setCurrentView} />
      {renderView()}
    </div>
  );
}

export default App;
