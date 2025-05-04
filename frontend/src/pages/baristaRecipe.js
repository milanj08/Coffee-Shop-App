//Used to display the home page of the barista
import React, { useContext, useState } from "react";
import { useNavigate } from 'react-router-dom';
import { OrderContext } from '../OrderContext';
import './baristaRecipe.css';
import './baristaCompleted';


const BaristaRecipe = () => {
    const navigate = useNavigate();

    // Gets order details from OrderContext
    const { recipes, orderNumber } = useContext(OrderContext);
    const [currentIndex, setCurrentIndex] = useState(0);

    // Get the current recipe based on currentIndex
    const currentRecipe = recipes[currentIndex];
    
    // Checks if we have additional recipes to make, otherwise go to the next page
    const handleNext = () => {
        if (currentIndex < recipes.length - 1) {
            setCurrentIndex(currentIndex + 1);
        } else {
            navigate('/baristaCompleted');
        }
    };

    return (
        <div>
            { /* RECIPE FOR: recipe name */ }
            <div>
                <h1 id="mainTitle">RECIPE FOR: {currentRecipe.recipe_name}</h1>
            </div>

            { /* Holds order number, labels and steps */ }
            <div className="recipe-container">
                { /* Order # */ }
                <div className="order-row">
                    <span id = "boxHeader">Order {orderNumber} : Drink #{currentRecipe.index}</span>
                </div>

                { /* Recipe labels */ }
                <div className="order-row" id = "second-row">
                    <span className="labels">POS NO.</span>
                    <span className="labels">IN. QUANTITY</span>
                    <span className="labels">IN. UNIT</span>
                    <span className="labels">INGREDIENT NAME</span>
                    <span className="labels">DESCRIPTION</span>
                </div>

                { /* Recipe steps */ }
                <div className="recipe-steps">
                    <div className="recipe-row">
                        <div className="recipe-cell">{currentRecipe.position_number}</div>
                        <div className="recipe-cell">{currentRecipe.ingredient_quantity}</div>
                        <div className="recipe-cell">{currentRecipe.ingredient_unit}</div>
                        <div className="recipe-cell">{currentRecipe.ingredient_name}</div>
                        <div className="recipe-cell">{currentRecipe.execution_description}</div>
                    </div>
                </div>
            </div>

            { /* Either go to the next recipe or complete order page */ }
            <div className ="nextStepButton">
                    <button onClick={handleNext}>{currentIndex < recipes.length - 1 ? 'Next Recipe' : 'Finish Order'}</button>
            </div>
        </div>
    );
};

export default BaristaRecipe;