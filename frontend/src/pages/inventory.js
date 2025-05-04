import React, { useState } from "react";
import { useNavigate } from 'react-router-dom';
import './managerHome';
import './inventory.css';


// 10% tax rate
const taxRate = 0.10;


// Just for designing until real data comes in
const tempInventory = [
    { unit: "001", name: "Milk", quantity: "57(oz)", price: 2.99},
    { unit: "002", name: "Sugar", quantity: "33(lbs)", price: 2.00}
];


const Inventory = () => {
    const navigate = useNavigate();


    // Fills an array with zeros based on the amount of items found in tempInventory
    const [quantities, setQuantities] = useState(Array(tempInventory.length).fill(0));
   
    // Sets inital quantities to zero
    const [order, setOrder] = useState([]);


    // After pressing the back button sends you to the manager home page
    const handleBackClick = () => {
        navigate("/managerHome");
    };


    // Updates quanity in our text box when users press the + or - button
    const updateQuantity = (index, delta) => {
        const newQuantities = [...quantities];
        newQuantities[index] = Math.max(0, newQuantities[index] + delta);
        setQuantities(newQuantities);
    };
   
    // Handles when a user manually changes the quantity
    const handleInputChange = (index, value) => {
        // clones current array to avoid updating it directly
        const newQuantities = [...quantities];
        // Updates quantities based on typed value or 0
        newQuantities[index] = parseInt(value) || 0;
        setQuantities(newQuantities);
    };


    //Adds items to the order summary
    const handleAddToOrder = (item, quantity) => {
        // Updates order summary using the previous state
        setOrder((prev) => {
            // Check if an item already items
            const existing = prev.find(entry => entry.name === item.name);


            // If it exists, update its quantity if needed otherwise keep it the same
            if (existing) {
                return prev.map(entry =>
                    entry.name === item.name
                        ? { ...entry, quantity: entry.quantity + quantity}
                        : entry
                );
            }
            return [...prev, {...item, quantity}];
        });
    };




    let subtotal = 0;
    for (let i = 0; i < order.length; i++){
        // Calculates the total from each item ordered
        subtotal += order[i].price * order[i].quantity;
    }


    const tax = subtotal * taxRate;
    const total = subtotal + tax;
   
    return (
        <div>
            { /* Header section, holds back button and title */ }
            <div className="header-container">
                <button id="backButton" onClick={handleBackClick}>BACK</button>
                <h1 id = "mainTitle">Inventory Management</h1>
            </div>


            { /* Holds inventory items and order summary */ }
            <div className="content-container">
                { /* Inventory Items */ }
                <div className="inventory-container">
                    { /* Iventory labels */ }
                    <div className="inventory-label-container">
                        <span className="labels">Unit</span>
                        <span className="labels">Item Name</span>
                        <span className="labels">Quantity</span>
                        <span className="labels">Price</span>
                    </div>


                    { /* Iventory Items */ }
                    { /* Map through each item to fill rows with item data */ }
                    {tempInventory.map((item, index) => (
                            <div key={index} className="inventory-row">
                                <span className="itemContent">{item.unit}</span>
                                <span className="itemContent">{item.name}</span>
                                <span className="itemContent">{item.quantity}</span>
                                <span className="itemContent">${item.price.toFixed(2)}</span>
                               
                                { /* Increment and decrement buttons */ }
                                <button className="itemButton" onClick={() => updateQuantity(index, 1)}>+</button>
                                <button className="itemButton" onClick={() => updateQuantity(index, -1)}>-</button>
                               
                                { /* Text box for updating quantity manually */ }
                                <input
                                    type="number"
                                    value={quantities[index]}
                                    onChange={(e) => handleInputChange(index, e.target.value)}
                                    style={{ width: '6vw' }}
                                />


                                <button className="addButton" onClick={() => handleAddToOrder(item, quantities[index])}>Add</button>
                            </div>
                    ))}
                </div>


                { /* Order Summary */ }
                <div className="order-container">
                    <h3>Order Summary</h3>


                    { /* Holds summary labels */ }
                    <div className="summaryHeader">
                        <span className="summaryLabels">Item</span>
                        <span className="summaryLabels">Quantity</span>
                        <span className="summaryLabels">Cost</span>
                    </div>
               
                    { /* Map through each item to fill rows with items to be ordered */ }
                    {order.map((item, idx) => (
                        <div key={idx} className="summaryHeader">
                            <span>{item.name}</span>
                            <span>{item.quantity}</span>
                            <span>${(item.price * item.quantity).toFixed(2)}</span>
                        </div>
                    ))}


                    { /* straight line to split items and cost */ }
                    <div style={{ height: '2px', backgroundColor: 'black', width: '100%', margin: '20px 0' }}></div>
                   
                    <div>Subtotal: ${subtotal.toFixed(2)}</div>
                    <div>Tax: ${tax.toFixed(2)}</div>
                    <div>Total: ${total.toFixed(2)}</div>
                    <div className="order-buttons">
                        <button id="orderButton">ORDER</button>
                        <button id="cancelButton" onClick={() => setOrder([])}>CANCEL</button>
                    </div>
                </div>
            </div>
        </div>
    );
};


export default Inventory;
