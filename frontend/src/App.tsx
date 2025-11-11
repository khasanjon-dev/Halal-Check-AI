import React, {useState, useRef} from 'react';
import {AlertCircle, CheckCircle, XCircle, Loader2, Search, Upload, Camera, FileText} from 'lucide-react';

const API_URL =
    window.location.hostname === 'localhost'
        ? 'http://localhost:8000'
        : 'http://backend:8000'; // auto switch for Docker

export default function HalalCheckApp() {
    const [mode, setMode] = useState('image'); // 'image' or 'text'
    const [productText, setProductText] = useState('');
    const [selectedImage, setSelectedImage] = useState(null);
    const [imagePreview, setImagePreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const fileInputRef = useRef(null);

    const handleImageSelect = (e) => {
        const file = e.target.files[0];
        if (file) {
            if (file.size > 10 * 1024 * 1024) {
                setError('Image size must be less than 10MB');
                return;
            }

            setSelectedImage(file);
            setError(null);
            setResult(null);

            const reader = new FileReader();
            reader.onloadend = () => setImagePreview(reader.result);
            reader.readAsDataURL(file);
        }
    };

    const analyzeImage = async () => {
        if (!selectedImage) return setError('Please select an image first');

        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const formData = new FormData();
            formData.append('image', selectedImage);

            const response = await fetch(`${API_URL}/analyze-image`, {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.message || 'Image analysis failed');
            setResult(data);
        } catch (err) {
            setError(err.message || 'Failed to analyze image.');
        } finally {
            setLoading(false);
        }
    };

    const analyzeText = async () => {
        if (!productText.trim()) return setError('Please enter product description');

        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const formData = new FormData();
            formData.append('text', productText);

            const response = await fetch(`${API_URL}/analyze-text`, {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.message || 'Text analysis failed');
            setResult(data);
        } catch (err) {
            setError(err.message || 'Failed to analyze product.');
        } finally {
            setLoading(false);
        }
    };

    const getStatusConfig = (status) => {
        const configs = {
            Halal: {
                icon: CheckCircle,
                color: 'bg-green-50 border-green-200',
                textColor: 'text-green-800',
                iconColor: 'text-green-600',
                badge: 'bg-green-100 text-green-800'
            },
            Doubtful: {
                icon: AlertCircle,
                color: 'bg-yellow-50 border-yellow-200',
                textColor: 'text-yellow-800',
                iconColor: 'text-yellow-600',
                badge: 'bg-yellow-100 text-yellow-800'
            },
            Haram: {
                icon: XCircle,
                color: 'bg-red-50 border-red-200',
                textColor: 'text-red-800',
                iconColor: 'text-red-600',
                badge: 'bg-red-100 text-red-800'
            }
        };
        return configs[status] || configs.Doubtful;
    };

    const resetImage = () => {
        setSelectedImage(null);
        setImagePreview(null);
        setResult(null);
        setError(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
    };

    const switchMode = (newMode) => {
        setMode(newMode);
        setResult(null);
        setError(null);
        if (newMode === 'image') setProductText('');
        else resetImage();
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-teal-50">
            <div className="container mx-auto px-4 py-8 max-w-5xl">
                {/* Header */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-emerald-600 rounded-2xl mb-4">
                        <Camera className="w-8 h-8 text-white"/>
                    </div>
                    <h1 className="text-4xl font-bold text-gray-900 mb-2">Halal Check AI</h1>
                    <p className="text-gray-600 text-lg">AI-powered halal product analyzer</p>
                </div>

                {/* Mode Selector */}
                <div className="flex gap-3 mb-6 justify-center">
                    <button
                        onClick={() => switchMode('image')}
                        className={`flex items-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all ${
                            mode === 'image'
                                ? 'bg-emerald-600 text-white shadow-lg'
                                : 'bg-white text-gray-700 border-2 border-gray-200 hover:border-emerald-300'
                        }`}
                    >
                        <Camera className="w-5 h-5"/> Scan Image
                    </button>
                    <button
                        onClick={() => switchMode('text')}
                        className={`flex items-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all ${
                            mode === 'text'
                                ? 'bg-emerald-600 text-white shadow-lg'
                                : 'bg-white text-gray-700 border-2 border-gray-200 hover:border-emerald-300'
                        }`}
                    >
                        <FileText className="w-5 h-5"/> Type Text
                    </button>
                </div>

                {/* Input Section */}
                <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 mb-6">
                    {mode === 'image' ? (
                        <>
                            {!imagePreview ? (
                                <div
                                    onClick={() => fileInputRef.current?.click()}
                                    className="border-3 border-dashed border-gray-300 rounded-xl p-12 text-center cursor-pointer hover:border-emerald-500 hover:bg-emerald-50 transition-all"
                                >
                                    <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4"/>
                                    <p className="text-gray-700 font-medium mb-2">Click to upload or drag & drop</p>
                                    <p className="text-sm text-gray-500">JPG, PNG or JPEG (Max 10MB)</p>
                                </div>
                            ) : (
                                <div className="relative">
                                    <img
                                        src={imagePreview}
                                        alt="Preview"
                                        className="w-full max-h-96 object-contain rounded-xl border-2 border-gray-200"
                                    />
                                    <button
                                        onClick={resetImage}
                                        className="absolute top-3 right-3 bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors font-medium"
                                    >
                                        Remove
                                    </button>
                                </div>
                            )}
                            <input
                                ref={fileInputRef}
                                type="file"
                                accept="image/*"
                                onChange={handleImageSelect}
                                className="hidden"
                            />
                            <div className="flex justify-end mt-4">
                                <button
                                    onClick={analyzeImage}
                                    disabled={loading || !selectedImage}
                                    className="px-8 py-3 bg-emerald-600 text-white rounded-xl font-semibold hover:bg-emerald-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                                >
                                    {loading ? (
                                        <>
                                            <Loader2 className="w-5 h-5 animate-spin"/>
                                            Analyzing...
                                        </>
                                    ) : (
                                        <>
                                            <Search className="w-5 h-5"/>
                                            Analyze Image
                                        </>
                                    )}
                                </button>
                            </div>
                        </>
                    ) : (
                        <>
                            <textarea
                                value={productText}
                                onChange={(e) => setProductText(e.target.value)}
                                placeholder="Enter product description or ingredients..."
                                className="w-full h-40 px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 resize-none text-gray-900 placeholder-gray-400"
                                disabled={loading}
                            />
                            <div className="flex justify-end mt-4">
                                <button
                                    onClick={analyzeText}
                                    disabled={loading || !productText.trim()}
                                    className="px-8 py-3 bg-emerald-600 text-white rounded-xl font-semibold hover:bg-emerald-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                                >
                                    {loading ? (
                                        <>
                                            <Loader2 className="w-5 h-5 animate-spin"/>
                                            Analyzing...
                                        </>
                                    ) : (
                                        <>
                                            <Search className="w-5 h-5"/>
                                            Analyze Text
                                        </>
                                    )}
                                </button>
                            </div>
                        </>
                    )}
                </div>

                {/* ✅ RESULT CARD */}
                {result && (
                    <div className="bg-white rounded-2xl shadow-md border border-gray-200 p-6 mb-6 text-center">
                        {result.status && (
                            <div
                                className={`inline-flex items-center gap-2 px-4 py-2 rounded-full font-semibold mb-3 ${getStatusConfig(result.status).badge}`}
                            >
                                {result.status}
                            </div>
                        )}
                        <h3 className="text-xl font-bold text-gray-900 mb-2">Result</h3>
                        <p className="text-gray-700">
                            {result.message || 'No detailed message from backend.'}
                        </p>
                    </div>
                )}

                {/* Error Message */}
                {error && (
                    <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 flex items-start gap-3">
                        <XCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5"/>
                        <div>
                            <h3 className="font-semibold text-red-900 mb-1">Error</h3>
                            <p className="text-red-700 text-sm">{error}</p>
                        </div>
                    </div>
                )}

                <div className="mt-8 text-center text-sm text-gray-500">
                    <p>AI analysis may not be 100% accurate — verify with certified halal sources.</p>
                </div>
            </div>
        </div>
    );
}
