<script setup lang="ts">

import { computed, onMounted } from 'vue';
import { useAuthStore } from '../store/auth';
import router from '../router';

const authStore = useAuthStore();


const isLoggedIn = computed(() => !!authStore.accessToken);


const logout = async() => {
  await authStore.logout();
  router.push('/login');
};


onMounted(async () => {
  if (!isLoggedIn.value && authStore.role && authStore.role.name !== 'admin') {
    await authStore.logout()
    router.push('/login');
}
})
</script>

<template>
    <header class="header">
    <div class="logo"> <a href="/panel">Biokeeper CMS</a></div>
    <!-- <nav class="navigation">
        <ul>
            <li>Каталог</li>
        </ul>
    </nav> -->
    <div class="user-actions">
        <div v-if="!isLoggedIn" class="login">
            <a href="/login">Войти</a>
        </div>
        <div v-if="isLoggedIn" class="user-profile">
            <span> {{ authStore.username }} </span>
            <a href="#" @click.prevent="logout">Выйти</a>
        </div>
    </div>
</header>
</template>


<style scoped>
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 20px;
    background-color: #f8f9fa; /* Цвет фона хедера */
}

.logo {
    font-size: 1.5rem;
}

.logo a {
    text-decoration: none;
}

.navigation ul {
    list-style-type: none;
    margin: 0;
    padding: 0;
}

.navigation ul li {
    display: inline-block;
    margin-right: 20px;
}

.navigation ul li:last-child {
    margin-right: 0;
}

.navigation ul li a {
    text-decoration: none;
    color: #333; /* Цвет текста ссылок */
}

.user-actions {
    display: flex;
    align-items: center;
}

.user-profile {
    margin-right: 20px;
}

.cart {
    margin-right: 10px;
}

a {
    margin-right: 10px;
    margin-left: 10px;
}

</style>