<script lang="ts" setup>
import { useAuthStore } from '../store/auth';
import { computed, onMounted, ref } from 'vue';
import router from '../router';
import {coreClient}  from '../utils/axios';
import {getPrettyDate} from '../utils/prettyDate';
import ChangeStatusOfResearchModal from './modals/ChangeStatusOfResearchModal.vue';
import axios from 'axios';
import ListOfPendingRequestsModal from './modals/ListOfPendingRequestsModal.vue';
import ListOfAcceptedParticipants from './modals/ListOfAcceptedParticipants.vue';

const authStore = useAuthStore();


interface User {
    user_id: string;
    username: string;
}

const pendingRequests = ref<User[]>([]);

const UpdatePendingRequests = async () => {
    try {
        const response = await coreClient.get<User[]>('/researches/' + `${research.value?.id}` + '/pending_requests');
        pendingRequests.value = response.data;
    } catch (error) {
        console.error('Error fetching pending requests:', error);
    }
}

const isListOfPendingRequestsModalVisible = ref(false);
const handleListOfPendingRequestsModal = (isVisible: boolean) => {
    if (isVisible)
        UpdatePendingRequests();
    isListOfPendingRequestsModalVisible.value = isVisible;
};

const acceptedParticipants = ref<User[]>([]);

const UpdateAcceptedParticipants = async () => {
    try {
        const response = await coreClient.get<User[]>('/researches/' + `${research.value?.id}` + '/accepted_participants');
        acceptedParticipants.value = response.data;
    } catch (error) {
        console.error('Error fetching accepted participants:', error);
    }
}

const isListOfAcceptedParticipantsModalVisible = ref(false);
const handleListOfAcceptedParticipantsModal = (isVisible: boolean) => {
    if (isVisible)
        UpdateAcceptedParticipants();
    isListOfAcceptedParticipantsModalVisible.value = isVisible;
};

interface Research {
    name: string;
    id: number;
    status: string;
    created_at: string;
    updated_at: string;
    created_by: string;
    day_start: string;
    day_end: string;
    n_samples: number;
    comment: string;
    approval_required: boolean;
    
}
const research = ref<Research>();

const isChangeStatusOfResearchModalVisible = ref(false);
const handleChangeStatusOfResearchModal = (isVisible: boolean) => {
    isChangeStatusOfResearchModalVisible.value = isVisible;
};


const isResearchActive = computed(() => {
    if (!research.value) 
        return false;
    return (research.value?.status  !== 'canceled' && research.value?.status  !== 'ended');
});

const UpdateResearchData = async () => {
    try {
        const response = await coreClient.get('/researches/'+research.value?.id);
        if (response.status === 200) {
            research.value = response.data;
        }
    }
    catch (error) {
        console.error('Error fetching research data:', error);
    }
}

onMounted(async () => {
    if (!authStore.accessToken && authStore.role && authStore.role.name !== 'admin') {
        await authStore.logout();
        router.push('/login');
    }
    else{
        try {
            const response = await coreClient.get<Research>('/researches/'+router.currentRoute.value.params.id);
            research.value = response.data;
            
            if (research.value?.created_by != String(authStore.user_id)) {
                router.push('/panel');
            }
        } catch (error) {
            if (axios.isAxiosError(error)) {
                if (error.response?.status === 404) {
                    router.push('/panel');
                }
            }
            console.error('Error fetching kit details:', error);
        }
    }
});

</script>


<template>
        <ChangeStatusOfResearchModal
        v-if="isChangeStatusOfResearchModalVisible"
        title="Изменить статус исследования"
        :research_id="String(research?.id)"
        :current_status="String(research?.status)"
        @close="handleChangeStatusOfResearchModal(false)"
        @submit="UpdateResearchData"
        />

        <ListOfPendingRequestsModal
        v-if="isListOfPendingRequestsModalVisible"
        title='Запросы на участие исследовании'
        :research_id="String(research?.id)"
        :users="pendingRequests"
        @close="handleListOfPendingRequestsModal(false)"
        @submit="UpdatePendingRequests"
        />

        <ListOfAcceptedParticipants
        v-if="isListOfAcceptedParticipantsModalVisible"
        title='Участники исследования'
        :research_id="String(research?.id)"
        :users="acceptedParticipants"
        @close="handleListOfAcceptedParticipantsModal(false)"
        @submit="UpdateAcceptedParticipants"
        />

        <div v-if="research" class="research-details">
            <h1 class="research-name">{{ research?.name }}</h1>
            <p class="research-comment">{{ research?.comment }}</p>
            <div class="research-info">
                <p><strong>Статус:</strong> {{ research?.status }}</p>
                <p><strong>Дата начала:</strong> {{ getPrettyDate(research?.day_start) }}</p>
                <p v-if="research?.day_end"><strong>Дата окончания:</strong> {{ getPrettyDate(research?.day_end) }}</p>
                <p><strong>Собрано образцов:</strong> {{ research?.n_samples }}</p>
                <p><strong>Необходимо подтверждение:</strong> {{ research?.approval_required ? 'Да' : 'Нет' }}</p>
            </div>
        </div>
        <button @click="handleChangeStatusOfResearchModal(true)" v-if="isResearchActive">Изменить статус исследования</button>
        <button v-if="research?.approval_required && isResearchActive" @click="handleListOfPendingRequestsModal(true)">Посмотреть запросы на участие в исследовании</button>
        <button v-if="research?.approval_required" @click="handleListOfAcceptedParticipantsModal(true)">Посмотреть участников исследования</button>
</template>

<style scoped>


.research-details {
    padding: 20px;
    border-radius: 8px;
}

.research-name {
    font-weight: bold;
    margin-bottom: 10px;
}

.research-comment {
    font-size: 16px;
    margin-bottom: 20px;
}

.research-info {
    font-size: 14px;
}
</style>
