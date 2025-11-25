import { useState } from 'react';
import SearchInterface from '../components/SearchInterface';
import ResultsDisplay from '../components/ResultsDisplay';
import DocumentFilter from '../components/DocumentFilter';
import './Search.css';

function Search() {
    const [results, setResults] = useState(null);
    const [selectedDocuments, setSelectedDocuments] = useState([]);

    const handleResults = (data) => {
        setResults(data);
    };

    const handleFilterChange = (docIds) => {
        setSelectedDocuments(docIds);
        // Clear results when filter changes
        setResults(null);
    };

    return (
        <div className="search-page">
            <div className="container">
                <div className="page-header">
                    <h2>Advanced Search</h2>
                    <p>Search across all your documents, images, and audio files</p>
                </div>

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
                        <h3>Start Search ing</h3>
                        <p>
                            {selectedDocuments.length > 0
                                ? `Searching in ${selectedDocuments.length} selected document(s)`
                                : 'Enter a question or search query above to find relevant content'
                            }
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}

export default Search;
