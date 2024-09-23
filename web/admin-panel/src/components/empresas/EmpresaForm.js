import React, { useState, useEffect } from 'react';
import { useTheme } from '../../contexts/ThemeContext';

const EmpresaForm = ({ empresa, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    nombre: '',
    direccion: '',
    telefono: '',
    email: '',
  });
  const { text, bg } = useTheme();

  useEffect(() => {
    if (empresa) {
      setFormData(empresa);
    }
  }, [empresa]);

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
        {empresa ? 'Edit Empresa' : 'Add Empresa'}
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
        <div>
          <label htmlFor="direccion" className={`block ${text.secondary} font-medium mb-1`}>
            Address
          </label>
          <input
            type="text"
            id="direccion"
            name="direccion"
            value={formData.direccion}
            onChange={handleChange}
            required
            className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary}`}
          />
        </div>
        <div>
          <label htmlFor="telefono" className={`block ${text.secondary} font-medium mb-1`}>
            Phone
          </label>
          <input
            type="tel"
            id="telefono"
            name="telefono"
            value={formData.telefono}
            onChange={handleChange}
            required
            className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary}`}
          />
        </div>
        <div>
          <label htmlFor="email" className={`block ${text.secondary} font-medium mb-1`}>
            Email
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
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
            {empresa ? 'Update' : 'Add'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default EmpresaForm;