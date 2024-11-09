// src/config/config.js

const getEnvVar = (key, defaultValue) => {
    const value = process.env[`REACT_APP_${key}`];
    if (!value && process.env.NODE_ENV === 'development') {
      console.warn(`Warning: Environmental variable ${key} is not set. Using default value: ${defaultValue}`);
    }
    return value || defaultValue;
  };
  
  const config = {
    api: {
      baseURL: getEnvVar('BACKEND_URL', 'http://localhost:5000'),
      timeout: 10000,
      withCredentials: true,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    }
  };
  
  export const getConfig = (path) => {
    return path.split('.').reduce((config, key) => config?.[key], config);
  };
  
  export default config;