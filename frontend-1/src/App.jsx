import React, {useState} from 'react';
import axios from 'axios';
import './App.css';

// Use environment variable or fallback to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [text, setText] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        setSelectedFile(file);
        // Clear text when file is selected
        if (file) {
            setText('');
            setResult(null);
        }
    };

    const handleTextChange = (event) => {
        const newText = event.target.value;
        setText(newText);
        // Clear file when text is entered
        if (newText) {
            setSelectedFile(null);
            setResult(null);
        }
    };

    const handleSubmit = async (event) => {
        event.preventDefault();

        if (!selectedFile && !text.trim()) {
            setResult({
                status: 'error',
                message: 'Please select a file or enter some text'
            });
            return;
        }

        setLoading(true);
        setResult(null);

        try {
            const formData = new FormData();

            if (selectedFile) {
                formData.append('image', selectedFile);
            }

            if (text.trim()) {
                formData.append('text', text.trim());
            }

            const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
                timeout: 30000, // 30 second timeout
            });

            setResult(response.data);

            // Reset form on success
            if (response.data.status === 'success') {
                setSelectedFile(null);
                setText('');
                // Clear file input
                const fileInput = document.getElementById('file-input');
                if (fileInput) fileInput.value = '';
            }
        } catch (error) {
            console.error('Upload error:', error);
            if (error.code === 'ECONNREFUSED') {
                setResult({
                    status: 'error',
                    message: 'Cannot connect to server. Please make sure the backend is running.'
                });
            } else {
                setResult({
                    status: 'error',
                    message: error.response?.data?.message || 'Upload failed. Please try again.'
                });
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container">
            <div className="header">
                <h1>Upload App</h1>
                <p>Upload images or text files easily</p>
            </div>

            <div className="upload-container">
                <form onSubmit={handleSubmit}>
                    <div className="upload-section">
                        <h3>Upload Image</h3>
                        <label className="file-input">
                            <input
                                id="file-input"
                                type="file"
                                accept="image/jpeg,image/png,image/gif,image/webp"
                                onChange={handleFileChange}
                                disabled={loading || text.trim()}
                            />
                            {selectedFile ? `Selected: ${selectedFile.name}` : 'Click to choose an image file (JPEG, PNG, GIF, WebP)...'}
                        </label>
                    </div>

                    <div className="divider">OR</div>

                    <div className="upload-section">
                        <h3>Enter Text</h3>
                        <textarea
                            className="text-input"
                            placeholder="Enter your text here..."
                            value={text}
                            onChange={handleTextChange}
                            disabled={loading || selectedFile}
                        />
                    </div>

                    <button
                        type="submit"
                        className="upload-button"
                        disabled={loading || (!selectedFile && !text.trim())}
                    >
                        {loading ? (
                            <div className="loading">
                                <div className="spinner"></div>
                                Uploading...
                            </div>
                        ) : (
                            'Upload'
                        )}
                    </button>
                </form>

                {result && (
                    <div className={`result ${result.status}`}>
                        {result.status === 'success' ? '✅ ' : '❌ '}
                        {result.message}
                    </div>
                )}
            </div>
        </div>
    );
}

export default App;