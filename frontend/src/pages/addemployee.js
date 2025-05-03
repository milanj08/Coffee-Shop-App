import React, { useState } from 'react'
import BackButton from '../components/backbutton'

export default function AddEmployee() {
    const [name, setName] = useState('')
    const [ssn, setSSN] = useState('')
    const [email, setEmail] = useState('')
    const [salary, setSalary] = useState('')
    //api to send to backend to add employee
    const handleSubmit = async () => {
        try {
            const response = await fetch('/api/employees', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name,
                    ssn,
                    email,
                    salary: parseFloat(salary),
                }),
            })

            if (!response.ok) {
                throw new Error('Failed to add employee')
            }

            alert('Employee added successfully')
        } catch (error) {
            alert(`Error: ${error.message}`)
        }
    }

    return (
        <>
            <div className="edit-employee-container">
                <div className="header-container">
                    <BackButton endpoint="employees" />
                    <h1 className="header">Add Employee</h1>
                </div>

                <div className="form-group">
                    <label>Name:</label>
                    <input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="Enter name"
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
