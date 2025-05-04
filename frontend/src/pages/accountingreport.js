import React from 'react';
import BackButton from '../components/backbutton';
import './accountingreport.css';

export default function AccountingReport() {
    const dummyData = [
        { timestamp: '2025-05-01 10:00:00', balance: '$5,000.00' },
        { timestamp: '2025-05-02 14:30:00', balance: '$5,500.00' },
        { timestamp: '2025-05-03 09:15:00', balance: '$6,000.00' },
    ];

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
                                <th>Balance</th>
                            </tr>
                        </thead>
                        <tbody>
                            {dummyData.map((entry, index) => (
                                <tr key={index}>
                                    <td>{entry.timestamp}</td>
                                    <td>{entry.balance}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </>
    );
}
