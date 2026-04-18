import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 15000,
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
