import React, { createContext, useState } from "react";

export const OrderContext = createContext();

export const OrderProvider = ({ children }) => {
    const [orderNumber, setOrderNumber] = useState(1);
    const [recipes, setRecipes] = useState([]);
    const [inventoryItems, setInventoryItems] = useState([]);

    return (
        <OrderContext.Provider value={{ inventoryItems, setInventoryItems, orderNumber, setOrderNumber, recipes, setRecipes }}>
            {children}
        </OrderContext.Provider>
    );
};

// File used to keep track of order number and customer orders across barista pages