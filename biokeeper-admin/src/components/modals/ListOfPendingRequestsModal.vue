<template>
    <Modal :title="title" @close="closeModal">
      <table>
        <tr v-for="user in users">
          <td>{{ user.username }}</td>
          <td>{{ user.user_id }}</td>
          <td><button @click="processPendingRequest(user.user_id, 'approve')">Принять</button></td>
          <td><button @click="processPendingRequest(user.user_id, 'decline')">Отклонить</button></td>
        </tr>
      </table>
      <template #footer>
      </template>
    </Modal>
  </template>
  
<script lang="ts" setup>
import Modal from '../Modal.vue';
import { coreClient } from '../../utils/axios';
import { AxiosError } from 'axios';
  

interface User {
    user_id: string;
    username: string;
}

const props = defineProps<{
    title: string;
    research_id: string;
    users: User[];
}>();

const emit = defineEmits(['close', 'submit']);

const closeModal = () => {
    emit('close');
};

const processPendingRequest = async (user_id: string, action : string) => {
  try {
    let response: any;
    switch (action) {
      case 'approve':
        response = await coreClient.post('/researches/' + `${props.research_id}` + '/approve_request', {candidate_identifier: user_id});
        break;
      case 'decline':
        response = await coreClient.post('/researches/' + `${props.research_id}` + '/decline_request', {candidate_identifier: user_id});
        break;
      default:
        break;
    }

    if (response.status === 200) {
      submitForm();
      return response.data;
    }

  } catch (error) {
    throw error; // Повторное выбрасывание ошибки для обработки в submitForm
  }
};

const submitForm = async () => {
  try {
    emit('submit');
  } catch (error) {
    if (error instanceof AxiosError) {
      alert(error.message);
      return;
    }
    else {
      console.error('Error creating kit:', error);
    }
  }
};
</script>
  
<style scoped>
label {
display: block;
margin-bottom: 0.5em;
}

input {
margin-bottom: 1em;
padding: 0.5em;
width: calc(100% - 1em);
}
</style>
