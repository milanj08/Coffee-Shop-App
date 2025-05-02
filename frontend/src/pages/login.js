// Shown when the user first opens the app
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './login.css';

export default function Login({ onLogin }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isRegistering, setIsRegistering] = useState(false);

    const navigate = useNavigate();

    const handleSubmit = (e) => {
        e.preventDefault();

        const users = JSON.parse(localStorage.getItem('users') || '{}'); //send this to the backend when it's set up.

        if (isRegistering) {
            if (users[username]) {
                setError('Username already exists');
            } else {
                users[username] = password;
                localStorage.setItem('users', JSON.stringify(users));
                setError('');
                alert('Registration successful! You can now log in.');
                setIsRegistering(false);
                setUsername('');
                setPassword('');
            }
        } else {
            if (users[username] && users[username] === password) {
                localStorage.setItem('currentUser', username);
                onLogin?.(username); // optional callback

                if (username.includes("manager")){
                    navigate('/managerHome');
                }else if(username.includes("barista")){
                    navigate('/baristaHome');
                }
            } else {
                setError('Invalid username or password');
            }
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
                    required
                />

                <label>Password:</label>
                <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />

                {error && <p className="error">{error}</p>}

                <button type="submit">{isRegistering ? 'Register' : 'Login'}</button>

                <p style={{ marginTop: '10px' }}>
                    {isRegistering ? (
                        <>
                            Already have an account?{' '}
                            <button type="button" onClick={() => setIsRegistering(false)} className="link-button">
                                Log in
                            </button>
                        </>
                    ) : (
                        <>
                            New here?{' '}
                            <button type="button" onClick={() => setIsRegistering(true)} className="link-button">
                                Create an account
                            </button>
                        </>
                    )}
                </p>
            </form>
        </div>
    );
}