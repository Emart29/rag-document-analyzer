import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentAPI } from '../services/api';

export const useDocuments = () => {
    const queryClient = useQueryClient();

    const documentsQuery = useQuery({
        queryKey: ['documents'],
        queryFn: async () => {
            const response = await documentAPI.list();
            // Map documents and ensure proper ID field for selection
            return response.data.documents.map(doc => ({
                ...doc,
                id: doc.document_id
            }));
        },
    });

    const uploadMutation = useMutation({
        mutationFn: ({ file, onProgress }) => documentAPI.upload(file, onProgress),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['documents'] });
        },
    });

    const deleteMutation = useMutation({
        mutationFn: (id) => documentAPI.delete(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['documents'] });
        },
    });

    return {
        documents: documentsQuery.data || [],
        isLoading: documentsQuery.isLoading,
        isError: documentsQuery.isError,
        error: documentsQuery.error,
        uploadDocument: uploadMutation.mutateAsync,
        isUploading: uploadMutation.isPending,
        deleteDocument: deleteMutation.mutateAsync,
        isDeleting: deleteMutation.isPending,
    };
};
