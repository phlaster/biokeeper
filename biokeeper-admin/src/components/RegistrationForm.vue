<script setup lang="ts">
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
  
  const username = ref('');
  const email = ref('');
  const password = ref('');
  const password2 = ref('');

  const router = useRouter();

  const register = async () => {
    try {
      const response = await axios.post('https://auth.biokeeper.ru/create', {
        username: username.value,
        email: email.value,
        password: password.value,
        password2: password2.value
      });
      console.log('Пользователь зарегистрирован:', response.data);

      router.push('/login');
    } catch (error) {
      console.error('Ошибка регистрации:', error);
    }
  };

</script>


<template>
    <form @submit.prevent="register">
      <input v-model="username" type="text" placeholder="Имя пользователя" required> <br>
      <input v-model="email" type="email" placeholder="Email" required><br>
      <input v-model="password" type="password" placeholder="Пароль" required><br>
      <input v-model="password2" type="password" placeholder="Повторите пароль" required><br>
      <button type="submit">Зарегистрироваться</button>
    </form>
    <p>Уже есть аккаунт? <router-link to="/login">Войти</router-link></p>
  </template>
  

  