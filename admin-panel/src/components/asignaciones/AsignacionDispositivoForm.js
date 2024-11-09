import React, { useState, useEffect } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import axios from 'axios';
import config from '../../config/config';

const AsignacionDispositivoForm = ({ asignacion, onSubmit, onCancel, loading }) => {
  const [formData, setFormData] = useState({
    dispositivo_gps_id: '',
    usuario_id: '',
    empresa_id: '',
  });
  const [dispositivos, setDispositivos] = useState([]);
  const [usuarios, setUsuarios] = useState([]);
  const [empresas, setEmpresas] = useState([]);
  const [loadingResources, setLoadingResources] = useState(true);
  const [error, setError] = useState(null);
  const { text, bg } = useTheme();

  useEffect(() => {
    if (asignacion) {
      setFormData(asignacion);
    }
    fetchInitialData();
  }, [asignacion]);

  const handleResourceError = (error, resource) => {
    console.error(`Error fetching ${resource}:`, error);
    return `Error loading ${resource}. ${error.response?.data?.message || ''}`;
  };

  const fetchInitialData = async () => {
    setLoadingResources(true);
    setError(null);
    
    try {
      // Realizamos las peticiones en paralelo pero manejamos los errores individualmente
      const results = await Promise.allSettled([
        fetchDispositivos(),
        fetchUsuarios(),
        fetchEmpresas()
      ]);

      // Verificamos si alguna petición falló
      const errors = results
        .filter(result => result.status === 'rejected')
        .map(result => result.reason);

      if (errors.length > 0) {
        setError(errors.join('\n'));
      }
    } catch (error) {
      setError('Error loading form data. Please try again.');
    } finally {
      setLoadingResources(false);
    }
  };

  const fetchDispositivos = async () => {
    try {
      const response = await axios.get(`${config.api.baseURL}/api/dispositivos`);
      if (response.data.success) {
        setDispositivos(response.data.dispositivos);
      } else {
        throw new Error(response.data.message || 'Failed to fetch devices');
      }
    } catch (error) {
      throw handleResourceError(error, 'dispositivos');
    }
  };

  const fetchUsuarios = async () => {
    try {
      const response = await axios.get(`${config.api.baseURL}/api/users`);
      // Manejamos tanto el formato {success: true, users: [...]} como el array directo
      const users = Array.isArray(response.data) 
        ? response.data 
        : response.data.users || [];
        
      // Verificamos que tengamos los campos necesarios en los usuarios
      if (users.length > 0 && users.every(user => user.id && user.username)) {
        setUsuarios(users);
      } else {
        console.warn('Users data structure might be incorrect:', users);
        setUsuarios([]);
        throw new Error('Invalid user data structure');
      }
    } catch (error) {
      throw handleResourceError(error, 'usuarios');
    }
  };

  const fetchEmpresas = async () => {
    try {
      const response = await axios.get(`${config.api.baseURL}/api/empresas`);
      if (response.data.success && response.data.empresas) {
        setEmpresas(response.data.empresas);
      } else {
        throw new Error(response.data.message || 'Failed to fetch companies');
      }
    } catch (error) {
      throw handleResourceError(error, 'empresas');
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    
    setFormData(prev => {
      const newData = { ...prev, [name]: value };
      
      // Lógica de exclusión mutua entre usuario y empresa
      if (name === 'usuario_id' && value) {
        newData.empresa_id = '';
      } else if (name === 'empresa_id' && value) {
        newData.usuario_id = '';
      }
      
      return newData;
    });

    if (error) setError(null);
  };

  const validateForm = () => {
    if (!formData.dispositivo_gps_id) {
      return 'Dispositivo GPS is required';
    }
    if (!formData.usuario_id && !formData.empresa_id) {
      return 'Either Usuario or Empresa must be selected';
    }
    if (formData.usuario_id && formData.empresa_id) {
      return 'Cannot assign to both Usuario and Empresa';
    }
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    try {
      await onSubmit(formData);
    } catch (error) {
      setError(error.response?.data?.message || 'Error submitting form. Please try again.');
    }
  };

  if (loadingResources) {
    return (
      <div className="w-full lg:w-1/3 flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div className="w-full lg:w-1/3">
      <h2 className={`text-xl font-semibold ${text.secondary} mb-4`}>
        {asignacion ? 'Edit Asignación' : 'Add Asignación'}
      </h2>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md whitespace-pre-line">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="dispositivo_gps_id" className={`block ${text.secondary} font-medium mb-1`}>
            Dispositivo GPS {dispositivos.length === 0 && '(No devices available)'}
          </label>
          <select
            id="dispositivo_gps_id"
            name="dispositivo_gps_id"
            value={formData.dispositivo_gps_id}
            onChange={handleChange}
            className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary} ${
              error && !formData.dispositivo_gps_id ? 'border-red-500' : ''
            }`}
            disabled={loading || dispositivos.length === 0}
          >
            <option value="">Select a device</option>
            {dispositivos.map((dispositivo) => (
              <option key={dispositivo.id} value={dispositivo.id}>
                {dispositivo.imei} - {dispositivo.modelo}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="usuario_id" className={`block ${text.secondary} font-medium mb-1`}>
            Usuario {usuarios.length === 0 && '(No users available)'}
          </label>
          <select
            id="usuario_id"
            name="usuario_id"
            value={formData.usuario_id}
            onChange={handleChange}
            className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary} ${
              error && !formData.usuario_id && !formData.empresa_id ? 'border-red-500' : ''
            }`}
            disabled={loading || formData.empresa_id || usuarios.length === 0}
          >
            <option value="">Select a user</option>
            {usuarios.map((usuario) => (
              <option key={usuario.id} value={usuario.id}>
                {usuario.username}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="empresa_id" className={`block ${text.secondary} font-medium mb-1`}>
            Empresa {empresas.length === 0 && '(No companies available)'}
          </label>
          <select
            id="empresa_id"
            name="empresa_id"
            value={formData.empresa_id}
            onChange={handleChange}
            className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary} ${
              error && !formData.usuario_id && !formData.empresa_id ? 'border-red-500' : ''
            }`}
            disabled={loading || formData.usuario_id || empresas.length === 0}
          >
            <option value="">Select a company</option>
            {empresas.map((empresa) => (
              <option key={empresa.id} value={empresa.id}>
                {empresa.nombre}
              </option>
            ))}
          </select>
        </div>

        <div className="flex justify-end space-x-2 pt-4">
          <button
            type="button"
            onClick={onCancel}
            className={`px-4 py-2 rounded-md ${bg.secondary} ${text.primary} 
              hover:opacity-80 transition-opacity`}
            disabled={loading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className={`px-4 py-2 rounded-md ${bg.primary} text-white 
              hover:opacity-90 transition-opacity
              ${loading || loadingResources ? 'opacity-50 cursor-not-allowed' : ''}`}
            disabled={loading || loadingResources}
          >
            {loading ? 'Processing...' : asignacion ? 'Update' : 'Add'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AsignacionDispositivoForm;