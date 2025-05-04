//Used to display the home page of the barista
import React, { useContext, useState } from "react";
import { OrderContext } from '../OrderContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './baristaHome.css';
import './login';
import './baristaRecipe';

const BaristaHome = () => {

    // Used to keep track of orders and order number
    const { setRecipes, orderNumber } = useContext(OrderContext);

    const navigate = useNavigate();

    // Log out button
    const handleLogOut = () => {
        navigate("/login")
    };

    // Tracks barista input
    const [orderItems, setOrderItems] = useState([
        { quantity: '', name: '' },
    ]);

    // Get input from text fields for order information
    const handleInputChange = (index, field, value) => {
        const updatedItems = [...orderItems];
        updatedItems[index][field] = value;

        // Save orders for later
        setOrderItems(updatedItems);
    };

    // Add additional entry to order field
    const handleAddItem = () => {
        setOrderItems([...orderItems, { quantity: '', name: '' }]);
    };

    // Remove entry from order field
    const handleRemoveItem = () => {
        setOrderItems(prevItems => prevItems.slice(0, -1));
    };

    // Check if the user has a payment method selected before proceeding
    const handlePay = async () => {
        if (paymentMethod.trim() === '') {
            // do not proceed if no payment method entered
            alert('Please enter a payment method before proceeding.');
            return;
        }
      
        // Used to store all recipes and their steps
        const allRecipes = [];
      
        
        for (const item of orderItems) {
            const name = item.name;
            const quantity = item.quantity;
    
            try {
                const response = await axios.get(`http://localhost:8000/api/recipes/?recipe_name=${encodeURIComponent(name)}`);
                const recipeData = response.data;
    
                if (recipeData.length === 0) {
                    // do not proceed if recipe cant be found in DB
                    alert(`No recipe found for ${name}`);
                    return;
                }
    
                // Add the recipe data to 'allRecipes' and tag it with an index
                for (let i = 0; i < quantity; i++) {
                    const indexedRecipeData = recipeData.map(recipe => ({
                        ...recipe,
                        // Add index to account for multiple orders of the same item
                        index: i + 1 
                    }));
                    allRecipes.push(...indexedRecipeData);
                }
            } catch (error) {
                console.error(`Error fetching recipe for ${name}:`, error);
                alert(`Failed to fetch recipe for ${name}`);
                return;
            }
        }
    
        if (allRecipes.length === 0) {
            alert("No valid recipes found.");
            return;
        }
    
        console.log("All Recipes:", allRecipes);
        setRecipes(allRecipes);
        navigate('/baristaRecipe');
    };

    const [paymentMethod, setPaymentMethod] = useState('');

    // Used to set date and time
    const now = new Date();
    const options = { weekday: 'long' }; // full weekday name
    const day = now.toLocaleDateString(undefined, options);
    const time = now.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });

    return (
        <div>
            { /* Header section, holds log out button and title */ }
            <div className="header-container">
                <button id = "logOutButton" onClick={handleLogOut}>LOG OUT</button>
                <h1 id = "mainTitle">Barista</h1>
            </div>

            { /* Holds labels, order field and payment row */ }
            <div className="body-container">

                { /* Order number */ }
                <div className="order-row">
                    <span id = "boxHeader">Order {String(orderNumber).padStart(2, '0')}</span>
                </div>

                { /* Day and Time */ }
                <div className="order-row" id = "secondRow">
                    <span className="labels">{day}</span>
                    <span className="labels">{time}</span>
                </div>

                { /* Order labels */ }
                <div className="order-row" id = "thirdRow">
                    <span className="labels">ITEM NO.</span>
                    <span className="labels">QUANTITY</span>
                    <span className="labels">ITEM NAME</span>
                </div>

                { /* Order field */ }
                <div className="ordered-items-container">
                    {orderItems.map((item, index) => (
                        <div className="item" key={index}>
                            <span className="labels">{index + 1}</span>
                            <input
                                type="number"
                                className="labels"
                                value={item.quantity}
                                onChange={(e) => handleInputChange(index, 'quantity', e.target.value)}
                                placeholder="0"
                            />
                            <input
                                type="text"
                                className="labels"
                                value={item.name}
                                onChange={(e) => handleInputChange(index, 'name', e.target.value)}
                                placeholder="Item Name"
                            />
                        </div>
                    ))}
                </div>

                { /* Add/remove row buttons*/ }
                <div className ="orderButtons">
                    <button onClick={handleAddItem}>Add Item</button>
                    <button onClick={handleRemoveItem}>Remove Item</button>
                </div>

                { /* pay button and payment method field */ }
                <div className="order-row" id="bottomRow">
                <button className="labels" id="payButton" onClick={handlePay}>PAY</button>
                    <input
                        type="text"
                        className="paymentField"
                        placeholder="Payment Method"
                        value={paymentMethod}
                        onChange={(e) => setPaymentMethod(e.target.value)}
                    />
                </div>
            </div>

        </div>
    );
};

export default BaristaHome;