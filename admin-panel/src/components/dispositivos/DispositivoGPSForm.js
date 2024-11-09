import React, { useState, useEffect } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import axios from 'axios';
import config from '../../config/config';
const DispositivoGPSForm = ({ dispositivo, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    imei: '',
    modelo: '',
    marca: '',
    tipo_gps_id: '',
  });
  const [tiposGPS, setTiposGPS] = useState([]);
  const [connectedIMEIs, setConnectedIMEIs] = useState([]);
  const [filteredIMEIs, setFilteredIMEIs] = useState([]);
  const [isManualIMEI, setIsManualIMEI] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { text, bg } = useTheme();

  useEffect(() => {
    if (dispositivo) {
      setFormData(dispositivo);
    }
    fetchInitialData();
  }, [dispositivo]);

  const fetchInitialData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchTiposGPS(),
        fetchConnectedIMEIs()
      ]);
    } catch (error) {
      setError('Error loading initial data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchTiposGPS = async () => {
    try {
      const response = await axios.get(`${config.api.baseURL}/api/tipos-gps`);
      if (response.data.success) {
        setTiposGPS(response.data.tipos);
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.error('Error fetching tipos GPS:', error);
      throw error;
    }
  };

  const fetchConnectedIMEIs = async () => {
    try {
      const response = await axios.get(`${config.api.baseURL}/api/gps/connected_devices`);
      if (Array.isArray(response.data)) {
        setConnectedIMEIs(response.data);
        setFilteredIMEIs(response.data);
      }
    } catch (error) {
      console.error('Error fetching connected IMEIs:', error);
      throw error;
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    if (name === 'imei') {
      filterIMEIs(value);
    }

    // Clear error when user starts typing
    if (error) {
      setError(null);
    }
  };

  const filterIMEIs = (value) => {
    if (!value.trim()) {
      setFilteredIMEIs(connectedIMEIs);
      return;
    }
    const filtered = connectedIMEIs.filter(imei => 
      imei.toLowerCase().includes(value.toLowerCase())
    );
    setFilteredIMEIs(filtered);
  };

  const handleIMEISelect = (imei) => {
    setFormData(prev => ({ ...prev, imei }));
    setFilteredIMEIs([]);
  };

  const validateForm = () => {
    if (!formData.imei.trim()) return 'IMEI is required';
    if (!formData.modelo.trim()) return 'Model is required';
    if (!formData.marca.trim()) return 'Brand is required';
    if (!formData.tipo_gps_id) return 'GPS Type is required';
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    try {
      await onSubmit(formData);
      // Reset form if it's a new entry
      if (!dispositivo) {
        setFormData({
          imei: '',
          modelo: '',
          marca: '',
          tipo_gps_id: '',
        });
      }
    } catch (error) {
      setError(error.response?.data?.message || 'Error submitting form. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="w-full lg:w-1/3 flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div className="w-full lg:w-1/3">
      <h2 className={`text-xl font-semibold ${text.secondary} mb-4`}>
        {dispositivo ? 'Edit Dispositivo GPS' : 'Add Dispositivo GPS'}
      </h2>
      
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="imei" className={`block ${text.secondary} font-medium mb-1`}>
            IMEI
          </label>
          <div className="relative">
            <input
              type="text"
              id="imei"
              name="imei"
              value={formData.imei}
              onChange={handleChange}
              className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary} ${
                error && !formData.imei ? 'border-red-500' : ''
              }`}
              placeholder={isManualIMEI ? "Enter IMEI manually" : "Select or type IMEI"}
            />
            <button
              type="button"
              onClick={() => {
                setIsManualIMEI(!isManualIMEI);
                setFilteredIMEIs(isManualIMEI ? connectedIMEIs : []);
              }}
              className={`absolute right-2 top-2 px-2 py-1 text-sm ${bg.secondary} rounded hover:opacity-80 transition-opacity`}
            >
              {isManualIMEI ? "Select" : "Manual"}
            </button>
          </div>
          {!isManualIMEI && filteredIMEIs.length > 0 && (
            <ul className={`mt-1 max-h-40 overflow-y-auto border rounded-md ${bg.input} shadow-lg`}>
              {filteredIMEIs.map(imei => (
                <li
                  key={imei}
                  onClick={() => handleIMEISelect(imei)}
                  className={`px-3 py-2 cursor-pointer hover:${bg.secondary} transition-colors`}
                >
                  {imei}
                </li>
              ))}
            </ul>
          )}
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
            className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary} ${
              error && !formData.modelo ? 'border-red-500' : ''
            }`}
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
            className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary} ${
              error && !formData.marca ? 'border-red-500' : ''
            }`}
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
            className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary} ${
              error && !formData.tipo_gps_id ? 'border-red-500' : ''
            }`}
          >
            <option value="">Select a type</option>
            {tiposGPS.map((tipo) => (
              <option key={tipo.id} value={tipo.id}>
                {tipo.nombre}
              </option>
            ))}
          </select>
        </div>

        <div className="flex justify-end space-x-2 pt-4">
          <button
            type="button"
            onClick={onCancel}
            className={`px-4 py-2 rounded-md ${bg.secondary} ${text.primary} hover:opacity-80 transition-opacity`}
            disabled={loading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className={`px-4 py-2 rounded-md ${bg.primary} text-white hover:opacity-90 transition-opacity ${
              loading ? 'opacity-50 cursor-not-allowed' : ''
            }`}
            disabled={loading}
          >
            {loading ? 'Processing...' : dispositivo ? 'Update' : 'Add'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default DispositivoGPSForm;