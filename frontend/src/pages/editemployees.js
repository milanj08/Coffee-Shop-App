import React, { useState } from 'react'
import BackButton from '../components/backbutton'
import './editemployees.css'

export default function EditEmployee() {
    const [salary, setSalary] = useState('')

    const handleDelete = () => {
        // placeholder for delete functionality
        alert('Employee deleted')
    }

    const handleSalaryChange = (e) => {
        setSalary(e.target.value)
    }
    //api to change salary of employee
    const handleSalarySubmit = async () => {
        try {
            const response = await fetch('/api/employees/update-salary', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ salary }),
            })

            if (!response.ok) {
                throw new Error('Failed to update salary')
            }

            alert('Salary updated successfully')
        } catch (error) {
            alert(`Error: ${error.message}`)
        }
    }

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            handleSalarySubmit()
        }
    }

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
    )
}
