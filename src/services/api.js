const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {'Content-Type': 'application/json', ...options.headers},
    ...options,
  });
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try { message = (await response.json()).detail || message; } catch {}
    throw new Error(message);
  }
  return response.status === 204 ? null : response.json();
}

export const getProjects = () => request('/projects');
export const getDashboard = () => request('/dashboard');
export const createProject = data => request('/projects', {method:'POST', body:JSON.stringify(data)});
export const getProject = id => request(`/projects/${id}`);
export const updateProject = (id,data) => request(`/projects/${id}`, {method:'PUT',body:JSON.stringify(data)});
export const deleteProject = id => request(`/projects/${id}`, {method:'DELETE'});
export const getScans = projectId => request(`/scans${projectId ? `?project_id=${projectId}` : ''}`);
export const createScan = data => request('/scans', {method:'POST',body:JSON.stringify(data)});
export const startScan = id => request(`/scans/${id}/start`, {method:'POST'});
export const cancelScan = id => request(`/scans/${id}/cancel`, {method:'POST'});
export const getScan = id => request(`/scans/${id}`);
export const getFindings = params => {
  const query = new URLSearchParams(Object.entries(params || {}).filter(([,v]) => v && v !== 'All'));
  return request(`/findings${query.size ? `?${query}` : ''}`);
};
export const getFinding = id => request(`/findings/${id}`);
export const updateFindingStatus = (id,status) => request(`/findings/${id}/status`, {method:'PATCH',body:JSON.stringify({status})});
export async function downloadReport(scanId, format) {
  const response = await fetch(`${API_BASE}/reports/${scanId}/${format}`);
  if (!response.ok) throw new Error((await response.json()).detail || 'Report generation failed');
  const blob = await response.blob();
  const url = URL.createObjectURL(blob); const anchor = document.createElement('a');
  anchor.href = url; anchor.download = `sentinel-scan-${scanId}.${format}`; anchor.click();
  URL.revokeObjectURL(url);
}
