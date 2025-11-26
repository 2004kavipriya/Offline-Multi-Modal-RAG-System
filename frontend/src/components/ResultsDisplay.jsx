import { useState } from 'react';
import CitationPanel from './CitationPanel';
import { exportResults } from '../api';
import './ResultsDisplay.css';

function ResultsDisplay({ results, question }) {
    const [selectedCitation, setSelectedCitation] = useState(null);
    const [showExportMenu, setShowExportMenu] = useState(false);
    const [exporting, setExporting] = useState(false);

    const handleExport = async (format) => {
        setExporting(true);
        try {
            const response = await exportResults(format, {
                question: question || '',
                answer: results.answer,
                citations: results.citations
            });

            // Create download link
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `search_results_${Date.now()}.${format}`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);

            setShowExportMenu(false);
        } catch (error) {
            console.error('Export failed:', error);
            alert('Export failed. Please try again.');
        } finally {
            setExporting(false);
        }
    };

    if (!results) {
        return null;
    }

    const { answer, citations, context_used } = results;

    // Parse citations in answer text
    const renderAnswerWithCitations = (text) => {
        const citationRegex = /\[(\d+)\]/g;
        const parts = [];
        let lastIndex = 0;
        let match;

        while ((match = citationRegex.exec(text)) !== null) {
            // Add text before citation
            if (match.index > lastIndex) {
                parts.push(
                    <span key={`text-${lastIndex}`}>
                        {text.substring(lastIndex, match.index)}
                    </span>
                );
            }

            // Add citation link
            const citationNum = parseInt(match[1]);
            const citation = citations.find(c => c.id === citationNum);

            parts.push(
                <button
                    key={`citation-${citationNum}`}
                    className="citation-link"
                    onClick={() => setSelectedCitation(citation)}
                    title={citation ? `View source: ${citation.source}` : ''}
                >
                    [{citationNum}]
                </button>
            );

            lastIndex = match.index + match[0].length;
        }

        // Add remaining text
        if (lastIndex < text.length) {
            parts.push(
                <span key={`text-${lastIndex}`}>
                    {text.substring(lastIndex)}
                </span>
            );
        }

        return parts;
    };

    return (
        <div className="results-display">
            <div className="answer-section glass-card animate-fade-in">
                <div className="answer-header">
                    <h3>Answer</h3>
                    <div className="answer-actions">
                        <div className="context-badges flex gap-sm">
                            {context_used.text_chunks > 0 && (
                                <span className="badge badge-info">
                                    📄 {context_used.text_chunks} docs
                                </span>
                            )}
                            {context_used.images > 0 && (
                                <span className="badge badge-info">
                                    🖼️ {context_used.images} images
                                </span>
                            )}
                            {context_used.audio_segments > 0 && (
                                <span className="badge badge-info">
                                    🎵 {context_used.audio_segments} audio
                                </span>
                            )}
                        </div>
                        <div className="export-container">
                            <button
                                className="export-btn"
                                onClick={() => setShowExportMenu(!showExportMenu)}
                                disabled={exporting}
                            >
                                📥 Export
                            </button>
                            {showExportMenu && (
                                <div className="export-menu">
                                    <button onClick={() => handleExport('pdf')}>
                                        📄 PDF
                                    </button>
                                    <button onClick={() => handleExport('docx')}>
                                        📝 DOCX
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                <div className="answer-content">
                    <p>{renderAnswerWithCitations(answer)}</p>
                </div>
            </div>

            {citations && citations.length > 0 && (
                <div className="citations-section">
                    <h4 className="citations-header">Sources ({citations.length})</h4>
                    <div className="citations-grid">
                        {citations
                            .sort((a, b) => (b.similarity || 0) - (a.similarity || 0))
                            .map((citation) => (
                                <div
                                    key={citation.id}
                                    className="citation-card glass-card"
                                >
                                    <div className="citation-header-row">
                                        <div className="citation-number">[{citation.id}]</div>
                                        <div className="relevance-badge" title={`Relevance: ${(citation.similarity * 100).toFixed(1)}%`}>
                                            {(citation.similarity * 100).toFixed(0)}%
                                        </div>
                                    </div>

                                    <div className="relevance-bar">
                                        <div
                                            className="relevance-fill"
                                            style={{ width: `${citation.similarity * 100}%` }}
                                        ></div>
                                    </div>

                                    <div className="citation-info">
                                        <div className="citation-type">
                                            {citation.type === 'text' && '📄'}
                                            {citation.type === 'image' && '🖼️'}
                                            {citation.type === 'audio' && '🎵'}
                                            <span className="badge badge-info">{citation.type}</span>
                                        </div>
                                        <div className="citation-source">{citation.source}</div>
                                        {citation.page && (
                                            <div className="citation-meta">Page {citation.page}</div>
                                        )}
                                    </div>

                                    <div className="citation-actions">
                                        <button
                                            className="btn-small btn-primary"
                                            onClick={() => setSelectedCitation(citation)}
                                            title="View retrieved context"
                                        >
                                            👁️ View Context
                                        </button>
                                        {citation.document_id && (
                                            <>
                                                <button
                                                    className="btn-small btn-secondary"
                                                    onClick={() => window.location.href = '/documents'}
                                                    title="View in Documents page"
                                                >
                                                    📁 View File
                                                </button>
                                                <button
                                                    className="btn-small btn-secondary"
                                                    onClick={() => window.open(`/api/documents/${citation.document_id}/content`, '_blank')}
                                                    title="Open full PDF in new tab"
                                                >
                                                    📄 Open PDF
                                                </button>
                                            </>
                                        )}
                                    </div>
                                </div>
                            ))}
                    </div>
                </div>
            )}

            {selectedCitation && (
                <CitationPanel
                    citation={selectedCitation}
                    onClose={() => setSelectedCitation(null)}
                />
            )}
        </div>
    );
}

export default ResultsDisplay;
