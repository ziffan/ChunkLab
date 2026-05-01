import axios from 'axios';

const isElectron = window.navigator.userAgent.toLowerCase().includes(' electron/');
const baseURL = isElectron 
  ? 'http://127.0.0.1:8000' 
  : (import.meta.env.VITE_API_BASE_URL || '');

const api = axios.create({
  baseURL: baseURL,
  timeout: 30000, // Tingkatkan timeout untuk native
});

export async function chunkMarkdown(payload) {
  try {
    const { data } = await api.post('/api/chunk', payload);
    return data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || error.message);
  }
}

export async function estimateTokens(payload) {
  try {
    const { data } = await api.post('/api/tokenize', payload);
    return data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || error.message);
  }
}

export async function testRegexPattern(payload) {
  try {
    const { data } = await api.post('/api/regex/test', payload);
    return data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || error.message);
  }
}

export async function fetchHealth() {
  try {
    const { data } = await api.get('/api/health');
    return data;
  } catch {
    return null;
  }
}

export async function retrieveChunks(payload) {
  try {
    const { data } = await api.post('/api/retrieve', payload, { timeout: 120000 });
    return data;
  } catch (error) {
    const err = new Error(
      error.response?.data?.message || error.response?.data?.detail || error.message
    );
    err.status = error.response?.status;
    throw err;
  }
}

export async function fetchOpenApiSpec() {
  const { data } = await api.get('/openapi.json');
  return data;
}

export async function fetchModels(provider, apiKey = null) {
  try {
    const params = { provider };
    if (apiKey) params.api_key = apiKey;
    const { data } = await api.get('/api/models', { params });
    return data;
  } catch (error) {
    return { available: false, models: [], error: error.message };
  }
}
