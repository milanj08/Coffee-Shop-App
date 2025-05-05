import React, { useState, useEffect } from "react";
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './managerHome';
import './inventory.css';


// 10% tax rate
const taxRate = 0.10;

const Inventory = () => {
    const navigate = useNavigate();
   
    const [inventoryItems, setInventoryItems] = useState([]);

    const [quantities, setQuantities] = useState([]);

    // Sets inital quantities to zero
    const [order, setOrder] = useState([]);

    const [accountBalance, setAccountBalance] = useState("0.00");


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

    const handleOrder = async () => {
        // Saving the items we want to order and how many into orderItems
        const orderItems = order.map(item => ({
            name: item.name,
            quantity: item.quantity
        }));
    
        console.log("Sending order:", orderItems);
    
        try {
            // Sends a message to the backend and prints the reponse to console
            const response = await axios.patch('http://localhost:8000/api/inventory/update/', { order: orderItems }, {headers: {'Content-Type': 'application/json'}});
            console.log(response.data);

            // Used to update our accounting balance based on how much we purchased
            const accountBalanceResponse = await axios.post('http://localhost:8000/api/accounting/purchase/', { total_purchase: total }, {headers: {'Content-Type': 'application/json'}});
            console.log(accountBalanceResponse.data);

            // Refresh our inventory and balance to reflect our purchase
            await fetchInventory(); 
            await fetchAccountBalance();

            // Clears current order
            setOrder([]);            
        } catch (error) {
            console.error("Error updating inventory:", error);
        }
    };
    

    // Receive all inventory found in database
    const fetchInventory = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/inventory/');
            setInventoryItems(response.data);
            setQuantities(Array(response.data.length).fill(0));
        } catch (error) {
            console.error("Failed to fetch inventory data:", error);
        }
    };

    const fetchAccountBalance = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/accounting/check/');
            setAccountBalance(response.data.account_balance);
        } catch (error) {
            console.error("Failed to fetch account balance:", error);
        }
    };

    // On page load: fetch current inventory
    useEffect(() => {
        fetchInventory();
        fetchAccountBalance();
    }, []);

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
                    {inventoryItems.map((item, index) => (
                            <div key={index} className="inventory-row">
                                <span className="itemContent">{item.unit}</span>
                                <span className="itemContent">{item.name}</span>
                                <span className="itemContent">{item.quantity}</span>
                                <span className="itemContent">${item.price}</span>
                               
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
                    <h3>Current Balance: ${accountBalance}</h3>
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
                        <button id="orderButton" onClick={handleOrder}>ORDER</button>
                        <button id="cancelButton" onClick={() => setOrder([])}>CANCEL</button>
                    </div>
                </div>
            </div>
        </div>
    );
};


export default Inventory;
