// Route guard.
//
// Wraps a route so that navigating to it while signed out - or signed in as
// the wrong role - sends you to the login page instead of rendering a screen
// that will just fill with 403s.
//
// This is CONVENIENCE, not security. Anyone can edit localStorage in devtools
// and get past it. What stops them is the API: every endpoint re-derives the
// role from the database on every request, so a barista who forces their way
// onto /managerHome sees a page whose requests all come back 403.
//
// That is the correct division. The client decides what to show; the server
// decides what is allowed. The original app only had the first half.

import React from 'react';
import { Navigate } from 'react-router-dom';
import { getRole, isSignedIn } from '../auth';

export default function RequireRole({ allow, children }) {
    if (!isSignedIn()) {
        return <Navigate to="/" replace />;
    }

    const role = getRole();
    if (allow && !allow.includes(role)) {
        return <Navigate to="/" replace />;
    }

    return children;
}
