import React, {useState, useRef} from 'react';
import {
    AlertCircle, CheckCircle, XCircle, Loader2, Search, Upload, Camera, FileText,
    Shield, Heart, Package, AlertTriangle, Info, History, Sparkles, BookOpen
} from 'lucide-react';

// TypeScript interfaces for API responses
interface HalalCheckResult {
    product_name: string;
    is_halal: string;
    halal_reason: string;
    is_edible: boolean;
    edible_reason: string;
    detected_ingredients: string[];
    harmful_or_suspicious: string[];
    allergens: string[];
    overall_summary: string;
}

interface HalalCheckResponse {
    id: number;
    device_id: string;
    product_name: string;
    is_halal: string;
    is_edible: boolean;
    result: HalalCheckResult;
    created_at: string;
}

// When accessing from browser (localhost/127.0.0.1), use localhost:8000
// When inside Docker network, use service name 'backend:8000'
const API_URL =
    (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
        ? 'http://localhost:8000'  // Browser access (most common)
        : 'http://backend:8000';    // Docker internal network

// Generate a unique device ID (stored in localStorage)
const getDeviceId = () => {
    let deviceId = localStorage.getItem('halal_check_device_id');
    if (!deviceId) {
        deviceId = `device_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        localStorage.setItem('halal_check_device_id', deviceId);
    }
    return deviceId;
};

export default function HalalCheckApp() {
    const [mode, setMode] = useState<'image' | 'text'>('image');
    const [productText, setProductText] = useState<string>('');
    const [selectedImage, setSelectedImage] = useState<File | null>(null);
    const [imagePreview, setImagePreview] = useState<string | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [result, setResult] = useState<HalalCheckResponse | null>(null);
    const [error, setError] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const deviceId = getDeviceId();

    const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            if (file.size > 10 * 1024 * 1024) {
                setError('Image size must be less than 10MB');
                return;
            }

            setSelectedImage(file);
            setError(null);
            setResult(null);

            const reader = new FileReader();
            reader.onloadend = () => setImagePreview(reader.result as string);
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
            formData.append('device_id', deviceId);

            const response = await fetch(`${API_URL}/api/v1/halal-check/analyze-image`, {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || 'Image analysis failed');
            }
            setResult(data);
        } catch (err: any) {
            setError(err.message || 'Failed to analyze image. Please check your connection and try again.');
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
            const response = await fetch(`${API_URL}/api/v1/halal-check/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: productText,
                    device_id: deviceId
                }),
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || 'Text analysis failed');
            }
            setResult(data);
        } catch (err: any) {
            setError(err.message || 'Failed to analyze product. Please check your connection and try again.');
        } finally {
            setLoading(false);
        }
    };

    const getStatusConfig = (isHalal: string) => {
        const status = typeof isHalal === 'string' ? isHalal.toLowerCase() : String(isHalal);

        if (status === 'true' || status === 'halal') {
            return {
                icon: CheckCircle,
                color: 'bg-gradient-to-br from-green-50 to-emerald-50 border-green-300',
                headerColor: 'bg-gradient-to-r from-green-500 to-emerald-600',
                textColor: 'text-green-800',
                iconColor: 'text-green-600',
                badge: 'bg-green-500 text-white shadow-lg shadow-green-500/50',
                label: 'Halal ✓',
                emoji: '✅'
            };
        } else if (status === 'false' || status === 'haram') {
            return {
                icon: XCircle,
                color: 'bg-gradient-to-br from-red-50 to-rose-50 border-red-300',
                headerColor: 'bg-gradient-to-r from-red-500 to-rose-600',
                textColor: 'text-red-800',
                iconColor: 'text-red-600',
                badge: 'bg-red-500 text-white shadow-lg shadow-red-500/50',
                label: 'Haram ✗',
                emoji: '❌'
            };
        } else {
            return {
                icon: AlertCircle,
                color: 'bg-gradient-to-br from-yellow-50 to-amber-50 border-yellow-300',
                headerColor: 'bg-gradient-to-r from-yellow-500 to-amber-600',
                textColor: 'text-yellow-800',
                iconColor: 'text-yellow-600',
                badge: 'bg-yellow-500 text-white shadow-lg shadow-yellow-500/50',
                label: 'Doubtful ⚠',
                emoji: '⚠️'
            };
        }
    };

    const resetImage = () => {
        setSelectedImage(null);
        setImagePreview(null);
        setResult(null);
        setError(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
    };

    const switchMode = (newMode: 'image' | 'text') => {
        setMode(newMode);
        setResult(null);
        setError(null);
        if (newMode === 'image') setProductText('');
        else resetImage();
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50">
            {/* Animated Background Elements */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-20 left-10 w-72 h-72 bg-emerald-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
                <div className="absolute top-40 right-10 w-72 h-72 bg-teal-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
                <div className="absolute bottom-20 left-1/2 w-72 h-72 bg-cyan-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>
            </div>

            <div className="container mx-auto px-4 py-8 max-w-6xl relative z-10">
                {/* Enhanced Header */}
                <div className="text-center mb-10">
                    <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-3xl mb-4 shadow-2xl shadow-emerald-500/30 animate-pulse-slow">
                        <Shield className="w-10 h-10 text-white"/>
                    </div>
                    <h1 className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-teal-600 mb-3">
                        Halal Check AI
                    </h1>
                    <p className="text-gray-600 text-xl font-medium flex items-center justify-center gap-2">
                        <Sparkles className="w-5 h-5 text-emerald-500"/>
                        AI-powered halal product analyzer with Gemini 2.0
                    </p>
                    <div className="mt-4 flex items-center justify-center gap-6 text-sm text-gray-500">
                        <span className="flex items-center gap-1">
                            <Camera className="w-4 h-4"/> Image OCR
                        </span>
                        <span className="flex items-center gap-1">
                            <FileText className="w-4 h-4"/> Text Analysis
                        </span>
                        <span className="flex items-center gap-1">
                            <Shield className="w-4 h-4"/> Halal Certified AI
                        </span>
                    </div>
                </div>

                {/* Enhanced Mode Selector */}
                <div className="flex gap-4 mb-8 justify-center">
                    <button
                        onClick={() => switchMode('image')}
                        className={`flex items-center gap-3 px-8 py-4 rounded-2xl font-bold text-lg transition-all transform hover:scale-105 ${
                            mode === 'image'
                                ? 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white shadow-2xl shadow-emerald-500/50'
                                : 'bg-white text-gray-700 border-2 border-gray-200 hover:border-emerald-400 hover:shadow-xl'
                        }`}
                    >
                        <Camera className="w-6 h-6"/>
                        <span>Scan Image</span>
                        {mode === 'image' && <Sparkles className="w-5 h-5"/>}
                    </button>
                    <button
                        onClick={() => switchMode('text')}
                        className={`flex items-center gap-3 px-8 py-4 rounded-2xl font-bold text-lg transition-all transform hover:scale-105 ${
                            mode === 'text'
                                ? 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white shadow-2xl shadow-emerald-500/50'
                                : 'bg-white text-gray-700 border-2 border-gray-200 hover:border-emerald-400 hover:shadow-xl'
                        }`}
                    >
                        <FileText className="w-6 h-6"/>
                        <span>Type Text</span>
                        {mode === 'text' && <Sparkles className="w-5 h-5"/>}
                    </button>
                </div>

                {/* Enhanced Input Section */}
                <div className="bg-white rounded-3xl shadow-2xl border-2 border-gray-100 p-8 mb-8 backdrop-blur-sm bg-opacity-95">
                    {mode === 'image' ? (
                        <>
                            {!imagePreview ? (
                                <div
                                    onClick={() => fileInputRef.current?.click()}
                                    className="border-4 border-dashed border-gray-300 rounded-2xl p-16 text-center cursor-pointer hover:border-emerald-500 hover:bg-gradient-to-br hover:from-emerald-50 hover:to-teal-50 transition-all duration-300 group"
                                >
                                    <Upload className="w-20 h-20 text-gray-400 mx-auto mb-6 group-hover:text-emerald-500 group-hover:scale-110 transition-all"/>
                                    <p className="text-gray-700 font-bold text-xl mb-3">Click to upload or drag & drop</p>
                                    <p className="text-gray-500 text-lg">JPG, PNG, WEBP or GIF (Max 10MB)</p>
                                    <div className="mt-6 flex items-center justify-center gap-4 text-sm text-gray-400">
                                        <span className="flex items-center gap-1">
                                            <Camera className="w-4 h-4"/> OCR Enabled
                                        </span>
                                        <span>•</span>
                                        <span className="flex items-center gap-1">
                                            <Shield className="w-4 h-4"/> Secure Upload
                                        </span>
                                    </div>
                                </div>
                            ) : (
                                <div className="relative group">
                                    <div className="absolute inset-0 bg-gradient-to-r from-emerald-500 to-teal-600 rounded-2xl blur opacity-25 group-hover:opacity-40 transition-opacity"></div>
                                    <img
                                        src={imagePreview}
                                        alt="Preview"
                                        className="relative w-full max-h-[500px] object-contain rounded-2xl border-4 border-white shadow-2xl"
                                    />
                                    <button
                                        onClick={resetImage}
                                        className="absolute top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-xl hover:bg-red-600 transition-all font-bold shadow-xl hover:scale-105 flex items-center gap-2"
                                    >
                                        <XCircle className="w-5 h-5"/>
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
                            <div className="flex justify-end mt-6">
                                <button
                                    onClick={analyzeImage}
                                    disabled={loading || !selectedImage}
                                    className="px-10 py-4 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-2xl font-bold text-lg hover:from-emerald-600 hover:to-teal-700 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all shadow-xl hover:shadow-2xl hover:scale-105 flex items-center gap-3"
                                >
                                    {loading ? (
                                        <>
                                            <Loader2 className="w-6 h-6 animate-spin"/>
                                            Analyzing with AI...
                                        </>
                                    ) : (
                                        <>
                                            <Search className="w-6 h-6"/>
                                            Analyze Image
                                            <Sparkles className="w-5 h-5"/>
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
                                placeholder="Enter product description or ingredients list...&#10;&#10;Example:&#10;Water, Sugar, Gelatin, Citric Acid, Natural Flavors, E120 (Carmine)"
                                className="w-full h-56 px-6 py-4 border-2 border-gray-300 rounded-2xl focus:ring-4 focus:ring-emerald-500/50 focus:border-emerald-500 resize-none text-gray-900 placeholder-gray-400 text-lg font-medium"
                                disabled={loading}
                            />
                            <div className="flex justify-between items-center mt-6">
                                <div className="text-sm text-gray-500 flex items-center gap-2">
                                    <Info className="w-4 h-4"/>
                                    <span>Tip: Include all ingredients for accurate analysis</span>
                                </div>
                                <button
                                    onClick={analyzeText}
                                    disabled={loading || !productText.trim()}
                                    className="px-10 py-4 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-2xl font-bold text-lg hover:from-emerald-600 hover:to-teal-700 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all shadow-xl hover:shadow-2xl hover:scale-105 flex items-center gap-3"
                                >
                                    {loading ? (
                                        <>
                                            <Loader2 className="w-6 h-6 animate-spin"/>
                                            Analyzing with AI...
                                        </>
                                    ) : (
                                        <>
                                            <Search className="w-6 h-6"/>
                                            Analyze Text
                                            <Sparkles className="w-5 h-5"/>
                                        </>
                                    )}
                                </button>
                            </div>
                        </>
                    )}
                </div>

                {/* Enhanced Result Card */}
                {result && result.result && (
                    <div className="bg-white rounded-3xl shadow-2xl border-2 border-gray-100 overflow-hidden animate-fade-in backdrop-blur-sm bg-opacity-95">
                        {/* Premium Status Header */}
                        <div className={`${getStatusConfig(result.is_halal).headerColor} p-8 text-white relative overflow-hidden`}>
                            <div className="absolute inset-0 bg-black opacity-10"></div>
                            <div className="relative z-10">
                                <div className="flex items-start justify-between mb-4">
                                    <div className="flex items-center gap-4">
                                        {React.createElement(getStatusConfig(result.is_halal).icon, {
                                            className: 'w-12 h-12 text-white drop-shadow-lg'
                                        })}
                                        <div>
                                            <div className="text-sm font-semibold opacity-90 mb-1 flex items-center gap-2">
                                                <Package className="w-4 h-4"/> PRODUCT ANALYSIS
                                            </div>
                                            <h2 className="text-3xl font-black drop-shadow-lg">
                                                {result.result.product_name || 'Product Analysis'}
                                            </h2>
                                        </div>
                                    </div>
                                    <div className={`${getStatusConfig(result.is_halal).badge} px-6 py-3 rounded-2xl font-black text-xl flex items-center gap-2`}>
                                        <span className="text-2xl">{getStatusConfig(result.is_halal).emoji}</span>
                                        {getStatusConfig(result.is_halal).label}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Enhanced Analysis Content */}
                        <div className="p-8 space-y-8">
                            {/* Halal Status Section */}
                            <div className={`${getStatusConfig(result.is_halal).color} rounded-2xl p-6 border-2`}>
                                <h3 className="text-xl font-black text-gray-900 mb-4 flex items-center gap-3">
                                    <div className="p-2 bg-white rounded-xl shadow-md">
                                        <Shield className={`w-6 h-6 ${getStatusConfig(result.is_halal).iconColor}`}/>
                                    </div>
                                    Halal Compliance Status
                                </h3>
                                <p className={`text-lg leading-relaxed ${getStatusConfig(result.is_halal).textColor} font-medium`}>
                                    {result.result.halal_reason}
                                </p>
                            </div>

                            {/* Food Safety Section */}
                            {result.result.edible_reason && (
                                <div className={`${result.is_edible ? 'bg-gradient-to-br from-green-50 to-emerald-50 border-green-300' : 'bg-gradient-to-br from-red-50 to-rose-50 border-red-300'} rounded-2xl p-6 border-2`}>
                                    <h3 className="text-xl font-black text-gray-900 mb-4 flex items-center gap-3">
                                        <div className={`p-2 ${result.is_edible ? 'bg-green-100' : 'bg-red-100'} rounded-xl shadow-md`}>
                                            <Heart className={`w-6 h-6 ${result.is_edible ? 'text-green-600' : 'text-red-600'}`}/>
                                        </div>
                                        Food Safety & Edibility
                                    </h3>
                                    <p className={`text-lg leading-relaxed ${result.is_edible ? 'text-green-800' : 'text-red-800'} font-medium`}>
                                        {result.result.edible_reason}
                                    </p>
                                </div>
                            )}

                            {/* Detected Ingredients with Enhanced Design */}
                            {result.result.detected_ingredients && result.result.detected_ingredients.length > 0 && (
                                <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-6 border-2 border-blue-200">
                                    <h3 className="text-xl font-black text-gray-900 mb-4 flex items-center gap-3">
                                        <div className="p-2 bg-blue-100 rounded-xl shadow-md">
                                            <BookOpen className="w-6 h-6 text-blue-600"/>
                                        </div>
                                        Detected Ingredients ({result.result.detected_ingredients.length})
                                    </h3>
                                    <div className="flex flex-wrap gap-3">
                                        {result.result.detected_ingredients.map((ingredient, idx) => (
                                            <span key={idx} className="px-5 py-2.5 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl text-sm font-bold shadow-lg hover:scale-105 transition-transform">
                                                {ingredient}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Harmful or Suspicious with Alert Design */}
                            {result.result.harmful_or_suspicious && result.result.harmful_or_suspicious.length > 0 && (
                                <div className="bg-gradient-to-br from-red-50 to-rose-50 rounded-2xl p-6 border-2 border-red-300 animate-pulse-slow">
                                    <h3 className="text-xl font-black text-gray-900 mb-4 flex items-center gap-3">
                                        <div className="p-2 bg-red-100 rounded-xl shadow-md">
                                            <AlertTriangle className="w-6 h-6 text-red-600"/>
                                        </div>
                                        ⚠️ Harmful or Suspicious Ingredients
                                    </h3>
                                    <div className="flex flex-wrap gap-3">
                                        {result.result.harmful_or_suspicious.map((item, idx) => (
                                            <span key={idx} className="px-5 py-2.5 bg-gradient-to-r from-red-500 to-rose-600 text-white rounded-xl text-sm font-bold shadow-lg flex items-center gap-2">
                                                <XCircle className="w-4 h-4"/>
                                                {item}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Allergens with Warning Design */}
                            {result.result.allergens && result.result.allergens.length > 0 && (
                                <div className="bg-gradient-to-br from-yellow-50 to-amber-50 rounded-2xl p-6 border-2 border-yellow-300">
                                    <h3 className="text-xl font-black text-gray-900 mb-4 flex items-center gap-3">
                                        <div className="p-2 bg-yellow-100 rounded-xl shadow-md">
                                            <AlertCircle className="w-6 h-6 text-yellow-600"/>
                                        </div>
                                        Allergen Information
                                    </h3>
                                    <div className="flex flex-wrap gap-3">
                                        {result.result.allergens.map((allergen, idx) => (
                                            <span key={idx} className="px-5 py-2.5 bg-gradient-to-r from-yellow-500 to-amber-600 text-white rounded-xl text-sm font-bold shadow-lg">
                                                {allergen}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Overall Summary with Premium Design */}
                            {result.result.overall_summary && (
                                <div className="bg-gradient-to-br from-gray-50 to-slate-50 rounded-2xl p-6 border-2 border-gray-200">
                                    <h3 className="text-xl font-black text-gray-900 mb-4 flex items-center gap-3">
                                        <div className="p-2 bg-gray-100 rounded-xl shadow-md">
                                            <Sparkles className="w-6 h-6 text-gray-600"/>
                                        </div>
                                        AI Summary
                                    </h3>
                                    <p className="text-gray-800 leading-relaxed text-lg font-medium">
                                        {result.result.overall_summary}
                                    </p>
                                </div>
                            )}

                            {/* Analysis Metadata */}
                            <div className="bg-gradient-to-r from-gray-50 to-slate-50 rounded-2xl p-6 border-2 border-gray-200">
                                <div className="flex items-center justify-between text-sm text-gray-600">
                                    <div className="flex items-center gap-6">
                                        <span className="flex items-center gap-2 font-semibold">
                                            <History className="w-4 h-4"/>
                                            {new Date(result.created_at).toLocaleString('en-US', {
                                                dateStyle: 'medium',
                                                timeStyle: 'short'
                                            })}
                                        </span>
                                        <span className="flex items-center gap-2 font-semibold">
                                            <Info className="w-4 h-4"/>
                                            Analysis ID: #{result.id}
                                        </span>
                                    </div>
                                    <span className="px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-xl font-bold text-xs shadow-md">
                                        Powered by Gemini AI
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Enhanced Error Message */}
                {error && (
                    <div className="bg-gradient-to-br from-red-50 to-rose-50 border-2 border-red-300 rounded-2xl p-6 mb-6 flex items-start gap-4 shadow-xl animate-shake">
                        <div className="p-3 bg-red-100 rounded-xl">
                            <XCircle className="w-8 h-8 text-red-600"/>
                        </div>
                        <div className="flex-1">
                            <h3 className="font-black text-red-900 mb-2 text-lg">Error Occurred</h3>
                            <p className="text-red-700 font-medium">{error}</p>
                        </div>
                    </div>
                )}

                {/* Enhanced Footer */}
                <div className="mt-12 text-center">
                    <div className="inline-flex items-center gap-2 px-6 py-3 bg-white rounded-2xl shadow-lg border border-gray-200 text-sm text-gray-600 mb-4">
                        <Info className="w-4 h-4 text-emerald-500"/>
                        <span className="font-semibold">
                            AI analysis may not be 100% accurate — always verify with certified halal authorities
                        </span>
                    </div>
                    <p className="text-gray-500 text-sm">
                        Powered by Google Gemini 2.0 Flash AI • Built with ❤️ for the Muslim community
                    </p>
                </div>
            </div>

            <style>{`
                @keyframes blob {
                    0%, 100% { transform: translate(0, 0) scale(1); }
                    33% { transform: translate(30px, -50px) scale(1.1); }
                    66% { transform: translate(-20px, 20px) scale(0.9); }
                }
                .animate-blob {
                    animation: blob 7s infinite;
                }
                .animation-delay-2000 {
                    animation-delay: 2s;
                }
                .animation-delay-4000 {
                    animation-delay: 4s;
                }
                .animate-pulse-slow {
                    animation: pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
                }
                @keyframes fade-in {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                .animate-fade-in {
                    animation: fade-in 0.5s ease-out;
                }
                @keyframes shake {
                    0%, 100% { transform: translateX(0); }
                    25% { transform: translateX(-5px); }
                    75% { transform: translateX(5px); }
                }
                .animate-shake {
                    animation: shake 0.5s ease-in-out;
                }
            `}</style>
        </div>
    );
}

