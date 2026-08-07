// Session storage for the signed-in user.
//
// What is kept here is a TOKEN and the account details the server sent back.
// The password is never stored, never held in state, and never leaves the
// login form - which is the whole point of this file existing.
//
// Storage choice: localStorage, so a refresh doesn't sign you out. The cost is
// that any JavaScript running on the page can read it, so an XSS bug leaks the
// token. The safer option is an httpOnly cookie, which JavaScript cannot read -
// but that means session auth and CORS-with-credentials across ports. Noted in
// the README rather than pretended away.

const TOKEN_KEY = 'authToken';
const ACCOUNT_KEY = 'account';

export function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

export function getAccount() {
    const raw = localStorage.getItem(ACCOUNT_KEY);
    if (!raw) {
        return null;
    }
    try {
        return JSON.parse(raw);
    } catch {
        // Corrupt or hand-edited value. Treat it as signed out rather than
        // crashing every page that reads it.
        return null;
    }
}

// `account` is the payload from /auth/login/ or /auth/register/:
// { username, first_name, last_name, email, role, token }
export function saveSession(account) {
    const { token, ...rest } = account;
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(ACCOUNT_KEY, JSON.stringify(rest));
}

export function clearSession() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(ACCOUNT_KEY);
}

export function isSignedIn() {
    return Boolean(getToken());
}

// The role stored here decides which screens the UI offers. It does NOT decide
// what the API allows - the server derives that from the Barista/Manager tables
// on every single request. Editing this value in devtools changes the menu you
// see and nothing else; the endpoints still return 403.
export function getRole() {
    const account = getAccount();
    return account ? account.role : null;
}
