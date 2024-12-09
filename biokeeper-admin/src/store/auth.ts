// src/store/auth.js
import { defineStore } from 'pinia';
import { decodeAccessToken } from '../utils/jwt';
import {authClient} from '../utils/axios';
import router from '../router';  // Импортируйте роутер
import axios from 'axios';

const refreshApiClient = axios.create({
  baseURL: 'https://auth.biokeeper.ru',
  headers: {
    'Content-Type': 'application/json'
  }
});

interface Role {
  id: number;
  name: string;
  info: string;
}

export const useAuthStore = defineStore({
  id: 'auth',
  state: () => ({
    accessToken: '',
    refreshToken: '',
    username: null as string | null,
    user_id: null as number | null,
    role: null as Role | null
  }),
  actions: {
    saveTokens(accessToken: string, refreshToken: string) {
      this.accessToken = accessToken;
      this.refreshToken = refreshToken;
      localStorage.setItem('accessToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
      this.decodeToken();
    },
    loadTokens() {
      const accessToken = localStorage.getItem('accessToken');
      const refreshToken = localStorage.getItem('refreshToken');
      if (accessToken && refreshToken) {
        this.accessToken = accessToken;
        this.refreshToken = refreshToken;
        this.decodeToken();
      }
    },
    decodeToken() {
      const payload = decodeAccessToken(this.accessToken);
      if (payload) {
        this.username = payload.username;
        this.user_id = payload.id;
        this.role = payload.role;
        if (payload.role.name != 'admin') {
          this.logout();
          router.push('/login');
        }
      }
    },
    async logout() {
      try {
        await authClient.post('/logout', {
          refresh_token: this.refreshToken
        });
        this.clearTokens();
      } catch (error) {
        this.clearTokens();
      }
    },
    async RefreshToken() {
      try {
        const response = await refreshApiClient.post('/refresh', {
          refresh_token: this.refreshToken
        });
        if (response.status === 401) {
          this.clearTokens();
          router.push('/login');
        } else {
          this.saveTokens(response.data.access_token, this.refreshToken);
        }
      } catch (error) {
        this.clearTokens();
        router.push('/login');
      }
    },

    clearTokens() {
      this.accessToken = '';
      this.refreshToken = '';
      this.username = null;
      this.user_id = null;
      this.role = null;
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
    }
  }
});
