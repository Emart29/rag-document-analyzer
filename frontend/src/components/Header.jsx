import React, { useEffect, useState } from 'react';
import { Brain, RotateCw, Activity, Sun, Moon } from 'lucide-react';
import { Button } from './ui/Button';
import { Badge } from './ui/Badge';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { systemAPI } from '../services/api';
import { toast } from '../hooks/use-toast';

export default function Header() {
    const queryClient = useQueryClient();


    const [isDark, setIsDark] = useState(() => {
        // Initialize from local storage or system preference
        return localStorage.getItem('theme') === 'dark' ||
            (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches);
    });

    useEffect(() => {
        // Sync DOM with state
        if (isDark) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    }, [isDark]);

    const toggleTheme = () => {
        const newMode = !isDark;
        setIsDark(newMode);
        if (newMode) {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        }
    };

    // Use a query to fetch system health
    const { data: health, isLoading, isError, refetch } = useQuery({
        queryKey: ['health'],
        queryFn: async () => {
            const res = await systemAPI.getHealth();
            return res.data;
        },
        // Refresh every 30 seconds
        refetchInterval: 30000,
        retry: 1
    });

    const handleRefresh = async () => {
        // Invalidate all queries to refresh the entire app state
        await queryClient.invalidateQueries();
        refetch();
        toast({ description: "Refreshed all data" });
    };

    const getStatusColor = (status) => {
        if (status === 'healthy' || status === 'ok') return 'success';
        if (status === 'degraded') return 'warning';
        return 'destructive';
    };

    const statusText = health?.status || (isError ? 'Unhealthy' : 'Unknown');

    return (
        <header className="border-b h-16 flex items-center px-6 justify-between bg-card text-card-foreground">
            <div className="flex items-center gap-2">
                <div className="bg-primary/10 p-2 rounded-lg">
                    <Brain className="h-6 w-6 text-primary" />
                </div>
                <div>
                    <h1 className="font-bold text-lg leading-none">RAG Document Analyzer</h1>
                    <p className="text-xs text-muted-foreground">v{import.meta.env.VITE_APP_VERSION || '1.0.0'}</p>
                </div>
            </div>

            <div className="flex items-center gap-4">
                {isLoading ? (
                    <Badge variant="outline" className="gap-1">
                        <Activity className="h-3 w-3 animate-pulse" />
                        Checking...
                    </Badge>
                ) : isError ? (
                    <Badge variant="destructive" className="gap-1">
                        <Activity className="h-3 w-3" />
                        Unhealthy
                    </Badge>
                ) : (
                    <Badge variant={getStatusColor(statusText)} className="gap-1 capitalize">
                        <Activity className="h-3 w-3" />
                        {statusText}
                    </Badge>
                )}

                <Button variant="ghost" size="icon" onClick={toggleTheme} title={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}>
                    {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
                </Button>

                <Button variant="ghost" size="icon" onClick={handleRefresh} title="Refresh Data">
                    <RotateCw className="h-4 w-4" />
                </Button>
            </div>
        </header>
    );
}
