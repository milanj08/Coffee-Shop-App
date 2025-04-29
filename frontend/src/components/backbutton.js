//used for back button for all pages that need one
import React from 'react';
import './backbutton.css';
import { useNavigate } from 'react-router-dom';

export default function BackButton({endpoint}) {
    
    const navigate = useNavigate();

    const handleBack = () => {
        navigate("/" + endpoint);
    };

    return (
        <div className="back-button-container">
            <button id="back" onClick={handleBack}>Back</button>
        </div>
    );
}