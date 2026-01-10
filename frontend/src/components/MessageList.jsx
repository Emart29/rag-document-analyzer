import React, { useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import { ScrollArea } from './ui/ScrollArea';
import { Loader2, MessageSquare } from 'lucide-react';

export default function MessageList({ messages, isLoading }) {
    const bottomRef = useRef(null);

    useEffect(() => {
        if (messages.length > 0) {
            // Small delay to ensure rendering is complete
            setTimeout(() => {
                bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
            }, 100);
        }
    }, [messages, isLoading]);

    if (messages.length === 0) {
        return (
            <div className="h-full flex flex-col items-center justify-center text-center p-8 text-muted-foreground opacity-50">
                <div className="bg-muted p-4 rounded-full mb-4">
                    <MessageSquare className="h-10 w-10" />
                </div>
                <h3 className="text-lg font-medium">No messages yet</h3>
                <p className="text-sm">Select documents and ask a question to get started.</p>
            </div>
        );
    }

    return (
        <ScrollArea className="h-full pr-4">
            <div className="flex flex-col pb-4">
                {messages.map((msg, index) => (
                    <MessageBubble key={index} message={msg} />
                ))}

                {isLoading && (
                    <div className="flex items-center gap-2 text-muted-foreground text-sm p-4">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>Thinking...</span>
                    </div>
                )}
                <div ref={bottomRef} />
            </div>
        </ScrollArea>
    );
}
