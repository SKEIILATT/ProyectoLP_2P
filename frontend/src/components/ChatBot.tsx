import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import SourceCitation from './SourceCitation';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  loading?: boolean;
  sources?: string[];
  isInsight?: boolean;
}

export default function ChatBot() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [generatingInsights, setGeneratingInsights] = useState(false);
  const [ragStatus, setRagStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Verificar estado del RAG al cargar
    checkRagHealth();

    // Mensaje de bienvenida
    setMessages([{
      id: '1',
      text: 'Bienvenido al asistente virtual de análisis de abandono estudiantil. Puedo responder preguntas sobre estadísticas de Ecuador 2022 y análisis de factores de riesgo.',
      sender: 'bot',
      timestamp: new Date()
    }]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const checkRagHealth = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/rag/health');
      setRagStatus(response.data.rag_loaded ? 'online' : 'offline');
    } catch (error) {
      setRagStatus('offline');
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: input,
      sender: 'user',
      timestamp: new Date()
    };

    const loadingMessage: Message = {
      id: (Date.now() + 1).toString(),
      text: '',
      sender: 'bot',
      timestamp: new Date(),
      loading: true
    };

    setMessages(prev => [...prev, userMessage, loadingMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/api/rag/query', {
        pregunta: input,
        modelo: 'tinyllama'
      }, {
        timeout: 180000,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });

      setMessages(prev => prev.filter(m => !m.loading));

      const botMessage: Message = {
        id: Date.now().toString(),
        text: response.data.respuesta,
        sender: 'bot',
        timestamp: new Date(),
        sources: response.data.sources || []
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error: any) {
      setMessages(prev => prev.filter(m => !m.loading));

      const errorMessage: Message = {
        id: Date.now().toString(),
        text: error.response?.data?.error || 'Lo siento, ocurrió un error al procesar tu pregunta. Asegúrate de que el servidor RAG esté corriendo.',
        sender: 'bot',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const generateInsights = async () => {
    if (generatingInsights || loading) return;

    setGeneratingInsights(true);

    const loadingMessage: Message = {
      id: Date.now().toString(),
      text: '',
      sender: 'bot',
      timestamp: new Date(),
      loading: true
    };

    setMessages(prev => [...prev, loadingMessage]);

    try {
      const response = await axios.post('http://localhost:8000/api/rag/insights', {
        modelo: 'tinyllama'
      }, {
        timeout: 180000,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });

      setMessages(prev => prev.filter(m => !m.loading));

      if (response.data.success && response.data.insights) {
        const insightsText = response.data.insights
          .map((insight: string, idx: number) => `${idx + 1}. ${insight}`)
          .join('\n\n');

        const botMessage: Message = {
          id: Date.now().toString(),
          text: insightsText,
          sender: 'bot',
          timestamp: new Date(),
          sources: response.data.sources || [],
          isInsight: true
        };

        setMessages(prev => [...prev, botMessage]);
      } else {
        const errorMessage: Message = {
          id: Date.now().toString(),
          text: response.data.error || 'No se pudieron generar insights',
          sender: 'bot',
          timestamp: new Date()
        };

        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error: any) {
      setMessages(prev => prev.filter(m => !m.loading));

      const errorMessage: Message = {
        id: Date.now().toString(),
        text: 'Error al generar insights. Asegúrate de que el servidor RAG esté corriendo.',
        sender: 'bot',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setGeneratingInsights(false);
    }
  };

  const exampleQuestions = [
    '¿Cuántos estudiantes abandonaron en 2022?',
    '¿Cuál es la tasa de deserción por sexo?',
    '¿Qué factores aumentan el riesgo de abandono?',
    '¿Cómo afectan las becas al abandono estudiantil?'
  ];

  return (
    <div className="min-h-screen bg-gray-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">Asistente Virtual RAG-EDU</h1>
              <p className="text-gray-600">Consulta información sobre abandono estudiantil usando IA</p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={generateInsights}
                disabled={generatingInsights || loading || ragStatus === 'offline'}
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all font-medium text-sm shadow-md"
              >
                {generatingInsights ? 'Generando...' : 'Generar Hallazgos'}
              </button>
              <div className="flex items-center space-x-2">
                <div className={`h-3 w-3 rounded-full ${
                  ragStatus === 'online' ? 'bg-green-500' :
                  ragStatus === 'offline' ? 'bg-red-500' :
                  'bg-yellow-500'
                }`}></div>
                <span className="text-sm text-gray-600">
                  {ragStatus === 'online' ? 'RAG Online' :
                   ragStatus === 'offline' ? 'RAG Offline' :
                   'Verificando...'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Chat Container */}
        <div className="bg-white rounded-xl shadow-lg flex flex-col" style={{ height: '600px' }}>
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-3 ${
                    message.sender === 'user'
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  {message.loading ? (
                    <div className="flex items-center space-x-2">
                      <div className="animate-bounce h-2 w-2 bg-gray-400 rounded-full"></div>
                      <div className="animate-bounce h-2 w-2 bg-gray-400 rounded-full delay-100"></div>
                      <div className="animate-bounce h-2 w-2 bg-gray-400 rounded-full delay-200"></div>
                    </div>
                  ) : (
                    <>
                      {message.isInsight && (
                        <div className="mb-2 pb-2 border-b border-gray-300">
                          <span className="text-xs font-semibold text-purple-700">HALLAZGOS AUTOMÁTICOS</span>
                        </div>
                      )}
                      <p className="whitespace-pre-wrap">{message.text}</p>
                      {message.sender === 'bot' && message.sources && message.sources.length > 0 && (
                        <SourceCitation sources={message.sources} />
                      )}
                      <p className={`text-xs mt-1 ${
                        message.sender === 'user' ? 'text-purple-200' : 'text-gray-500'
                      }`}>
                        {message.timestamp.toLocaleTimeString('es-ES', {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </p>
                    </>
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Example Questions */}
          {messages.length === 1 && (
            <div className="px-6 pb-4">
              <p className="text-sm text-gray-600 mb-2">Preguntas de ejemplo:</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {exampleQuestions.map((question, idx) => (
                  <button
                    key={idx}
                    onClick={() => setInput(question)}
                    className="text-left text-sm bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-lg px-3 py-2 transition-colors"
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input Area */}
          <div className="border-t border-gray-200 p-4">
            <div className="flex items-end space-x-2">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Escribe tu pregunta aquí..."
                className="flex-1 resize-none border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                rows={2}
                disabled={loading || ragStatus === 'offline'}
              />
              <button
                onClick={sendMessage}
                disabled={loading || !input.trim() || ragStatus === 'offline'}
                className="bg-purple-600 text-white rounded-lg px-6 py-3 hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
              >
                {loading ? 'Enviando...' : 'Enviar'}
              </button>
            </div>
            {ragStatus === 'offline' && (
              <p className="text-sm text-red-600 mt-2">
                El servicio RAG no está disponible. Inicia el servidor Python con: python backend-python/rag/rag_api.py
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
