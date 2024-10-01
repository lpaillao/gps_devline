import React from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { PencilIcon, TrashIcon } from '@heroicons/react/24/solid';

const EmpresaList = ({ empresas, onSelectEmpresa, onDeleteEmpresa }) => {
  const { text, bg } = useTheme();

  return (
    <div className="w-full lg:w-2/3">
      <h2 className={`text-xl font-semibold ${text.secondary} mb-4`}>Empresas List</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className={`${bg.secondary}`}>
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Address</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Phone</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className={`${bg.primary} divide-y divide-gray-200`}>
            {empresas.map((empresa) => (
              <tr key={empresa.id}>
                <td className="px-6 py-4 whitespace-nowrap">{empresa.nombre}</td>
                <td className="px-6 py-4 whitespace-nowrap">{empresa.direccion}</td>
                <td className="px-6 py-4 whitespace-nowrap">{empresa.telefono}</td>
                <td className="px-6 py-4 whitespace-nowrap">{empresa.email}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    onClick={() => onSelectEmpresa(empresa)}
                    className="text-indigo-600 hover:text-indigo-900 mr-2"
                  >
                    <PencilIcon className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => onDeleteEmpresa(empresa.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    <TrashIcon className="w-5 h-5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default EmpresaList;