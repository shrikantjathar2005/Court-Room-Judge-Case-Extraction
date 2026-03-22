import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { documentService } from '../services/documentService';
import { ConfidenceBadge, ConfidenceBar, StatusBadge } from '../components/StatsCard';
import {
  HiOutlineDocumentText,
  HiOutlineCog,
  HiOutlinePencil,
  HiOutlineTrash,
  HiOutlineRefresh,
  HiOutlineDownload,
} from 'react-icons/hi';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';

export default function DocumentViewer() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAdmin } = useAuth();
  const [document, setDocument] = useState(null);
  const [ocrResults, setOcrResults] = useState([]);
  const [ocrStatus, setOcrStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    loadDocument();
  }, [id]);

  const loadDocument = async () => {
    try {
      const doc = await documentService.getDocument(id);
      setDocument(doc);

      if (doc.status === 'processed' || doc.status === 'reviewed') {
        const results = await documentService.getOCRResults(id);
        setOcrResults(results);
      }

      if (doc.status === 'processing') {
        pollStatus();
      }
    } catch (error) {
      toast.error('Failed to load document');
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const triggerOCR = async () => {
    setProcessing(true);
    try {
      await documentService.triggerOCR(id);
      toast.success('OCR processing started!');
      pollStatus();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to start OCR');
      setProcessing(false);
    }
  };

  const pollStatus = () => {
    const interval = setInterval(async () => {
      try {
        const status = await documentService.getOCRStatus(id);
        setOcrStatus(status);

        if (status.status === 'processed' || status.status === 'reviewed') {
          clearInterval(interval);
          setProcessing(false);
          setOcrResults(status.results || []);
          setDocument((prev) => ({ ...prev, status: status.status }));
          toast.success('OCR processing complete!');
        } else if (status.status === 'failed') {
          clearInterval(interval);
          setProcessing(false);
          setDocument((prev) => ({ ...prev, status: 'failed' }));
          toast.error('OCR processing failed');
        }
      } catch (error) {
        clearInterval(interval);
        setProcessing(false);
      }
    }, 3000);

    // Clear after 5 minutes max
    setTimeout(() => {
      clearInterval(interval);
      setProcessing(false);
    }, 300000);
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this document?')) return;
    try {
      await documentService.deleteDocument(id);
      toast.success('Document deleted');
      navigate('/');
    } catch (error) {
      toast.error('Failed to delete document');
    }
  };

  if (loading) {
    return (
      <div className="page-container flex items-center justify-center min-h-[60vh]">
        <div className="spinner" />
      </div>
    );
  }

  if (!document) return null;

  return (
    <div className="page-container animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="section-title text-2xl">{document.title}</h1>
          <div className="flex items-center gap-3 mt-2">
            <StatusBadge status={document.status} />
            {document.department && (
              <span className="text-sm text-gray-500">{document.department}</span>
            )}
            {document.document_type && (
              <span className="text-sm text-gray-500">• {document.document_type}</span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {document.status === 'uploaded' && (
            <button
              id="trigger-ocr-btn"
              onClick={triggerOCR}
              disabled={processing}
              className="btn-primary flex items-center gap-2"
            >
              {processing ? (
                <><span className="spinner" /> Processing...</>
              ) : (
                <><HiOutlineCog className="w-4 h-4" /> Run OCR</>
              )}
            </button>
          )}

          {(document.status === 'processed' || document.status === 'reviewed') && (
            <Link
              to={`/documents/${id}/correct`}
              className="btn-secondary flex items-center gap-2"
            >
              <HiOutlinePencil className="w-4 h-4" /> Correct Text
            </Link>
          )}

          <button
            onClick={async () => {
              try {
                const blob = await documentService.getDocumentFile(id);
                const fileUrl = window.URL.createObjectURL(blob);
                window.open(fileUrl, '_blank');
              } catch (error) {
                toast.error('Failed to open document file');
              }
            }}
            className="btn-secondary flex items-center gap-2"
          >
            <HiOutlineDownload className="w-4 h-4" /> View File
          </button>

          {isAdmin && (
            <button
              onClick={handleDelete}
              className="btn-danger flex items-center gap-2"
            >
              <HiOutlineTrash className="w-4 h-4" /> Delete
            </button>
          )}
        </div>
      </div>

      {/* Document Info */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="glass-card p-6">
          <h3 className="text-sm font-medium text-gray-400 mb-4">Document Info</h3>
          <dl className="space-y-3 text-sm">
            <div className="flex justify-between">
              <dt className="text-gray-500">File Type</dt>
              <dd className="text-gray-200">{document.file_type?.toUpperCase()}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">File Size</dt>
              <dd className="text-gray-200">
                {document.file_size ? `${(document.file_size / 1024).toFixed(1)} KB` : '—'}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Pages</dt>
              <dd className="text-gray-200">{document.total_pages}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Document Date</dt>
              <dd className="text-gray-200">
                {document.document_date || '—'}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Uploaded</dt>
              <dd className="text-gray-200">
                {new Date(document.created_at).toLocaleString()}
              </dd>
            </div>
          </dl>
        </div>

        {ocrStatus && (
          <div className="glass-card p-6 lg:col-span-2">
            <h3 className="text-sm font-medium text-gray-400 mb-4">OCR Statistics</h3>
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div>
                <p className="text-2xl font-bold text-primary-400">{ocrStatus.processed_pages}</p>
                <p className="text-xs text-gray-500">Pages Processed</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-emerald-400">
                  {ocrStatus.average_confidence?.toFixed(1) || '—'}%
                </p>
                <p className="text-xs text-gray-500">Avg Confidence</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-cyan-400">{ocrStatus.total_pages}</p>
                <p className="text-xs text-gray-500">Total Pages</p>
              </div>
            </div>
            {ocrStatus.average_confidence && (
              <ConfidenceBar score={ocrStatus.average_confidence} />
            )}
          </div>
        )}
      </div>

      {/* Processing Status */}
      {processing && (
        <div className="glass-card p-6 mb-8 border-amber-500/30">
          <div className="flex items-center gap-3">
            <div className="spinner" />
            <div>
              <p className="font-medium text-amber-400">Processing document...</p>
              <p className="text-sm text-gray-500">
                {ocrStatus
                  ? `Page ${ocrStatus.processed_pages} of ${ocrStatus.total_pages}`
                  : 'Starting OCR pipeline...'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* OCR Results */}
      {ocrResults.length > 0 && (
        <div className="space-y-4">
          <h2 className="section-title text-xl">OCR Results</h2>
          {ocrResults.map((result) => (
            <div key={result.id} className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium text-gray-400">
                    Page {result.page_number}
                  </span>
                  <StatusBadge status={result.status} />
                  {result.confidence_score && (
                    <ConfidenceBadge score={result.confidence_score} />
                  )}
                </div>
                {result.processing_time && (
                  <span className="text-xs text-gray-500">
                    {result.processing_time.toFixed(1)}s
                  </span>
                )}
              </div>

              {result.raw_text ? (
                <div className="bg-surface-900/50 rounded-xl p-4 max-h-[300px] overflow-y-auto">
                  <pre className="devanagari-text whitespace-pre-wrap text-gray-300">
                    {result.raw_text}
                  </pre>
                </div>
              ) : result.error_message ? (
                <div className="bg-red-500/10 rounded-xl p-4">
                  <p className="text-sm text-red-400">{result.error_message}</p>
                </div>
              ) : (
                <p className="text-gray-500 text-sm">No text extracted</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
