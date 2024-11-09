import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTheme } from '../../contexts/ThemeContext';
import EmpresaList from './EmpresaList';
import EmpresaForm from './EmpresaForm';
import { BuildingOfficeIcon, PlusIcon } from '@heroicons/react/24/solid';
import config from '../../config/config';
const EmpresaManagement = () => {
  const [empresas, setEmpresas] = useState([]);
  const [selectedEmpresa, setSelectedEmpresa] = useState(null);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { text, bg } = useTheme();

  useEffect(() => {
    fetchEmpresas();
  }, []);

  const handleError = (error, action) => {
    console.error(`Error ${action}:`, error);
    const errorMessage = error.response?.data?.message || `Error ${action}. Please try again.`;
    setError(errorMessage);
    setTimeout(() => setError(null), 5000);
  };

  const fetchEmpresas = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${config.api.baseURL}/api/empresas`);
      if (response.data.success) {
        setEmpresas(response.data.empresas);
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      handleError(error, 'fetching empresas');
    } finally {
      setLoading(false);
    }
  };

  const handleAddEmpresa = async (newEmpresa) => {
    setLoading(true);
    try {
      const response = await axios.post(`${config.api.baseURL}/api/empresas`, newEmpresa);
      if (response.data.success) {
        await fetchEmpresas();
        setIsFormVisible(false);
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      handleError(error, 'adding empresa');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateEmpresa = async (updatedEmpresa) => {
    setLoading(true);
    try {
      const response = await axios.put(
        `${config.api.baseURL}/api/empresas/${updatedEmpresa.id}`, 
        updatedEmpresa
      );
      if (response.data.success) {
        await fetchEmpresas();
        setSelectedEmpresa(null);
        setIsFormVisible(false);
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      handleError(error, 'updating empresa');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteEmpresa = async (empresaId) => {
    if (!window.confirm('¿Está seguro de que desea eliminar esta empresa?')) {
      return;
    }

    setLoading(true);
    try {
      const response = await axios.delete(`${config.api.baseURL}/api/empresas/${empresaId}`);
      if (response.data.success) {
        await fetchEmpresas();
        if (selectedEmpresa?.id === empresaId) {
          setSelectedEmpresa(null);
          setIsFormVisible(false);
        }
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      handleError(error, 'deleting empresa');
    } finally {
      setLoading(false);
    }
  };

  const handleAddClick = () => {
    setSelectedEmpresa(null);
    setIsFormVisible(true);
    setError(null);
  };

  return (
    <div className="flex flex-col space-y-6">
      <div className="flex justify-between items-center">
        <h1 className={`text-2xl font-bold ${text.primary} flex items-center`}>
          <BuildingOfficeIcon className="w-8 h-8 mr-2 text-primary-500" />
          Empresa Management
        </h1>
        <button
          onClick={handleAddClick}
          className={`${bg.primary} text-white px-4 py-2 rounded-lg flex items-center 
            hover:opacity-90 transition-opacity disabled:opacity-50`}
          disabled={loading}
        >
          <PlusIcon className="w-5 h-5 mr-2" />
          Add Empresa
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {loading && !isFormVisible && (
        <div className="flex justify-center py-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
        </div>
      )}

      <div className="flex flex-col lg:flex-row space-y-6 lg:space-y-0 lg:space-x-6">
        <EmpresaList
          empresas={empresas}
          onSelectEmpresa={(empresa) => {
            setSelectedEmpresa(empresa);
            setIsFormVisible(true);
            setError(null);
          }}
          onDeleteEmpresa={handleDeleteEmpresa}
          loading={loading}
        />
        
        {(isFormVisible || selectedEmpresa) && (
          <EmpresaForm
            empresa={selectedEmpresa}
            onSubmit={selectedEmpresa ? handleUpdateEmpresa : handleAddEmpresa}
            onCancel={() => {
              setSelectedEmpresa(null);
              setIsFormVisible(false);
              setError(null);
            }}
            loading={loading}
          />
        )}
      </div>
    </div>
  );
};

export default EmpresaManagement;