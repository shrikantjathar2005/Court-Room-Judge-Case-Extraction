import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { documentService } from '../services/documentService';
import { HiOutlineUpload, HiOutlineDocumentText, HiOutlineX } from 'react-icons/hi';
import toast from 'react-hot-toast';

export default function UploadDocument() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [metadata, setMetadata] = useState({
    title: '',
    department: '',
    document_date: '',
    document_type: '',
  });

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      if (!metadata.title) {
        setMetadata((prev) => ({
          ...prev,
          title: acceptedFiles[0].name.replace(/\.[^.]+$/, ''),
        }));
      }
    }
  }, [metadata.title]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/tiff': ['.tiff', '.tif'],
    },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024, // 50MB
  });

  const handleChange = (e) => {
    setMetadata({ ...metadata, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      toast.error('Please select a file');
      return;
    }
    if (!metadata.title.trim()) {
      toast.error('Please enter a title');
      return;
    }

    setLoading(true);
    try {
      const doc = await documentService.uploadDocument(file, metadata);
      toast.success('Document uploaded successfully!');
      navigate(`/documents/${doc.id}`);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="page-container animate-fade-in">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <h1 className="section-title text-3xl">Upload Document</h1>
          <p className="text-gray-500 mt-1 font-hindi">दस्तावेज़ अपलोड करें</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Dropzone */}
          <div
            {...getRootProps()}
            className={`glass-card p-8 text-center cursor-pointer transition-all duration-300
              ${isDragActive ? 'border-primary-500 bg-primary-600/10' : 'hover:border-primary-500/30'}
              ${file ? 'border-emerald-500/30' : ''}`}
          >
            <input {...getInputProps()} />

            {file ? (
              <div className="flex items-center justify-center gap-4">
                <div className="p-3 rounded-xl bg-emerald-600/10">
                  <HiOutlineDocumentText className="w-8 h-8 text-emerald-400" />
                </div>
                <div className="text-left">
                  <p className="font-medium text-gray-200">{file.name}</p>
                  <p className="text-sm text-gray-500">{formatFileSize(file.size)}</p>
                </div>
                <button
                  type="button"
                  onClick={(e) => { e.stopPropagation(); setFile(null); }}
                  className="p-2 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-xl transition-all"
                >
                  <HiOutlineX className="w-5 h-5" />
                </button>
              </div>
            ) : (
              <div>
                <HiOutlineUpload className="w-12 h-12 text-gray-500 mx-auto mb-3" />
                <p className="text-gray-300 font-medium">
                  {isDragActive ? 'Drop your file here...' : 'Drag & drop a file here, or click to select'}
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  Supports PDF, JPG, PNG, TIFF (max 50MB)
                </p>
              </div>
            )}
          </div>

          {/* Metadata Form */}
          <div className="glass-card p-6 space-y-4">
            <h3 className="font-semibold text-gray-200 mb-4">Document Metadata</h3>

            <div>
              <label className="block text-sm text-gray-400 mb-1.5">Title *</label>
              <input
                id="upload-title"
                type="text"
                name="title"
                value={metadata.title}
                onChange={handleChange}
                className="input-field"
                placeholder="Document title"
                required
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1.5">Department</label>
                <input
                  id="upload-department"
                  type="text"
                  name="department"
                  value={metadata.department}
                  onChange={handleChange}
                  className="input-field"
                  placeholder="e.g., Revenue, Home Affairs"
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1.5">Document Type</label>
                <select
                  id="upload-type"
                  name="document_type"
                  value={metadata.document_type}
                  onChange={handleChange}
                  className="input-field"
                >
                  <option value="">Select type</option>
                  <option value="judgment">Judgment (निर्णय)</option>
                  <option value="order">Order (आदेश)</option>
                  <option value="petition">Petition (याचिका)</option>
                  <option value="notification">Notification (अधिसूचना)</option>
                  <option value="circular">Circular (परिपत्र)</option>
                  <option value="gazette">Gazette (राजपत्र)</option>
                  <option value="report">Report (रिपोर्ट)</option>
                  <option value="other">Other (अन्य)</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1.5">Document Date</label>
              <input
                id="upload-date"
                type="date"
                name="document_date"
                value={metadata.document_date}
                onChange={handleChange}
                className="input-field"
              />
            </div>
          </div>

          {/* Submit */}
          <button
            id="upload-submit"
            type="submit"
            disabled={loading || !file}
            className="btn-primary w-full flex items-center justify-center gap-2 text-lg py-3"
          >
            {loading ? (
              <>
                <span className="spinner" />
                Uploading...
              </>
            ) : (
              <>
                <HiOutlineUpload className="w-5 h-5" />
                Upload Document
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
