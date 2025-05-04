import Box from '../components/Box.js';
import React from 'react';
import { useNavigate } from 'react-router-dom';
import BackButton from '../components/backbutton.js';
import './employee.css';

export default function Employees() {
    const navigate = useNavigate();

    const employees = [
        { name: 'Alice' },
        { name: 'Bob' },
        { name: 'Charlie' }
    ];

    const handleAdd = () => {
        navigate("/addEmployee");
    };

    return (
        <>
            <div className="employees-page">
                <div className="back-button-container">
                    <BackButton endpoint="managerHome" />
                </div>

                <div className="employees-header">
                    <h1>Employee Management</h1>
                    <button id="addEmployee" onClick={handleAdd}>Add Employee</button>
                </div>

                <div className="boxes-grid">
                    {employees.map((employee, index) => (
                        <Box key={index} name={employee.name} />
                    ))}
                </div>
            </div>
        </>
    );
}
