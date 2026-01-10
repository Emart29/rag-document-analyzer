import { useState } from 'react';
import PropTypes from 'prop-types';
import { useDocuments } from '../hooks/useDocuments';
import { Card } from './ui/Card';
import { Button } from './ui/Button';
import { Checkbox } from './ui/Checkbox';
import { Trash2, Calendar, File, Layers, Archive } from 'lucide-react';
import { formatFileSize, formatDate } from '../services/api';
import { toast } from '../hooks/use-toast';

import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/Dialog";
import { Badge } from './ui/Badge';


// Need to implement Skeleton component too! It was missing.
function DocumentSkeleton() {
    return (
        <div className="flex items-start space-x-4 p-4 border rounded-lg">
            <div className="h-10 w-10 rounded-lg bg-muted animate-pulse" />
            <div className="space-y-2 flex-1">
                <div className="h-4 w-[80%] bg-muted animate-pulse rounded" />
                <div className="h-3 w-[50%] bg-muted animate-pulse rounded" />
            </div>
        </div>
    )
}

export default function DocumentList({ selectedIds = [], onSelectionChange }) {
    const { documents, isLoading, isError, deleteDocument, isDeleting } = useDocuments();
    const [deleteId, setDeleteId] = useState(null);

    const handleToggle = (id) => {
        if (selectedIds.includes(id)) {
            onSelectionChange(selectedIds.filter(itemId => itemId !== id));
        } else {
            onSelectionChange([...selectedIds, id]);
        }
    };

    const handleDelete = async () => {
        if (!deleteId) return;
        try {
            await deleteDocument(deleteId);
            setDeleteId(null);
            // Remove from selection if deleted
            if (selectedIds.includes(deleteId)) {
                onSelectionChange(selectedIds.filter(id => id !== deleteId));
            }
            toast({
                title: "Success",
                description: "Document deleted successfully",
                variant: "success",
            });
        } catch {
            toast({
                title: "Error",
                description: "Failed to delete document",
                variant: "destructive",
            });
        }
    };

    if (isLoading) {
        return (
            <div className="space-y-4 pr-4">
                <DocumentSkeleton />
                <DocumentSkeleton />
                <DocumentSkeleton />
            </div>
        );
    }

    if (isError) {
        return (
            <div className="p-4 text-center text-destructive">
                <p>Failed to load documents</p>
            </div>
        );
    }

    if (documents.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center p-8 text-center h-[300px] border-2 border-dashed rounded-lg border-muted">
                <div className="bg-muted/50 p-4 rounded-full mb-4">
                    <Archive className="h-8 w-8 text-muted-foreground" />
                </div>
                <h3 className="font-semibold">No documents</h3>
                <p className="text-sm text-muted-foreground mt-1">Upload a PDF to get started</p>
            </div>
        );
    }

    return (
        <>
            <div className="space-y-3 pr-4 pb-20">
                {documents.map((doc) => (
                    <Card key={doc.id} className="relative overflow-hidden transition-all hover:border-primary/50 group">
                        <div className="p-4 flex gap-3">
                            <div className="pt-1">
                                <Checkbox
                                    checked={selectedIds.includes(doc.id)}
                                    onCheckedChange={() => handleToggle(doc.id)}
                                />
                            </div>
                            <div className="flex-1 space-y-2">
                                <div className="flex items-start justify-between">
                                    <div className="font-medium text-sm line-clamp-1 break-all" title={doc.filename}>
                                        {doc.filename}
                                    </div>
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        className="h-6 w-6 text-muted-foreground hover:text-destructive shrink-0 -mr-2 -mt-1 opacity-0 group-hover:opacity-100 transition-opacity"
                                        onClick={() => setDeleteId(doc.id)}
                                    >
                                        <Trash2 className="h-4 w-4" />
                                    </Button>
                                </div>

                                <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
                                    <Badge variant="secondary" className="font-normal text-[10px] px-1.5 h-5 flex gap-1">
                                        <Layers className="h-3 w-3" />
                                        {doc.chunk_count || 0} chunks
                                    </Badge>
                                    <span className="flex items-center gap-1">
                                        <File className="h-3 w-3" />
                                        {formatFileSize(doc.file_size)}
                                    </span>
                                    <span className="flex items-center gap-1">
                                        <Calendar className="h-3 w-3" />
                                        {formatDate(doc.upload_date).split(',')[0]}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </Card>
                ))}
            </div>

            <Dialog open={!!deleteId} onOpenChange={(open) => !open && setDeleteId(null)}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Delete Document</DialogTitle>
                        <DialogDescription>
                            Are you sure you want to delete this document? This action cannot be undone.
                        </DialogDescription>
                    </DialogHeader>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setDeleteId(null)}>Cancel</Button>
                        <Button variant="destructive" onClick={handleDelete} disabled={isDeleting}>
                            {isDeleting ? "Deleting..." : "Delete"}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </>
    );
}

DocumentList.propTypes = {
    selectedIds: PropTypes.array,
    onSelectionChange: PropTypes.func.isRequired,
};


