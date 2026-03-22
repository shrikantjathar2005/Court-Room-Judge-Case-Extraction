import { useState } from 'react';
import { Link } from 'react-router-dom';
import { searchService } from '../services/searchService';
import { ConfidenceBadge, StatusBadge } from '../components/StatsCard';
import {
  HiOutlineSearch,
  HiOutlineFilter,
  HiOutlineDocumentText,
  HiOutlineEye,
  HiOutlineX,
} from 'react-icons/hi';

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    department: '',
    document_type: '',
    date_from: '',
    date_to: '',
    fuzzy: true,
  });

  const handleSearch = async (e) => {
    e?.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const searchFilters = {};
      if (filters.department) searchFilters.department = filters.department;
      if (filters.document_type) searchFilters.document_type = filters.document_type;
      if (filters.date_from) searchFilters.date_from = filters.date_from;
      if (filters.date_to) searchFilters.date_to = filters.date_to;
      searchFilters.fuzzy = filters.fuzzy;

      const data = await searchService.search(query, searchFilters);
      setResults(data);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const clearFilters = () => {
    setFilters({
      department: '',
      document_type: '',
      date_from: '',
      date_to: '',
      fuzzy: true,
    });
  };

  return (
    <div className="page-container animate-fade-in">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="section-title text-3xl">Search Documents</h1>
          <p className="text-gray-500 mt-1 font-hindi">दस्तावेज़ खोजें</p>
        </div>

        {/* Search Bar */}
        <form onSubmit={handleSearch} className="mb-6">
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <HiOutlineSearch className="absolute left-4 top-3.5 w-5 h-5 text-gray-500" />
              <input
                id="search-input"
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="input-field pl-12 text-lg"
                placeholder="Search in Hindi or English... (हिंदी या अंग्रेजी में खोजें)"
              />
            </div>
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className={`btn-secondary flex items-center gap-2 ${showFilters ? 'border-primary-500/50' : ''}`}
            >
              <HiOutlineFilter className="w-4 h-4" />
              Filters
            </button>
            <button id="search-submit" type="submit" disabled={loading} className="btn-primary flex items-center gap-2">
              {loading ? <span className="spinner" /> : <HiOutlineSearch className="w-4 h-4" />}
              Search
            </button>
          </div>
        </form>

        {/* Filters Panel */}
        {showFilters && (
          <div className="glass-card p-6 mb-6 animate-slide-up">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-400">Filters</h3>
              <button onClick={clearFilters} className="text-xs text-primary-400 hover:text-primary-300">
                Clear all
              </button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-xs text-gray-500 mb-1">Department</label>
                <input
                  type="text"
                  value={filters.department}
                  onChange={(e) => setFilters({ ...filters, department: e.target.value })}
                  className="input-field text-sm"
                  placeholder="e.g., Revenue"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Document Type</label>
                <select
                  value={filters.document_type}
                  onChange={(e) => setFilters({ ...filters, document_type: e.target.value })}
                  className="input-field text-sm"
                >
                  <option value="">All types</option>
                  <option value="judgment">Judgment</option>
                  <option value="order">Order</option>
                  <option value="petition">Petition</option>
                  <option value="notification">Notification</option>
                  <option value="circular">Circular</option>
                  <option value="gazette">Gazette</option>
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Date From</label>
                <input
                  type="date"
                  value={filters.date_from}
                  onChange={(e) => setFilters({ ...filters, date_from: e.target.value })}
                  className="input-field text-sm"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Date To</label>
                <input
                  type="date"
                  value={filters.date_to}
                  onChange={(e) => setFilters({ ...filters, date_to: e.target.value })}
                  className="input-field text-sm"
                />
              </div>
            </div>
            <div className="mt-4 flex items-center gap-2">
              <label className="flex items-center gap-2 text-sm text-gray-400 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filters.fuzzy}
                  onChange={(e) => setFilters({ ...filters, fuzzy: e.target.checked })}
                  className="rounded border-surface-700 bg-surface-800 text-primary-500 focus:ring-primary-500"
                />
                Fuzzy search (handle OCR errors)
              </label>
            </div>
          </div>
        )}

        {/* Results */}
        {results && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm text-gray-400">
                {results.total} result{results.total !== 1 ? 's' : ''} for{' '}
                <span className="text-primary-400">"{results.query}"</span>
              </p>
            </div>

            {results.results.length === 0 ? (
              <div className="text-center py-16">
                <HiOutlineDocumentText className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                <p className="text-gray-500">No documents found</p>
                <p className="text-sm text-gray-600 mt-1 font-hindi">कोई दस्तावेज़ नहीं मिला</p>
              </div>
            ) : (
              <div className="space-y-3">
                {results.results.map((item, index) => (
                  <div
                    key={`${item.document_id}-${index}`}
                    className="glass-card p-5 hover:border-primary-500/30 transition-all duration-300 animate-slide-up"
                    style={{ animationDelay: `${index * 50}ms` }}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <Link
                          to={`/documents/${item.document_id}`}
                          className="text-lg font-medium text-gray-200 hover:text-primary-400 transition-colors"
                        >
                          {item.title}
                        </Link>
                        <div className="flex items-center gap-3 mt-1">
                          {item.department && (
                            <span className="text-xs text-gray-500">{item.department}</span>
                          )}
                          {item.document_type && (
                            <span className="text-xs text-gray-500">• {item.document_type}</span>
                          )}
                          {item.document_date && (
                            <span className="text-xs text-gray-500">• {item.document_date}</span>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {item.confidence_score && (
                          <ConfidenceBadge score={item.confidence_score} />
                        )}
                        <span className="text-xs text-gray-600">
                          Score: {item.score?.toFixed(2)}
                        </span>
                      </div>
                    </div>

                    {/* Highlighted text snippet */}
                    {item.highlights && item.highlights.length > 0 ? (
                      <div className="mt-3 bg-surface-900/50 rounded-xl p-3">
                        {item.highlights.map((hl, i) => (
                          <div key={i} className="text-sm text-gray-400 devanagari-text">
                            {hl.fragments.map((frag, j) => (
                              <p
                                key={j}
                                className="mb-1"
                                dangerouslySetInnerHTML={{ __html: frag }}
                              />
                            ))}
                          </div>
                        ))}
                      </div>
                    ) : item.text_snippet ? (
                      <div className="mt-3 bg-surface-900/50 rounded-xl p-3">
                        <p className="text-sm text-gray-400 devanagari-text line-clamp-3">
                          {item.text_snippet}
                        </p>
                      </div>
                    ) : null}

                    <div className="mt-3 flex justify-end">
                      <Link
                        to={`/documents/${item.document_id}`}
                        className="flex items-center gap-1 text-sm text-primary-400 hover:text-primary-300 transition-colors"
                      >
                        <HiOutlineEye className="w-4 h-4" />
                        View Document
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Empty state when no search yet */}
        {!results && !loading && (
          <div className="text-center py-16">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-primary-600/10 rounded-2xl mb-4">
              <HiOutlineSearch className="w-10 h-10 text-primary-400" />
            </div>
            <p className="text-gray-400 text-lg">Search across all digitized documents</p>
            <p className="text-gray-600 mt-1 font-hindi">
              हिंदी और अंग्रेजी दोनों में खोज समर्थित है
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
