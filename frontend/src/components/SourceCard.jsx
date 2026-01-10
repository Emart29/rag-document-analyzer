import React, { useState } from 'react';
import { Card, CardContent } from './ui/Card';
import { Badge } from './ui/Badge';
import { ChevronDown, ChevronUp, FileText, ExternalLink } from 'lucide-react';
import { cn } from '../lib/utils';
import { Button } from './ui/Button';

export default function SourceCard({ source }) {
    const [isExpanded, setIsExpanded] = useState(false);

    // Parse source info if needed, assuming source object structure from backend
    // Backend likely returns: { document_name, page_number, score, text }
    // Score is usually 0-1, so multiply by 100 for percentage

    const relevance = Math.round((source.score || 0) * 100);

    return (
        <Card className="mb-3 transition-all hover:shadow-md border-l-4 border-l-primary/50">
            <CardContent className="p-3">
                <div className="flex items-start justify-between gap-2 mb-2">
                    <div className="flex items-center gap-1.5 overflow-hidden">
                        <FileText className="h-4 w-4 text-primary shrink-0" />
                        <span className="text-sm font-medium truncate" title={source.metadata?.filename || "Unknown Document"}>
                            {source.metadata?.filename || "Unknown Document"}
                        </span>
                    </div>
                    <Badge variant={relevance > 70 ? "success" : "secondary"} className="text-[10px] h-5 px-1 shrink-0">
                        {relevance}% Match
                    </Badge>
                </div>

                <div className="text-xs text-muted-foreground flex items-center justify-between mb-2">
                    <span>Page {source.metadata?.page_number || source.metadata?.page_label || "?"}</span>
                    <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0"
                        onClick={() => setIsExpanded(!isExpanded)}
                    >
                        {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4 bg-muted/50 rounded-sm" />}
                    </Button>
                </div>

                <div className={cn(
                    "text-sm bg-muted/30 p-2 rounded text-muted-foreground font-mono transition-all",
                    !isExpanded && "line-clamp-3 max-h-[4.5em] overflow-hidden"
                )}>
                    {source.text || source.page_content}
                </div>
            </CardContent>
        </Card>
    );
}
