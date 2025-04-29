import React from 'react'
import BackButton from '../components/backbutton'

export default function AddEmployee() {
    return (
        <>
        <div className="edit-employee-container">
            <div classname = "header-container">
                <BackButton endpoint = "employees" />
                <h1 className='header'>Add Employee</h1>
            </div>
        </div>
        </>
    )
}
