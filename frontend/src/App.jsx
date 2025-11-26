import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Search from './pages/Search';
import Documents from './pages/Documents';
import Navbar from './components/Navbar';
import KeyboardShortcutsHelp from './components/KeyboardShortcutsHelp';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';
import './App.css';

function AppContent() {
    const { showHelp, setShowHelp } = useKeyboardShortcuts();

    return (
        <div className="app">
            <Navbar />
            <KeyboardShortcutsHelp isOpen={showHelp} onClose={() => setShowHelp(false)} />

            <main className="main-content">
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/search" element={<Search />} />
                    <Route path="/documents" element={<Documents />} />
                </Routes>
            </main>

            <footer className="footer">
                <div className="container">
                    <p className="footer-text">
                        Multimodal RAG System - Offline AI-Powered Search
                    </p>
                </div>
            </footer>
        </div>
    );
}

function App() {
    return (
        <Router>
            <AppContent />
        </Router>
    );
}

export default App;
