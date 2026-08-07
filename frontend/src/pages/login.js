// Shown when the user first opens the app.
//
// The previous version kept a { username: password } map in localStorage in
// plain text, compared the password in the browser, and decided the role with
// username.includes("manager"). All three of those are gone:
//
//   - The password is sent to the server and never stored anywhere.
//   - The server compares it against a hash and issues a token.
//   - The role comes back from the server, derived from the database.
//
// Editing the stored role in devtools now changes which buttons you see and
// nothing else. Every endpoint checks the role again, server-side.

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api, { readApiError } from '../api';
import { saveSession } from '../auth';
import './login.css';

export default function Login({ onLogin }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [email, setEmail] = useState('');
    const [error, setError] = useState('');
    const [isRegistering, setIsRegistering] = useState(false);
    const [busy, setBusy] = useState(false);

    const navigate = useNavigate();

    // The server decides where you land, from the role it derived. The client
    // does not inspect the username.
    const goToHomeFor = (role) => {
        if (role === 'manager') {
            navigate('/managerHome');
        } else if (role === 'barista') {
            navigate('/baristaHome');
        } else {
            setError('This account has no role assigned. Contact a manager.');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setBusy(true);

        try {
            const endpoint = isRegistering ? 'auth/register/' : 'auth/login/';
            const body = isRegistering
                ? { username, password, first_name: firstName, last_name: lastName, email }
                : { username, password };

            const response = await api.post(endpoint, body);

            // Stores the token and the account details. Never the password.
            saveSession(response.data);
            onLogin?.(response.data);
            goToHomeFor(response.data.role);
        } catch (err) {
            setError(
                readApiError(
                    err,
                    isRegistering ? 'Could not create the account.' : 'Invalid username or password.'
                )
            );
        } finally {
            setBusy(false);
        }
    };

    return (
        <div className="login-container">
            <h2>{isRegistering ? 'Register' : 'Login'}</h2>
            <form onSubmit={handleSubmit} className="login-form">
                <label>Username:</label>
                <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    autoComplete="username"
                    required
                />

                <label>Password:</label>
                <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    autoComplete={isRegistering ? 'new-password' : 'current-password'}
                    required
                />

                {/* Registration needs enough to create the employee record.
                    Note there is no role selector - new accounts are always
                    baristas, decided by the server. */}
                {isRegistering && (
                    <>
                        <label>First Name:</label>
                        <input
                            type="text"
                            value={firstName}
                            onChange={(e) => setFirstName(e.target.value)}
                            required
                        />

                        <label>Last Name:</label>
                        <input
                            type="text"
                            value={lastName}
                            onChange={(e) => setLastName(e.target.value)}
                            required
                        />

                        <label>Email:</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </>
                )}

                {error && <p className="error" style={{ whiteSpace: 'pre-line' }}>{error}</p>}

                <button type="submit" disabled={busy}>
                    {busy ? 'Please wait…' : isRegistering ? 'Register' : 'Login'}
                </button>

                <p style={{ marginTop: '10px' }}>
                    {isRegistering ? (
                        <>
                            Already have an account?{' '}
                            <button
                                type="button"
                                onClick={() => { setIsRegistering(false); setError(''); }}
                                className="link-button"
                            >
                                Log in
                            </button>
                        </>
                    ) : (
                        <>
                            New here?{' '}
                            <button
                                type="button"
                                onClick={() => { setIsRegistering(true); setError(''); }}
                                className="link-button"
                            >
                                Create an account
                            </button>
                        </>
                    )}
                </p>
            </form>
        </div>
    );
}
