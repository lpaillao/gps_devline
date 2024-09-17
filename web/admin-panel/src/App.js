import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import { ThemeProvider } from './contexts/ThemeContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './components/layout/Layout';
import LandingPage from './components/LandingPage';
import LoginPage from './components/LoginPage';
import RegisterPage from './components/RegisterPage';
import Dashboard from './components/dashboard/Dashboard';
import UserManagement from './components/users/UserManagement';
import VehicleManagement from './components/vehicles/VehicleManagement';
import AdminPanel from './components/admin/AdminPanel';
import GPSVehicleManagement from './components/gps/GPSVehicleManagement';
import MenuManagement from './components/admin/MenuManagement/MenuManagement';
import RoleManagement from './components/admin/RoleManagement/RoleManagement';
import RoleMenuAssociation from './components/admin/RoleMenuAssociation/RoleMenuAssociation';

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  return children;
};

const DynamicRoutes = () => {
  const { user } = useAuth();
  const [menuRoutes, setMenuRoutes] = useState([]);

  useEffect(() => {
    const fetchMenuRoutes = async () => {
      if (user && user.role_id) {
        try {
          const response = await axios.get(`http://localhost/devline_app/gps_devline/backend/index.php?action=getMenusByRoleId&roleId=${user.role_id}`, {
            withCredentials: true
          });
          if (response.data.success) {
            setMenuRoutes(response.data.menus);
          }
        } catch (error) {
          console.error('Error fetching menu routes:', error);
        }
      }
    };

    fetchMenuRoutes();
  }, [user]);

  const getComponentForRoute = (url) => {
    switch(url) {
      case '/dashboard': return Dashboard;
      case '/users': return UserManagement;
      case '/vehicles': return VehicleManagement;
      case '/admin': return AdminPanel;
      case '/gps-vehicle': return GPSVehicleManagement;
      case '/admin/menus': return MenuManagement;
      case '/admin/roles': return RoleManagement;
      case '/admin/role-menu': return RoleMenuAssociation;
      default: return () => <div>Page not found</div>;
    }
  };

  return (
    <Routes>
      {menuRoutes.map((route) => (
        <Route 
          key={route.id} 
          path={route.url} 
          element={React.createElement(getComponentForRoute(route.url))}
        />
      ))}
    </Routes>
  );
};

function App() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <Router>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route
              path="/*"
              element={
                <ProtectedRoute>
                  <Layout>
                    <DynamicRoutes />
                  </Layout>
                </ProtectedRoute>
              }
            />
          </Routes>
        </Router>
      </ThemeProvider>
    </AuthProvider>
  );
}

export default App;