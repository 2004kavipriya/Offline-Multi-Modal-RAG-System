import '../styles/CitationCard.css'

function CitationCard({ citation, expanded, onToggle }) {
    const getTypeIcon = (type) => {
        switch (type) {
            case 'pdf': return '📄'
            case 'docx': return '📝'
            case 'image': return '🖼️'
            case 'audio': return '🎵'
            default: return '📎'
        }
    }

    return (
        <div className={`citation-card ${expanded ? 'expanded' : ''}`}>
            <div className="citation-header" onClick={onToggle}>
                <div className="citation-title">
                    <span className="citation-number">[{citation.citation_id}]</span>
                    <span className="citation-icon">{getTypeIcon(citation.document_type)}</span>
                    <span className="citation-filename">{citation.filename}</span>
                </div>
                <div className="citation-meta">
                    {citation.page_number && (
                        <span className="meta-badge">Page {citation.page_number}</span>
                    )}
                    {citation.timestamp && (
                        <span className="meta-badge">⏱️ {citation.timestamp}</span>
                    )}
                    <span className="expand-icon">{expanded ? '▼' : '▶'}</span>
                </div>
            </div>

            {expanded && (
                <div className="citation-content">
                    <div className="citation-excerpt">
                        <p className="excerpt-label">Excerpt:</p>
                        <p className="excerpt-text">{citation.excerpt}</p>
                    </div>
                    <div className="citation-footer">
                        <span className="relevance-score">
                            Relevance: {(citation.relevance_score * 100).toFixed(0)}%
                        </span>
                    </div>
                </div>
            )}
        </div>
    )
}

export default CitationCard
