import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/login'; 
import baristaHome from './pages/baristaHome';
import ManagerHome from './pages/managerHome';
import Inventory from './pages/inventory';
import Employees from './pages/employees';

function App() {
  return (
    <>
    <Router>
        <Routes>
            <Route exact path = "/" element = { <Login /> }/>

            <Route path = "/baristaHome" element = { <baristaHome /> }/>

            <Route path = "/managerHome" element = { <ManagerHome /> }/>

            <Route path = "/inventory" element = { <Inventory /> }/>

            <Route path = "/employees" element = { <Employees /> }/>

            {/* Redirect any unmatched routes to the login page */}
            <Route path = "*" element = { <Navigate to="/" /> }/>
            
        </Routes>
    </Router>
</>
  );
}

export default App;
