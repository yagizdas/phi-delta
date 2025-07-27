'use client'

import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

export default function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [thinkingSteps, setThinkingSteps] = useState([]);
  const [isThinking, setIsThinking] = useState(false);
  const [isThinkingExpanded, setIsThinkingExpanded] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [modelFiles, setModelFiles] = useState([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [sessions, setSessions] = useState([]);
  const [isLoadingSessions, setIsLoadingSessions] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [isModelFilesBubbleOpen, setIsModelFilesBubbleOpen] = useState(false);
  const [isStreamingActive, setIsStreamingActive] = useState(false); // New state to track streaming
  const containerRef = useRef(null);
  const fileInputRef = useRef(null);
  const currentThinkingStepsRef = useRef([]);
  const titleGenerationTimeoutRef = useRef(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [messages, isThinking, thinkingSteps]);

  // Get current session ID on component mount
  useEffect(() => {
    getCurrentSessionId();
  }, []);

  // Fetch model files when currentSessionId changes
  useEffect(() => {
    const fetchModelFiles = async () => {
      // Don't fetch model files while streaming is active
      if (isStreamingActive) {
        console.log('⏸️ Deferring model files fetch - streaming in progress');
        return;
      }
      
      if (!currentSessionId) {
        console.log('⏳ No session ID available yet, skipping model files fetch');
        return;
      }

      try {
        console.log('🔍 Fetching model files for session:', currentSessionId);
        const response = await fetch(`/api/get-model-files?session_id=${currentSessionId}`);
        console.log('📡 Response status:', response.status, response.statusText);
        
        if (response.ok) {
          const files = await response.json();
          console.log('📁 Received files:', files);
          console.log('📁 Files type:', typeof files);
          console.log('📁 Files array?', Array.isArray(files));
          console.log('📁 Files length:', files?.length);
          
          setModelFiles(files);
          console.log('✅ Model files updated in state');
        } else {
          console.error('❌ Failed to fetch model files:', response.status, response.statusText);
        }
      } catch (error) {
        console.error('💥 Error fetching model files:', error);
      }
    };
    
    if (currentSessionId) {
      // Initial fetch (only if not streaming)
      if (!isStreamingActive) {
        fetchModelFiles();
      }
      
      // Set up polling every 5 seconds (but skip during streaming)
      const interval = setInterval(() => {
        if (!isStreamingActive) {
          fetchModelFiles();
        }
      }, 5000);
      
      // Cleanup interval on component unmount
      return () => clearInterval(interval);
    }
  }, [currentSessionId, isStreamingActive]); // Added isStreamingActive dependency


    const handleNewChat = async () => {
    // Clear title generation timeout
    if (titleGenerationTimeoutRef.current) {
      clearTimeout(titleGenerationTimeoutRef.current);
      titleGenerationTimeoutRef.current = null;
    }

    const newChat = await fetch('/api/new-chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!newChat.ok) {
        console.error('Failed to start new chat:', newChat.statusText);
        return;
    }
    setMessages([]);
    setInput('');
    setUploadedFiles([]);
    setIsThinking(false);
    setIsStreamingActive(false); // Reset streaming state
    setThinkingSteps([]);
    currentThinkingStepsRef.current = [];
    setIsSidebarOpen(false);

    const chatData = await newChat.json();
    console.log('🆕 New chat started:', chatData);
    
    // Get the current session ID after creating new chat
    await getCurrentSessionId();
  }

  // Function to get current session ID from backend
  const getCurrentSessionId = async () => {
    try {
      console.log('🔄 Getting current session ID from backend...');
      const response = await fetch('/api/current-session');
      
      if (response.ok) {
        const sessionInfo = await response.json();
        console.log('� Current session info:', sessionInfo);
        
        if (sessionInfo.has_session && sessionInfo.session_id) {
          setCurrentSessionId(sessionInfo.session_id);
          console.log('✅ Current session ID set:', sessionInfo.session_id);
        } else {
          console.log('ℹ️ No active session found');
          setCurrentSessionId(null);
        }
      } else {
        console.error('❌ Failed to get current session info');
        setCurrentSessionId(null);
      }
    } catch (error) {
      console.error('Error getting current session ID:', error);
      setCurrentSessionId(null);
    }
  };

  // Session management functions
  const fetchSessions = async () => {
    setIsLoadingSessions(true);
    try {
      const response = await fetch('/api/sessions');
      if (response.ok) {
        const data = await response.json();
        setSessions(data.sessions || []);
      }
    } catch (error) {
      console.error('Error fetching sessions:', error);
    } finally {
      setIsLoadingSessions(false);
    }
  };

  const saveCurrentSession = async () => {
    try {
      const response = await fetch('/api/save-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      if (response.ok) {
        const data = await response.json();
        console.log('Session saved:', data.session_id);
        await fetchSessions(); // Refresh session list
      }
    } catch (error) {
      console.error('Error saving session:', error);
    }
  };

  const loadSession = async (sessionId) => {
    // Clear title generation timeout
    if (titleGenerationTimeoutRef.current) {
      clearTimeout(titleGenerationTimeoutRef.current);
      titleGenerationTimeoutRef.current = null;
    }

    try {
      const response = await fetch(`/api/load-session/${sessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      if (response.ok) {
        // Clear current chat state
        setMessages([]);
        setInput('');
        setThinkingSteps([]);
        setIsThinking(false);
        setIsStreamingActive(false); // Reset streaming state
        setUploadedFiles([]);
        currentThinkingStepsRef.current = [];
        
        // Update current session ID
        setCurrentSessionId(sessionId);
        console.log('🆔 Current session ID updated to:', sessionId);
        
        // Get chat history from the loaded session using the new get-chat endpoint
        const chatResponse = await fetch('/api/get-chat');
        if (chatResponse.ok) {
          const chatData = await chatResponse.json();
          console.log('📜 Loaded chat data:', chatData);
          
          // The chat data should contain an array of messages
          const chatHistory = chatData.chat || [];
          
          // Set the messages directly since they're already in the correct format
          setMessages(chatHistory);
          console.log('✅ Chat history loaded with', chatHistory.length, 'messages');
        } else {
          console.error('❌ Failed to fetch chat history');
        }
        
        setIsSidebarOpen(false);
        console.log('Session loaded:', sessionId);
      }
    } catch (error) {
      console.error('Error loading session:', error);
    }
  };

  const deleteSession = async (sessionId) => {
    try {
      const response = await fetch(`/api/session/${sessionId}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        await fetchSessions(); // Refresh session list
        console.log('Session deleted:', sessionId);
      }
    } catch (error) {
      console.error('Error deleting session:', error);
    }
  };

  // Fetch sessions when sidebar opens
  useEffect(() => {
    if (isSidebarOpen) {
      fetchSessions();
    }
  }, [isSidebarOpen]);

  // Close model files bubble when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (isModelFilesBubbleOpen && !event.target.closest('.model-files-bubble')) {
        setIsModelFilesBubbleOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isModelFilesBubbleOpen]);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    // Prepare the message with file references
    let messageContent = input;
    
    // Add file references invisibly to the message
    if (uploadedFiles.length > 0) {
      const fileReferences = uploadedFiles.map(file => `FILE: ${file.name}`).join('\n');
      messageContent = fileReferences + '\n' + input;
      console.log('📎 Message with file references:', messageContent);
    }
    
    // Create user message with attached files
    const userMsg = { 
      role: 'user', 
      content: input, 
      attachedFiles: uploadedFiles.length > 0 ? [...uploadedFiles] : null 
    };
  
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setUploadedFiles([]); // Clear uploaded files after sending
    setIsThinking(true);
    setIsStreamingActive(false); // Reset streaming state
    setThinkingSteps([]);
    currentThinkingStepsRef.current = []; // Reset the ref for new request

    try {
      // Start polling for thinking steps
      const thinkingInterval = setInterval(async () => {
        // Skip thinking steps polling during streaming
        if (isStreamingActive) {
          return;
        }
        
        try {
          const thinkingRes = await fetch('/api/get-chat-history');
          
          if (!thinkingRes.ok) {
            console.warn('Thinking API not available yet');
            return;
          }
          
          const steps = await thinkingRes.json();
          console.log('Received thinking steps:', steps);
          
          if (Array.isArray(steps) && steps.length > 0) {
            setThinkingSteps(steps);
            currentThinkingStepsRef.current = steps; // Keep ref updated
          }
        } catch (error) {
          console.error('Error fetching thinking steps:', error);
        }
      }, 500);

      // Start polling for processing status
      const statusInterval = setInterval(async () => {
        // Skip status polling during streaming
        if (isStreamingActive) {
          return;
        }
        
        try {
          const statusRes = await fetch('/api/get-processing-status');
          const status = await statusRes.json();
          
          console.log('Processing status:', status); // Debug log
          
          if (!status.is_processing && status.has_result) {
            // Processing is complete, get the streaming final result
            clearInterval(thinkingInterval);
            clearInterval(statusInterval);
            
            // Update thinking status to show we're finalizing
            setThinkingSteps(prev => [...prev, {
              step: prev.length + 1,
              description: "Finalizing response..."
            }]);
            
            try {
              const resultRes = await fetch('/api/get-final-result');
              
              // Check if it's a streaming response
              const contentType = resultRes.headers.get('content-type');
              
              if (contentType && contentType.includes('text/plain')) {
                // Handle streaming response from get-final-result
                console.log('🚀 Starting final result streaming');
                setIsStreamingActive(true); // Mark streaming as active
                
                const reader = resultRes.body.getReader();
                const decoder = new TextDecoder();
                
                // Use the ref to get the most current thinking steps
                const currentThinkingSteps = [...currentThinkingStepsRef.current];
                
                // Now hide thinking UI and add placeholder message
                setIsThinking(false);
                
                // Add a placeholder message that will be updated with streaming content
                const assistantMsgIndex = messages.length + 1; // +1 because we added user message
                setMessages(prev => [...prev, { 
                  role: 'assistant', 
                  content: '',
                  thinkingSteps: currentThinkingSteps.length > 0 ? currentThinkingSteps : null,
                  thinkingDuration: currentThinkingSteps.length > 0 ? `${currentThinkingSteps.length} steps` : null
                }]);
                
                let accumulatedContent = '';
                
                try {
                  while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    
                    const chunk = decoder.decode(value, { stream: true });
                    accumulatedContent += chunk;
                    
                    // Update the assistant message in real-time
                    setMessages(prev => prev.map((msg, idx) => 
                      idx === assistantMsgIndex ? { ...msg, content: accumulatedContent } : msg
                    ));
                  }
                  
                  console.log('✅ Final result streaming completed');
                  setIsStreamingActive(false); // Mark streaming as complete
                  
                } catch (streamError) {
                  console.error('Streaming error:', streamError);
                  setIsStreamingActive(false); // Mark streaming as complete even on error
                  setMessages(prev => prev.map((msg, idx) => 
                    idx === assistantMsgIndex ? { ...msg, content: accumulatedContent + '\n\n[Stream interrupted]' } : msg
                  ));
                }
              } else {
                // Fallback to JSON response (in case the endpoint changes back)
                setIsThinking(false); // Hide thinking UI
                
                const resultData = await resultRes.json();
                console.log('Final result data:', resultData); // Debug log
                
                if (resultData.result) {
                  // Use the ref to get the most current thinking steps
                  const currentThinkingSteps = [...currentThinkingStepsRef.current];
                  
                  // Create assistant message with the current thinking steps
                  const assistantMsg = {
                    role: 'assistant',
                    content: resultData.result,
                    thinkingSteps: currentThinkingSteps.length > 0 ? currentThinkingSteps : null,
                    thinkingDuration: currentThinkingSteps.length > 0 ? `${currentThinkingSteps.length} steps` : null
                  };
                  
                  setMessages(prev => [...prev, assistantMsg]);
                }
              }
            } catch (resultError) {
              console.error('Error fetching final result:', resultError);
              setIsThinking(false); // Hide thinking UI on error
              
              // Use the ref to get the most current thinking steps
              const currentThinkingSteps = [...currentThinkingStepsRef.current];
              
              const errorMsg = {
                role: 'assistant',
                content: 'Sorry, there was an error retrieving the final result.',
                thinkingSteps: currentThinkingSteps.length > 0 ? currentThinkingSteps : null,
                thinkingDuration: currentThinkingSteps.length > 0 ? `${currentThinkingSteps.length} steps` : null
              };
              setMessages(prev => [...prev, errorMsg]);
            }
            return;
          }
        } catch (error) {
          console.error('Error checking processing status:', error);
        }
      }, 1000);

      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: messageContent }),
      });
      
      // Check if response is streaming (text/plain) or JSON
      const contentType = res.headers.get('content-type');
      
      if (contentType && contentType.includes('text/plain')) {
        // Handle streaming response
        console.log('🚀 Starting immediate streaming response');
        setIsStreamingActive(true); // Mark streaming as active
        
        clearInterval(thinkingInterval);
        clearInterval(statusInterval);
        setIsThinking(false);
        
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        
        // Add a placeholder message that will be updated
        const assistantMsgIndex = messages.length + 1; // +1 because we added user message
        setMessages(prev => [...prev, { role: 'assistant', content: '' }]);
        
        let accumulatedContent = '';
        
        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value, { stream: true });
            accumulatedContent += chunk;
            
            // Update the assistant message in real-time
            setMessages(prev => prev.map((msg, idx) => 
              idx === assistantMsgIndex ? { ...msg, content: accumulatedContent } : msg
            ));
          }
          
          console.log('✅ Immediate streaming completed');
          setIsStreamingActive(false); // Mark streaming as complete
          
        } catch (streamError) {
          console.error('Streaming error:', streamError);
          setIsStreamingActive(false); // Mark streaming as complete even on error
          setMessages(prev => prev.map((msg, idx) => 
            idx === assistantMsgIndex ? { ...msg, content: accumulatedContent + '\n\n[Stream interrupted]' } : msg
          ));
        }
      } else {
        // Handle JSON response (for agentic tasks)
        const { reply } = await res.json();
        
        // If it's not agentic (immediate response), clear intervals and show result
        if (!reply.includes('🔄 Processing')) {
          clearInterval(thinkingInterval);
          clearInterval(statusInterval);
          setIsThinking(false);
          setMessages(prev => [...prev, { role: 'assistant', content: reply }]);
        }
        // If it's agentic, the intervals will handle the final result
      }
      
    } catch (error) {
      setIsThinking(false);
      setIsStreamingActive(false); // Reset streaming state on error
      
      // Use the ref to get the most current thinking steps
      const currentThinkingSteps = [...currentThinkingStepsRef.current];
      
      const errorMsg = {
        role: 'assistant',
        content: 'Sorry, something went wrong.',
        thinkingSteps: currentThinkingSteps.length > 0 ? currentThinkingSteps : null,
        thinkingDuration: currentThinkingSteps.length > 0 ? `${currentThinkingSteps.length} steps` : null
      };
      setMessages(prev => [...prev, errorMsg]);
      console.error('Chat error:', error);
    }
  };

  const handleKeyDown = e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileUpload = async (event) => {
    const files = Array.from(event.target.files);
    
    for (const file of files) {
      try {
        console.log(`📤 Uploading file: ${file.name}`);
        
        // Create form data for the upload
        const formData = new FormData();
        formData.append('file', file);
        
        // Add file to list with uploading status
        setUploadedFiles(prev => [...prev, {
          name: file.name,
          type: file.type,
          uploading: true
        }]);
        
        // Upload to server
        const response = await fetch('/api/upload-file', {
          method: 'POST',
          body: formData
        });
        
        const result = await response.json();
        
        if (response.ok && result.status === 'success') {
          console.log(`✅ File uploaded successfully: ${result.file_path}`);
          
          // Update file status to uploaded
          setUploadedFiles(prev => prev.map(f => 
            f.name === file.name && f.uploading ? {
              ...f,
              uploaded: true,
              uploading: false,
              serverPath: result.file_path,
              serverFilename: result.filename
            } : f
          ));
        } else {
          console.error(`❌ Failed to upload ${file.name}:`, result.message);
          
          // Update file status to error
          setUploadedFiles(prev => prev.map(f => 
            f.name === file.name && f.uploading ? {
              ...f,
              uploaded: false,
              uploading: false,
              error: true,
              errorMessage: result.message
            } : f
          ));
        }
      } catch (error) {
        console.error(`💥 Error uploading ${file.name}:`, error);
        
        // Update file status to error
        setUploadedFiles(prev => prev.map(f => 
          f.name === file.name && f.uploading ? {
            ...f,
            uploaded: false,
            uploading: false,
            error: true,
            errorMessage: error.message
          } : f
        ));
      }
    }
    
    // Reset the input value so the same file can be selected again
    event.target.value = '';
  };

  const removeFile = (index) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const addModelFileToChat = (fileName) => {
    // Create a fake file object for the model file
    const modelFile = {
      name: fileName,
      type: 'model-file', // Add a type to distinguish from uploaded files
      isModelFile: true
    };
    
    // Check if file is already added
    if (!uploadedFiles.some(file => file.name === fileName)) {
      setUploadedFiles(prev => [...prev, modelFile]);
      console.log('📎 Model file added to chat:', fileName);
    }
  };

  // Function to remove a file from chat (for deselecting)
  const removeModelFileFromChat = (fileName) => {
    setUploadedFiles(prev => prev.filter(file => file.name !== fileName));
    console.log('❌ Model file removed from chat:', fileName);
  };

  // Helper function to check if a file is already added to chat
  const isFileAddedToChat = (fileName) => {
    return uploadedFiles.some(file => file.name === fileName);
  };

  // Function to generate chat title
  const generateChatTitle = async (sessionId) => {
    if (!sessionId) return;
    
    // Don't generate title while streaming is active
    if (isStreamingActive) {
      console.log('⏸️ Deferring title generation - streaming in progress');
      return;
    }
    
    try {
      console.log('🏷️ Generating title for session:', sessionId);
      const response = await fetch(`/api/get-chat-title/${sessionId}`);
      
      if (response.ok) {
        const data = await response.json();
        if (data.status === 'success') {
          console.log('✅ Title generated:', data.title);
          // Always refresh sessions to show the new title, regardless of sidebar state
          await fetchSessions();
        }
      } else {
        console.error('❌ Failed to generate title');
      }
    } catch (error) {
      console.error('💥 Error generating title:', error);
    }
  };

  // Function to schedule title generation after idle period
  const scheduleTitleGeneration = () => {
    // Clear any existing timeout
    if (titleGenerationTimeoutRef.current) {
      clearTimeout(titleGenerationTimeoutRef.current);
    }

    // Only generate title if we have a current session and some messages
    if (currentSessionId && messages.length >= 2) { // At least one exchange (user + assistant)
      titleGenerationTimeoutRef.current = setTimeout(() => {
        generateChatTitle(currentSessionId);
      }, 3000); // 3 seconds of idle time
    }
  };

  // Effect to trigger title generation when conversation ends and user goes idle
  useEffect(() => {
    // Schedule title generation when:
    // 1. Not currently thinking/processing
    // 2. Have messages in the conversation
    // 3. Have a current session
    // 4. Not currently streaming
    if (!isThinking && !isStreamingActive && messages.length >= 2 && currentSessionId) {
      scheduleTitleGeneration();
    }

    // Cleanup timeout on unmount
    return () => {
      if (titleGenerationTimeoutRef.current) {
        clearTimeout(titleGenerationTimeoutRef.current);
      }
    };
  }, [isThinking, isStreamingActive, messages.length, currentSessionId]); // Added isStreamingActive dependency

  // Clear title generation timeout when user starts typing
  const handleInputChange = (e) => {
    setInput(e.target.value);
    
    // Clear title generation timeout when user starts typing
    if (titleGenerationTimeoutRef.current) {
      clearTimeout(titleGenerationTimeoutRef.current);
      titleGenerationTimeoutRef.current = null;
    }
  };


  return (
    <div className="h-screen flex bg-slate-900">
      {/* Sidebar */}
      <div className={`${isSidebarOpen ? 'w-80' : 'w-0'} transition-all duration-300 bg-slate-800/60 backdrop-blur-md border-r border-slate-700/50 overflow-hidden`}>
        <div className="h-full flex flex-col">
          {/* Sidebar Header */}
          <div className="p-6 border-b border-slate-700/30">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold bg-gradient-to-r from-slate-200 to-slate-300 bg-clip-text text-transparent">Conversations</h2>
              <button
                onClick={() => setIsSidebarOpen(false)}
                className="text-slate-400 hover:text-slate-200 p-2 rounded-lg hover:bg-slate-700/50 transition-all duration-200"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
          
          {/* Content */}
          <div className="flex-1 overflow-y-auto">
            {/* Sessions Section */}
            <div className="p-6">
              {isLoadingSessions ? (
                <div className="flex flex-col items-center justify-center py-12 space-y-3">
                  <div className="animate-spin rounded-full h-8 w-8 border-2 border-emerald-400 border-t-transparent"></div>
                  <span className="text-slate-400 text-sm">Loading sessions...</span>
                </div>
              ) : sessions.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 space-y-3">
                  <div className="w-16 h-16 rounded-full bg-slate-700/50 flex items-center justify-center">
                    <svg className="w-8 h-8 text-slate-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <span className="text-slate-400 text-sm">No saved conversations yet</span>
                  <span className="text-slate-500 text-xs text-center px-4">Start chatting to create your first session</span>
                </div>
              ) : (
                <div className="space-y-3">
                  {sessions.slice(0, 10).map((session, index) => {
                    const isCurrentSession = currentSessionId === session.session_id;
                    return (
                      <div
                        key={session.session_id}
                        className={`group relative p-4 rounded-xl border transition-all duration-300 cursor-pointer hover:shadow-lg hover:shadow-slate-900/20 hover:-translate-y-0.5 ${
                          isCurrentSession
                            ? 'bg-gradient-to-br from-emerald-500/20 to-teal-500/20 border-emerald-500/50 shadow-lg shadow-emerald-900/20'
                            : 'bg-gradient-to-br from-slate-700/30 to-slate-700/20 border-slate-600/40 hover:from-slate-600/40 hover:to-slate-600/30 hover:border-slate-500/60'
                        }`}
                        onClick={() => loadSession(session.session_id)}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1 min-w-0 pr-3">
                            <div className={`font-medium leading-relaxed transition-colors ${
                              isCurrentSession 
                                ? 'text-emerald-100 group-hover:text-emerald-50' 
                                : 'text-slate-200 group-hover:text-white'
                            }`} style={{ 
                              display: '-webkit-box',
                              WebkitLineClamp: 2,
                              WebkitBoxOrient: 'vertical',
                              overflow: 'hidden',
                              lineHeight: '1.4',
                              maxHeight: '2.8em'
                            }}>
                              {session.title}
                            </div>
                            <div className={`text-xs mt-2 transition-colors ${
                              isCurrentSession 
                                ? 'text-emerald-400/80 group-hover:text-emerald-300' 
                                : 'text-slate-500 group-hover:text-slate-400'
                            }`}>
                              {isCurrentSession ? 'Current session' : new Date(session.timestamp).toLocaleDateString()}
                            </div>
                          </div>
                          <div className="flex-shrink-0 flex items-start space-x-2">
                            {isCurrentSession && (
                              <div className="flex items-center mt-1">
                                <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                              </div>
                            )}
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                deleteSession(session.session_id);
                              }}
                              className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-red-400 p-1 rounded-md hover:bg-red-500/10 transition-all duration-200"
                            >
                              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" clipRule="evenodd" />
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                              </svg>
                            </button>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Toggle Sidebar Button */}
        {!isSidebarOpen && (
          <button
            onClick={() => setIsSidebarOpen(true)}
            className="fixed top-2 left-4 z-30 bg-slate-800/80 backdrop-blur-sm border border-slate-700/50 text-slate-300 hover:text-slate-100 hover:bg-slate-700/80 hover:scale-105 p-3 rounded-lg transition-all duration-200 shadow-lg cursor-pointer group"
          >
            {/* Three-line hamburger menu icon */}
            <svg className="w-6 h-6 transition-transform duration-200 group-hover:scale-110" fill="currentColor" viewBox="0 0 24 24">
              <path d="M3 12h18M3 6h18M3 18h18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
            </svg>
          </button>
        )}

        {/* New Chat Button - Enhanced */}
        <button
          onClick={() => handleNewChat()}
          className="fixed top-2 right-4 z-30 bg-gradient-to-r from-emerald-600/90 to-teal-600/90 hover:from-emerald-500 hover:to-teal-500 backdrop-blur-sm border border-emerald-500/30 text-white hover:text-white hover:scale-105 px-4 py-3 rounded-xl transition-all duration-300 shadow-lg shadow-emerald-900/20 hover:shadow-emerald-900/40 cursor-pointer group flex items-center space-x-2"
        >
          {/* Plus icon */}
          <svg 
            className="w-4 h-4 transition-transform duration-300 group-hover:rotate-90" 
            fill="currentColor" 
            viewBox="0 0 20 20"
          >
            <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
          </svg>
          <span className="font-medium text-sm">New Chat</span>
        </button>

        {/* Model Files Bubble */}
        <div className="fixed top-2 right-36 z-30 model-files-bubble">
          <button
            onClick={() => setIsModelFilesBubbleOpen(!isModelFilesBubbleOpen)}
            className="bg-slate-800/80 backdrop-blur-sm border border-slate-700/50 text-slate-300 hover:text-slate-100 hover:bg-slate-700/80 hover:scale-105 p-3 rounded-lg transition-all duration-200 shadow-lg cursor-pointer group flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
            </svg>
            <span className="font-medium text-sm hidden sm:block">Files</span>
            {modelFiles.length > 0 && (
              <span className="bg-emerald-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                {modelFiles.length}
              </span>
            )}
          </button>
          
          {/* Model Files Dropdown */}
          {isModelFilesBubbleOpen && (
            <div className="absolute top-full right-0 mt-2 w-80 bg-slate-800/95 backdrop-blur-md border border-slate-700/50 rounded-xl shadow-2xl shadow-slate-900/50 overflow-hidden animate-in slide-in-from-top-2 duration-200">
              <div className="p-4 border-b border-slate-700/50">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-slate-200">Session Files</h3>
                  <button
                    onClick={() => setIsModelFilesBubbleOpen(false)}
                    className="text-slate-400 hover:text-slate-200 p-1 rounded-md hover:bg-slate-700/50 transition-all duration-200"
                  >
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </button>
                </div>
              </div>
              
              <div className="max-h-64 overflow-y-auto p-4">
                {modelFiles.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-8 space-y-3">
                    <div className="w-12 h-12 rounded-full bg-slate-700/50 flex items-center justify-center">
                      <svg className="w-6 h-6 text-slate-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="text-center">
                      <p className="text-slate-400 text-sm">No files in this session</p>
                      <p className="text-slate-500 text-xs mt-1">Upload documents to get started</p>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {modelFiles.map((file, index) => {
                      const isAdded = isFileAddedToChat(file);
                      return (
                        <div
                          key={index}
                          className={`group relative p-3 rounded-lg border transition-all duration-200 cursor-pointer text-slate-300 hover:shadow-lg hover:-translate-y-0.5 ${
                            isAdded 
                              ? 'bg-gradient-to-r from-emerald-500/20 to-teal-500/20 border-emerald-500/40 hover:from-emerald-500/30 hover:to-teal-500/30 hover:border-emerald-500/60' 
                              : 'bg-slate-700/30 border-slate-600/40 hover:bg-slate-600/40 hover:border-slate-500/60'
                          }`}
                          onClick={() => {
                            if (isAdded) {
                              removeModelFileFromChat(file);
                            } else {
                              addModelFileToChat(file);
                            }
                            // Don't close the bubble when adding/removing a file
                          }}
                        >
                          <div className="flex items-center space-x-3">
                            <div className="flex-shrink-0">
                              <div className={`w-8 h-8 rounded-lg border flex items-center justify-center ${
                                isAdded 
                                  ? 'bg-gradient-to-br from-emerald-500/30 to-teal-500/30 border-emerald-500/50' 
                                  : 'bg-gradient-to-br from-blue-500/20 to-purple-500/20 border-blue-500/30'
                              }`}>
                                <svg className={`w-4 h-4 ${isAdded ? 'text-emerald-300' : 'text-blue-400'}`} fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                                </svg>
                              </div>
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className={`text-sm font-medium truncate transition-colors ${
                                isAdded 
                                  ? 'text-emerald-200 group-hover:text-emerald-100' 
                                  : 'group-hover:text-white'
                              }`}>{file}</p>
                              <p className={`text-xs transition-colors ${
                                isAdded 
                                  ? 'text-emerald-400/80 group-hover:text-emerald-300' 
                                  : 'text-slate-500 group-hover:text-slate-400'
                              }`}>
                                {isAdded ? 'Click to remove' : 'Click to attach'}
                              </p>
                            </div>
                            <div className={`transition-opacity ${isAdded ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'}`}>
                              {isAdded ? (
                                <svg className="w-4 h-4 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                                </svg>
                              ) : (
                                <svg className="w-4 h-4 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                                </svg>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Horizontal nav lock-up - sticky app bar */}
        <header className="sticky top-0 z-20 bg-slate-900/80 backdrop-blur-md border-b border-slate-700/50">
          <div className="max-w-6xl mx-auto px-6 py-4">
            <div className="flex items-center justify-center">
              {/* Centered logo with icon */}
              <div className="flex items-center gap-0.5 hover:scale-105 transition-transform duration-200">
                {/* Logo icon */}
                <img
                  src="/squarelogophidelta.png"
                  alt="phiDelta"
                  className="w-9 h-9 object-contain"
                />
                {/* Word-mark - responsive */}
                <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-100 cursor-pointer mb-1">
                  <span className="text-slate-300">phi</span>
                  <span className="bg-gradient-to-r from-emerald-400 to-cyan-500 bg-clip-text text-transparent">
                    Delta
                  </span>
                </h1>
              </div>
            </div>
          </div>
        </header>

        
        {/* Main Chat Area */}
        <main ref={containerRef} className="flex-1 overflow-auto p-6 space-y-8">
          {messages.length === 0 ? (
            // Welcome/Start Page - Full lock-up for hero
            <div className="flex flex-col items-center justify-center min-h-[60vh]">
              {/* Full lock-up - hero placement */}
              <div className="flex flex-col items-center space-y-6">
                <div className="flex items-center space-x-3">
                  {/* Hero glyph */}
                  <img
                    src="/logophidelta.png"
                    alt="phiDelta"
                    className="w-56 h-5 md:w-64 md:h-64 object-contain select-none pointer-events-none"
                  />
                  {/* Hero word-mark */}

                </div>
                {/* Subtitle with proper spacing */}

              </div>
              
              {/* Main content with proper clear-space */}
              <div className="text-center space-y-6 max-w-2xl">
                <div className="space-y-4">
                  <h2 className="text-3xl md:text-4xl font-bold text-slate-100">
                    What's on the agenda today?
                  </h2>
                  <p className="text-lg text-slate-400 leading-relaxed">
                    I'm here to help you research, analyze, and explore any topic. Upload documents, ask questions, and let's dive deep into knowledge together.
                  </p>
                </div>
                
                {/* Example prompts */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8">
                  <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-xl p-4 hover:bg-slate-800/60 transition-colors cursor-pointer group"
                       onClick={() => setInput("Analyze the latest trends in artificial intelligence research")}>
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 mt-1">
                        <svg className="w-5 h-5 text-emerald-400" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                        </svg>
                      </div>
                      <div>
                        <h3 className="font-medium text-slate-200 group-hover:text-emerald-400 transition-colors">
                          Research Analysis
                        </h3>
                        <p className="text-sm text-slate-400 mt-1">
                          Analyze the latest trends in artificial intelligence research
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-xl p-4 hover:bg-slate-800/60 transition-colors cursor-pointer group"
                       onClick={() => setInput("Summarize and compare key findings from my uploaded documents")}>
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 mt-1">
                        <svg className="w-5 h-5 text-teal-400" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                        </svg>
                      </div>
                      <div>
                        <h3 className="font-medium text-slate-200 group-hover:text-teal-400 transition-colors">
                          Document Analysis
                        </h3>
                        <p className="text-sm text-slate-400 mt-1">
                          Summarize and compare key findings from my uploaded documents
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-xl p-4 hover:bg-slate-800/60 transition-colors cursor-pointer group"
                       onClick={() => setInput("Help me understand complex scientific concepts with clear explanations")}>
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 mt-1">
                        <svg className="w-5 h-5 text-cyan-400" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                        </svg>
                      </div>
                      <div>
                        <h3 className="font-medium text-slate-200 group-hover:text-cyan-400 transition-colors">
                          Concept Explanation
                        </h3>
                        <p className="text-sm text-slate-400 mt-1">
                          Help me understand complex scientific concepts with clear explanations
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-xl p-4 hover:bg-slate-800/60 transition-colors cursor-pointer group"
                       onClick={() => setInput("Create a comprehensive research plan for my project")}>
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 mt-1">
                        <svg className="w-5 h-5 text-purple-400" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                        </svg>
                      </div>
                      <div>
                        <h3 className="font-medium text-slate-200 group-hover:text-purple-400 transition-colors">
                          Research Planning
                        </h3>
                        <p className="text-sm text-slate-400 mt-1">
                          Create a comprehensive research plan for my project
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            // Chat Messages
            messages.map((msg, idx) => (
              <div
                key={idx}
                className={`max-w-3xl mx-auto p-6 rounded-2xl transition-all duration-200 break-words overflow-wrap-anywhere ${
                  msg.role === 'user' 
                    ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white ml-auto max-w-2xl shadow-lg shadow-emerald-900/20' 
                    : 'bg-slate-800/40 backdrop-blur-sm border border-slate-700/30 text-slate-50 shadow-xl shadow-slate-900/20 hover:bg-slate-800/50 transition-colors duration-300'
                }`}
              >

                {/* Show thinking steps for assistant messages - moved to top */}
                {msg.role === 'assistant' && msg.thinkingSteps && msg.thinkingSteps.length > 0 && (
                  <div className="mb-3 pb-3 border-b border-slate-600/50">
                    <details className="group">
                      <summary className="flex items-center cursor-pointer text-slate-400 hover:text-slate-300 transition-colors">
                        <div className="flex items-center">
                          <span className="text-sm font-medium">
                            Thought for {msg.thinkingDuration}
                          </span>
                        </div>
                        <svg className="w-4 h-4 ml-2 transform transition-transform group-open:rotate-180" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                        </svg>
                      </summary>
                      <div className="mt-3 space-y-2 pl-6 border-l-2 border-slate-600/30">
                        {msg.thinkingSteps.map((step, stepIdx) => (
                          <div key={stepIdx} className="flex items-start space-x-3">
                            <div className="flex-shrink-0 mt-1">
                              <div className="w-2 h-2 bg-blue-400 rounded-full ml-[2px] mt-[3px]"></div>
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="text-slate-300 text-sm leading-relaxed">
                                <span className="text-blue-400 font-medium">Step {step.step}:</span>{' '}
                                {step.description}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </details>
                  </div>
                )}

                {/* Show phiDelta indicator for assistant messages - moved below thinking steps */}
                {msg.role === 'assistant' && (
                  <div className="flex items-center mb-4 pb-3 border-b border-slate-600/30">
                    <div className="flex items-center space-x-2">
                      <img
                        src="/squaregreenlogophidelta.png"
                        alt="phiDelta"
                        className="w-5 h-5 object-contain opacity-90"
                      />
                      <span className="text-emerald-400 text-sm font-semibold tracking-wide">phiDelta</span>
                    </div>
                  </div>
                )}
                
                {/* Show attached files for user messages */}
                {msg.role === 'user' && msg.attachedFiles && msg.attachedFiles.length > 0 && (
                  <div className="mb-3 pb-3 border-b border-white/20">
                    <div className="flex items-center mb-2">
                      <svg className="w-4 h-4 text-white/80 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                      </svg>
                      <span className="text-sm font-medium text-white/90">Files Attached:</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {msg.attachedFiles.map((file, fileIdx) => (
                        <div key={fileIdx} className="flex items-center bg-white/20 backdrop-blur-sm rounded-lg px-3 py-1 text-sm" title={file.name}>
                          <svg className="w-4 h-4 text-white/80 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                          </svg>
                          <span className="text-white/90 mr-2">
                            {file.name.length > 30 ? `${file.name.slice(0, 30)}...` : file.name}
                          </span>
                          {file.isModelFile && (
                            <span className="text-xs bg-emerald-500/30 text-emerald-200 px-2 py-0.5 rounded-full">
                              Document
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                <ReactMarkdown
                  remarkPlugins={[remarkGfm, remarkMath]}
                  rehypePlugins={[rehypeKatex]}
                  components={{
                    div: ({node, ...props}) => <div className={`prose prose-lg max-w-none break-words ${
                      msg.role === 'user' ? 'prose-invert' : 'prose-slate prose-invert'
                    }`} {...props} />,
                    p: ({node, ...props}) => <p className="whitespace-pre-line break-words leading-relaxed mb-5 text-slate-100 text-base" {...props} />,
                    text: ({node, ...props}) => <span className="break-words leading-relaxed text-slate-100" {...props} />,
                    ul: ({node, ...props}) => <ul className="space-y-3 my-5 pl-6 list-disc marker:text-emerald-400" {...props} />,
                    ol: ({node, ...props}) => <ol className="space-y-3 my-5 pl-6 list-decimal marker:text-emerald-400" {...props} />,
                    li: ({node, ...props}) => <li className="leading-relaxed text-slate-100 pl-2 text-base" {...props} />,
                    h1: ({node, ...props}) => <h1 className="text-2xl font-bold text-slate-50 mb-4 mt-6 border-b border-slate-600/50 pb-3" {...props} />,
                    h2: ({node, ...props}) => <h2 className="text-xl font-semibold text-slate-100 mb-4 mt-6" {...props} />,
                    h3: ({node, ...props}) => <h3 className="text-lg font-medium text-slate-200 mb-3 mt-5" {...props} />,
                    h4: ({node, ...props}) => <h4 className="text-base font-medium text-slate-200 mb-3 mt-4" {...props} />,
                    h5: ({node, ...props}) => <h5 className="text-sm font-medium text-slate-300 mb-2 mt-3" {...props} />,
                    h6: ({node, ...props}) => <h6 className="text-sm font-medium text-slate-300 mb-2 mt-3" {...props} />,
                    strong: ({node, ...props}) => <strong className="font-semibold text-slate-50" {...props} />,
                    em: ({node, ...props}) => <em className="italic text-slate-200" {...props} />,
                    blockquote: ({node, ...props}) => <blockquote className="border-l-4 border-emerald-400/70 pl-4 py-3 my-5 bg-slate-700/30 rounded-r-lg text-slate-200 italic" {...props} />,
                    code: ({node, inline, ...props}) => 
                      inline ? 
                        <code className="bg-slate-700/60 text-emerald-300 px-2 py-1 rounded text-sm font-mono border border-slate-600/30" {...props} /> :
                        <code className="block bg-slate-900/60 text-slate-200 p-4 rounded-lg overflow-x-auto my-5 text-sm font-mono border border-slate-600/40 leading-relaxed" {...props} />,
                    pre: ({node, ...props}) => <pre className="bg-slate-900/60 text-slate-200 p-4 rounded-lg overflow-x-auto my-5 border border-slate-600/40" {...props} />,
                    table: ({node, ...props}) => <table className="min-w-full divide-y divide-slate-600 my-5 border border-slate-600/40 rounded-lg overflow-hidden" {...props} />,
                    thead: ({node, ...props}) => <thead className="bg-slate-700/50" {...props} />,
                    tbody: ({node, ...props}) => <tbody className="bg-slate-800/20 divide-y divide-slate-600" {...props} />,
                    tr: ({node, ...props}) => <tr className="hover:bg-slate-700/30 transition-colors" {...props} />,
                    th: ({node, ...props}) => <th className="px-4 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider" {...props} />,
                    td: ({node, ...props}) => <td className="px-4 py-3 text-sm text-slate-200" {...props} />,
                    a: ({node, ...props}) => <a className="text-emerald-400 hover:text-emerald-300 underline transition-colors font-medium" {...props} />
                  }}
                >
                  {msg.content}
                </ReactMarkdown>
              </div>
            ))
          )}
          
          {/* Thinking Component - appears after all messages */}
          {isThinking && (
            <div className="max-w-3xl mx-auto">
              <div className="bg-slate-800/60 backdrop-blur-sm border border-slate-700/50 rounded-2xl shadow-xl shadow-slate-900/30 overflow-hidden">
                {/* Thinking Header */}
                <div 
                  className="flex items-center justify-between p-4 cursor-pointer hover:bg-slate-700/30 transition-colors"
                  onClick={() => setIsThinkingExpanded(!isThinkingExpanded)}
                >
                  <div className="flex items-center space-x-1">
                    <div className="relative">
                      {/* Rotating glyph as thinking indicator */}
                      <img
                        src="/squaregreenlogophidelta.png"
                        alt="Thinking"
                        className="w-4 h-4 object-contain animate-bounce"
                      />
                    </div>
                    <span className="text-emerald-400 font-medium">Thinking...</span>
                    {thinkingSteps.length > 0 && (
                      <span className="text-slate-400 text-sm">
                        Step {thinkingSteps.length}
                      </span>
                    )}
                  </div>
                  <div className={`transform transition-transform duration-200 ${isThinkingExpanded ? 'rotate-180' : ''}`}>
                    <svg className="w-5 h-5 text-slate-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
                
                {/* Thinking Steps */}
                {isThinkingExpanded && (
                  <div className="border-t border-slate-700/50 p-4 space-y-3 max-h-60 overflow-y-auto">
                    {thinkingSteps.length === 0 ? (
                      <div className="flex items-center space-x-3 text-slate-400">
                        <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                        <span className="text-sm">Initializing...</span>
                      </div>
                    ) : (
                      thinkingSteps.map((step, idx) => (
                        <div key={idx} className="flex items-start space-x-3 group">
                          <div className="flex-shrink-0 mt-1">
                            <div className="w-2 h-2 bg-emerald-400 rounded-full"></div>
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="text-slate-300 text-sm leading-relaxed">
                              <span className="text-emerald-400 font-medium">Step {step.step}:</span>{' '}
                              {step.description}
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                    
                    {/* Current thinking indicator */}
                    {thinkingSteps.length > 0 && (
                      <div className="flex items-center space-x-3 text-slate-400">
                        <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                        <span className="text-sm animate-pulse">Processing...</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </main>
        
        <footer className={`p-6 backdrop-blur-sm  border-slate-700/50 ${messages.length === 0 ? 'flex items-left justify-center' : ''}`}>
          <div className={`${messages.length === 0 ? 'w-full max-w-2xl' : 'max-w-2xl'} mx-auto`}>
            {/* File Upload List */}
            {uploadedFiles.length > 0 && (
              <div className="mb-4 p-3 bg-slate-700/30 rounded-xl border border-slate-600/30">
                <div className="flex flex-wrap gap-2">
                  {uploadedFiles.map((file, index) => (
                    <div key={index} className="flex items-center bg-slate-600/50 rounded-lg px-3 py-1 text-sm" title={file.name}>
                      <svg className="w-4 h-4 text-slate-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                      </svg>
                      <span className="text-slate-300 mr-2">
                        {file.name.length > 25 ? `${file.name.slice(0, 25)}...` : file.name}
                      </span>
                      
                      {/* Upload status indicators */}
                      {file.uploading && (
                        <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded-full mr-2">
                          ⏳ Uploading...
                        </span>
                      )}
                      {file.uploaded === true && (
                        <span className="text-xs bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-full mr-2">
                          ✓ Uploaded
                        </span>
                      )}
                      {file.uploaded === false && file.error && (
                        <span className="text-xs bg-red-500/20 text-red-400 px-2 py-0.5 rounded-full mr-2" title={file.errorMessage}>
                          ✗ Failed
                        </span>
                      )}
                      {file.isModelFile && (
                        <span className="text-xs bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-full mr-2">
                          Document
                        </span>
                      )}
                      
                      <button
                        onClick={() => removeFile(index)}
                        className="text-slate-400 hover:text-red-400 transition-colors cursor-pointer"
                      >
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            <div className="flex items-center space-x-4">
              {/* Document Upload Button */}
              <button
                onClick={() => fileInputRef.current?.click()}
                className="bg-slate-700/50 hover:bg-slate-600/50 border border-slate-600/50 hover:border-slate-500/50 text-slate-300 px-3 py-3 rounded-full transition-all duration-200 font-medium shadow-lg hover:shadow-slate-900/50 flex items-center space-x-2 cursor-pointer"
                title="Upload documents"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                </svg>
              </button>
              
              {/* Hidden file input */}
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.jpeg,.png,.docx"
                onChange={handleFileUpload}
                className="hidden"
              />
              
              <div className="flex-1 relative">
                <textarea
                  className="w-full bg-slate-700/50 backdrop-blur-sm border border-slate-600/50 rounded-4xl p-4 text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 resize-none transition-all duration-200 shadow-lg"
                  placeholder="Ask your research question..."
                  value={input}
                  onChange={handleInputChange}
                  onKeyDown={handleKeyDown}
                  rows={2}
                />
              </div>
              
              <button
                onClick={handleSend}
                className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white px-6 py-3 rounded-2xl transition-all duration-200 font-medium shadow-lg shadow-emerald-900/30 hover:shadow-emerald-900/50 hover:scale-105 active:scale-95 cursor-pointer"
              >
                <span className="flex items-center">
                  Send
                  <svg className="ml-2 w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z"></path>
                  </svg>
                </span>
              </button>
            </div>
          </div>
        </footer>
        
        {/* Fixed Microsoft logo in bottom right corner */}
        <div className="fixed bottom-6 right-6 z-40">
          <div className="relative group">
            <div className="bg-slate-800/80 backdrop-blur-sm border border-slate-700/50 rounded-xl p-3 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
              <img
                src="/microsoftlogo.png"
                alt="Microsoft"
                className="w-8 h-8 object-contain opacity-80 hover:opacity-100 transition-opacity duration-300"
              />
            </div>
            {/* Tooltip - positioned to show above the logo */}
            <div className="absolute bottom-full right-0 mb-2 bg-slate-800/90 backdrop-blur-sm border border-slate-700/50 rounded-lg px-3 py-2 text-sm text-slate-200 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none whitespace-nowrap">
              Microsoft AI Innovators Internship Project
              <div className="text-xs text-slate-400 mt-1">Kemal Yagiz Daskiran</div>

            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
