<template>
    <Modal :title="title" @close="closeModal">
      <div>
        <button v-if="props.current_status === 'pending' || props.current_status === 'paused'"
        @click="ChangeStatus(props.research_id,'start')">Запустить</button>

        <button v-if="props.current_status === 'ongoing'"
        @click="ChangeStatus(props.research_id,'pause')">Приостановить</button>

        <button v-if="props.current_status === 'ongoing' || props.current_status === 'paused'"
        @click="ChangeStatus(props.research_id,'end')">Завершить</button>

        <button v-if="props.current_status !== 'ended'"
        @click="ChangeStatus(props.research_id,'cancel')">Отменить</button>
      </div>
      <template #footer>
        <button @click="closeModal">Отмена</button>
      </template>
    </Modal>
  </template>
  
<script lang="ts" setup>
import Modal from '../Modal.vue';
import { coreClient } from '../../utils/axios';
import axios from 'axios';
  
const props = defineProps<{
    title: string;
    research_id: string;
    current_status: string;
}>();

class StatusConflictException extends Error {
  constructor(message: string) {
    super(message);
    this.name = "StatusConflictException";
  }
}

const emit = defineEmits(['close', 'submit']);

const closeModal = () => {
    emit('close');
};

const ChangeStatus = async (research_id: string, command: string) => {
  try {
    
        const response = await coreClient.put('/researches/' + `${research_id}` + '/' + `${command}`);
        if (response.status === 200) {
            submitForm();
            return response.data;
        }
        

    }
   catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 409) {
        throw new StatusConflictException(error.response.data?.detail);
        // if (error.response.data?.detail === 'Number of QRS should be positive') {
        //   throw new StatusConflictException('Исследование уже идёт');
        // }
        // if (error.response.data?.detail === 'Number of QRS should be less than 100') {
        //   throw new StatusConflictException('Исследование уже завершено');
        // }
        // if (error.response.data?.detail === 'Number of QRS should be less than 100') {
        //   throw new StatusConflictException('Исследование уже отменено');
        // }
        // if (error.response.data?.detail === 'Number of QRS should be less than 100') {
        //   throw new StatusConflictException('Исследование уже приостановлено');
        // }
      }
    }
    throw error; // Повторное выбрасывание ошибки для обработки в submitForm
  }
};

const submitForm = async () => {
  try {
    emit('submit');
    closeModal();
  } catch (error) {
    if (error instanceof StatusConflictException) {
        alert(error.message);
      return;
    }
    else {
      console.error('Error changing research status', error);
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

button {
    display: block
}
</style>
