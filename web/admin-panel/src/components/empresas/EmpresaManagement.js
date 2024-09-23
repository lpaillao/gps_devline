import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTheme } from '../../contexts/ThemeContext';
import EmpresaList from './EmpresaList';
import EmpresaForm from './EmpresaForm';
import { BuildingOfficeIcon, PlusIcon } from '@heroicons/react/24/solid';
import { API_BASE_URL } from '../../config';

const EmpresaManagement = () => {
  const [empresas, setEmpresas] = useState([]);
  const [selectedEmpresa, setSelectedEmpresa] = useState(null);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const { text, bg } = useTheme();

  useEffect(() => {
    fetchEmpresas();
  }, []);

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

  const handleAddEmpresa = async (newEmpresa) => {
    try {
      const response = await axios.post(`${API_BASE_URL}?action=createEmpresa`, newEmpresa);
      if (response.data.success) {
        fetchEmpresas();
        setIsFormVisible(false);
      }
    } catch (error) {
      console.error('Error adding empresa:', error);
    }
  };

  const handleUpdateEmpresa = async (updatedEmpresa) => {
    try {
      const response = await axios.post(`${API_BASE_URL}?action=updateEmpresa`, updatedEmpresa);
      if (response.data.success) {
        fetchEmpresas();
        setSelectedEmpresa(null);
        setIsFormVisible(false);
      }
    } catch (error) {
      console.error('Error updating empresa:', error);
    }
  };

  const handleDeleteEmpresa = async (empresaId) => {
    try {
      const response = await axios.delete(`${API_BASE_URL}?action=deleteEmpresa&id=${empresaId}`);
      if (response.data.success) {
        fetchEmpresas();
      }
    } catch (error) {
      console.error('Error deleting empresa:', error);
    }
  };

  return (
    <div className="flex flex-col space-y-6">
      <div className="flex justify-between items-center">
        <h1 className={`text-2xl font-bold ${text.primary} flex items-center`}>
          <BuildingOfficeIcon className="w-8 h-8 mr-2 text-primary-500" />
          Empresa Management
        </h1>
        <button
          onClick={() => setIsFormVisible(true)}
          className={`${bg.primary} text-white px-4 py-2 rounded-lg flex items-center`}
        >
          <PlusIcon className="w-5 h-5 mr-2" />
          Add Empresa
        </button>
      </div>
      <div className="flex flex-col lg:flex-row space-y-6 lg:space-y-0 lg:space-x-6">
        <EmpresaList
          empresas={empresas}
          onSelectEmpresa={setSelectedEmpresa}
          onDeleteEmpresa={handleDeleteEmpresa}
        />
        {(isFormVisible || selectedEmpresa) && (
          <EmpresaForm
            empresa={selectedEmpresa}
            onSubmit={selectedEmpresa ? handleUpdateEmpresa : handleAddEmpresa}
            onCancel={() => {
              setSelectedEmpresa(null);
              setIsFormVisible(false);
            }}
          />
        )}
      </div>
    </div>
  );
};

export default EmpresaManagement;