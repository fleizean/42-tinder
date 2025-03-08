import { useTheme } from "next-themes";
import { FaSun, FaMoon, FaDesktop } from "react-icons/fa";
import { useState } from "react";
import { IconType } from "react-icons";

interface ThemeOption {
  id: 'light' | 'dark';
  name: string;
  icon: IconType;
}

const themes: ThemeOption[] = [
  { id: 'light', name: 'Açık Tema', icon: FaSun },
  { id: 'dark', name: 'Koyu Tema', icon: FaMoon },
];

const ThemeToggler = () => {
  const { theme, setTheme } = useTheme();
  const [isOpen, setIsOpen] = useState(false);
  
  const getCurrentTheme = (): ThemeOption => {
    return themes.find(t => t.id === theme) || themes[0];
  };

  const currentTheme = getCurrentTheme();

  return (
    <div className="relative">
      <button
        aria-label='theme toggler'
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-600"
      >
        {currentTheme.icon && <currentTheme.icon className="w-4 h-4 mr-2" />}
        {currentTheme.name}
      </button>

      {isOpen && (
        <div className="absolute left-0 w-full mt-1 bg-white rounded-md shadow-lg dark:bg-gray-700">
          {themes.map((themeOption) => (
            <button
              key={themeOption.id}
              onClick={() => {
                setTheme(themeOption.id);
                setIsOpen(false);
              }}
              className={`flex items-center w-full px-4 py-2 text-sm ${
                theme === themeOption.id
                  ? 'text-primary bg-gray-100 dark:bg-gray-600'
                  : 'text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              <themeOption.icon className="w-4 h-4 mr-2" />
              {themeOption.name}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default ThemeToggler;