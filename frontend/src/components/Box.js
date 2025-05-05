//used for Employee Management
import './box.css';
import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function Box({ name, ssn }) {
    const navigate = useNavigate();

    const handleEdit = () => {
        navigate("/editEmployee", { state: { ssn } });
    };

    return (
        <div className="box">
            <h2>{name}</h2>
            <button id="editButton" onClick={handleEdit}>Edit</button>
        </div>
    );
}
