
import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import './App.css';
import Index from './pages/Index';
import Personas from './pages/Personas';
import Simulations from './pages/Simulations';
import Settings from './pages/Settings';
import NotFound from './pages/NotFound';
import Interviews from './pages/Interviews';
import { Toaster } from './components/ui/sonner';
import { ThemeProvider } from './components/ui/theme-provider';
import { SetupService } from './services/setupService';
import { PersonasProvider } from './contexts/PersonasContext';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 1000 * 60 * 5, // 5 minutes
    },
  },
});

function App() {
  const [isInitializing, setIsInitializing] = useState(true);

  useEffect(() => {
    const initialize = async () => {
      try {
        // Replace this with your actual API key if provided
        const openaiKey = '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';

        if (openaiKey) {
          await SetupService.setupOpenAIKey(openaiKey);
        }
      } catch (error) {
        console.error('Initialization error:', error);
      } finally {
        setIsInitializing(false);
      }
    };

    initialize();
  }, []);

  if (isInitializing) {
    return <div className="flex items-center justify-center h-screen">Initializing UXAgent...</div>;
  }

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="light" storageKey="uxagent-theme">
        <PersonasProvider>
          <Router>
            <Routes>
              <Route path="/" element={<Index />} />
              <Route path="/personas" element={<Personas />} />
              <Route path="/simulations" element={<Simulations />} />
              <Route path="/interviews" element={<Interviews />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
            <Toaster />
          </Router>
        </PersonasProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
