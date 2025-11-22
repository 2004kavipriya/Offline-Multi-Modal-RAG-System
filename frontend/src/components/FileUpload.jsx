import { useState, useCallback } from 'react'
import { uploadFile, uploadMultipleFiles } from '../services/api'
import '../styles/FileUpload.css'

function FileUpload() {
    const [files, setFiles] = useState([])
    const [uploading, setUploading] = useState(false)
    const [uploadProgress, setUploadProgress] = useState(0)
    const [uploadResults, setUploadResults] = useState([])
    const [dragActive, setDragActive] = useState(false)

    const handleDrag = useCallback((e) => {
        e.preventDefault()
        e.stopPropagation()
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true)
        } else if (e.type === 'dragleave') {
            setDragActive(false)
        }
    }, [])

    const handleDrop = useCallback((e) => {
        e.preventDefault()
        e.stopPropagation()
        setDragActive(false)

        const droppedFiles = Array.from(e.dataTransfer.files)
        setFiles((prev) => [...prev, ...droppedFiles])
    }, [])

    const handleFileSelect = (e) => {
        const selectedFiles = Array.from(e.target.files)
        setFiles((prev) => [...prev, ...selectedFiles])
    }

    const removeFile = (index) => {
        setFiles((prev) => prev.filter((_, i) => i !== index))
    }

    const handleUpload = async () => {
        if (files.length === 0) return

        setUploading(true)
        setUploadProgress(0)
        setUploadResults([])

        try {
            const results = []

            for (let i = 0; i < files.length; i++) {
                const file = files[i]
                const result = await uploadFile(file, (progress) => {
                    const overallProgress = ((i + progress / 100) / files.length) * 100
                    setUploadProgress(Math.round(overallProgress))
                })
                results.push({ file: file.name, ...result })
            }

            setUploadResults(results)
            setFiles([])
            setUploadProgress(100)
        } catch (error) {
            console.error('Upload error:', error)
            setUploadResults([{
                success: false,
                message: error.response?.data?.detail || 'Upload failed'
            }])
        } finally {
            setUploading(false)
        }
    }

    const getFileIcon = (filename) => {
        const ext = filename.split('.').pop().toLowerCase()
        if (['pdf'].includes(ext)) return '📄'
        if (['doc', 'docx'].includes(ext)) return '📝'
        if (['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(ext)) return '🖼️'
        if (['mp3', 'wav', 'm4a', 'ogg'].includes(ext)) return '🎵'
        return '📎'
    }

    const formatFileSize = (bytes) => {
        if (bytes < 1024) return bytes + ' B'
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
    }

    return (
        <div className="file-upload">
            <div className="upload-card">
                <h2>Upload Documents</h2>
                <p className="upload-description">
                    Upload PDFs, DOCX files, images, or audio recordings for semantic search
                </p>

                {/* Drop Zone */}
                <div
                    className={`drop-zone ${dragActive ? 'active' : ''}`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                >
                    <div className="drop-zone-content">
                        <div className="upload-icon">📁</div>
                        <p className="drop-text">Drag and drop files here</p>
                        <p className="drop-subtext">or</p>
                        <label className="file-select-btn">
                            <input
                                type="file"
                                multiple
                                onChange={handleFileSelect}
                                accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.gif,.bmp,.mp3,.wav,.m4a,.ogg"
                                style={{ display: 'none' }}
                            />
                            Browse Files
                        </label>
                        <p className="supported-formats">
                            Supported: PDF, DOCX, Images (JPG, PNG), Audio (MP3, WAV)
                        </p>
                    </div>
                </div>

                {/* File List */}
                {files.length > 0 && (
                    <div className="file-list">
                        <h3>Selected Files ({files.length})</h3>
                        {files.map((file, index) => (
                            <div key={index} className="file-item">
                                <span className="file-icon">{getFileIcon(file.name)}</span>
                                <div className="file-info">
                                    <p className="file-name">{file.name}</p>
                                    <p className="file-size">{formatFileSize(file.size)}</p>
                                </div>
                                <button
                                    className="remove-btn"
                                    onClick={() => removeFile(index)}
                                    disabled={uploading}
                                >
                                    ✕
                                </button>
                            </div>
                        ))}

                        <button
                            className="upload-btn"
                            onClick={handleUpload}
                            disabled={uploading}
                        >
                            {uploading ? `Uploading... ${uploadProgress}%` : 'Upload All'}
                        </button>
                    </div>
                )}

                {/* Upload Progress */}
                {uploading && (
                    <div className="progress-bar">
                        <div
                            className="progress-fill"
                            style={{ width: `${uploadProgress}%` }}
                        />
                    </div>
                )}

                {/* Upload Results */}
                {uploadResults.length > 0 && (
                    <div className="upload-results">
                        <h3>Upload Results</h3>
                        {uploadResults.map((result, index) => (
                            <div
                                key={index}
                                className={`result-item ${result.success ? 'success' : 'error'}`}
                            >
                                <span className="result-icon">
                                    {result.success ? '✓' : '✗'}
                                </span>
                                <div className="result-info">
                                    <p className="result-file">{result.file || result.filename}</p>
                                    <p className="result-message">
                                        {result.success
                                            ? result.processed
                                                ? 'Uploaded and processed successfully'
                                                : 'Uploaded (processing...)'
                                            : result.message}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}

export default FileUpload
