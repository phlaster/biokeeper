import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosRequestHeaders, InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '../store/auth';
import router from '../router';  // Импортируйте роутер

const setupInterceptors = (client: AxiosInstance) => {
  client.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      const authStore = useAuthStore();
      if (authStore.accessToken) {
        (config.headers as AxiosRequestHeaders)['Authorization'] = `Bearer ${authStore.accessToken}`;
      }
      return config;
    },
    (error: AxiosError) => Promise.reject(error)
  );

  client.interceptors.response.use(
    response => response,
    async error => {
      const authStore = useAuthStore();
      const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

      if (error.response.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;
        try {
          await authStore.RefreshToken();
          (originalRequest.headers as AxiosRequestHeaders)['Authorization'] = `Bearer ${authStore.accessToken}`;
          return client(originalRequest);
        } catch (refreshError) {
          authStore.clearTokens();
          router.push('/login');  // Перенаправляем на страницу логина
          return Promise.reject(refreshError);
        }
      }

      return Promise.reject(error);
    }
  );
};


// Создание клиента для auth.biokeeper.ru
const authClient = axios.create({
  baseURL: 'https://auth.biokeeper.ru',
  headers: {
    'Content-Type': 'application/json'
  }
});
// Применение интерцепторов
setupInterceptors(authClient);


// Создание клиента для core.biokeeper.ru
const coreClient = axios.create({
  baseURL: 'https://core.biokeeper.ru',
  headers: {
    'Content-Type': 'application/json'
  }
});
// Применение интерцепторов
setupInterceptors(coreClient);

export { authClient, coreClient };

