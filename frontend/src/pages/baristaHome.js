//Used to display the home page of the barista
import React, { useContext, useState } from "react";
import { OrderContext } from '../OrderContext';
import { useNavigate } from 'react-router-dom';
import './baristaHome.css';
import './login';
import './baristaRecipe';

const BaristaHome = () => {

    // Used to keep track of orders and order number
    const { setOrders, orderNumber } = useContext(OrderContext);

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
    const handlePay = () => {
        if (paymentMethod.trim() === '') {
          alert('Please enter a payment method before proceeding.');
          return; // do not proceed
        }
        // Saves current order
        setOrders(orderItems);
        // Proceed to the recipe page
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
                    <span class="labels">{day}</span>
                    <span class="labels">{time}</span>
                </div>

                { /* Order labels */ }
                <div className="order-row" id = "thirdRow">
                    <span class="labels">ITEM NO.</span>
                    <span class="labels">QUANTITY</span>
                    <span class="labels">ITEM NAME</span>
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