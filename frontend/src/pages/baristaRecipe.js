//Used to display the home page of the barista
import React, { useContext, useState } from "react";
import { useNavigate } from 'react-router-dom';
import { OrderContext } from '../OrderContext';
import './baristaRecipe.css';
import './baristaCompleted';


const BaristaRecipe = () => {
    const navigate = useNavigate();

    // Gets order details from OrderContext
    const { orders, setOrders, setOrderNumber, orderNumber } = useContext(OrderContext);
    const [currentIndex, setCurrentIndex] = useState(0);
    const currentDrink = orders[currentIndex];

    // Checks if we have additional recipes to make, otherwise go to the next page
    const handleNext = () => {
        if (currentIndex < orders.length - 1) {
            setCurrentIndex(currentIndex + 1);
        } else {
            navigate('/baristaCompleted');
        }
    };

    return (
        <div>
            { /* RECIPE FOR: recipe name */ }
            <div>
                <h1 id = "mainTitle">RECIPE FOR: {currentDrink?.name}</h1>
            </div>

            { /* Holds order number, labels and steps */ }
            <div className="recipe-container">
                { /* Order # */ }
                <div className="order-row">
                    <span id = "boxHeader">Order {String(orderNumber).padStart(2, '0')}</span>
                </div>

                { /* Recipe labels */ }
                <div className="order-row" id = "second-row">
                    <span class="labels">POS NO.</span>
                    <span class="labels">IN. QUANTITY</span>
                    <span class="labels">IN. UNIT</span>
                    <span class="labels">INGREDIENT NAME</span>
                    <span class="labels">DESCRIPTION</span>
                </div>

                { /* Recipe steps */ }
                <div className="recipe-steps">
                    { /* Creates 3 recipe rows for styling */ }
                    {[...Array(3)].map((_, index) => (
                        <div className="recipe-row" key={index}>
                            <div className="recipe-cell">01</div>
                            <div className="recipe-cell"></div>
                            <div className="recipe-cell"></div>
                            <div className="recipe-cell"></div>
                            <div className="recipe-cell"></div>
                        </div>
                    ))}
                </div>
            </div>

            { /* Either go to the next recipe or complete order page */ }
            <div className ="nextStepButton">
                    <button onClick={handleNext}>Next Recipe / Finish Order</button>
            </div>
        </div>
    );
};

export default BaristaRecipe;