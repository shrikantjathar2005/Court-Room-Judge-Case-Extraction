import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { documentService } from '../services/documentService';
import { ConfidenceBadge, ConfidenceBar } from '../components/StatsCard';
import { HiOutlineSave, HiOutlineArrowLeft, HiOutlineCheck, HiOutlineClock } from 'react-icons/hi';
import toast from 'react-hot-toast';

export default function CorrectionInterface() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [document, setDocument] = useState(null);
  const [ocrResults, setOcrResults] = useState([]);
  const [corrections, setCorrections] = useState({});
  const [saving, setSaving] = useState({});
  const [history, setHistory] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [id]);

  const loadData = async () => {
    try {
      const doc = await documentService.getDocument(id);
      setDocument(doc);

      const results = await documentService.getOCRResults(id);
      setOcrResults(results);

      // Initialize corrections with current text
      const correctionMap = {};
      for (const result of results) {
        correctionMap[result.id] = result.raw_text || '';
        // Load correction history
        try {
          const hist = await documentService.getCorrectionHistory(result.id);
          if (hist.corrections && hist.corrections.length > 0) {
            correctionMap[result.id] = hist.corrections[0].corrected_text || result.raw_text;
            setHistory((prev) => ({ ...prev, [result.id]: hist }));
          }
        } catch (e) {
          // No corrections yet
        }
      }
      setCorrections(correctionMap);
    } catch (error) {
      toast.error('Failed to load document');
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const handleTextChange = (ocrResultId, text) => {
    setCorrections((prev) => ({ ...prev, [ocrResultId]: text }));
  };

  const handleSave = async (ocrResultId) => {
    setSaving((prev) => ({ ...prev, [ocrResultId]: true }));
    try {
      await documentService.submitCorrection(ocrResultId, corrections[ocrResultId]);
      toast.success('Correction saved!');
      // Reload history
      const hist = await documentService.getCorrectionHistory(ocrResultId);
      setHistory((prev) => ({ ...prev, [ocrResultId]: hist }));
    } catch (error) {
      toast.error('Failed to save correction');
    } finally {
      setSaving((prev) => ({ ...prev, [ocrResultId]: false }));
    }
  };

  if (loading) {
    return (
      <div className="page-container flex items-center justify-center min-h-[60vh]">
        <div className="spinner" />
      </div>
    );
  }

  return (
    <div className="page-container animate-fade-in">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <button
          onClick={() => navigate(`/documents/${id}`)}
          className="p-2 text-gray-400 hover:text-white hover:bg-surface-700 rounded-xl transition-all"
        >
          <HiOutlineArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="section-title text-2xl">Correction Interface</h1>
          <p className="text-gray-500 text-sm mt-0.5">{document?.title}</p>
        </div>
      </div>

      {/* Side-by-side correction panels */}
      {ocrResults.map((result) => (
        <div key={result.id} className="glass-card mb-6 overflow-hidden">
          {/* Page header */}
          <div className="px-6 py-3 border-b border-surface-700/50 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-sm font-medium text-gray-300">Page {result.page_number}</span>
              {result.confidence_score && (
                <ConfidenceBadge score={result.confidence_score} />
              )}
            </div>
            <div className="flex items-center gap-2">
              {history[result.id]?.total_versions > 0 && (
                <span className="flex items-center gap-1 text-xs text-gray-500">
                  <HiOutlineClock className="w-3 h-3" />
                  v{history[result.id]?.total_versions}
                </span>
              )}
              <button
                id={`save-correction-${result.page_number}`}
                onClick={() => handleSave(result.id)}
                disabled={saving[result.id]}
                className="btn-primary text-sm py-1.5 px-4 flex items-center gap-1.5"
              >
                {saving[result.id] ? (
                  <span className="spinner w-3 h-3" />
                ) : (
                  <HiOutlineSave className="w-4 h-4" />
                )}
                Save
              </button>
            </div>
          </div>

          {/* Side by side: Original | Editable */}
          <div className="grid grid-cols-1 lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-surface-700/50">
            {/* Original OCR text */}
            <div className="p-6">
              <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-3">
                Original OCR Text (मूल OCR पाठ)
              </h4>
              <div className="bg-surface-900/50 rounded-xl p-4 max-h-[400px] overflow-y-auto">
                <pre className="devanagari-text whitespace-pre-wrap text-gray-400">
                  {result.raw_text || 'No text extracted'}
                </pre>
              </div>
            </div>

            {/* Editable corrected text */}
            <div className="p-6">
              <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-3">
                Corrected Text (सुधारा हुआ पाठ)
              </h4>
              <textarea
                id={`correction-text-${result.page_number}`}
                value={corrections[result.id] || ''}
                onChange={(e) => handleTextChange(result.id, e.target.value)}
                className="textarea-devanagari"
                style={{ minHeight: '300px' }}
                placeholder="Enter corrected text here..."
              />
            </div>
          </div>

          {/* Confidence bar */}
          {result.confidence_score && (
            <div className="px-6 py-3 border-t border-surface-700/50">
              <div className="flex items-center gap-3">
                <span className="text-xs text-gray-500">Confidence</span>
                <div className="flex-1">
                  <ConfidenceBar score={result.confidence_score} />
                </div>
                <span className="text-xs text-gray-400">{result.confidence_score?.toFixed(1)}%</span>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
