import React, { useState, useRef } from 'react';
import { Button } from './ui/Button';
import { Textarea } from './ui/Textarea';
import MessageList from './MessageList';
import SourceCard from './SourceCard';
import { Send, Eraser, Loader2 } from 'lucide-react';
import { queryAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';
import { Badge } from './ui/Badge';
import { ScrollArea } from './ui/ScrollArea';

function generateId() {
    return Math.random().toString(36).substring(2, 15);
}

export default function ChatInterface({ selectedIds }) {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [conversationId, setConversationId] = useState(generateId());
    const [currentSources, setCurrentSources] = useState([]);
    const { toast } = useToast();
    const textareaRef = useRef(null);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;
        if (selectedIds.length === 0) {
            toast({
                variant: "destructive",
                title: "No documents selected",
                description: "Please select at least one document from the sidebar to ask questions."
            });
            return;
        }

        const userMessage = {
            role: 'user',
            content: input,
            timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);
        setCurrentSources([]); // Clear previous sources for new query context

        try {
            // API Call
            const response = await queryAPI.ask(userMessage.content, selectedIds, conversationId);

            const assistantMessage = {
                role: 'assistant',
                content: response.data.answer || "I couldn't generate an answer.",
                sources: response.data.sources || [],
                timestamp: new Date().toISOString()
            };

            setMessages(prev => [...prev, assistantMessage]);

            // Update current sources panel
            if (response.data.sources && response.data.sources.length > 0) {
                setCurrentSources(response.data.sources);
            }

        } catch (error) {
            console.error(error);
            const errorMessage = {
                role: 'system',
                error: true,
                content: error.response?.data?.detail || "Failed to get response from server.",
                timestamp: new Date().toISOString()
            };
            setMessages(prev => [...prev, errorMessage]);
            toast({
                variant: "destructive",
                title: "Error",
                description: "Failed to process your request."
            });
        } finally {
            setIsLoading(false);
            // Reset height of textarea
            if (textareaRef.current) {
                textareaRef.current.style.height = 'auto';
            }
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleClear = () => {
        setMessages([]);
        setCurrentSources([]);
        setConversationId(generateId());
        toast({ description: "Conversation cleared" });
    };

    return (
        <div className="flex flex-1 h-[calc(100vh-64px)] overflow-hidden">
            {/* Middle: Chat Area */}
            <div className="flex-1 flex flex-col min-w-0 bg-background">
                <div className="border-b p-3 flex justify-between items-center bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-background/60">
                    <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">Topic Context:</span>
                        {selectedIds.length === 0 ? (
                            <Badge variant="outline" className="text-xs text-muted-foreground border-dashed">No documents selected</Badge>
                        ) : (
                            <Badge variant="secondary" className="text-xs">{selectedIds.length} documents selected</Badge>
                        )}
                    </div>
                    <Button variant="ghost" size="sm" onClick={handleClear} title="Clear Conversation">
                        <Eraser className="h-4 w-4 mr-2" />
                        Clear Chat
                    </Button>
                </div>

                <div className="flex-1 overflow-hidden p-4">
                    <MessageList messages={messages} isLoading={isLoading} />
                </div>

                <div className="p-4 border-t bg-card">
                    <div className="relative">
                        <Textarea
                            ref={textareaRef}
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder={selectedIds.length > 0 ? "Ask a question about the selected documents..." : "Select documents to start asking questions..."}
                            className="min-h-[60px] max-h-[200px] pr-12 resize-none py-3"
                            disabled={isLoading}
                        />
                        <div className="absolute right-2 bottom-2 text-xs text-muted-foreground">
                            {input.length} chars
                        </div>
                        <Button
                            size="icon"
                            className="absolute right-2 top-2 h-8 w-8"
                            onClick={handleSend}
                            disabled={!input.trim() || isLoading || selectedIds.length === 0}
                        >
                            {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                        </Button>
                    </div>
                    <div className="mt-2 text-center">
                        <p className="text-[10px] text-muted-foreground">
                            AI answers are generated based on the selected documents. Check sources for accuracy.
                        </p>
                    </div>
                </div>
            </div>

            {/* Right: Sources Panel */}
            <div className="w-[350px] border-l bg-muted/10 flex flex-col shrink-0">
                <div className="p-4 border-b h-14 flex items-center">
                    <h3 className="font-semibold text-sm flex items-center gap-2">
                        Sources
                        {currentSources.length > 0 && <Badge variant="secondary" className="rounded-full px-2 h-5 text-[10px]">{currentSources.length}</Badge>}
                    </h3>
                </div>
                <ScrollArea className="flex-1 p-4">
                    {currentSources.length > 0 ? (
                        currentSources.map((source, idx) => (
                            <SourceCard key={idx} source={source} />
                        ))
                    ) : (
                        <div className="text-center p-8 text-muted-foreground">
                            <p className="text-sm">Sources will appear here after you ask a question.</p>
                        </div>
                    )}
                </ScrollArea>
            </div>
        </div>
    );
}
