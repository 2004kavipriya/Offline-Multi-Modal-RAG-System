import { useState, useEffect } from 'react';
import api from '../api';
import './SearchHistorySidebar.css';

function SearchHistorySidebar({ onHistoryClick, onCollapseChange }) {
    const [history, setHistory] = useState([]);
    const [isCollapsed, setIsCollapsed] = useState(true); // Start collapsed

    const fetchHistory = async () => {
        try {
            const response = await api.get('/search-history');
            if (Array.isArray(response.data)) {
                setHistory(response.data);
            }
        } catch (error) {
            console.error('Error fetching search history:', error);
        }
    };

    useEffect(() => {
        fetchHistory();

        // Refresh history every 5 seconds to pick up new searches
        const interval = setInterval(fetchHistory, 5000);
        return () => clearInterval(interval);
    }, []);

    const handleClearHistory = async () => {
        if (!window.confirm('Clear all search history?')) return;

        try {
            await api.delete('/search-history');
            setHistory([]);
        } catch (error) {
            console.error('Error clearing history:', error);
        }
    };

    const formatTime = (isoString) => {
        const date = new Date(isoString);
        const now = new Date();
        const diff = now - date;

        if (diff < 60000) return 'Just now';
        if (diff < 3600000) {
            const mins = Math.floor(diff / 60000);
            return `${mins}m ago`;
        }
        if (diff < 86400000) {
            const hours = Math.floor(diff / 3600000);
            return `${hours}h ago`;
        }
        const days = Math.floor(diff / 86400000);
        if (days === 1) return 'Yesterday';
        if (days < 7) return `${days}d ago`;
        return date.toLocaleDateString();
    };

    const toggleCollapse = () => {
        const newState = !isCollapsed;
        setIsCollapsed(newState);
        if (onCollapseChange) {
            onCollapseChange(newState);
        }
    };

    return (
        <div className={`history-sidebar ${isCollapsed ? 'collapsed' : ''}`}>
            <div className="sidebar-header">
                <button
                    className="toggle-btn"
                    onClick={toggleCollapse}
                    title={isCollapsed ? 'Expand' : 'Collapse'}
                >
                    {isCollapsed ? '▶' : '◀'}
                </button>
                {!isCollapsed && (
                    <>
                        <h3>History</h3>
                        {history.length > 0 && (
                            <button
                                className="clear-all-btn"
                                onClick={handleClearHistory}
                                title="Clear all history"
                            >
                                ✕
                            </button>
                        )}
                    </>
                )}
            </div>

            {!isCollapsed && (
                <div className="sidebar-content">
                    {history.length === 0 ? (
                        <div className="empty-state">
                            <span className="empty-icon">🕒</span>
                            <p>No searches yet</p>
                        </div>
                    ) : (
                        <div className="history-items">
                            {history.map((item) => (
                                <div
                                    key={item.id}
                                    className="history-item"
                                    onClick={() => onHistoryClick(item.query)}
                                    title={item.query}
                                >
                                    <div className="item-query">{item.query}</div>
                                    <div className="item-time">{formatTime(item.timestamp)}</div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default SearchHistorySidebar;
