import { useState } from 'react'
import QueryInterface from './components/QueryInterface'
import FileUpload from './components/FileUpload'
import DocumentsList from './components/DocumentsList'
import ResultsDisplay from './components/ResultsDisplay'
import './styles/App.css'

function App() {
    const [results, setResults] = useState(null)
    const [loading, setLoading] = useState(false)
    const [activeTab, setActiveTab] = useState('query') // 'query', 'upload', or 'documents'

    const handleQueryResults = (queryResults) => {
        setResults(queryResults)
    }

    const handleLoading = (isLoading) => {
        setLoading(isLoading)
    }

    return (
        <div className="app">
            {/* Header */}
            <header className="app-header">
                <div className="header-content">
                    <div className="logo">
                        <div className="logo-icon">🔍</div>
                        <h1>Multimodal RAG</h1>
                    </div>
                    <p className="tagline">Intelligent Search Across Documents, Images & Audio</p>
                </div>
            </header>

            {/* Main Content */}
            <main className="app-main">
                <div className="container">
                    {/* Tab Navigation */}
                    <div className="tab-nav">
                        <button
                            className={`tab-button ${activeTab === 'query' ? 'active' : ''}`}
                            onClick={() => setActiveTab('query')}
                        >
                            <span className="tab-icon">💬</span>
                            Query & Search
                        </button>
                        <button
                            className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
                            onClick={() => setActiveTab('upload')}
                        >
                            <span className="tab-icon">📤</span>
                            Upload Documents
                        </button>
                        <button
                            className={`tab-button ${activeTab === 'documents' ? 'active' : ''}`}
                            onClick={() => setActiveTab('documents')}
                        >
                            <span className="tab-icon">📚</span>
                            My Documents
                        </button>
                    </div>

                    {/* Tab Content */}
                    <div className="tab-content">
                        {activeTab === 'query' ? (
                            <div className="query-section">
                                <QueryInterface
                                    onResults={handleQueryResults}
                                    onLoading={handleLoading}
                                />
                                {results && (
                                    <ResultsDisplay results={results} loading={loading} />
                                )}
                            </div>
                        ) : activeTab === 'upload' ? (
                            <div className="upload-section">
                                <FileUpload />
                            </div>
                        ) : (
                            <div className="documents-section">
                                <DocumentsList />
                            </div>
                        )}
                    </div>
                </div>
            </main>

            {/* Footer */}
            <footer className="app-footer">
                <p>Powered by FAISS + PostgreSQL + MinIO | Offline Multimodal RAG System</p>
            </footer>
        </div>
    )
}

export default App
