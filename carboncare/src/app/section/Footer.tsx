import { useTheme } from '@/Context/ThemeContext';  // Adjust path if needed

export const Footer = () => {
  const { theme } = useTheme();  // Get the current theme from context

  return (
    <footer className={`container mx-auto py-2 ${theme === 'dark' ? 'bg-black' : 'bg-white'}`}>
      <div className={`flex justify-between items-center border-t ${theme === 'dark' ? 'border-white text-white' : 'border-black text-black'} pt-6`}>
        <p>&copy; 2024 CarbonCare</p>
        <p>Team Raptors</p>
      </div>
    </footer>
  );
};
