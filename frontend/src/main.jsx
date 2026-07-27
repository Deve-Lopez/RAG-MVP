import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';

/* Importación de estilos de terceros (Bootstrap) y de la hoja de estilos global personalizada (Theme) */
import 'bootstrap/dist/css/bootstrap.min.css';
import "./styles/theme.css";

/* Punto de entrada de la aplicación: monta el componente raíz dentro del elemento DOM 'root' utilizando React.StrictMode */
ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
);