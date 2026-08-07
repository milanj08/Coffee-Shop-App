//Manger Home Page after login
import React from "react";
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { clearSession } from '../auth';
import { API_BASE_URL } from '../config';
import './managerHome.css';
import './inventory';
import './employees';
import './login';


const ManagerHome = () => {
    const navigate = useNavigate();

    const handleEmployeesClick = () => {
        navigate("/employees");
    };

    const handleInventoryClick = () => {
        navigate("/inventory");
    };

    const handleReportsClick = () => {
        navigate("/reports");
    };

    // Deletes the token server-side, then clears it locally. See the note in
    // baristaHome - DRF tokens do not expire on their own.
    const handleLogOut = async () => {
        try {
            await api.post(`${API_BASE_URL}auth/logout/`);
        } catch (error) {
            console.error('Logout request failed:', error);
        }
        clearSession();
        navigate('/');
    };
    
    return (
        <div>
            <div className="header-container">
                <button id = "logOutButton" onClick={handleLogOut}>LOG OUT</button>
                <h1 id = "mainTitle">Manager</h1>
            </div>
            
            <div className="button-container">
                <button className = "menuOptions" onClick={handleEmployeesClick}>Managing Employees</button>
                <button className = "menuOptions" onClick={handleInventoryClick}>Managing Inventory</button>
                <button className = "menuOptions" onClick={handleReportsClick}>Accounting Reports</button>
            </div>
        </div>
    );
};

export default ManagerHome;