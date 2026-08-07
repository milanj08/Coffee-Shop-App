//Used to display the home page of the barista
import React, { useContext, useEffect, useState } from "react";
import { OrderContext } from '../OrderContext';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { clearSession } from '../auth';
import './baristaHome.css';
import './login';
import './baristaRecipe';
import { API_BASE_URL } from '../config';

const BaristaHome = () => {

    // Used to keep track of orders and order number
    const { setRecipes, orderNumber } = useContext(OrderContext);

    const navigate = useNavigate();

    // Log out button.
    //
    // Deletes the token server-side before clearing it locally. DRF tokens
    // never expire on their own, so clearing localStorage alone would leave a
    // key that still works for anyone who copied it.
    const handleLogOut = async () => {
        try {
            await api.post(`${API_BASE_URL}auth/logout/`);
        } catch (error) {
            // Already invalid, or the server is down. Sign out locally either
            // way - refusing to log someone out is worse than a stale token.
            console.error('Logout request failed:', error);
        }
        clearSession();
        navigate('/');
    };

    // Tracks barista input
    const [orderItems, setOrderItems] = useState([
        { quantity: '', name: '' },
    ]);

    // Menu prices, keyed by lowercased drink name.
    //
    // This is for DISPLAY ONLY - so the barista can tell the customer what they
    // owe. The server still prices the sale from its own Menu table when the
    // order is submitted, and its number is the one that gets charged. If the
    // two ever disagree, the server is right and this is stale.
    const [menuPrices, setMenuPrices] = useState({});

    // Fetched once when the page loads rather than per drink per order.
    useEffect(() => {
        api.get(`${API_BASE_URL}menu/`)
            .then(response => {
                const prices = {};
                for (const drink of response.data) {
                    // DRF serializes DecimalField as a string, so parse it.
                    prices[drink.name.toLowerCase()] = parseFloat(drink.price);
                }
                setMenuPrices(prices);
            })
            .catch(error => console.error('Failed to load menu prices:', error));
    }, []);

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

        // For each item the customer ordered, get the steps for each recipe.
        // Pricing is not done here - the server computes the total from
        // Menu.price so a client cannot name its own amount.
        for (const item of orderItems) {
            const name = item.name;
            const quantity = item.quantity;
    
            try {
                const response = await api.get(`${API_BASE_URL}recipes/?recipe_name=${encodeURIComponent(name)}`);
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


        // Record sales in the backend. The server timestamps the sale and
        // prices it from the menu, so neither is sent from here.
        const salePayload = {
            payment_method: paymentMethod.toLowerCase(),
            items: orderItems.map(item => ({
                drink_name: item.name,
                quantity: parseInt(item.quantity, 10),
            })),
        };

        console.log("Sale payload:", salePayload);
    
        try {
            const saleMade = await api.post(`${API_BASE_URL}sales/record-sale`, salePayload);
            console.log("SALE MADE:", saleMade);
        } catch (error) {
            console.error(`Failed to record sale:`, error);
            alert('Failed to record sale');
            return;
        }
            
        console.log("All Recipes:", allRecipes);
        setRecipes(allRecipes);
        navigate('/baristaRecipe');
    };

    const [paymentMethod, setPaymentMethod] = useState('');

    // Running total, recomputed on every render from the current order.
    // A name that isn't on the menu is flagged rather than silently counted as
    // free - a typo should not quietly undercharge the customer.
    let orderTotal = 0;
    let hasUnknownItem = false;

    for (const item of orderItems) {
        const name = item.name.trim().toLowerCase();
        if (name === '') continue;

        const unitPrice = menuPrices[name];
        if (unitPrice === undefined) {
            hasUnknownItem = true;
            continue;
        }

        orderTotal += unitPrice * (parseInt(item.quantity, 10) || 0);
    }

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
                    <span className="labels" id="orderTotal">
                        {hasUnknownItem
                            ? 'ITEM NOT ON MENU'
                            : `TOTAL $${orderTotal.toFixed(2)}`}
                    </span>
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