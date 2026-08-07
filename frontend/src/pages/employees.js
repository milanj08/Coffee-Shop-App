import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Box from '../components/Box.js';
import BackButton from '../components/backbutton.js';
import './employee.css';
import api, { readApiError } from '../api';
import { API_BASE_URL } from '../config';

export default function Employees() {
    const navigate = useNavigate();
    const [employees, setEmployees] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const handleAdd = () => {
        navigate("/addEmployee");
    };

    useEffect(() => {
        const fetchEmployees = async () => {
            try {
                // Was fetch(). axios throws on a non-2xx response, so the
                // explicit response.ok check is no longer needed - and the
                // auth token is attached by the interceptor in api.js.
                const response = await api.get(`${API_BASE_URL}baristas/`);
                const parsedEmployees = response.data.map(barista => ({
                    name: `${barista.ssn.first_name} ${barista.ssn.last_name}`,
                    ssn: barista.ssn.ssn
                }));
                setEmployees(parsedEmployees);
            } catch (err) {
                console.error(err);
                setError(readApiError(err, 'Failed to load employees.'));
            } finally {
                setLoading(false);
            }
        };

        fetchEmployees();
    }, []);

    return (
        <div className="employees-page">
            <div className="back-button-container">
                <BackButton endpoint="managerHome" />
            </div>

            <div className="employees-header">
                <h1>Employee Management</h1>
                <button id="addEmployee" onClick={handleAdd}>Add Employee</button>
            </div>

            <div className="boxes-grid">
                {loading && <p>Loading employees...</p>}
                {error && <p>{error}</p>}
                {!loading && !error && employees.map((employee, index) => (
                    <Box key={index} name={employee.name} ssn={employee.ssn} />
                ))}
            </div>
        </div>
    );
}
