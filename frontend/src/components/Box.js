//used for Employee Management
import './box.css';
import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function Box({name}) {
    const navigate = useNavigate();

    //navigates to edit employee page
    const handleEdit = () => {
        navigate("/editEmployee");
    };

    return(
        <>
        <div className = "box">
            <h2>{name}</h2>
            <button id="editButton" onClick={handleEdit}>Edit</button>
        </div>
        </>
    )
}
