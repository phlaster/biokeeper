<script setup lang="ts">
  import { computed, onMounted, ref } from 'vue';
  import axios from 'axios';
  import { useRouter } from 'vue-router';
  import { useAuthStore } from '../store/auth';
  
  const username = ref('');
  const password = ref('');
  const authStore = useAuthStore();
  const router = useRouter();

  const isLoggedIn = computed(() => !!authStore.accessToken);
  const isAdmin = computed(() => !!authStore.role && authStore.role.name === 'admin');

  
  const login = async () => {
    try {
      const response = await axios.post('https://auth.biokeeper.ru/token', new URLSearchParams({
        grant_type: 'password',
        username: username.value,
        password: password.value,
      }), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      authStore.saveTokens(response.data.access_token, response.data.refresh_token);
      if (authStore.role && authStore.role.name !== 'admin') {
        alert('У вас нет прав администратора');
        await authStore.logout();
      }
      else {
      // Перенаправить пользователя на страницу каталога
        router.push('/panel');
      }
    } catch (error) {
      console.error('Error logging in:', error);
    }
  };

  onMounted(async () => {
    if (isLoggedIn.value && isAdmin.value) {
    router.replace('/panel');
  }
  });
</script>

<template>
    <div>
      <form @submit.prevent="login">
        <input v-model="username" type="text" placeholder="Username" />
        <input v-model="password" type="password" placeholder="Password" />
        <button type="submit">Login</button>
        <p>Нет аккаунта? <router-link to="/register">Зарегистрироваться</router-link></p>
      </form>
    </div>
  </template>
  

  