import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/login'; 
import BaristaHome from './pages/baristaHome';
import BaristaRecipe from './pages/baristaRecipe';
import BaristaCompleted from './pages/baristaCompleted';
import ManagerHome from './pages/managerHome';
import Inventory from './pages/inventory';
import Employees from './pages/employees';
import EditEmployee from './pages/editemployees';
import AddEmployees from './pages/addemployee';
import { OrderProvider } from './OrderContext';

function App() {
  return (
    <>
    <OrderProvider>
      <Router>
          <Routes>
              <Route exact path = "/" element = { <Login /> }/>

              <Route path = "/baristaHome" element = { <BaristaHome /> }/>

              <Route path = "/baristaRecipe" element = { <BaristaRecipe /> }/>

              <Route path = "/baristaCompleted" element = { <BaristaCompleted /> }/>

              <Route path = "/managerHome" element = { <ManagerHome /> }/>

              <Route path = "/inventory" element = { <Inventory /> }/>

              <Route path = "/employees" element = { <Employees /> }/>

              <Route path = "/editEmployee" element = { <EditEmployee /> }/>

              <Route path = "/addEmployee" element = { <AddEmployees /> }/>

              {/* Redirect any unmatched routes to the login page */}
              <Route path = "*" element = { <Navigate to="/" /> }/>
              
          </Routes>
      </Router>
    </OrderProvider>
</>
  );
}

export default App;
