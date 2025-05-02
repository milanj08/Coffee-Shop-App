//Used to display the home page of the barista
import React, { useContext } from "react";
import { useNavigate } from 'react-router-dom';
import { OrderContext } from '../OrderContext';

const BaristaCompleted = () => {
    const navigate = useNavigate();
    const { setOrderNumber } = useContext(OrderContext);

    const handleCompleteOrder = () => {
        // Increment the order number
        setOrderNumber(prev => prev + 1);
        // Navigate back to the home page
        navigate('/baristaHome');
    };

    return (
        <div>
            <h1 id="mainTitle">ORDER COMPLETED</h1>
            <div className="nextStepButton">
                <button onClick={handleCompleteOrder}>NEXT ORDER</button>
            </div>
        </div>
    );
};

export default BaristaCompleted;