import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Upload, Search, Image as ImageIcon, X, CheckCircle, AlertCircle } from 'lucide-react';
import axios from 'axios';

// Types
interface SearchResult {
  name: string;
  similarity: number;
  id: string;
}

interface DetectionResult {
  class_name: string;
  confidence: number;
  bbox: number[];
}

interface IndexResponse {
  id: string;
  name: string;
  status: string;
  timestamp: string;
}

interface SearchResponse {
  results: SearchResult[];
}

interface CaptionResponse {
  success: boolean;
  caption: string;
}

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string>('');
  const [imageName, setImageName] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [detections, setDetections] = useState<DetectionResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isCaptioning, setIsCaptioning] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  const [stats, setStats] = useState({ total_images: 0, indexed_images: [] });
  const [autoIndexing, setAutoIndexing] = useState(false);
  const [lastIndexedHash, setLastIndexedHash] = useState<string | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const hashFile = async (file: File): Promise<string> => {
    const buffer = await file.arrayBuffer();
    const digest = await crypto.subtle.digest('SHA-256', buffer);
    return Array.from(new Uint8Array(digest))
      .map((b) => b.toString(16).padStart(2, '0'))
      .join('');
  };

  // Handle image selection
  const handleImageSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
      setMessage(null);
      setDetections([]);

      const fileHash = await hashFile(file);
      const alreadyIndexed = lastIndexedHash === fileHash;
      if (!alreadyIndexed) {
        setLastIndexedHash(null);
      }

      // Auto-generate name using captioning endpoint
      let autoCaption = '';
      try {
        setIsCaptioning(true);
        setImageName("");
        const form = new FormData();
        form.append('file', file);
        const resp = await axios.post<CaptionResponse>(`${API_BASE_URL}/caption`, form, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        autoCaption = resp.data?.caption || '';
        setImageName(autoCaption);
      } catch (err: any) {
        // ignore caption errors; backend will still index with fallback name
        setImageName("");
      } finally {
        setIsCaptioning(false);
      }

      // Detect objects for quick summary
      try {
        const detectForm = new FormData();
        detectForm.append('file', file);
        const detectResp = await axios.post<{ detections: DetectionResult[] }>(
          `${API_BASE_URL}/detect`,
          detectForm,
          {
            headers: { 'Content-Type': 'multipart/form-data' },
          }
        );
        setDetections(detectResp.data?.detections || []);
      } finally {
        // nothing extra
      }

      if (autoIndexing && !alreadyIndexed) {
        try {
          setIsLoading(true);
          const response = await handleIndexInternal(file, autoCaption);
          setMessage({
            type: 'success',
            text: `Image auto-added as "${response.name}"`
          });
          setLastIndexedHash(fileHash);
          fetchStats();
        } catch (err: any) {
          setMessage({
            type: 'error',
            text: err.response?.data?.detail || 'Auto indexing failed'
          });
        } finally {
          setIsLoading(false);
        }
      }
    }
  };

  // Clear image selection
  const clearImage = () => {
    setSelectedImage(null);
    setImagePreview('');
    setImageName('');
    setSearchResults([]);
    setDetections([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleIndexInternal = async (file: File, captionOverride?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    const nameToUse = captionOverride ?? imageName;
    if (nameToUse.trim()) {
      formData.append('name', nameToUse.trim());
    }

    const response = await axios.post<IndexResponse>(`${API_BASE_URL}/index`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  };

  // Index image
  const handleIndex = async () => {
    if (!selectedImage) {
      setMessage({ type: 'error', text: 'Please select an image' });
      return;
    }

    setIsLoading(true);
    setMessage(null);

    try {
      const response = await handleIndexInternal(selectedImage);

      setMessage({ 
        type: 'success', 
        text: `Image indexed successfully as "${response.name}"` 
      });
      const fileHash = await hashFile(selectedImage);
      setLastIndexedHash(fileHash);
      
      // Clear form
      clearImage();
      
      // Refresh stats
      fetchStats();
      
    } catch (error: any) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Failed to index image' 
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Search similar images
  const handleSearch = async () => {
    if (!selectedImage) {
      setMessage({ type: 'error', text: 'Please select an image to search' });
      return;
    }

    setIsLoading(true);
    setMessage(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedImage);
      formData.append('top_k', '3');

      const response = await axios.post<SearchResponse>(`${API_BASE_URL}/search`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setSearchResults(response.data.results);
      
      if (response.data.results.length === 0) {
        setMessage({ type: 'error', text: 'No similar images found' });
      } else {
        setMessage({ type: 'success', text: `Found ${response.data.results.length} similar images` });
      }
      
    } catch (error: any) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Failed to search images' 
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch statistics
  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  // Clear all data
  const handleClearAll = async () => {
    if (!window.confirm('Are you sure you want to clear all indexed images?')) {
      return;
    }

    try {
      await axios.delete(`${API_BASE_URL}/clear`);
      setMessage({ type: 'success', text: 'All data cleared successfully' });
      setSearchResults([]);
      fetchStats();
    } catch (error: any) {
      setMessage({ type: 'error', text: 'Failed to clear data' });
    }
  };

  // Load stats on component mount
  React.useEffect(() => {
    fetchStats();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Navbar */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <Search className="h-8 w-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">
                Visual Search Engine
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                {stats.total_images} images indexed
              </div>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={handleClearAll}
                className="text-red-600 hover:text-red-700"
              >
                Clear All
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Message Display */}
        {message && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`mb-6 p-4 rounded-lg flex items-center space-x-2 ${
              message.type === 'success' 
                ? 'bg-green-100 text-green-800 border border-green-200' 
                : 'bg-red-100 text-red-800 border border-red-200'
            }`}
          >
            {message.type === 'success' ? (
              <CheckCircle className="h-5 w-5" />
            ) : (
              <AlertCircle className="h-5 w-5" />
            )}
            <span>{message.text}</span>
          </motion.div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Index Image Card */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card className="h-full">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Upload className="h-6 w-6 text-blue-600" />
                  <span>Upload & Index Image</span>
                </CardTitle>
                <CardDescription>
                  Upload an image to add it to the search index. Name is optional.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Image Upload */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Image
                  </label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/*"
                      onChange={handleImageSelect}
                      className="hidden"
                    />
                    {imagePreview ? (
                      <div className="space-y-4">
                        <img
                          src={imagePreview}
                          alt="Preview"
                          className="mx-auto h-32 w-32 object-cover rounded-lg"
                        />
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={clearImage}
                          className="text-red-600 hover:text-red-700"
                        >
                          <X className="h-4 w-4 mr-2" />
                          Remove
                        </Button>
                        {/* Auto name display inside upload tile */}
                        <div className="text-left">
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Auto Name
                          </label>
                          <div className="text-sm text-gray-800 bg-gray-50 border rounded-md px-3 py-2">
                            {isCaptioning ? 'Generating name…' : (imageName || 'Will be generated during indexing')}
                          </div>
                        </div>
                        {/* Detection summary inside upload tile */}
                        {detections.length > 0 && (
                          <div className="text-left w-full">
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Detected Objects
                            </label>
                            <ul className="space-y-1 text-sm text-gray-800 bg-gray-50 border rounded-md px-3 py-2 max-h-40 overflow-auto">
                              {detections.map((det, idx) => (
                                <li key={`${det.class_name}-${idx}`} className="flex justify-between">
                                  <span>{det.class_name}</span>
                                  <span className="text-gray-500">{(det.confidence * 100).toFixed(0)}%</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="space-y-2">
                        <ImageIcon className="mx-auto h-12 w-12 text-gray-400" />
                        <Button
                          variant="outline"
                          onClick={() => fileInputRef.current?.click()}
                        >
                          Choose Image
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex items-center justify-between text-sm text-gray-700">
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={autoIndexing}
                      onChange={(e) => setAutoIndexing(e.target.checked)}
                      className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                    />
                    <span>Auto add to database</span>
                  </label>
                  {autoIndexing && lastIndexedHash && selectedImage && (
                    <span className="text-xs text-gray-500">
                      last added: {lastIndexedHash.slice(0, 8)}
                    </span>
                  )}
                </div>

                {/* Index Button */}
                <Button
                  onClick={handleIndex}
                  disabled={!selectedImage || isLoading}
                  className="w-full"
                >
                  {isLoading ? 'Indexing...' : 'Index Image'}
                </Button>
              </CardContent>
            </Card>
          </motion.div>

          {/* Search Image Card */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="h-full">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Search className="h-6 w-6 text-green-600" />
                  <span>Search Similar Images</span>
                </CardTitle>
                <CardDescription>
                  Upload an image to find similar images in the index
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Image Upload for Search */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Image to Search
                  </label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
                    {imagePreview ? (
                      <div className="space-y-4">
                        <img
                          src={imagePreview}
                          alt="Preview"
                          className="mx-auto h-32 w-32 object-cover rounded-lg"
                        />
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={clearImage}
                          className="text-red-600 hover:text-red-700"
                        >
                          <X className="h-4 w-4 mr-2" />
                          Remove
                        </Button>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        <ImageIcon className="mx-auto h-12 w-12 text-gray-400" />
                        <Button
                          variant="outline"
                          onClick={() => fileInputRef.current?.click()}
                        >
                          Choose Image
                        </Button>
                      </div>
                    )}
                  </div>
                </div>

                {/* Search Button */}
                <Button
                  onClick={handleSearch}
                  disabled={!selectedImage || isLoading}
                  className="w-full"
                  variant="secondary"
                >
                  {isLoading ? 'Searching...' : 'Search Similar Images'}
                </Button>

                {/* Search Results */}
                {searchResults.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-3"
                  >
                    <h3 className="font-medium text-gray-900">Search Results:</h3>
                    {searchResults.map((result, index) => (
                      <motion.div
                        key={result.id}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="bg-gray-50 rounded-lg p-4 border"
                      >
                        <div className="flex justify-between items-center">
                          <div>
                            <h4 className="font-medium text-gray-900">{result.name}</h4>
                            <p className="text-sm text-gray-600">ID: {result.id}</p>
                          </div>
                          <div className="text-right">
                            <div className="text-lg font-bold text-blue-600">
                              {(result.similarity * 100).toFixed(1)}%
                            </div>
                            <div className="text-xs text-gray-500">similarity</div>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </motion.div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Stats Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-8"
        >
          <Card>
            <CardHeader>
              <CardTitle>Index Statistics</CardTitle>
              <CardDescription>
                Overview of indexed images in the system
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {stats.total_images}
                  </div>
                  <div className="text-sm text-blue-800">Total Images</div>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {stats.indexed_images?.length || 0}
                  </div>
                  <div className="text-sm text-green-800">Indexed Images</div>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">
                    ResNet50
                  </div>
                  <div className="text-sm text-purple-800">Model</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}

export default App;



