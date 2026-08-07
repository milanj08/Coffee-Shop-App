import React, { useState } from 'react'
import BackButton from '../components/backbutton'
import api, { readApiError } from '../api';
import { API_BASE_URL } from '../config';
// Was missing. CRA only bundles a stylesheet if a module imports it, so none
// of this page's styles were being applied.
import './addemployee.css';

export default function AddEmployee() {
    const [first_name, setFirstName] = useState('')
    const [last_name, setLastName] = useState('')
    const [ssn, setSSN] = useState('')
    const [email, setEmail] = useState('')
    const [salary, setSalary] = useState('')

    const handleSubmit = async () => {
        try {
            // Was fetch(). axios serializes the body, sets the JSON content
            // type, throws on non-2xx, and the api instance adds the auth
            // token - so all of that boilerplate is gone.
            await api.post(`${API_BASE_URL}baristas/`, {
                ssn: {
                    ssn: parseInt(ssn),
                    first_name,
                    last_name,
                    email,
                    salary: parseFloat(salary),
                },
                day: '2025-05-01',
                start_time: '08:00:00',
                end_time: '16:00:00',
            })

            alert('Employee added successfully')
        } catch (error) {
            // readApiError surfaces what the server actually said - a salary
            // validation message, or "This action is restricted to managers."
            alert(readApiError(error, 'Failed to add employee.'))
        }
    }

    return (
        <>
            <div className="edit-employee-container">
                <div className="header-container">
                    <BackButton endpoint="employees" />
                </div>
                <h1 className="header">Add Employee</h1>
                <div className="form-group">
                    <label>First Name:</label>
                    <input
                        type="text"
                        value={first_name}
                        onChange={(e) => setFirstName(e.target.value)}
                        placeholder="Enter first name"
                    />

                    <label>Last Name:</label>
                    <input
                        type="text"
                        value={last_name}
                        onChange={(e) => setLastName(e.target.value)}
                        placeholder="Enter last name"
                    />

                    <label>SSN:</label>
                    <input
                        type="text"
                        value={ssn}
                        onChange={(e) => setSSN(e.target.value)}
                        placeholder="Enter SSN"
                    />

                    <label>Email:</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="Enter email"
                    />

                    <label>Salary:</label>
                    <input
                        type="number"
                        value={salary}
                        onChange={(e) => setSalary(e.target.value)}
                        placeholder="Enter salary"
                    />

                    <button onClick={handleSubmit} className="submit-button">
                        Submit
                    </button>
                </div>
            </div>
        </>
    )
}
