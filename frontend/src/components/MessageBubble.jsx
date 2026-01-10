import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { User, Bot, Copy, Check, Info } from 'lucide-react';
import { cn } from '../lib/utils';
import { Button } from './ui/Button';
import { Badge } from './ui/Badge';
import { useToast } from '../hooks/use-toast';
import { formatDate } from '../services/api';

export default function MessageBubble({ message }) {
    const { role, content, timestamp, sources, error } = message;
    const isUser = role === 'user';
    const { toast } = useToast();
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText(content);
        setCopied(true);
        toast({ description: "Message copied to clipboard" });
        setTimeout(() => setCopied(false), 2000);
    };

    if (error) {
        const errorMsg = typeof error === 'object' ? JSON.stringify(error) : String(error);
        return (
            <div className="flex w-full justify-center my-4">
                <div className="bg-destructive/10 text-destructive px-4 py-2 rounded-lg text-sm flex items-center gap-2 border border-destructive/20">
                    <Info className="h-4 w-4" />
                    {errorMsg}
                </div>
            </div>
        );
    }

    return (
        <div className={cn(
            "flex w-full gap-3 mb-6",
            isUser ? "flex-row-reverse" : "flex-row"
        )}>
            <div className={cn(
                "flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-full border shadow",
                isUser ? "bg-primary text-primary-foreground" : "bg-card text-card-foreground"
            )}>
                {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
            </div>

            <div className={cn(
                "flex flex-col max-w-[80%]",
                isUser ? "items-end" : "items-start"
            )}>
                <div className="flex items-center gap-2 mb-1 px-1">
                    <span className="text-xs text-muted-foreground">
                        {isUser ? 'You' : 'Assistant'}
                    </span>
                    <span className="text-[10px] text-muted-foreground/60">
                        {timestamp ? formatDate(timestamp).split(',')[1] : ''}
                    </span>
                </div>

                <div className={cn(
                    "relative rounded-lg px-4 py-3 text-sm shadow-sm",
                    isUser
                        ? "bg-primary text-primary-foreground rounded-tr-none"
                        : "bg-card border text-card-foreground rounded-tl-none"
                )}>
                    {!isUser && (
                        <Button
                            variant="ghost"
                            size="icon"
                            className="absolute right-1 top-1 h-6 w-6 text-muted-foreground hover:text-foreground opacity-0 group-hover:opacity-100 transition-opacity"
                            onClick={handleCopy}
                        >
                            {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                        </Button>
                    )}

                    <div className={cn("markdown-content", isUser ? "text-primary-foreground" : "text-card-foreground")}>
                        {isUser ? (
                            <p className="whitespace-pre-wrap">{String(content)}</p>
                        ) : (
                            <ReactMarkdown remarkPlugins={[remarkGfm]} components={{
                                code({ inline, className, children, ...props }) {
                                    return !inline ? (
                                        <pre className="bg-muted p-2 rounded-md my-2 overflow-x-auto text-xs">
                                            <code className={className} {...props}>{children}</code>
                                        </pre>
                                    ) : (
                                        <code className="bg-muted px-1 py-0.5 rounded text-xs font-mono" {...props}>
                                            {children}
                                        </code>
                                    )
                                }
                            }}>
                                {String(content || '')}
                            </ReactMarkdown>
                        )}
                    </div>
                </div>

                {!isUser && sources && sources.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-2 px-1">
                        {sources.map((source, idx) => (
                            <Badge key={idx} variant="outline" className="text-[10px] px-1.5 h-5 cursor-help hover:bg-muted" title="Source citation">
                                Ref {idx + 1}
                            </Badge>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
