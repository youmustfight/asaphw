// @ts-nocheck

// Vite is expecting this odd import syntax
export const getTargetEnv = (): string => {
  return import.meta.env.VITE_TARGET_ENV;
};

export const getServiceApiUrl = (): string => {
  return import.meta.env.VITE_SERVICE_API_URL;
};
