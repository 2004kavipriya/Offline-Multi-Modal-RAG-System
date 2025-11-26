import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

export const useKeyboardShortcuts = () => {
    const navigate = useNavigate();
    const [showHelp, setShowHelp] = useState(false);

    useEffect(() => {
        const handleKeyDown = (event) => {
            // Ignore if typing in an input or textarea (except for Escape)
            if (
                (event.target.tagName === 'INPUT' ||
                    event.target.tagName === 'TEXTAREA' ||
                    event.target.isContentEditable) &&
                event.key !== 'Escape'
            ) {
                return;
            }

            // Global Shortcuts

            // ? - Toggle Help
            if (event.key === '?' && !event.ctrlKey && !event.metaKey && !event.altKey) {
                event.preventDefault();
                setShowHelp(prev => !prev);
            }

            // / - Focus Search
            if (event.key === '/' && !event.ctrlKey && !event.metaKey && !event.altKey) {
                event.preventDefault();
                const searchInput = document.getElementById('search-input');
                if (searchInput) {
                    searchInput.focus();
                } else {
                    // If not on a page with search, maybe navigate to search?
                    // For now, let's assume we want to go to home/search page first
                    navigate('/');
                    // We might need a small timeout to let the page load before focusing
                    setTimeout(() => {
                        const input = document.getElementById('search-input');
                        if (input) input.focus();
                    }, 100);
                }
            }

            // Ctrl+K or Cmd+K - Focus Search (Standard)
            if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
                event.preventDefault();
                const searchInput = document.getElementById('search-input');
                if (searchInput) {
                    searchInput.focus();
                } else {
                    navigate('/');
                    setTimeout(() => {
                        const input = document.getElementById('search-input');
                        if (input) input.focus();
                    }, 100);
                }
            }

            // Escape - Close Help / Blur Input
            if (event.key === 'Escape') {
                if (showHelp) {
                    setShowHelp(false);
                } else if (document.activeElement.tagName === 'INPUT') {
                    document.activeElement.blur();
                }
            }

            // Navigation Shortcuts

            // Alt+1 - Home
            if (event.altKey && event.key === '1') {
                event.preventDefault();
                navigate('/');
            }

            // Alt+2 - Search
            if (event.altKey && event.key === '2') {
                event.preventDefault();
                navigate('/search');
            }

            // Alt+3 - Documents
            if (event.altKey && event.key === '3') {
                event.preventDefault();
                navigate('/documents');
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => {
            window.removeEventListener('keydown', handleKeyDown);
        };
    }, [navigate, showHelp]);

    return { showHelp, setShowHelp };
};
