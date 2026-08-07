import React, { useEffect, useState } from 'react';
import api, { readApiError } from '../api';
import BackButton from '../components/backbutton';
import './accountingreport.css';
import { API_BASE_URL } from '../config';

export default function AccountingReport() {
    const [data, setData] = useState([]);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await api.get(`${API_BASE_URL}accounting/`); 
                const transformedData = response.data.map((entry) => ({
                    ...entry,
                    timestamp: `${entry.day} ${entry.time}`,
                }));
                setData(transformedData);
            } catch (err) {
                // readApiError surfaces the server's own message - a 403 now
                // reads "This action is restricted to managers." instead of a
                // generic failure that could mean anything.
                setError(readApiError(err, 'Error fetching data'));
            }
        };

        fetchData();
    }, []);

    // There used to be an early `if (error) return <div>{error}</div>` here.
    // It rendered the message INSTEAD of the page - including instead of the
    // back button - so any failure left you on a dead screen with no way out
    // except the browser's back button.
    //
    // An error state is still a state of this page, not a replacement for it.
    // Chrome and layout stay; only the content area changes.
    return (
        <>
            <div className="report-page-container">
                <div className="back-button-container">
                    <BackButton endpoint="managerHome" />
                </div>

                <div className="report-content">
                    <h1 className="header">Accounting Report</h1>

                    {error && <p className="report-error">{error}</p>}

                    {!error && <table className="accounting-table">
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
                    </table>}
                </div>
            </div>
        </>
    );
}
