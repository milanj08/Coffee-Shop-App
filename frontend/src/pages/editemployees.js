import React from 'react'
import BackButton from '../components/backbutton'

export default function EditEmployee() {
    return (
        <>
        <div className="edit-employee-container">
            <div classname = "header-container">
                <BackButton endpoint = "employees" />
                <h1 className='header'>Edit Employee</h1>
            </div>
        </div>
        </>
    )
}
