import React from 'react';
import './KeyboardShortcutsHelp.css';

const KeyboardShortcutsHelp = ({ isOpen, onClose }) => {
    if (!isOpen) return null;

    const shortcuts = [
        { key: '/', description: 'Focus Search' },
        { key: 'Ctrl + K', description: 'Focus Search' },
        { key: 'Esc', description: 'Close Modals / Blur Input' },
        { key: '?', description: 'Toggle Shortcuts Help' },
        { key: 'Alt + 1', description: 'Go to Home' },
        { key: 'Alt + 2', description: 'Go to Search' },
        { key: 'Alt + 3', description: 'Go to Documents' },
    ];

    return (
        <div className="shortcuts-overlay" onClick={onClose}>
            <div className="shortcuts-modal glass-card" onClick={e => e.stopPropagation()}>
                <div className="shortcuts-header">
                    <h3>Keyboard Shortcuts</h3>
                    <button className="close-btn" onClick={onClose}>&times;</button>
                </div>
                <div className="shortcuts-list">
                    {shortcuts.map((shortcut, index) => (
                        <div key={index} className="shortcut-item">
                            <span className="shortcut-key">
                                {shortcut.key.split(' ').map((k, i) => (
                                    <kbd key={i}>{k}</kbd>
                                ))}
                            </span>
                            <span className="shortcut-desc">{shortcut.description}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default KeyboardShortcutsHelp;
