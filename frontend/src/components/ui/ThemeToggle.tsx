import { useTheme } from "@/Context/ThemeContext";
import { Sun, Moon } from "lucide-react";

const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === "dark";

  return (
    <div className="flex items-center gap-2">
      <div 
        onClick={toggleTheme}
        className={`
          w-14 h-7 rounded-full p-1 cursor-pointer
          transition-colors duration-200 ease-in-out
          ${isDark ? 'bg-slate-700' : 'bg-slate-200'}
          relative
        `}
      >
        <div
          className={`
            absolute w-5 h-5 rounded-full 
            transition-transform duration-200 ease-in-out
            flex items-center justify-center
            ${isDark ? 'translate-x-7 bg-slate-900' : 'translate-x-0 bg-white'}
          `}
        >
          {isDark ? (
            <Moon className="w-3 h-3 text-white" />
          ) : (
            <Sun className="w-3 h-3 text-yellow-500" />
          )}
        </div>
      </div>
    </div>
  );
};

export default ThemeToggle;