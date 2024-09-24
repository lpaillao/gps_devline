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
  const [connectedIMEIs, setConnectedIMEIs] = useState([]);
  const [filteredIMEIs, setFilteredIMEIs] = useState([]);
  const [isManualIMEI, setIsManualIMEI] = useState(false);
  const { text, bg } = useTheme();

  useEffect(() => {
    if (dispositivo) {
      setFormData(dispositivo);
    }
    fetchTiposGPS();
    fetchConnectedIMEIs();
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

  const fetchConnectedIMEIs = async () => {
    try {
      const response = await axios.get('http://167.71.106.231:5000/api/connected_devices');
      setConnectedIMEIs(response.data);
      setFilteredIMEIs(response.data);
    } catch (error) {
      console.error('Error fetching connected IMEIs:', error);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    if (name === 'imei') {
      filterIMEIs(value);
    }
  };

  const filterIMEIs = (value) => {
    const filtered = connectedIMEIs.filter(imei => imei.includes(value));
    setFilteredIMEIs(filtered);
  };

  const handleIMEISelect = (imei) => {
    setFormData({ ...formData, imei });
    setFilteredIMEIs([]);
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
          <div className="relative">
            <input
              type="text"
              id="imei"
              name="imei"
              value={formData.imei}
              onChange={handleChange}
              required
              className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary}`}
              placeholder={isManualIMEI ? "Enter IMEI manually" : "Select or type IMEI"}
            />
            <button
              type="button"
              onClick={() => setIsManualIMEI(!isManualIMEI)}
              className={`absolute right-2 top-2 px-2 py-1 text-sm ${bg.secondary} rounded`}
            >
              {isManualIMEI ? "Select" : "Manual"}
            </button>
          </div>
          {!isManualIMEI && filteredIMEIs.length > 0 && (
            <ul className={`mt-1 max-h-40 overflow-y-auto border rounded-md ${bg.input}`}>
              {filteredIMEIs.map(imei => (
                <li
                  key={imei}
                  onClick={() => handleIMEISelect(imei)}
                  className={`px-3 py-2 cursor-pointer hover:${bg.secondary}`}
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