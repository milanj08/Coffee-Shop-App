//Used to display the home page of the barista
import React from "react";
import { useNavigate } from 'react-router-dom';
import './baristaHome.css';
import './login';


const BaristaHome = () => {
    const navigate = useNavigate();

    const handleLogOut = () => {
        navigate("/login")
    };

    
    return (
        <div>
            <div className="header-container">
                <button id = "logOutButton" onClick={handleLogOut}>LOG OUT</button>
                <h1 id = "mainTitle">Barista</h1>
            </div>

            <div className="order-container">
                <div className="order-row">
                    <span id = "boxHeader">Order #</span>
                </div>

                <div className="order-row" id = "secondRow">
                    <span class="labels">DAY</span>
                    <span class="labels">TIME</span>
                </div>

                <div className="order-row" id = "thirdRow">
                    <span class="labels">ITEM NO.</span>
                    <span class="labels">QUANTITY</span>
                    <span class="labels">ITEM NAME</span>
                </div>

                <div className="ordered-items-container">
                    <div class = "item">
                        <span class="labels">1</span>
                        <span class="labels">2</span>
                        <span class="labels">Mocha Latte</span>
                    </div>
                    <div class = "item">
                        <span class="labels">2</span>
                        <span class="labels">2</span>
                        <span class="labels">Mocha Latte</span>
                    </div>
                    <div class = "item">
                        <span class="labels">3</span>
                        <span class="labels">2</span>
                        <span class="labels">Mocha Latte</span>
                    </div>
                    <div class = "item">
                        <span class="labels">4</span>
                        <span class="labels">2</span>
                        <span class="labels">Mocha Latte</span>
                    </div>
                </div>

                <div className="order-row" id = "bottomRow">
                    <button class="labels" id="payButton">PAY</button>
                    <span class="labels">PAYMENT METHOD</span>
                </div>
            </div>

        </div>
    );
};

export default BaristaHome;