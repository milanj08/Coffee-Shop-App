import React, { useEffect, useState } from 'react';
import axios from 'axios';
import BackButton from '../components/backbutton';
import './accountingreport.css';
import { API_BASE_URL } from '../config';

export default function AccountingReport() {
    const [data, setData] = useState([]);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get(`${API_BASE_URL}accounting/`); 
                const transformedData = response.data.map((entry) => ({
                    ...entry,
                    timestamp: `${entry.day} ${entry.time}`,
                }));
                setData(transformedData);
            } catch (err) {
                setError('Error fetching data');
            }
        };

        fetchData();
    }, []);

    if (error) return <div>{error}</div>;

    return (
        <>
            <div className="report-page-container">
                <div className="back-button-container">
                    <BackButton endpoint="managerHome" />
                </div>

                <div className="report-content">
                    <h1 className="header">Accounting Report</h1>

                    <table className="accounting-table">
                        <thead>
                            <tr>
                                <th>Timestamp</th>
                                <th>Account Balance</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.length > 0 ? (
                                data.map((entry, index) => (
                                    <tr key={index}>
                                        <td>{entry.timestamp}</td>
                                        <td>${Number(entry.account_balance).toFixed(2)}</td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="2">No data available</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </>
    );
}
