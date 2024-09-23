import React, { useState, useEffect } from 'react';
import { useTheme } from '../../contexts/ThemeContext';

const TipoGPSForm = ({ tipoGPS, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    nombre: '',
  });
  const { text, bg } = useTheme();

  useEffect(() => {
    if (tipoGPS) {
      setFormData(tipoGPS);
    }
  }, [tipoGPS]);

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
        {tipoGPS ? 'Edit Tipo GPS' : 'Add Tipo GPS'}
      </h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="nombre" className={`block ${text.secondary} font-medium mb-1`}>
            Name
          </label>
          <input
            type="text"
            id="nombre"
            name="nombre"
            value={formData.nombre}
            onChange={handleChange}
            required
            className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary}`}
          />
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
            {tipoGPS ? 'Update' : 'Add'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default TipoGPSForm;