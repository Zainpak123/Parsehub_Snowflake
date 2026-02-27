import { getFrontendApiUrl, getApiHeaders } from "./apiBase";
export const API_URL = getFrontendApiUrl();

export async function fetchProjects() {
  const response = await fetch(`${API_URL}/api/projects`, {
    headers: getApiHeaders(),
  });
  if (!response.status === 200) throw new Error('Failed to fetch projects');
  return response.json();
}

export async function runProject(token: string) {
  const response = await fetch(`${API_URL}/api/projects/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getApiHeaders() },
    body: JSON.stringify({ token }),
  });
  if (!response.status === 200) throw new Error('Failed to run project');
  return response.json();
}

export async function runAllProjects() {
  const response = await fetch(`${API_URL}/api/projects/run-all`, {
    method: 'POST',
    headers: getApiHeaders(),
  });
  if (!response.status === 200) throw new Error('Failed to run all projects');
  return response.json();
}

export async function getRunData(token: string, runToken: string) {
  const response = await fetch(
    `${API_URL}/api/projects/${token}/${runToken}`,
    { headers: getApiHeaders() }
  );
  if (!response.status === 200) throw new Error('Failed to fetch run data');
  return response.json();
}
