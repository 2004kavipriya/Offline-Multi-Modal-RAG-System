import { useState, useEffect } from 'react';
import api from '../api';
import './SearchHistory.css';

function SearchHistory({ onHistoryClick }) {
    const [history, setHistory] = useState([]);
    const [isOpen, setIsOpen] = useState(false);

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

        // Less than 1 minute
        if (diff < 60000) return 'Just now';

        // Less than 1 hour
        if (diff < 3600000) {
            const mins = Math.floor(diff / 60000);
            return `${mins} min${mins > 1 ? 's' : ''} ago`;
        }

        // Less than 24 hours
        if (diff < 86400000) {
            const hours = Math.floor(diff / 3600000);
            return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        }

        // More than 24 hours
        return date.toLocaleDateString();
    };

    return (
        <div className="search-history-container">
            <button
                className="history-toggle"
                onClick={() => setIsOpen(!isOpen)}
            >
                <span className="history-icon">🕒</span>
                <span className="history-title">Recent Searches</span>
                <span className="history-count">{history.length}</span>
                <span className="arrow">{isOpen ? '▲' : '▼'}</span>
            </button>

            {isOpen && (
                <div className="history-dropdown">
                    <div className="history-header">
                        <span className="header-title">Search History</span>
                        <button
                            className="clear-btn"
                            onClick={handleClearHistory}
                        >
                            Clear All
                        </button>
                    </div>
                    <div className="history-list">
                        {history.length === 0 ? (
                            <div className="empty-history">
                                No search history yet. Perform a search to start tracking your queries.
                            </div>
                        ) : (
                            history.map((item) => (
                                <div
                                    key={item.id}
                                    className="history-item"
                                    onClick={() => onHistoryClick(item.query)}
                                >
                                    <div className="history-query">{item.query}</div>
                                    <div className="history-meta">
                                        <span className="history-time">{formatTime(item.timestamp)}</span>
                                        <span className="history-results">{item.result_count} results</span>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

export default SearchHistory;
