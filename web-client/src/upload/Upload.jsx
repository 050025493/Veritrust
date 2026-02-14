import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const Upload = ({ onBack }) => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [selectedVisualization, setSelectedVisualization] = useState(0);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  // Handle file selection
  const handleFileSelect = (selectedFile) => {
    if (selectedFile && selectedFile.type.startsWith('video/')) {
      setFile(selectedFile);
      setError(null);
      setResult(null);

      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreview(e.target.result);
      };
      reader.readAsArrayBuffer(selectedFile);
    } else {
      setError('Please select a valid video file');
    }
  };

  // Handle drop
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Request with Grad-CAM enabled
      const response = await fetch(`${API_URL}/predict-video?include_gradcam=true`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const data = await response.json();
      setResult(data);
      
      // Set first visualization as default
      if (data.gradcam_frames && data.gradcam_frames.length > 0) {
        setSelectedVisualization(0);
      }
    } catch (err) {
      setError(err.message || 'Error analyzing video. Make sure the backend is running.');
      console.error('Upload error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Result color based on prediction
  const getResultColor = (prediction) => {
    switch (prediction) {
      case 'REAL':
        return 'from-green-400 to-emerald-400';
      case 'FAKE':
        return 'from-red-400 to-rose-400';
      case 'SUSPICIOUS':
        return 'from-yellow-400 to-orange-400';
      default:
        return 'from-cyan-400 to-purple-400';
    }
  };

  const getResultBg = (prediction) => {
    switch (prediction) {
      case 'REAL':
        return 'bg-green-500/10 border-green-500/30';
      case 'FAKE':
        return 'bg-red-500/10 border-red-500/30';
      case 'SUSPICIOUS':
        return 'bg-yellow-500/10 border-yellow-500/30';
      default:
        return 'bg-white/5 border-white/10';
    }
  };

  return (
    <div className="relative min-h-screen bg-black overflow-hidden">
      {/* Background gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-black/60 to-black/80 z-0" />

      {/* Content */}
      <div className="relative z-10 max-w-6xl mx-auto px-6 py-16">
        
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-12"
        >
          <button
            onClick={onBack}
            className="mb-6 px-4 py-2 rounded-full text-cyan-400 border border-cyan-500/30 bg-cyan-500/10 hover:bg-cyan-500/20 transition-all duration-300 text-sm font-medium"
          >
            ← Back to Home
          </button>
          
          <h1 className="text-5xl md:text-6xl font-extrabold text-white mb-4">
            Verify Your <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400">Media</span>
          </h1>
          <p className="text-xl text-neutral-400">Upload a video to detect deepfakes with AI-powered heatmap visualization</p>
        </motion.div>

        {!result ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="space-y-8"
          >
            {/* Upload Area */}
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Drop Zone */}
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={`relative p-12 rounded-2xl border-2 border-dashed transition-all duration-300 cursor-pointer ${
                  dragActive
                    ? 'border-cyan-400 bg-cyan-500/10'
                    : 'border-white/20 bg-white/5 hover:bg-white/10'
                }`}
              >
                <input
                  type="file"
                  accept="video/*"
                  onChange={(e) => handleFileSelect(e.target.files[0])}
                  className="absolute inset-0 opacity-0 cursor-pointer"
                />
                
                <div className="flex flex-col items-center justify-center">
                  <div className="mb-4 p-4 rounded-full bg-gradient-to-br from-cyan-500/20 to-purple-500/20">
                    <svg className="w-8 h-8 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-bold text-white mb-2">Drop your video here</h3>
                  <p className="text-neutral-400 text-center">or click to browse (MP4, WebM, MOV, AVI)</p>
                  {file && <p className="mt-4 text-cyan-400 font-mono text-sm">{file.name}</p>}
                </div>
              </div>

              {/* File Info */}
              {file && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="p-4 rounded-lg bg-white/5 border border-white/10"
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-neutral-300">
                      <span className="font-semibold">{file.name}</span>
                      <span className="text-neutral-500 ml-2">({(file.size / (1024 * 1024)).toFixed(2)}MB)</span>
                    </span>
                    <button
                      type="button"
                      onClick={() => {
                        setFile(null);
                        setPreview(null);
                        setResult(null);
                      }}
                      className="text-neutral-400 hover:text-white transition-colors"
                    >
                      ✕
                    </button>
                  </div>
                  
                  {/* Progress bar */}
                  <div className="w-full h-1 bg-white/10 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-cyan-400 to-purple-400 w-full rounded-full"></div>
                  </div>
                </motion.div>
              )}

              {/* Error Message */}
              {error && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400"
                >
                  {error}
                </motion.div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={!file || loading}
                className="w-full px-8 py-4 rounded-full bg-gradient-to-r from-cyan-400 to-purple-400 text-black font-bold text-lg hover:shadow-[0_0_30px_rgba(6,182,212,0.4)] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Analyzing with Grad-CAM...
                  </span>
                ) : (
                  'Analyze Video with AI Heatmap'
                )}
              </button>
            </form>

            {/* Features Info */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="grid md:grid-cols-3 gap-4 mt-12"
            >
              <div className="p-4 rounded-lg bg-white/5 border border-white/10">
                <div className="text-cyan-400 font-bold mb-2">⚡ Fast</div>
                <p className="text-sm text-neutral-400">Analysis completes in seconds</p>
              </div>
              <div className="p-4 rounded-lg bg-white/5 border border-white/10">
                <div className="text-purple-400 font-bold mb-2">🎯 Grad-CAM</div>
                <p className="text-sm text-neutral-400">Visual heatmaps show detection areas</p>
              </div>
              <div className="p-4 rounded-lg bg-white/5 border border-white/10">
                <div className="text-green-400 font-bold mb-2">🔍 Accurate</div>
                <p className="text-sm text-neutral-400">98.5% detection accuracy</p>
              </div>
            </motion.div>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="space-y-8"
          >
            {/* Result Card */}
            <div className={`p-8 rounded-2xl backdrop-blur-xl border ${getResultBg(result.prediction)}`}>
              <div className="mb-6">
                <span className={`inline-block px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest bg-gradient-to-r ${getResultColor(result.prediction)} text-transparent bg-clip-text`}>
                  {result.prediction}
                </span>
              </div>

              <h2 className="text-4xl font-extrabold text-white mb-4">
                {result.prediction === 'REAL' && '✓ Content Verified'}
                {result.prediction === 'FAKE' && '⚠ Deepfake Detected'}
                {result.prediction === 'SUSPICIOUS' && '? Suspicious Content'}
              </h2>

              <div className="mb-8 space-y-3">
                <div>
                  <p className="text-neutral-400 text-sm mb-2">Confidence Score</p>
                  <div className="flex items-end gap-4">
                    <div className="text-5xl font-extrabold text-white">
                      {(result.confidence * 100).toFixed(1)}%
                    </div>
                    <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${result.confidence * 100}%` }}
                        transition={{ duration: 1, ease: 'easeOut' }}
                        className={`h-full bg-gradient-to-r ${getResultColor(result.prediction)}`}
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Grad-CAM Visualizations */}
              {result.gradcam_frames && result.gradcam_frames.length > 0 && (
                <div className="mt-8 space-y-4">
                  <h3 className="text-2xl font-bold text-white mb-4">
                    🔍 AI Detection Heatmaps
                  </h3>
                  <p className="text-neutral-400 text-sm mb-4">
                    Red areas indicate regions the AI identified as potential deepfake indicators
                  </p>

                  {/* Main Visualization Display */}
                  <div className="rounded-lg overflow-hidden border border-white/20">
                    <AnimatePresence mode="wait">
                      <motion.img
                        key={selectedVisualization}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.3 }}
                        src={result.gradcam_frames[selectedVisualization].image}
                        alt={`Grad-CAM visualization ${selectedVisualization + 1}`}
                        className="w-full h-auto"
                      />
                    </AnimatePresence>
                    <div className="p-4 bg-white/5">
                      <div className="flex justify-between items-center">
                        <span className="text-neutral-300 text-sm">
                          Frame {result.gradcam_frames[selectedVisualization].frame_number}
                        </span>
                        <span className="text-white font-semibold">
                          Score: {(result.gradcam_frames[selectedVisualization].score * 100).toFixed(1)}%
                        </span>
                        {result.gradcam_frames[selectedVisualization].detection_frame && (
                          <span className="px-2 py-1 rounded bg-red-500/20 text-red-400 text-xs font-bold">
                            DETECTION FRAME
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Thumbnail Navigation */}
                  {result.gradcam_frames.length > 1 && (
                    <div className="flex gap-2 overflow-x-auto pb-2">
                      {result.gradcam_frames.map((vis, idx) => (
                        <button
                          key={idx}
                          onClick={() => setSelectedVisualization(idx)}
                          className={`flex-shrink-0 rounded-lg overflow-hidden border-2 transition-all ${
                            selectedVisualization === idx
                              ? 'border-cyan-400 scale-105'
                              : 'border-white/20 hover:border-white/40'
                          }`}
                        >
                          <img
                            src={vis.image}
                            alt={`Thumbnail ${idx + 1}`}
                            className="w-24 h-24 object-cover"
                          />
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}

              <div className="grid md:grid-cols-2 gap-4 mt-8">
                <div className="p-4 rounded-lg bg-white/5 border border-white/10">
                  <p className="text-neutral-400 text-sm mb-1">File</p>
                  <p className="text-white font-mono truncate">{result.filename}</p>
                </div>
                <div className="p-4 rounded-lg bg-white/5 border border-white/10">
                  <p className="text-neutral-400 text-sm mb-1">Visualizations</p>
                  <p className="text-cyan-400 font-semibold">
                    {result.gradcam_frames?.length || 0} Grad-CAM frames
                  </p>
                </div>
              </div>

              {/* Interpretation */}
              <div className="p-4 rounded-lg bg-white/5 border border-white/10 mt-4">
                <p className="text-white font-semibold mb-2">How to interpret the heatmaps:</p>
                <ul className="text-neutral-400 text-sm space-y-1">
                  <li>• <span className="text-red-400 font-semibold">Red/Hot areas</span>: Regions with strongest deepfake indicators</li>
                  <li>• <span className="text-blue-400 font-semibold">Blue/Cool areas</span>: Regions that appear more authentic</li>
                  <li>• The model focuses on facial features, edges, and inconsistencies</li>
                  <li>• Multiple frames show consistency of detection across the video</li>
                </ul>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4">
              <button
                onClick={() => {
                  setFile(null);
                  setPreview(null);
                  setResult(null);
                  setError(null);
                  setSelectedVisualization(0);
                }}
                className="flex-1 px-8 py-4 rounded-full bg-white/10 border border-white/20 text-white font-bold text-lg hover:bg-white/20 transition-all duration-300"
              >
                Analyze Another
              </button>
              <button
                onClick={onBack}
                className="flex-1 px-8 py-4 rounded-full bg-white text-black font-bold text-lg hover:bg-neutral-200 transition-all duration-300"
              >
                Back to Home
              </button>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default Upload;