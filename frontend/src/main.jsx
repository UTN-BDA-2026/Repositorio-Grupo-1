import { StrictMode, useState } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";
import Admin from "./Admin.jsx";

function AppWrapper() {
  const [currentView, setCurrentView] = useState("dashboard");

  return (
    <>
      <App view={currentView} onViewChange={setCurrentView} />
      <Admin view={currentView} onViewChange={setCurrentView} />
    </>
  );
}

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <AppWrapper />
  </StrictMode>,
);
