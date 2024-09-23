import React, { useState, useEffect } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import axios from 'axios';
import { API_BASE_URL } from '../../config';

const AsignacionDispositivoForm = ({ asignacion, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    dispositivo_gps_id: '',
    usuario_id: '',
    empresa_id: '',
  });
  const [dispositivos, setDispositivos] = useState([]);
  const [usuarios, setUsuarios] = useState([]);
  const [empresas, setEmpresas] = useState([]);
  const { text, bg } = useTheme();

  useEffect(() => {
    if (asignacion) {
      setFormData(asignacion);
    }
    fetchDispositivos();
    fetchUsuarios();
    fetchEmpresas();
  }, [asignacion]);

  const fetchDispositivos = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}?action=getAllDispositivosGPS`);
      if (response.data.success) {
        setDispositivos(response.data.dispositivos);
      }
    } catch (error) {
      console.error('Error fetching dispositivos:', error);
    }
  };

  const fetchUsuarios = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}?action=getAllUsers`);
      if (response.data.success) {
        setUsuarios(response.data.users);
      }
    } catch (error) {
      console.error('Error fetching usuarios:', error);
    }
  };

  const fetchEmpresas = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}?action=getAllEmpresas`);
      if (response.data.success) {
        setEmpresas(response.data.empresas);
      }
    } catch (error) {
      console.error('Error fetching empresas:', error);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="w-full lg:w-1/3">
      <h2 className={`text-xl font-semibold ${text.secondary} mb-4`}>
        {asignacion ? 'Edit Asignación' : 'Add Asignación'}
      </h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="dispositivo_gps_id" className={`block ${text.secondary} font-medium mb-1`}>
            Dispositivo GPS
          </label>
          <select
            id="dispositivo_gps_id"
            name="dispositivo_gps_id"
            value={formData.dispositivo_gps_id}
            onChange={handleChange}
            required
            className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary}`}
          >
            <option value="">Select a device</option>
            {dispositivos.map((dispositivo) => (
              <option key={dispositivo.id} value={dispositivo.id}>
                {dispositivo.imei}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="usuario_id" className={`block ${text.secondary} font-medium mb-1`}>
            Usuario
          </label>
          <select
            id="usuario_id"
            name="usuario_id"
            value={formData.usuario_id}
            onChange={handleChange}
            className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary}`}
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
            Empresa
          </label>
          <select
            id="empresa_id"
            name="empresa_id"
            value={formData.empresa_id}
            onChange={handleChange}
            className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary}`}
          >
            <option value="">Select a company</option>
            {empresas.map((empresa) => (
              <option key={empresa.id} value={empresa.id}>
                {empresa.nombre}
              </option>
            ))}
          </select>
        </div>
        <div className="flex justify-end space-x-2">
          <button
            type="button"
            onClick={onCancel}
            className={`px-4 py-2 rounded-md ${bg.secondary} ${text.primary}`}
          >
            Cancel
          </button>
          <button
            type="submit"
            className={`px-4 py-2 rounded-md ${bg.primary} text-white`}
          >
            {asignacion ? 'Update' : 'Add'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AsignacionDispositivoForm;