import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import { ThemeProvider } from './contexts/ThemeContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { API_BASE_URL } from './config';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
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
import EmpresaManagement from './components/empresas/EmpresaManagement';
import DispositivoGPSManagement from './components/dispositivos/DispositivoGPSManagement';
import TipoGPSManagement from './components/tiposgps/TipoGPSManagement';
import UbicacionManagement from './components/ubicaciones/UbicacionManagement';
import AsignacionDispositivoManagement from './components/asignaciones/AsignacionDispositivoManagement';
import ControlZonesManagement from './components/zona/ControlZonesManagement';



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
          const response = await axios.get(`${API_BASE_URL}?action=getMenusByRoleId&roleId=${user.role_id}`, {
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
      case '/empresas': return EmpresaManagement;
      case '/dispositivos': return DispositivoGPSManagement;
      case '/tipos-gps': return TipoGPSManagement;
      case '/ubicaciones': return UbicacionManagement;
      case '/asignaciones': return AsignacionDispositivoManagement;
      case '/control-zones': return ControlZonesManagement;
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
                  <ToastContainer position="top-right" autoClose={3000} />
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