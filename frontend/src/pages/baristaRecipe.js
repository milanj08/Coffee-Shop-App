//Used to display the home page of the barista
import React, { useContext, useState, useEffect } from "react";
import { useNavigate } from 'react-router-dom';
import { OrderContext } from '../OrderContext';
import './baristaRecipe.css';
import './baristaCompleted';


const BaristaRecipe = () => {
    const navigate = useNavigate();

    // Gets recipe details and order number from OrderContext
    const { recipes, orderNumber } = useContext(OrderContext);

    // Tracks which recipe group the barista will see
    const [currentIndex, setCurrentIndex] = useState(0);

    // Stores recipes with its corresponding set of steps
    const [groupedRecipes, setGroupedRecipes] = useState([]);

    // Groups each recipe with its corresponding steps on page load
    useEffect(() => {
        const grouped = {};
    
        for (const step of recipes) {
            const key = `${step.recipe_name}-${step.index}`;
            if (!grouped[key]) {
                grouped[key] = [];
            }
            grouped[key].push(step);
        }
    
        // Convert object to array of arrays
        setGroupedRecipes(Object.values(grouped));
    }, [recipes]);
    
    
    // Checks if we have additional recipes to make, otherwise go to the next page
    const handleNext = () => {
        if (currentIndex < groupedRecipes.length - 1) {
            setCurrentIndex(currentIndex + 1);
        } else {
            navigate('/baristaCompleted');
        }
    };

    // Wait to open the page until groundedRecipes is done being made
    if (groupedRecipes.length === 0) {
        return <div>Loading recipes...</div>;
    }

    // Get the recipes steps
    const currentRecipeSteps = groupedRecipes[currentIndex];

    return (
        <div>
            { /* RECIPE FOR: recipe name */ }
            <div>
                <h1 id="mainTitle">RECIPE FOR: {currentRecipeSteps[0].recipe_name}</h1>
            </div>

            { /* Holds order number, labels and steps */ }
            <div className="recipe-container">
                { /* Order # */ }
                <div className="order-row">
                    <span id = "boxHeader">Order {orderNumber} : Drink #{currentRecipeSteps[0].index}</span>
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
                    {currentRecipeSteps.map((step, index) => (
                        <div key={index} className="recipe-row">
                            <div className="recipe-cell">{step.position_number}</div>
                            <div className="recipe-cell">{step.ingredient_quantity}</div>
                            <div className="recipe-cell">{step.ingredient_unit}</div>
                            <div className="recipe-cell">{step.ingredient_name}</div>
                            <div className="recipe-cell">{step.execution_description}</div>
                        </div>
                    ))}
                </div>
            </div>

            { /* Either go to the next recipe or complete order page */ }
            <div className ="nextStepButton">
                    <button onClick={handleNext}>{currentIndex < groupedRecipes.length - 1 ? 'Next Recipe' : 'Finish Order'}</button>
            </div>
        </div>
    );
};

export default BaristaRecipe;