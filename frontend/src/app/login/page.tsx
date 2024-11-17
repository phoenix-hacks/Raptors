"use client";

import Link from 'next/link';
import Image from 'next/image';
import Logo from '@/assets/logo.png';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import { useTheme } from '@/Context/ThemeContext';

const LoginPage = () => {
    const router = useRouter();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { theme }=useTheme();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const { error } = await supabase.auth.signInWithPassword({
                email,
                password,
            });

            if (error) throw error;

            router.push('/');
        } catch (error: any) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen">
            <div className="flex items-center justify-center">
                <Image
                    src={Logo}
                    alt="CarbonCare Logo"
                    width={50}
                    height={50}
                    className="mr-2 py-4"
                    priority
                />
                <h1 className="text-2xl font-bold mb-0">
                    <Link href="/">
                        CarbonCare
                    </Link>
                </h1>
            </div>
            <form className={`border ${theme === 'dark' ? 'border-white' : 'border-black'} px-8 pt-6 pb-8 mb-4 w-96`} onSubmit={handleLogin}>
                {error && (
                    <div className="mb-4 text-red-500 text-sm text-center">
                        {error}
                    </div>
                )}
                <div className="mb-4">
                    <label className={`block ${theme === 'dark' ? 'text-white' : 'text-black'}  text-sm font-bold mb-2`} htmlFor="email">
                        Email
                    </label>
                    <input
                        className={`shadow appearance-none border w-full py-2 px-3 ${theme === 'dark' ? 'bg-black text-white' : 'bg-gray-200 text-black'} leading-tight focus:outline-none focus:shadow-outline focus:border-primary`}
                        id="email"
                        type="email"
                        placeholder="enter your email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                </div>
                <div className="mb-4">
                    <label className={`block ${theme === 'dark' ? 'text-white' : 'text-black'}  text-sm font-bold mb-2`} htmlFor="password">
                        Password
                    </label>
                    <input
                        className={`shadow appearance-none border w-full py-2 px-3 ${theme === 'dark' ? 'bg-black text-white' : 'bg-gray-200 text-black'} leading-tight focus:outline-none focus:shadow-outline focus:border-primary`}
                        id="password"
                        type="password"
                        placeholder="enter your password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <div className="flex items-center justify-center py-2">
                    <button
                        className={`${theme === 'dark' ? 'bg-black text-white' : 'bg-gray-200 text-black'} hover:text-primary border font-bold py-2 px-4 focus:outline-none focus:shadow-outline disabled:opacity-50`}
                        type="submit"
                        disabled={loading}
                    >
                        {loading ? 'Loading...' : 'Login'}
                    </button>
                </div>
                <p className="text-gray-400 text-sm pt-2 text-center">
                    Don&apos;t have an account?{' '}
                    <Link href="/signup" className="text-primary hover:underline">
                        Signup
                    </Link>
                </p>
            </form>
        </div>
    );
};

export default LoginPage;