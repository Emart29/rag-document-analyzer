import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/Tabs';
import { Button } from './ui/Button';
import { XCircle, FileText, UploadCloud } from 'lucide-react';
import DocumentList from './DocumentList';
import DocumentUpload from './DocumentUpload';
import { ScrollArea } from './ui/ScrollArea';
import { Badge } from './ui/Badge';

export default function Sidebar({ selectedIds, onSelectionChange }) {
    return (
        <div className="w-[320px] bg-card border-r flex flex-col h-[calc(100vh-64px)] shrink-0">
            <Tabs defaultValue="documents" className="flex-1 flex flex-col">
                <div className="p-4 pb-2">
                    <TabsList className="grid w-full grid-cols-2">
                        <TabsTrigger value="documents" className="flex items-center gap-2">
                            <FileText className="h-4 w-4" />
                            Documents
                        </TabsTrigger>
                        <TabsTrigger value="upload" className="flex items-center gap-2">
                            <UploadCloud className="h-4 w-4" />
                            Upload
                        </TabsTrigger>
                    </TabsList>
                </div>

                <div className="px-4 py-2 border-b bg-muted/20 min-h-[40px] flex items-center justify-between">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <span>Selected:</span>
                        <Badge variant={selectedIds.length > 0 ? "default" : "secondary"}>
                            {selectedIds.length}
                        </Badge>
                    </div>
                    {selectedIds.length > 0 && (
                        <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 px-2 text-xs hover:bg-destructive/10 hover:text-destructive"
                            onClick={() => onSelectionChange([])}
                        >
                            <XCircle className="h-3 w-3 mr-1" />
                            Clear
                        </Button>
                    )}
                </div>

                <TabsContent value="documents" className="flex-1 overflow-hidden p-0 m-0 data-[state=active]:flex data-[state=active]:flex-col">
                    <ScrollArea className="flex-1 px-4 py-4">
                        <DocumentList selectedIds={selectedIds} onSelectionChange={onSelectionChange} />
                    </ScrollArea>
                </TabsContent>

                <TabsContent value="upload" className="flex-1 p-4 m-0 overflow-hidden">
                    <DocumentUpload />
                </TabsContent>
            </Tabs>
        </div>
    );
}
