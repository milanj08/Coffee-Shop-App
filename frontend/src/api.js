// The configured axios instance every page uses.
//
// Import this instead of axios directly. The request interceptor attaches the
// auth token to every call, so no page has to remember to - and a page that
// forgets can't exist.
//
// Every page used to import axios (or call fetch) and build its own request.
// That was fine while the API was open. With authentication it would mean the
// token appearing in a dozen places, and one missed spot is a 401 that only
// shows up when somebody clicks that particular button.

import axios from 'axios';
import { API_BASE_URL } from './config';
import { getToken } from './auth';

const api = axios.create({
    baseURL: API_BASE_URL,
});

// Runs before every request leaves the browser.
api.interceptors.request.use((config) => {
    const token = getToken();
    if (token) {
        // "Token <key>" is the format DRF's TokenAuthentication expects.
        // "Bearer <key>" is the JWT convention and will NOT work here.
        config.headers.Authorization = `Token ${token}`;
    }
    return config;
});

// Turns an axios error into something worth showing a person.
//
// DRF answers with { detail: "..." } for auth and permission failures and
// { field: ["message"] } for validation failures. Without this you get
// "Request failed with status code 403" and have to open devtools to find out
// that the real message was "This action is restricted to managers."
export function readApiError(error, fallback = 'Something went wrong.') {
    const data = error.response?.data;

    if (!data) {
        return 'Could not reach the server. Is the backend running?';
    }
    if (typeof data === 'string') {
        return data;
    }
    if (data.detail) {
        return data.detail;
    }
    if (data.error) {
        return data.error;
    }

    const messages = Object.entries(data).map(
        ([field, value]) => `${field}: ${Array.isArray(value) ? value.join(' ') : value}`
    );
    return messages.length ? messages.join('\n') : fallback;
}

// Deliberately no response interceptor.
//
// A 401 could be redirected to the login page automatically, which is tidier
// for the user. It also hides the failure: an unrelated permissions bug would
// silently sign people out and look like a session problem. Errors surface at
// the call site instead, so you see which request failed and why.

export default api;
