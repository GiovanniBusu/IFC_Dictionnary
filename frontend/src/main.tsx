import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import App from './App.tsx'
import { OutputLanguageProvider } from './outputLanguage.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <OutputLanguageProvider>
        <App />
      </OutputLanguageProvider>
    </BrowserRouter>
  </StrictMode>,
)
