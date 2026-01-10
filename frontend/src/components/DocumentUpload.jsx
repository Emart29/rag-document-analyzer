import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { Button } from './ui/Button';
import { Progress } from './ui/Progress';
import { toast } from '../hooks/use-toast';
import { useDocuments } from '../hooks/useDocuments';
import { formatFileSize } from '../services/api';
import { cn } from '../lib/utils';
import { Alert, AlertDescription, AlertTitle } from './ui/Alert';
import { Card, CardContent } from './ui/Card';

export default function DocumentUpload() {
    const [file, setFile] = useState(null);
    const [progress, setProgress] = useState(0);
    const [error, setError] = useState(null);
    const { uploadDocument, isUploading } = useDocuments();

    const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
        setError(null);
        if (rejectedFiles.length > 0) {
            const rejection = rejectedFiles[0];
            if (rejection.errors[0].code === 'file-too-large') {
                setError('File is too large. Max size is 10MB.');
            } else if (rejection.errors[0].code === 'file-invalid-type') {
                setError('Invalid file type. Only PDF files are allowed.');
            } else {
                setError(rejection.errors[0].message);
            }
            return;
        }

        if (acceptedFiles.length > 0) {
            setFile(acceptedFiles[0]);
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/pdf': ['.pdf']
        },
        maxSize: 10 * 1024 * 1024, // 10MB
        multiple: false,
        disabled: isUploading
    });

    const handleUpload = async () => {
        if (!file) return;

        try {
            setProgress(0);
            await uploadDocument({
                file,
                onProgress: (val) => setProgress(val)
            });
            toast({
                title: "Success",
                description: "Document uploaded successfully",
                variant: "success",
            });
            setFile(null);
            setProgress(0);
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.detail || "Failed to upload document");
            toast({
                title: "Error",
                description: "Failed to upload document",
                variant: "destructive",
            });
        }
    };

    const clearFile = (e) => {
        e.stopPropagation();
        setFile(null);
        setError(null);
        setProgress(0);
    };

    return (
        <div className="space-y-4 h-full flex flex-col">
            <div
                {...getRootProps()}
                className={cn(
                    "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors flex-1 flex flex-col items-center justify-center min-h-[200px]",
                    isDragActive ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-primary/50",
                    isUploading && "pointer-events-none opacity-50",
                    error && "border-destructive/50 bg-destructive/5"
                )}
            >
                <input {...getInputProps()} />

                {file ? (
                    <div className="flex flex-col items-center gap-4 w-full max-w-xs">
                        <div className="relative">
                            <div className="bg-primary/10 p-4 rounded-full">
                                <FileText className="h-8 w-8 text-primary" />
                            </div>
                            {!isUploading && (
                                <button
                                    onClick={clearFile}
                                    className="absolute -top-2 -right-2 bg-destructive text-white rounded-full p-1 hover:bg-destructive/90 transition-colors"
                                >
                                    <X className="h-3 w-3" />
                                </button>
                            )}
                        </div>
                        <div className="text-center">
                            <p className="font-medium truncate max-w-[200px]">{file.name}</p>
                            <p className="text-sm text-muted-foreground">{formatFileSize(file.size)}</p>
                        </div>
                    </div>
                ) : (
                    <div className="flex flex-col items-center gap-2">
                        <div className="bg-muted p-4 rounded-full">
                            <Upload className="h-8 w-8 text-muted-foreground" />
                        </div>
                        <p className="font-medium">Click to upload or drag & drop</p>
                        <p className="text-sm text-muted-foreground">PDF only (max 10MB)</p>
                    </div>
                )}
            </div>

            {error && (
                <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>Error</AlertTitle>
                    <AlertDescription>{error}</AlertDescription>
                </Alert>
            )}

            {/* Upload Progress or Button */}
            {file && (
                <div className="space-y-4">
                    {isUploading ? (
                        <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                                <span>Uploading...</span>
                                <span>{progress}%</span>
                            </div>
                            <Progress value={progress} />
                        </div>
                    ) : (
                        <Button className="w-full" onClick={handleUpload}>
                            Upload Document
                        </Button>
                    )}
                </div>
            )}
        </div>
    );
}
