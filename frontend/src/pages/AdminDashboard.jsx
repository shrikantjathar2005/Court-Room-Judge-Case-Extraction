import { useState, useEffect } from 'react';
import { searchService } from '../services/searchService';
import { StatsCard, StatusBadge } from '../components/StatsCard';
import {
  HiOutlineDocumentText,
  HiOutlineUsers,
  HiOutlineChartBar,
  HiOutlineCheckCircle,
  HiOutlineDownload,
  HiOutlineCog,
} from 'react-icons/hi';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import toast from 'react-hot-toast';

const CHART_COLORS = ['#ef4444', '#f59e0b', '#06b6d4', '#10b981'];

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [accuracy, setAccuracy] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [statsData, accuracyData, usersData] = await Promise.all([
        searchService.getAdminStats(),
        searchService.getAccuracyStats(),
        searchService.getUsers(),
      ]);
      setStats(statsData);
      setAccuracy(accuracyData);
      setUsers(usersData);
    } catch (error) {
      toast.error('Failed to load admin data');
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async (userId, newRole) => {
    try {
      await searchService.updateUser(userId, { role: newRole });
      setUsers((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, role: newRole } : u))
      );
      toast.success('User role updated');
    } catch (error) {
      toast.error('Failed to update user');
    }
  };

  if (loading) {
    return (
      <div className="page-container flex items-center justify-center min-h-[60vh]">
        <div className="spinner" />
      </div>
    );
  }

  // Chart data
  const documentStatusData = stats ? 
    Object.entries(stats.documents_by_status || {}).map(([key, value]) => ({
      name: key.charAt(0).toUpperCase() + key.slice(1),
      count: value,
    })) : [];

  const confidenceData = accuracy?.confidence_distribution ?
    Object.entries(accuracy.confidence_distribution).map(([label, count]) => ({
      name: label,
      count,
    })) : [];

  return (
    <div className="page-container animate-fade-in">
      <div className="mb-8">
        <h1 className="section-title text-3xl">Admin Dashboard</h1>
        <p className="text-gray-500 mt-1 font-hindi">प्रशासनिक डैशबोर्ड</p>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatsCard
          title="Total Users"
          value={stats?.total_users || 0}
          icon={HiOutlineUsers}
          gradient="from-primary-400 to-purple-400"
        />
        <StatsCard
          title="Total Documents"
          value={stats?.total_documents || 0}
          icon={HiOutlineDocumentText}
          gradient="from-cyan-400 to-blue-400"
        />
        <StatsCard
          title="OCR Pages"
          value={stats?.total_ocr_pages || 0}
          icon={HiOutlineCog}
          gradient="from-amber-400 to-orange-400"
        />
        <StatsCard
          title="Total Corrections"
          value={stats?.total_corrections || 0}
          icon={HiOutlineCheckCircle}
          gradient="from-emerald-400 to-green-400"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Document Status Chart */}
        <div className="glass-card p-6">
          <h3 className="text-sm font-medium text-gray-400 mb-4">Documents by Status</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={documentStatusData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} />
              <Tooltip
                contentStyle={{
                  background: '#0f172a',
                  border: '1px solid #1e293b',
                  borderRadius: '12px',
                  color: '#f1f5f9',
                }}
              />
              <Bar dataKey="count" fill="#6366f1" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Confidence Distribution */}
        <div className="glass-card p-6">
          <h3 className="text-sm font-medium text-gray-400 mb-4">OCR Confidence Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={confidenceData}
                dataKey="count"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={90}
                label={({ name, count }) => `${name}: ${count}`}
                labelLine={false}
              >
                {confidenceData.map((_, index) => (
                  <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  background: '#0f172a',
                  border: '1px solid #1e293b',
                  borderRadius: '12px',
                  color: '#f1f5f9',
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Accuracy Stats */}
      {accuracy && (
        <div className="glass-card p-6 mb-8">
          <h3 className="text-sm font-medium text-gray-400 mb-4">OCR Accuracy Tracking</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
            <div>
              <p className="text-2xl font-bold text-primary-400">
                {accuracy.average_confidence?.toFixed(1)}%
              </p>
              <p className="text-xs text-gray-500">Average Confidence</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-emerald-400">
                {accuracy.total_documents_processed}
              </p>
              <p className="text-xs text-gray-500">Docs Processed</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-amber-400">
                {accuracy.corrected_pages}
              </p>
              <p className="text-xs text-gray-500">Pages Corrected</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-cyan-400">
                {accuracy.correction_rate}%
              </p>
              <p className="text-xs text-gray-500">Correction Rate</p>
            </div>
          </div>
        </div>
      )}

      {/* Export Dataset */}
      <div className="glass-card p-6 mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-medium text-gray-200">Feedback Dataset Export</h3>
            <p className="text-sm text-gray-500 mt-1">
              Export OCR → corrected text pairs for model training
            </p>
          </div>
          <div className="flex gap-2">
            <a
              href="/api/admin/feedback-dataset?format=json"
              className="btn-secondary flex items-center gap-2 text-sm"
            >
              <HiOutlineDownload className="w-4 h-4" />
              JSON
            </a>
            <a
              href="/api/admin/feedback-dataset?format=csv"
              className="btn-primary flex items-center gap-2 text-sm"
            >
              <HiOutlineDownload className="w-4 h-4" />
              CSV
            </a>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="glass-card overflow-hidden">
        <div className="px-6 py-4 border-b border-surface-700/50">
          <h3 className="section-title text-lg">User Management</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-surface-700/50">
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Email</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Role</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-700/30">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-surface-800/50 transition-colors">
                  <td className="px-6 py-4 text-sm text-gray-200">{user.full_name || '—'}</td>
                  <td className="px-6 py-4 text-sm text-gray-400">{user.email}</td>
                  <td className="px-6 py-4">
                    <span className={`badge ${
                      user.role === 'admin' ? 'badge-error' :
                      user.role === 'reviewer' ? 'badge-warning' : 'badge-info'
                    }`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={user.is_active ? 'badge-success' : 'badge-error'}>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <select
                      value={user.role}
                      onChange={(e) => handleRoleChange(user.id, e.target.value)}
                      className="input-field text-xs py-1 px-2 w-auto"
                    >
                      <option value="user">User</option>
                      <option value="reviewer">Reviewer</option>
                      <option value="admin">Admin</option>
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
