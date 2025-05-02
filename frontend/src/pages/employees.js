import Box from '../components/Box.js';
import React from 'react';
import { useNavigate } from 'react-router-dom';
import BackButton from '../components/backbutton.js';

export default function Employees() {
    const navigate = useNavigate();

    //dummy data for baristas
    const employees = [
        { name: 'Alice' },
        { name: 'Bob' },
        { name: 'Charlie' }
    ];

    //navigates to add employee page
    const handleAdd = () => {
        navigate("/addEmployee");
    };

    return (
        <>
            <div classname = "managingemployees">
                <div className="header-container">
                    <BackButton endpoint = "managerHome" />
                    <h1 className='header'>Employee Management</h1>
                </div>
                <button id="addEmployee" onClick={handleAdd}>Add Employee</button>
                <div classname = "boxes-container">
                    {employees.map((employee, index) => (
                        <Box key={index} name={employee.name} />
                    ))}
                </div>
            </div>
        </>
    );
}
