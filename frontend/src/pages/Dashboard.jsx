import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { documentService } from '../services/documentService';
import { StatsCard, StatusBadge } from '../components/StatsCard';
import {
  HiOutlineDocumentText,
  HiOutlineUpload,
  HiOutlineSearch,
  HiOutlineEye,
  HiOutlineClock,
  HiOutlineCheckCircle,
  HiOutlineChartBar,
} from 'react-icons/hi';

export default function Dashboard() {
  const { user } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ total: 0 });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const result = await documentService.listDocuments(1, 10);
      setDocuments(result.documents || []);
      setStats({ total: result.total || 0 });
    } catch (error) {
      console.error('Failed to load documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const statusCounts = documents.reduce((acc, doc) => {
    acc[doc.status] = (acc[doc.status] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="page-container animate-fade-in">
      {/* Welcome Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
          Welcome back, {user?.full_name || 'User'}
        </h1>
        <p className="text-gray-500 mt-1 font-hindi">दस्तावेज़ प्रबंधन डैशबोर्ड</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatsCard
          title="Total Documents"
          value={stats.total}
          icon={HiOutlineDocumentText}
          gradient="from-primary-400 to-cyan-400"
        />
        <StatsCard
          title="Processed"
          value={statusCounts.processed || 0}
          icon={HiOutlineCheckCircle}
          gradient="from-emerald-400 to-green-400"
        />
        <StatsCard
          title="Processing"
          value={statusCounts.processing || 0}
          icon={HiOutlineClock}
          gradient="from-amber-400 to-yellow-400"
        />
        <StatsCard
          title="Uploaded"
          value={statusCounts.uploaded || 0}
          icon={HiOutlineUpload}
          gradient="from-cyan-400 to-blue-400"
        />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <Link to="/upload" className="glass-card p-6 hover:border-primary-500/30 transition-all duration-300 group cursor-pointer">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-xl bg-primary-600/10 group-hover:bg-primary-600/20 transition-colors">
              <HiOutlineUpload className="w-6 h-6 text-primary-400" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-100">Upload Document</h3>
              <p className="text-sm text-gray-500">दस्तावेज़ अपलोड करें</p>
            </div>
          </div>
        </Link>

        <Link to="/search" className="glass-card p-6 hover:border-cyan-500/30 transition-all duration-300 group cursor-pointer">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-xl bg-cyan-600/10 group-hover:bg-cyan-600/20 transition-colors">
              <HiOutlineSearch className="w-6 h-6 text-cyan-400" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-100">Search Documents</h3>
              <p className="text-sm text-gray-500">दस्तावेज़ खोजें</p>
            </div>
          </div>
        </Link>

        <div className="glass-card p-6 hover:border-emerald-500/30 transition-all duration-300 group">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-xl bg-emerald-600/10 group-hover:bg-emerald-600/20 transition-colors">
              <HiOutlineChartBar className="w-6 h-6 text-emerald-400" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-100">Analytics</h3>
              <p className="text-sm text-gray-500">विश्लेषण देखें</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Documents */}
      <div className="glass-card overflow-hidden">
        <div className="px-6 py-4 border-b border-surface-700/50">
          <h2 className="section-title text-xl">Recent Documents</h2>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="spinner" />
          </div>
        ) : documents.length === 0 ? (
          <div className="text-center py-12">
            <HiOutlineDocumentText className="w-12 h-12 text-gray-600 mx-auto mb-3" />
            <p className="text-gray-500">No documents yet</p>
            <Link to="/upload" className="btn-primary inline-block mt-4">
              Upload First Document
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-surface-700/50">
                  <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                  <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Department</th>
                  <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                  <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                  <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-700/30">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-surface-800/50 transition-colors">
                    <td className="px-6 py-4">
                      <p className="font-medium text-gray-200 truncate max-w-[200px]">{doc.title}</p>
                      <p className="text-xs text-gray-500">{doc.file_type?.toUpperCase()}</p>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-400">{doc.department || '—'}</td>
                    <td className="px-6 py-4 text-sm text-gray-400">{doc.document_type || '—'}</td>
                    <td className="px-6 py-4"><StatusBadge status={doc.status} /></td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4">
                      <Link
                        to={`/documents/${doc.id}`}
                        className="inline-flex items-center gap-1 text-primary-400 hover:text-primary-300 text-sm transition-colors"
                      >
                        <HiOutlineEye className="w-4 h-4" />
                        View
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
