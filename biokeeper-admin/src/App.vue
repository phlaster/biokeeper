<script setup lang="ts">
import Header from './components/Header.vue';

import { useAuthStore } from './store/auth';

const authStore = useAuthStore();
authStore.loadTokens();
</script>

<template>
    <Header />
    <main>
        <router-view />

    </main>
</template>

<style scoped>
main {
  max-width: 1200px; /* Максимальная ширина элемента main */
  margin: 0 auto; /* Автоматическое выравнивание по центру */
  padding: 0 20px; /* Отступы слева и справа */
}
</style>
