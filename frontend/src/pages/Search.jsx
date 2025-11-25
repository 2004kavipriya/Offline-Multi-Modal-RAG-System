import { useState } from 'react';
import SearchInterface from '../components/SearchInterface';
import ResultsDisplay from '../components/ResultsDisplay';
import DocumentFilter from '../components/DocumentFilter';
import SimilaritySearch from '../components/SimilaritySearch';
import './Search.css';

function Search() {
    const [results, setResults] = useState(null);
    const [selectedDocuments, setSelectedDocuments] = useState([]);
    const [searchMode, setSearchMode] = useState('text'); // 'text' or 'similarity'

    const handleResults = (data) => {
        setResults(data);
    };

    const handleFilterChange = (docIds) => {
        setSelectedDocuments(docIds);
        setResults(null);
    };

    return (
        <div className="search-page">
            <div className="container">
                <div className="page-header">
                    <h2>Advanced Search</h2>
                    <p>Search across all your documents</p>
                </div>

                <div className="search-mode-toggle">
                    <button
                        className={`mode-btn ${searchMode === 'text' ? 'active' : ''}`}
                        onClick={() => setSearchMode('text')}
                    >
                        💬 Text Query
                    </button>
                    <button
                        className={`mode-btn ${searchMode === 'similarity' ? 'active' : ''}`}
                        onClick={() => setSearchMode('similarity')}
                    >
                        📤 Find Similar
                    </button>
                </div>

                {searchMode === 'text' ? (
                    <>
                        <DocumentFilter
                            selectedDocuments={selectedDocuments}
                            onFilterChange={handleFilterChange}
                        />

                        <SearchInterface
                            onResults={handleResults}
                            selectedDocuments={selectedDocuments}
                        />

                        {results && <ResultsDisplay results={results} />}

                        {!results && (
                            <div className="search-placeholder glass-card">
                                <span className="placeholder-icon">🔍</span>
                                <h3>Start Searching</h3>
                                <p>
                                    {selectedDocuments.length > 0
                                        ? `Searching in ${selectedDocuments.length} selected document(s)`
                                        : 'Enter a question or search query above to find relevant content'
                                    }
                                </p>
                            </div>
                        )}
                    </>
                ) : (
                    <SimilaritySearch />
                )}
            </div>
        </div>
    );
}

export default Search;
