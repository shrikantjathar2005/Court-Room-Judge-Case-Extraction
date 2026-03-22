import api from './api';

export const searchService = {
  async search(query, filters = {}) {
    const response = await api.post('/search/', {
      query,
      ...filters,
    });
    return response.data;
  },

  async suggest(query) {
    const response = await api.get('/search/suggest', { params: { q: query } });
    return response.data;
  },

  async getAdminStats() {
    const response = await api.get('/admin/stats');
    return response.data;
  },

  async getAccuracyStats() {
    const response = await api.get('/admin/accuracy');
    return response.data;
  },

  async getUsers() {
    const response = await api.get('/admin/users');
    return response.data;
  },

  async updateUser(userId, data) {
    const response = await api.put(`/admin/users/${userId}`, data);
    return response.data;
  },
};
