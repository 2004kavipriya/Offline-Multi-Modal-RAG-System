import { useState } from 'react'
import { ragQuery, search, crossModalSearch } from '../services/api'
import '../styles/QueryInterface.css'

function QueryInterface({ onResults, onLoading }) {
    const [query, setQuery] = useState('')
    const [searchMode, setSearchMode] = useState('rag') // 'rag', 'search', 'cross-modal'
    const [error, setError] = useState(null)

    const handleSubmit = async (e) => {
        e.preventDefault()

        if (!query.trim()) {
            setError('Please enter a query')
            return
        }

        setError(null)
        onLoading(true)

        try {
            let response

            if (searchMode === 'rag') {
                response = await ragQuery(query)
            } else if (searchMode === 'search') {
                response = await search(query)
            } else {
                response = await crossModalSearch(query)
            }

            onResults(response)
        } catch (err) {
            setError(err.response?.data?.detail || 'An error occurred. Please try again.')
            console.error('Query error:', err)
        } finally {
            onLoading(false)
        }
    }

    return (
        <div className="query-interface">
            <div className="query-card">
                <h2>Ask a Question</h2>
                <p className="query-description">
                    Search across your documents, images, and audio files using natural language
                </p>

                {/* Search Mode Selector */}
                <div className="mode-selector">
                    <button
                        className={`mode-btn ${searchMode === 'rag' ? 'active' : ''}`}
                        onClick={() => setSearchMode('rag')}
                        title="AI-powered answers with citations"
                    >
                        <span className="mode-icon">🤖</span>
                        <span>AI Answer</span>
                    </button>
                    <button
                        className={`mode-btn ${searchMode === 'search' ? 'active' : ''}`}
                        onClick={() => setSearchMode('search')}
                        title="Semantic search results"
                    >
                        <span className="mode-icon">🔍</span>
                        <span>Search</span>
                    </button>
                    <button
                        className={`mode-btn ${searchMode === 'cross-modal' ? 'active' : ''}`}
                        onClick={() => setSearchMode('cross-modal')}
                        title="Search across text and images"
                    >
                        <span className="mode-icon">🖼️</span>
                        <span>Cross-Modal</span>
                    </button>
                </div>

                {/* Query Form */}
                <form onSubmit={handleSubmit} className="query-form">
                    <div className="input-wrapper">
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="e.g., What are the key findings in the 2024 report?"
                            className="query-input"
                        />
                        <button type="submit" className="submit-btn">
                            <span className="btn-icon">→</span>
                            <span>Search</span>
                        </button>
                    </div>
                </form>

                {error && (
                    <div className="error-message">
                        <span className="error-icon">⚠️</span>
                        {error}
                    </div>
                )}

                {/* Quick Examples */}
                <div className="quick-examples">
                    <p className="examples-label">Try asking:</p>
                    <div className="example-chips">
                        <button
                            className="example-chip"
                            onClick={() => setQuery('Summarize the main points from the documents')}
                        >
                            Summarize documents
                        </button>
                        <button
                            className="example-chip"
                            onClick={() => setQuery('Show me screenshots related to the dashboard')}
                        >
                            Find screenshots
                        </button>
                        <button
                            className="example-chip"
                            onClick={() => setQuery('What was discussed in the meeting recording?')}
                        >
                            Meeting notes
                        </button>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default QueryInterface
