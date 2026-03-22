import api from './api';

export const documentService = {
  async uploadDocument(file, metadata) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', metadata.title);
    if (metadata.department) formData.append('department', metadata.department);
    if (metadata.document_date) formData.append('document_date', metadata.document_date);
    if (metadata.document_type) formData.append('document_type', metadata.document_type);

    const response = await api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  async listDocuments(page = 1, pageSize = 20, filters = {}) {
    const params = { page, page_size: pageSize, ...filters };
    const response = await api.get('/documents/', { params });
    return response.data;
  },

  async getDocument(id) {
    const response = await api.get(`/documents/${id}`);
    return response.data;
  },

  async getDocumentFile(id) {
    const response = await api.get(`/documents/${id}/file`, {
      responseType: 'blob',
    });
    return response.data;
  },

  async deleteDocument(id) {
    await api.delete(`/documents/${id}`);
  },

  async triggerOCR(documentId, options = {}) {
    const response = await api.post(`/ocr/process/${documentId}`, options);
    return response.data;
  },

  async getOCRStatus(documentId) {
    const response = await api.get(`/ocr/status/${documentId}`);
    return response.data;
  },

  async getOCRResults(documentId) {
    const response = await api.get(`/ocr/results/${documentId}`);
    return response.data;
  },

  async submitCorrection(ocrResultId, correctedText) {
    const response = await api.post(`/corrections/${ocrResultId}`, {
      corrected_text: correctedText,
    });
    return response.data;
  },

  async getCorrectionHistory(ocrResultId) {
    const response = await api.get(`/corrections/${ocrResultId}/history`);
    return response.data;
  },

  async getPendingReviews(page = 1, pageSize = 20) {
    const response = await api.get('/corrections/pending/review', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },
};
