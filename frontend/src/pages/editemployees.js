import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import BackButton from '../components/backbutton';
import './editemployees.css';
import { API_BASE_URL } from '../config';

export default function EditEmployee() {
    const location = useLocation();
    const ssn = location.state?.ssn || '';

    const [salary, setSalary] = useState('');

    const handleDelete = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}employees/delete/?ssn=${encodeURIComponent(ssn)}`, {
                method: 'DELETE',
            });

            if (!response.ok) {
                throw new Error('Failed to delete employee');
            }

            alert('Employee deleted successfully');
        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    };

    const handleSalaryChange = (e) => setSalary(e.target.value);

    const handleSalarySubmit = async () => {
        if (!salary || isNaN(salary) || Number(salary) <= 0) {
            alert('Please enter a valid salary');
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}employees/update-salary/?ssn=${encodeURIComponent(ssn)}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ salary }),
            });

            if (!response.ok) {
                throw new Error('Failed to update salary');
            }

            alert('Salary updated successfully');
        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            handleSalarySubmit();  // Trigger salary update on Enter key press
        }
    };

    return (
        <>
            <div className="header-container">
                <BackButton endpoint="employees" />
            </div>
            <h1 className="header">Edit Employee</h1>
            <div className="edit-employee-form-group">
                <label htmlFor="salary">Salary:</label>
                <input
                    type="number"
                    id="salary"
                    value={salary}
                    onChange={handleSalaryChange}
                    onKeyDown={handleKeyDown} 
                    placeholder="Enter new salary"
                />
            </div>
            <button onClick={handleDelete} className="delete-button">
                Delete Employee
            </button>
        </>
    );
}
