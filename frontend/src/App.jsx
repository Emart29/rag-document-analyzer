import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import { Toaster } from './components/ui/Toaster';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 60000,
    },
  },
});

function App() {
  const [selectedIds, setSelectedIds] = useState([]);

  return (
    <QueryClientProvider client={queryClient}>
      <div className="flex flex-col h-screen bg-background text-foreground overflow-hidden selection:bg-primary/20">
        <Header />
        <div className="flex flex-1 overflow-hidden">
          <Sidebar selectedIds={selectedIds} onSelectionChange={setSelectedIds} />
          <main className="flex-1 flex flex-col min-w-0 relative">
            <div className="absolute inset-0 bg-dotted-pattern opacity-5 pointer-events-none" />
            <ChatInterface selectedIds={selectedIds} />
          </main>
        </div>
        <Toaster />
      </div>
    </QueryClientProvider>
  );
}

export default App;
