import Link from 'next/link';
import Image from 'next/image';
import Logo from '@/assets/logo.png';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/Context/AuthContext';
import { supabase } from '@/lib/supabase';
import ThemeToggle from '@/components/ui/ThemeToggle';
import { useTheme } from '@/Context/ThemeContext';

export const Header = () => {
    const router = useRouter();
    const { user } = useAuth();
    const { theme } = useTheme();

    const handleSignOut = async () => {
        await supabase.auth.signOut();
        router.push('/');
    };

    return (
        <header className={`container ${theme === 'dark' ? 'text-white' : 'text-black'} py-2`}>
            <div className={`mx-auto flex justify-between items-center py-2 border-b ${theme === 'dark' ? 'border-white' : 'border-black'}`}>
                <div className="flex items-center">
                    <Image
                        src={Logo}
                        alt="CarbonCare Logo"
                        width={50}
                        height={50}
                        className="md:mr-2 mb-2"
                        priority
                    />
                    <h1 className={`text-xl md:text-2xl font-bold ${theme === 'dark' ? 'text-white' : 'text-black'}`}>
                        <Link href="/">CarbonCare</Link>
                    </h1>
                </div>

                <nav className="flex items-center space-x-2 md:space-x-6 font-semibold">
                    <ThemeToggle />
                    <ul className="flex space-x-2 md:space-x-4">
                        {!user ? (
                            <>
                                <li>
                                    <Link href="/signup" className={`text-sm md:text-base ${theme === 'dark' ? 'text-white' : 'text-black'} hover:text-primary transition-colors duration-300`}>
                                        Signup
                                    </Link>
                                </li>
                                <li>
                                    <Link href="/login" className={`text-sm md:text-base ${theme === 'dark' ? 'text-white' : 'text-black'} hover:text-primary transition-colors duration-300`}>
                                        Login
                                    </Link>
                                </li>
                            </>
                        ) : (
                            <li>
                                <button
                                    onClick={handleSignOut}
                                    className={`text-sm md:text-base ${theme === 'dark' ? 'text-white' : 'text-black'} hover:text-primary transition-colors duration-300`}
                                >
                                    Logout
                                </button>
                            </li>
                        )}
                    </ul>
                </nav>
            </div>
        </header>
    );
};