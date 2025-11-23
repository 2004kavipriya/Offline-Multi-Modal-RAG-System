import { useState, useEffect } from 'react'
import { getDocuments, deleteDocument } from '../services/api'
import '../styles/DocumentsList.css'

function DocumentsList() {
    const [documents, setDocuments] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [deletingId, setDeletingId] = useState(null)

    useEffect(() => {
        loadDocuments()
    }, [])

    const loadDocuments = async () => {
        try {
            setLoading(true)
            setError(null)
            const data = await getDocuments()
            setDocuments(data)
        } catch (err) {
            setError('Failed to load documents: ' + err.message)
        } finally {
            setLoading(false)
        }
    }

    const handleDelete = async (documentId, filename) => {
        if (!window.confirm(`Are you sure you want to delete "${filename}"?`)) {
            return
        }

        try {
            setDeletingId(documentId)
            await deleteDocument(documentId)
            // Remove from list
            setDocuments(documents.filter(doc => doc.document_id !== documentId))
        } catch (err) {
            alert('Failed to delete document: ' + err.message)
        } finally {
            setDeletingId(null)
        }
    }

    const formatFileSize = (bytes) => {
        if (bytes < 1024) return bytes + ' B'
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
        return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
    }

    const formatDate = (dateString) => {
        const date = new Date(dateString)
        return date.toLocaleString()
    }

    const getTypeIcon = (type) => {
        const icons = {
            pdf: '📄',
            docx: '📝',
            image: '🖼️',
            audio: '🎵',
            text: '📃'
        }
        return icons[type] || '📁'
    }

    if (loading) {
        return (
            <div className="documents-list">
                <div className="loading-container">
                    <div className="loading-spinner"></div>
                    <p>Loading documents...</p>
                </div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="documents-list">
                <div className="error-container">
                    <p className="error-message">❌ {error}</p>
                    <button onClick={loadDocuments} className="retry-button">
                        Retry
                    </button>
                </div>
            </div>
        )
    }

    return (
        <div className="documents-list">
            <div className="documents-header">
                <h2>📚 Uploaded Documents</h2>
                <button onClick={loadDocuments} className="refresh-button">
                    🔄 Refresh
                </button>
            </div>

            {documents.length === 0 ? (
                <div className="empty-state">
                    <p className="empty-icon">📭</p>
                    <p className="empty-text">No documents uploaded yet</p>
                    <p className="empty-hint">Upload some files to get started!</p>
                </div>
            ) : (
                <>
                    <div className="documents-stats">
                        <span className="stat">
                            <strong>{documents.length}</strong> document{documents.length !== 1 ? 's' : ''}
                        </span>
                        <span className="stat">
                            <strong>{documents.reduce((sum, doc) => sum + doc.num_chunks, 0)}</strong> chunks
                        </span>
                    </div>

                    <div className="documents-grid">
                        {documents.map((doc) => (
                            <div key={doc.document_id} className="document-card">
                                <div className="document-icon">
                                    {getTypeIcon(doc.document_type)}
                                </div>

                                <div className="document-info">
                                    <h3 className="document-name">{doc.filename}</h3>

                                    <div className="document-meta">
                                        <span className="meta-item">
                                            <span className="meta-label">Type:</span>
                                            <span className="meta-value">{doc.document_type.toUpperCase()}</span>
                                        </span>
                                        <span className="meta-item">
                                            <span className="meta-label">Size:</span>
                                            <span className="meta-value">{formatFileSize(doc.file_size)}</span>
                                        </span>
                                        <span className="meta-item">
                                            <span className="meta-label">Chunks:</span>
                                            <span className="meta-value">{doc.num_chunks}</span>
                                        </span>
                                        <span className="meta-item">
                                            <span className="meta-label">Status:</span>
                                            <span className={`status-badge ${doc.processed ? 'processed' : 'pending'}`}>
                                                {doc.processed ? '✅ Processed' : '⏳ Pending'}
                                            </span>
                                        </span>
                                    </div>

                                    <div className="document-date">
                                        Uploaded: {formatDate(doc.upload_date)}
                                    </div>
                                </div>

                                <button
                                    className="delete-button"
                                    onClick={() => handleDelete(doc.document_id, doc.filename)}
                                    disabled={deletingId === doc.document_id}
                                >
                                    {deletingId === doc.document_id ? '⏳' : '🗑️'}
                                </button>
                            </div>
                        ))}
                    </div>
                </>
            )}
        </div>
    )
}

export default DocumentsList
