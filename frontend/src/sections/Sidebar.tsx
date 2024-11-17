import React from 'react';
import { useState, useEffect } from 'react';
import { Trash2, PanelRight, FileText, MessageCircle, Clock, Download, X } from 'lucide-react';
import { Sheet, SheetContent, SheetTrigger, SheetHeader, SheetTitle } from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { supabase } from '@/lib/supabase';
import { cn } from '@/lib/utils';
import { useTheme } from '@/Context/ThemeContext';

type Session = {
    id: string;
    title: string;
    created_at: string;
    message_count?: number;
    files?: {
        id: string;
        file_name: string;
        file_type: string;
        file_path: string;
        created_at: string;
    }[];
};

interface SidebarProps {
    onSessionSelect: (sessionId: string) => void;
    currentSessionId?: string | null;
    onDeleteSession?: (sessionId: string) => void;
}

export const Sidebar = ({
    onSessionSelect,
    currentSessionId,
    onDeleteSession
}: SidebarProps) => {
    const [sessions, setSessions] = useState<Session[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [isOpen, setIsOpen] = useState(false);
    const { theme }=useTheme();

    useEffect(() => {
        if (isOpen) {
            fetchSessions();
        }
    }, [isOpen, currentSessionId]);

    const fetchSessions = async () => {
        setIsLoading(true);
        try {
            const { data: sessionsData, error: sessionsError } = await supabase
                .from('chat_sessions')
                .select(`
                    id,
                    title,
                    created_at,
                    messages:messages(count),
                    files:session_files (
                        id,
                        file_name,
                        file_type,
                        file_path,
                        created_at
                    )
                `)
                .order('created_at', { ascending: false });

            if (sessionsError) throw sessionsError;

            const processedSessions = sessionsData?.map(session => ({
                ...session,
                message_count: session.messages?.[0]?.count || 0,
            })) || [];

            setSessions(processedSessions);
        } catch (error) {
            console.error('Error fetching sessions:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
        e.stopPropagation();

        setIsLoading(true);
        try {
            const { data: files } = await supabase
                .from('session_files')
                .select('file_path')
                .eq('session_id', sessionId);

            if (files) {
                for (const file of files) {
                    await supabase.storage
                        .from('chat-files')
                        .remove([file.file_path]);
                }
            }

            const { error } = await supabase
                .from('chat_sessions')
                .delete()
                .eq('id', sessionId);

            if (error) throw error;

            setSessions(prev => prev.filter(session => session.id !== sessionId));
            onDeleteSession?.(sessionId);
        } catch (error) {
            console.error('Error deleting session:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDownloadFile = async (filePath: string, fileName: string, e: React.MouseEvent) => {
        e.stopPropagation();
        try {
            const { data, error } = await supabase.storage
                .from('chat-files')
                .download(filePath);

            if (error) throw error;

            const url = window.URL.createObjectURL(data);
            const a = document.createElement('a');
            a.href = url;
            a.download = fileName;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error('Error downloading file:', error);
        }
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now.getTime() - date.getTime();

        const minutes = Math.floor(diff / (1000 * 60));
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));

        if (days === 0) {
            if (hours === 0) {
                return minutes <= 1 ? 'Just now' : `${minutes} minutes ago`;
            } else {
                return hours === 1 ? 'An hour ago' : `${hours} hours ago`;
            }
        } else if (days === 1) {
            return 'Yesterday';
        } else if (days < 7) {
            return `${days} days ago`;
        } else {
            return date.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
                hour: 'numeric',
                minute: 'numeric',
                hour12: true
            });
        }
    };


    const filteredSessions = sessions.filter(session =>
        session.title.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <Sheet open={isOpen} onOpenChange={setIsOpen}>
            <SheetTrigger asChild>
                <Button
                    size="icon"
                    className={`${theme === 'dark' ? 'bg-black text-white' : 'bg-white text-black'} hover:bg-white hover:text-primary rounded-none fixed left-3 top-3 z-50 transition-colors duration-300`}
                    aria-label="Open chat history"
                >
                    <PanelRight className="h-5 w-5" />
                </Button>
            </SheetTrigger>
            <SheetContent
                side="left"
                className={`w-[350px] p-0 ${theme === 'dark' ? 'bg-black' : 'bg-white'} border-r`}
            >
                <SheetHeader className="p-4 border-b">
                    <div className="flex items-center justify-between">
                        <SheetTitle className={`text-lg font-semibold ${theme === 'dark' ? 'text-white' : 'text-black'} `}>Chat History</SheetTitle>
                        <Button
                            size="icon"
                            onClick={() => setIsOpen(false)}
                            className={`h-8 w-8 rounded-none ${theme === 'dark' ? 'bg-black text-white' : 'bg-white text-black'} hover:text-primary hover:${theme === 'dark' ? 'bg-black' : 'bg-white'}  transition-colors duration-300`}
                        >
                            <X className="h-5 w-5" />
                        </Button>
                    </div>
                    <input
                        type="text"
                        placeholder="Search conversations..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className={`w-full px-3 py-2 ${theme === 'dark' ? 'bg-black text-white' : 'bg-white text-black'} border ${theme === 'dark' ? 'border-white' : 'border-black'} text-sm focus:outline-none focus:border-primary`}
                    />
                </SheetHeader>
                <ScrollArea className="h-[calc(100vh-120px)] p-4">
                    <div className="space-y-2">
                        {isLoading ? (
                            <div className="text-center">Loading...</div>
                        ) : filteredSessions.length === 0 ? (
                            <div className="text-center">No conversations found.</div>
                        ) : (
                            filteredSessions.map((session) => (
                                <div
                                    key={session.id}
                                    onClick={() => onSessionSelect(session.id)}
                                    className={cn(
                                        "p-3 border hover:border-primary cursor-pointer transition-all duration-300",
                                        currentSessionId === session.id && "border-primary",
                                        theme==='dark' ? 'border-white':'border-black' 
                                    )}
                                >
                                    <div className="flex justify-between items-start gap-2">
                                        <div className="flex-1 min-w-0">
                                            <h3 className={`font-medium ${theme === 'dark' ? 'text-white' : 'text-black'}  truncate`}>
                                                {session.title}
                                            </h3>
                                            <div className={`flex items-center gap-2 mt-1 text-sm ${theme === 'dark' ? 'text-white' : 'text-black'} `}>
                                                <Clock className="h-3 w-3" />
                                                <span>{formatDate(session.created_at)}</span>
                                            </div>
                                            <div className={`flex items-center gap-2 mt-1 text-sm ${theme === 'dark' ? 'text-white' : 'text-black'} `}>
                                                <MessageCircle className="h-3 w-3" />
                                                {session.message_count} messages
                                            </div>
                                        </div>
                                        <Button
                                            size="icon"
                                            className={`h-8 w-8 rounded-none ${theme === 'dark' ? 'bg-black text-white' : 'bg-white text-black'} hover:text-red-500 hover:${theme === 'dark' ? 'bg-black' : 'bg-white'} transition-colors duration-300`}
                                            onClick={(e) => handleDeleteSession(session.id, e)}
                                            disabled={isLoading}
                                        >
                                            <Trash2 className="h-5 w-5" />
                                        </Button>
                                    </div>
                                    {session.files && session.files.length > 0 && (
                                        <>
                                            <Separator className={`my-2 ${theme === 'dark' ? 'bg-white' : 'bg-black'}`} />
                                            <div className="space-y-1">
                                                {session.files.map((file) => (
                                                    <div
                                                        key={file.id}
                                                        className={`flex items-center justify-between text-sm ${theme === 'dark' ? 'text-white' : 'text-black'}  p-1`}
                                                    >
                                                        <div className="flex items-center gap-2 truncate">
                                                            <FileText className="h-3 w-3 flex-shrink-0" />
                                                            <span className="truncate">{file.file_name}</span>
                                                        </div>
                                                        <Button
                                                            size="icon"
                                                            className={`h-5 w-5 rounded-none ${theme === 'dark' ? 'bg-black text-white' : 'bg-white text-black'} hover:text-primary hover:bg-black transition-colors duration-300`}
                                                            onClick={(e) => handleDownloadFile(file.file_path, file.file_name, e)}
                                                        >
                                                            <Download className="h-5 w-5" />
                                                        </Button>
                                                    </div>
                                                ))}
                                            </div>
                                        </>
                                    )}
                                </div>
                            ))
                        )}
                    </div>
                </ScrollArea>
            </SheetContent>
        </Sheet>
    );
};

export default Sidebar;