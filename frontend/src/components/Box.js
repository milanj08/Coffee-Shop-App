//used for Employee Management
import React from 'react';

export default function Box({name}) {
    return(
        <div className = "box">
            <h2>{name}</h2>
            <button className = "editButton">Edit</button>
        </div>
    )
}
