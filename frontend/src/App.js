import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { PaperAirplaneIcon, DocumentPlusIcon } from '@heroicons/react/24/outline';

// URL de l'API backend - utilise l'hôte actuel pour éviter les problèmes CORS
const API_URL = `${window.location.protocol}//${window.location.hostname}:5005`;

// Configure axios defaults
axios.defaults.timeout = 60000; // 60 seconds timeout - increased to handle RAG processing
axios.defaults.withCredentials = false; // Don't include credentials for cross-origin requests

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [fileUploading, setFileUploading] = useState(false);
  const [fileUploadSuccess, setFileUploadSuccess] = useState(false);
  const endOfMessagesRef = useRef(null);
  const fileInputRef = useRef(null);

  // Scroll vers le bas quand il y a de nouveaux messages
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Gérer l'envoi du message
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { text: input, isUser: true };
    setMessages([...messages, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Chat endpoint with explicit error handling
      const response = await axios.post(`${API_URL}/chat`, {
        query: input
      }, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });

      // Extraire la réponse et les sources
      const botMessage = {
        text: response.data.answer || "Je n'ai pas de réponse à cette question.",
        isUser: false,
        sources: response.data.sources || []
      };

      setMessages(prevMessages => [...prevMessages, botMessage]);
    } catch (error) {
      console.error('Erreur lors de l\'envoi du message:', error);
      
      // Display a more informative error message
      let errorText = "Désolé, une erreur s'est produite. Veuillez réessayer.";
      
      // Check for specific error types and provide better feedback
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        if (error.response.status === 502) {
          errorText = "Le serveur est temporairement indisponible ou la requête a pris trop de temps. Veuillez réessayer avec une question plus simple ou vérifier que le backend est en cours d'exécution.";
        } else if (error.response.data && error.response.data.message) {
          errorText = `Erreur: ${error.response.data.message}`;
        }
      } else if (error.request) {
        // The request was made but no response was received
        errorText = "Impossible de communiquer avec le serveur. Veuillez vérifier votre connexion et que le backend est en cours d'exécution.";
      }
      
      const errorMessage = {
        text: errorText,
        isUser: false,
        isSystem: true
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Gérer le téléchargement de fichier
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setFileUploadSuccess(false);
  };

  const handleFileUpload = async () => {
    if (!file) return;

    setFileUploading(true);
    
    try {
      // Create a FormData object to send the file
      const formData = new FormData();
      formData.append('file', file);
      
      // File upload endpoint - automatically becomes /load_documents
      const response = await axios.post(`${API_URL}/load_documents`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setFileUploadSuccess(true);
      
      // Message d'information pour l'utilisateur
      const systemMessage = {
        text: `Le fichier ${file.name} a été chargé avec succès et est maintenant disponible pour les requêtes.`,
        isUser: false,
        isSystem: true
      };
      setMessages(prevMessages => [...prevMessages, systemMessage]);
      setFile(null);
    } catch (error) {
      console.error('Erreur lors du chargement du fichier:', error);
      const errorMessage = {
        text: `Erreur: ${error.response?.data?.error || "Une erreur s'est produite lors du chargement du fichier."}`,
        isUser: false,
        isSystem: true
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setFileUploading(false);
    }
  };

  // Déclencher le clic sur l'input de fichier caché
  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm p-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-xl font-bold text-gray-900">RAG ChatBot</h1>
        </div>
      </header>

      {/* Chat Container */}
      <div className="flex-1 overflow-hidden flex flex-col max-w-5xl w-full mx-auto p-4">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto mb-4 rounded-lg">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center text-gray-500">
              <div className="text-center p-6 max-w-md">
                <h2 className="text-2xl font-semibold mb-3">Bienvenue dans le RAG ChatBot!</h2>
                <p className="mb-4">
                  Posez-moi des questions sur les documents chargés ou téléchargez de nouveaux documents pour enrichir ma base de connaissances.
                </p>
              </div>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`mb-4 ${
                  message.isUser ? 'text-right' : 'text-left'
                }`}
              >
                <div
                  className={`inline-block p-4 rounded-lg max-w-[80%] ${
                    message.isUser
                      ? 'bg-primary text-white rounded-br-none'
                      : message.isSystem
                      ? 'bg-yellow-100 text-gray-800 rounded-bl-none'
                      : 'bg-botmessage text-gray-800 rounded-bl-none'
                  }`}
                >
                  <ReactMarkdown className="prose">
                    {message.text}
                  </ReactMarkdown>
                  
                  {/* Afficher les sources si elles existent */}
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-gray-200 text-xs text-gray-500">
                      <p className="font-semibold">Sources:</p>
                      <ul className="list-disc pl-4">
                        {message.sources.map((source, idx) => (
                          <li key={idx}>
                            {source.source ? 
                              (source.id ? `${source.source} (ID: ${source.id})` : source.source) : 
                              `Document #${source.id || idx}`}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="text-left mb-4">
              <div className="inline-block p-4 rounded-lg bg-botmessage text-gray-800 rounded-bl-none">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-75"></div>
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-150"></div>
                </div>
              </div>
            </div>
          )}
          <div ref={endOfMessagesRef} />
        </div>

        {/* File Upload UI */}
        {file && (
          <div className="bg-white p-3 rounded-lg shadow-sm mb-4 flex items-center justify-between">
            <div className="flex items-center">
              <DocumentPlusIcon className="h-5 w-5 text-gray-500 mr-2" />
              <span className="text-sm text-gray-700 truncate">{file.name}</span>
            </div>
            <button
              onClick={handleFileUpload}
              disabled={fileUploading}
              className={`px-3 py-1 rounded-md text-sm ${
                fileUploading
                  ? 'bg-gray-300 text-gray-500'
                  : 'bg-primary-light text-white hover:bg-primary'
              }`}
            >
              {fileUploading ? 'Chargement...' : 'Charger'}
            </button>
          </div>
        )}

        {/* Input Area */}
        <div className="bg-white rounded-lg shadow-sm">
          <form onSubmit={handleSendMessage} className="flex items-center p-2">
            <button
              type="button"
              onClick={triggerFileInput}
              className="p-2 text-gray-500 hover:text-primary rounded-full"
              title="Charger un document"
            >
              <DocumentPlusIcon className="h-5 w-5" />
            </button>
            <input
              type="file"
              ref={fileInputRef}
              className="hidden"
              onChange={handleFileChange}
              accept=".jsonl"
            />
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Posez votre question..."
              className="flex-1 border-0 focus:ring-0 focus:outline-none p-2 bg-transparent"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className={`p-2 rounded-full ${
                input.trim() && !isLoading
                  ? 'text-primary hover:bg-gray-100'
                  : 'text-gray-400'
              }`}
            >
              <PaperAirplaneIcon className="h-5 w-5" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default App;