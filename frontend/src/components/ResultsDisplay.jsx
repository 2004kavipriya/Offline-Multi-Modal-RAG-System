import { useState } from 'react'
import CitationCard from './CitationCard'
import '../styles/ResultsDisplay.css'

function ResultsDisplay({ results, loading }) {
    const [expandedCitation, setExpandedCitation] = useState(null)

    if (loading) {
        return (
            <div className="results-display">
                <div className="loading-container">
                    <div className="loading-spinner"></div>
                    <p>Searching and generating answer...</p>
                </div>
            </div>
        )
    }

    if (!results) return null

    const isRAGResponse = results.answer !== undefined
    const isSearchResponse = results.results !== undefined

    return (
        <div className="results-display">
            {/* RAG Answer */}
            {isRAGResponse && (
                <div className="answer-section">
                    <h2>Answer</h2>
                    <div className="answer-card">
                        <div className="answer-content">
                            {results.answer}
                        </div>
                        {results.context_used > 0 && (
                            <div className="context-info">
                                <span className="info-icon">ℹ️</span>
                                Based on {results.context_used} relevant document{results.context_used > 1 ? 's' : ''}
                            </div>
                        )}
                    </div>

                    {/* Citations */}
                    {results.citations && results.citations.length > 0 && (
                        <div className="citations-section">
                            <h3>Sources ({results.citations.length})</h3>
                            <div className="citations-grid">
                                {results.citations.map((citation) => (
                                    <CitationCard
                                        key={citation.citation_id}
                                        citation={citation}
                                        expanded={expandedCitation === citation.citation_id}
                                        onToggle={() =>
                                            setExpandedCitation(
                                                expandedCitation === citation.citation_id
                                                    ? null
                                                    : citation.citation_id
                                            )
                                        }
                                    />
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Search Results */}
            {isSearchResponse && (
                <div className="search-results-section">
                    <h2>Search Results ({results.total_results})</h2>
                    <div className="results-grid">
                        {results.results.map((result, index) => (
                            <div key={index} className="result-card">
                                <div className="result-header">
                                    <span className="result-type-badge">
                                        {result.document_type}
                                    </span>
                                    <span className="result-score">
                                        {(result.relevance_score * 100).toFixed(0)}% match
                                    </span>
                                </div>
                                <h3 className="result-filename">{result.filename}</h3>
                                <p className="result-content">{result.content}</p>
                                {result.page_number && (
                                    <p className="result-meta">Page {result.page_number}</p>
                                )}
                                {result.timestamp && (
                                    <p className="result-meta">⏱️ {result.timestamp}</p>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}

export default ResultsDisplay
