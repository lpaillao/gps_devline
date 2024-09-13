import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import Layout from './components/layout/Layout';
import Dashboard from './components/dashboard/Dashboard';
import UserManagement from './components/users/UserManagement';
import VehicleManagement from './components/vehicles/VehicleManagement';
import AdminPanel from './components/admin/AdminPanel';
import GPSVehicleManagement from './components/gps/GPSVehicleManagement';

function App() {
  return (
    <ThemeProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/users" element={<UserManagement />} />
            <Route path="/vehicles" element={<VehicleManagement />} />
            <Route path="/admin" element={<AdminPanel />} />
            <Route path="/gps-vehicle" element={<GPSVehicleManagement />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;