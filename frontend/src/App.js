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
import AccountingReport from './pages/accountingreport';
import RequireRole from './components/RequireRole';
import { OrderProvider } from './OrderContext';

// Every route except the login page is wrapped in RequireRole. Navigating
// straight to /managerHome while signed out, or while signed in as a barista,
// now redirects rather than rendering a screen full of failed requests.
//
// Managers are allowed onto the barista screens because a manager covering the
// counter is a real thing. Baristas are not allowed onto manager screens.
//
// This only controls what the UI offers. The API checks the role again on
// every request - see cafe/permissions.py.
const ANY_EMPLOYEE = ['barista', 'manager'];
const MANAGER_ONLY = ['manager'];

function App() {
  return (
    <>
    <OrderProvider>
      <Router>
          <Routes>
              <Route exact path = "/" element = { <Login /> }/>

              <Route path = "/baristaHome" element = {
                <RequireRole allow={ANY_EMPLOYEE}><BaristaHome /></RequireRole>
              }/>

              <Route path = "/baristaRecipe" element = {
                <RequireRole allow={ANY_EMPLOYEE}><BaristaRecipe /></RequireRole>
              }/>

              <Route path = "/baristaCompleted" element = {
                <RequireRole allow={ANY_EMPLOYEE}><BaristaCompleted /></RequireRole>
              }/>

              <Route path = "/managerHome" element = {
                <RequireRole allow={MANAGER_ONLY}><ManagerHome /></RequireRole>
              }/>

              <Route path = "/inventory" element = {
                <RequireRole allow={MANAGER_ONLY}><Inventory /></RequireRole>
              }/>

              <Route path = "/employees" element = {
                <RequireRole allow={MANAGER_ONLY}><Employees /></RequireRole>
              }/>

              <Route path = "/editEmployee" element = {
                <RequireRole allow={MANAGER_ONLY}><EditEmployee /></RequireRole>
              }/>

              <Route path = "/addEmployee" element = {
                <RequireRole allow={MANAGER_ONLY}><AddEmployees /></RequireRole>
              }/>

              <Route path = "/reports" element = {
                <RequireRole allow={MANAGER_ONLY}><AccountingReport/></RequireRole>
              }/>

              {/* Redirect any unmatched routes to the login page */}
              <Route path = "*" element = { <Navigate to="/" /> }/>

          </Routes>
      </Router>
    </OrderProvider>
</>
  );
}

export default App;
