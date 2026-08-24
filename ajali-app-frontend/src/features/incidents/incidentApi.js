const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const request = async (path, options = {}) => {
  const token = localStorage.getItem('access_token');
  const headers = new Headers(options.headers);

  if (token) headers.set('Authorization', `Bearer ${token}`);
  if (!(options.body instanceof FormData)) headers.set('Content-Type', 'application/json');

  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(payload.message || payload.error || 'The incident request failed.');
  }

  return payload;
};

export const incidentApi = {
  list: (params = {}) => request(`/incidents?${new URLSearchParams(params)}`),
  get: (id) => request(`/incidents/${id}`),
  create: (incident) => request('/incidents', {
    method: 'POST',
    body: JSON.stringify(incident),
  }),
  update: (id, incident) => request(`/incidents/${id}`, {
    method: 'PUT',
    body: JSON.stringify(incident),
  }),
  remove: (id) => request(`/incidents/${id}`, { method: 'DELETE' }),
  search: (query, params = {}) => request(`/incidents/search?${new URLSearchParams({ q: query, ...params })}`),
  filter: (params = {}) => request(`/incidents/filter?${new URLSearchParams(params)}`),
  statusHistory: (id) => request(`/incidents/${id}/status-history`),
  upload: (id, mediaType, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return request(`/incidents/${id}/${mediaType}`, { method: 'POST', body: formData });
  },
};
