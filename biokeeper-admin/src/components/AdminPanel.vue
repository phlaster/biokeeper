<script lang="ts" setup>
import { useAuthStore } from '../store/auth';
import { computed, onMounted, ref } from 'vue';
import router from '../router';
import {coreClient}  from '../utils/axios';
import {getPrettyDateTime} from '../utils/prettyDate';

import CreateKitModal from './modals/CreateKitModal.vue'; // добавляем
import CreateResearchModal from './modals/CreateResearchModal.vue';


const authStore = useAuthStore();

interface Research {
    id: number;
    name: string;
    status: string;
    created_at: string;
}

const researches = ref<Research[]>([]);

interface Kit {
    id: number;
    unique_hex: string;
    n_qrs: number;
    owner_id: number;
    owner_name: string;
    created_at: string;
    
}
const kits = ref<Kit[]>([]);
const sortedKits = computed(() => {
  return kits.value.slice().sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
});




const isCreateKitModalVisible = ref(false);
const handleCreateKitModal = (isVisible: boolean) => {
  isCreateKitModalVisible.value = isVisible;
};


const isCreateResearchModalVisible = ref(false);
const handleCreateResearchModal = (isVisible: boolean) => {
    isCreateResearchModalVisible.value = isVisible;
};



const UpdateResearches = async () => {
    try {
        const response = await coreClient.get<Research[]>('/me/created_researches/');
        researches.value = response.data;
    } catch (error) {
        console.error('Error fetching researches:', error);
    }
}

const UpdateKits = async () => {
    try {
        const response = await coreClient.get<Kit[]>('/me/created_kits/');
        kits.value = response.data;
    } catch (error) {
        console.error('Error fetching kits:', error);
    }
}

onMounted(async () => {
    if (!authStore.accessToken && authStore.role && authStore.role.name !== 'admin') {
        await authStore.logout();
        router.push('/login');
    }
    else{
        
        await UpdateResearches();
        await UpdateKits();   
    }
});

</script>


<template>

    <div>
        <h1>User: {{ authStore?.username }}</h1>
        <h1>Role: {{ authStore?.role?.name }}</h1>

        <h2>Список исследований</h2>

        <CreateResearchModal
        v-if="isCreateResearchModalVisible"
        title="Создать новое исследование"
        @close="handleCreateResearchModal(false)"
        @submit="UpdateResearches"
        />
        
        <button @click="handleCreateResearchModal(true)">Создать исследование</button>
        <table class="styled-table">
            <tr>
                <th>
                    Исследование
                </th>
                <th>
                    Статус
                </th>
            </tr>
            <tr v-for="research in researches" :key="research.id">
                <td>
                <a class="link" @click.prevent="router.push(`/researches/${research.id}`)">{{ research.name }}</a>
                </td>
                <td>
                {{ research.status }}
                </td>
            </tr>
        </table>


        <CreateKitModal
        v-if="isCreateKitModalVisible"
        title="Создать новый набор"
        @close="handleCreateKitModal(false)"
        @submit="UpdateKits"
        />
        
        <h2>Созданные наборы</h2>
        <button @click="handleCreateKitModal(true)">Создать набор</button>
        <table class="styled-table">
            <tr>
                <th>
                    Id
                </th>
                <th>
                    Код
                </th>
                <th>
                    Количество QR-кодов
                </th>
                <th>
                    Владелец
                </th>
                <th>
                    Дата создания
                </th>
            </tr>
            <tr v-for="kit in sortedKits" :key="kit.id">
                <td>
                    {{ kit.id }}
                </td>
                <td>
                    <a class="link" @click.prevent="router.push(`/kits/${kit.id}`)">{{ kit.unique_hex }}</a>
                </td>
                <td>
                    {{ kit.n_qrs }}
                </td>
                <td>
                    <a v-if="kit.owner_id" class="link" @click.prevent="router.push(`/user/${kit.owner_id}`)">{{ kit?.owner_name }}</a>
                </td>
                <td>
                    {{ getPrettyDateTime(kit?.created_at) }}
                </td>
            </tr>
        </table>


    </div>
</template>


<style scoped>




</style>