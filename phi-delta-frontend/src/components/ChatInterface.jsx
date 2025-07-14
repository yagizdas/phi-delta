'use client'

import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [thinkingSteps, setThinkingSteps] = useState([]);
  const [isThinking, setIsThinking] = useState(false);
  const [isThinkingExpanded, setIsThinkingExpanded] = useState(true);
  const containerRef = useRef(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [messages, isThinking, thinkingSteps]);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsThinking(true);
    setThinkingSteps([]);

    try {
      // Start polling for thinking steps
      const thinkingInterval = setInterval(async () => {
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
          }
        } catch (error) {
          console.error('Error fetching thinking steps:', error);
        }
      }, 500);

      // Start polling for processing status
      const statusInterval = setInterval(async () => {
        try {
          const statusRes = await fetch('/api/get-processing-status');
          const status = await statusRes.json();
          
          if (!status.is_processing && status.has_result) {
            // Processing is complete, get the final result
            const resultRes = await fetch('/api/get-final-result');
            const resultData = await resultRes.json();
            
            if (resultData.result) {
              clearInterval(thinkingInterval);
              clearInterval(statusInterval);
              setIsThinking(false);
              setMessages(prev => [...prev, { role: 'assistant', content: resultData.result }]);
              return;
            }
          }
        } catch (error) {
          console.error('Error checking processing status:', error);
        }
      }, 1000);

      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      });
      
      const { reply } = await res.json();
      
      // If it's not agentic (immediate response), clear intervals and show result
      if (!reply.includes('🔄 Processing')) {
        clearInterval(thinkingInterval);
        clearInterval(statusInterval);
        setIsThinking(false);
        setMessages(prev => [...prev, { role: 'assistant', content: reply }]);
      }
      // If it's agentic, the intervals will handle the final result
      
    } catch (error) {
      setIsThinking(false);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, something went wrong.' }]);
      console.error('Chat error:', error);
    }
  };

  const handleKeyDown = e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <header className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700/50 p-6 flex items-center justify-center">
        <h1 className="text-2xl font-bold text-slate-100 tracking-wide">
          <span className="text-emerald-400">Phi</span> <span className="text-slate-300">Delta</span>
          <span className="text-xs ml-2 text-slate-400 font-normal">Research Agent</span>
        </h1>
      </header>
      <main ref={containerRef} className="flex-1 overflow-auto p-6 space-y-6">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`max-w-3xl mx-auto p-5 rounded-2xl whitespace-pre-line transition-all duration-200 ${
              msg.role === 'user' 
                ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white ml-auto max-w-2xl shadow-lg shadow-emerald-900/20' 
                : 'bg-slate-800/60 backdrop-blur-sm border border-slate-700/50 text-slate-100 shadow-xl shadow-slate-900/30'
            }`}
          >
            {msg.role === 'assistant' && (
              <div className="flex items-center mb-3 text-emerald-400 text-sm font-medium">
                <div className="w-2 h-2 bg-emerald-400 rounded-full mr-2 animate-pulse"></div>
                Research Agent
              </div>
            )}
	    <ReactMarkdown
		remarkPlugins={[remarkGfm]}
		components={{
		  div: ({node, ...props}) => <div className={`prose prose-sm max-w-none ${
                    msg.role === 'user' ? 'prose-invert' : 'prose-slate prose-invert'
                  }`} {...props} />
		}}
	    >
	      {msg.content}
	    </ReactMarkdown>
          </div>
        ))}
        
        {/* Thinking Component - appears after all messages */}
        {isThinking && (
          <div className="max-w-3xl mx-auto">
            <div className="bg-slate-800/60 backdrop-blur-sm border border-slate-700/50 rounded-2xl shadow-xl shadow-slate-900/30 overflow-hidden">
              {/* Thinking Header */}
              <div 
                className="flex items-center justify-between p-4 cursor-pointer hover:bg-slate-700/30 transition-colors"
                onClick={() => setIsThinkingExpanded(!isThinkingExpanded)}
              >
                <div className="flex items-center space-x-3">
                  <div className="relative">
                    <div className="w-3 h-3 bg-emerald-400 rounded-full animate-pulse"></div>
                    <div className="absolute inset-0 w-3 h-3 bg-emerald-400 rounded-full animate-ping opacity-30"></div>
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
      <footer className="p-6 bg-slate-800/30 backdrop-blur-sm border-t border-slate-700/50">
        <div className="max-w-4xl mx-auto flex items-end space-x-4">
          <div className="flex-1 relative">
            <textarea
              className="w-full bg-slate-700/50 backdrop-blur-sm border border-slate-600/50 rounded-2xl p-4 text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 resize-none transition-all duration-200 shadow-lg"
              placeholder="Ask your research question..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={2}
            />
          </div>
          <button
            onClick={handleSend}
            className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white px-6 py-3 rounded-2xl transition-all duration-200 font-medium shadow-lg shadow-emerald-900/30 hover:shadow-emerald-900/50 hover:scale-105 active:scale-95"
          >
            <span className="flex items-center">
              Send
              <svg className="ml-2 w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z"></path>
              </svg>
            </span>
          </button>
        </div>
      </footer>
    </div>
  );
}
