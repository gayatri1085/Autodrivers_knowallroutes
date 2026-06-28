import { useState, useEffect } from "react";
import Home from "./pages/Home";
import "./styles.css";

export default function App() {
  const [darkMode, setDarkMode] = useState(
    () => window.matchMedia("(prefers-color-scheme: dark)").matches
  );

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", darkMode ? "dark" : "light");
  }, [darkMode]);

  return <Home darkMode={darkMode} onToggleDarkMode={() => setDarkMode((d) => !d)} />;
}
