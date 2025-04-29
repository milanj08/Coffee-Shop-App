import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './login'; 
import bHome from './baristaHome';
import ManagerHome from './managerHome';
import Inventory from './inventory';

function App() {
  return (
    <>
    <Router>
        <Routes>
            <Route exact path = "/" element = { <Login /> }/>

            <Route path = "/baristaHome" element = { <bHome /> }/>

            <Route path = "/managerHome" element = { <ManagerHome /> }/>

            <Route path = "/inventory" element = { <Inventory /> }/>

            {/* Redirect any unmatched routes to the login page */}
            <Route path = "*" element = { <Navigate to="/" /> }/>
            
        </Routes>
    </Router>
</>
  );
}

export default App;
