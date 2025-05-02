import React, { createContext, useState } from "react";

export const OrderContext = createContext();

export const OrderProvider = ({ children }) => {
    const [orders, setOrders] = useState([]);
    const [orderNumber, setOrderNumber] = useState(1);
    return (
        <OrderContext.Provider value={{ orders, setOrders, orderNumber, setOrderNumber }}>
            {children}
        </OrderContext.Provider>
    );
};

// File used to keep track of order number and customer orders across barista pages