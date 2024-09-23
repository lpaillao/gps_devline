import React, { useState, useEffect } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import axios from 'axios';
import { API_BASE_URL } from '../../config';

const DispositivoGPSForm = ({ dispositivo, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    imei: '',
    modelo: '',
    marca: '',
    tipo_gps_id: '',
  });
  const [tiposGPS, setTiposGPS] = useState([]);
  const { text, bg } = useTheme();

  useEffect(() => {
    if (dispositivo) {
      setFormData(dispositivo);
    }
    fetchTiposGPS();
  }, [dispositivo]);

  const fetchTiposGPS = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}?action=getAllTiposGPS`);
      if (response.data.success) {
        setTiposGPS(response.data.tipos);
      }
    } catch (error) {
      console.error('Error fetching tipos GPS:', error);
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
        {dispositivo ? 'Edit Dispositivo GPS' : 'Add Dispositivo GPS'}
      </h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="imei" className={`block ${text.secondary} font-medium mb-1`}>
            IMEI
          </label>
          <input
            type="text"
            id="imei"
            name="imei"
            value={formData.imei}
            onChange={handleChange}
            required
            className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary}`}
          />
        </div>
        <div>
          <label htmlFor="modelo" className={`block ${text.secondary} font-medium mb-1`}>
            Modelo
          </label>
          <input
            type="text"
            id="modelo"
            name="modelo"
            value={formData.modelo}
            onChange={handleChange}
            required
            className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary}`}
          />
        </div>
        <div>
          <label htmlFor="marca" className={`block ${text.secondary} font-medium mb-1`}>
            Marca
          </label>
          <input
            type="text"
            id="marca"
            name="marca"
            value={formData.marca}
            onChange={handleChange}
            required
            className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary}`}
          />
        </div>
        <div>
          <label htmlFor="tipo_gps_id" className={`block ${text.secondary} font-medium mb-1`}>
            Tipo GPS
          </label>
          <select
            id="tipo_gps_id"
            name="tipo_gps_id"
            value={formData.tipo_gps_id}
            onChange={handleChange}
            required
            className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary}`}
          >
            <option value="">Select a type</option>
            {tiposGPS.map((tipo) => (
              <option key={tipo.id} value={tipo.id}>
                {tipo.nombre}
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
            {dispositivo ? 'Update' : 'Add'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default DispositivoGPSForm;