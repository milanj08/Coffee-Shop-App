// Managing Employees Screen
import Box from '../components/Box';
import React from 'react';

export default function Employees() {
    //dummy data for employees
    const employees = [
        { name: 'Alice' },
        { name: 'Bob' },
        { name: 'Charlie' }
    ];

    return (
        <div>
            {employees.map((employee, index) => (
                <Box key={index} name={employee.name} />
            ))}
        </div>
    );
}
