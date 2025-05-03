import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "uno.css";
import { initSentry } from "./utils/sentry";

// Sentry izleme sistemini başlat
initSentry();

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);