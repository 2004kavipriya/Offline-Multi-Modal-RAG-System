import './CitationPanel.css';

function CitationPanel({ citation, onClose }) {
    if (!citation) return null;

    return (
        <div className="citation-panel-overlay" onClick={onClose}>
            <div className="citation-panel glass-card" onClick={(e) => e.stopPropagation()}>
                <div className="panel-header">
                    <div>
                        <h3>Source [{citation.id}]</h3>
                        <div className="relevance-display">
                            Relevance: <strong>{(citation.similarity * 100).toFixed(1)}%</strong>
                        </div>
                    </div>
                    <button className="btn close-button" onClick={onClose}>
                        ✕
                    </button>
                </div>

                <div className="panel-content">
                    <div className="citation-detail">
                        <label>Type</label>
                        <div className="detail-value">
                            {citation.type === 'text' && '📄 Text'}
                            {citation.type === 'image' && '🖼️ Image'}
                            {citation.type === 'audio' && '🎵 Audio'}
                        </div>
                    </div>

                    <div className="citation-detail">
                        <label>Source Document</label>
                        <div className="detail-value">{citation.source}</div>
                    </div>

                    {citation.page && (
                        <div className="citation-detail">
                            <label>Page</label>
                            <div className="detail-value">{citation.page}</div>
                        </div>
                    )}

                    <div className="citation-detail">
                        <label>Retrieved Context</label>
                        <div className="detail-value context-content">
                            {citation.full_content || citation.content}
                        </div>
                    </div>

                    {citation.image_url && (
                        <div className="citation-detail">
                            <label>Image Preview</label>
                            <div className="image-preview">
                                <img src={citation.image_url} alt="Citation" />
                            </div>
                        </div>
                    )}
                </div>

                <div className="panel-footer">
                    {citation.document_id && (
                        <button
                            className="btn btn-primary"
                            onClick={() => window.open(`/api/documents/${citation.document_id}/content`, '_blank')}
                        >
                            📄 Open Full Document
                        </button>
                    )}
                    <button className="btn" onClick={onClose}>Close</button>
                </div>
            </div>
        </div>
    );
}

export default CitationPanel;
