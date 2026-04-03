import { appConfig } from '../../config/appConfig';

const buildApiUrl = (path) => {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${appConfig.apiBaseUrl}${normalizedPath}`;
};

const parseResponsePayload = async (response) => {
  const contentType = String(response.headers.get('content-type') || '').toLowerCase();
  if (contentType.includes('application/json')) {
    return response.json();
  }
  const text = await response.text();
  return text || null;
};

const toErrorMessage = (payload, fallback) => {
  if (!payload) {
    return fallback;
  }
  if (typeof payload === 'string') {
    return payload;
  }
  if (typeof payload?.detail === 'string') {
    return payload.detail;
  }
  return fallback;
};

export const getStoredToken = () => localStorage.getItem(appConfig.authStorageKeys.token);

export const apiFetch = async (path, options = {}) => {
  const {
    token,
    headers,
    withAuth = true,
    ...restOptions
  } = options;

  const resolvedToken = token === undefined ? getStoredToken() : token;
  const requestHeaders = { ...(headers || {}) };
  if (withAuth && resolvedToken) {
    requestHeaders.Authorization = `Bearer ${resolvedToken}`;
  }

  const response = await fetch(buildApiUrl(path), {
    ...restOptions,
    headers: requestHeaders
  });

  const payload = await parseResponsePayload(response);
  if (!response.ok) {
    const defaultMessage = `HTTP ${response.status}`;
    throw new Error(toErrorMessage(payload, defaultMessage));
  }

  return payload;
};

export const apiUrl = buildApiUrl;
