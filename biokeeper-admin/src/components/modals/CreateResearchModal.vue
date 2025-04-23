<template>
    <Modal :title="title" @close="closeModal">
      <div>
        <label for="researchName">Название исследования:</label>
        <input type="text" id="researchName" v-model="researchName" />

        <label for="researchComment">Описание</label>
        <textarea id="researchComment" v-model="researchComment"></textarea>
        
        <label for="dayStart">Дата начала</label>
        <input type="date" id="dayStart" v-model="dayStart">

        <label for="approvalRequired">Требуется ли согласование?</label>
        <input type="checkbox" id="approvalRequired" v-model="approvalRequired">
        <p v-if="!approvalRequired" style="color: red"><b>!Согласование не требуется!</b></p>
      </div>
      <template #footer>
        <button @click="submitForm">Создать</button>
        <button @click="closeModal">Отмена</button>
      </template>
    </Modal>
  </template>
  
<script lang="ts" setup>
import { ref } from 'vue';
import Modal from '../Modal.vue';
import { coreClient } from '../../utils/axios';
import axios from 'axios';
  
const {title} = defineProps<{
  title: string;
}>();

class ResearchAlreadyExistsException extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ResearchAlreadyExistsException";
  }
}

const emit = defineEmits(['close', 'submit']);



const researchName = ref<string>('');
const researchComment = ref<string>('');
const approvalRequired = ref<boolean>(true);
const dayStart = ref<string>('');

const closeModal = () => {
    emit('close');
};

const createResearch = async (researchName: string, researchComment: string, approvalRequired: boolean, dayStart: string) => {
  try {
    const response = await coreClient.post('/researches', {research_name : researchName, 
        research_comment: researchComment, approval_required: approvalRequired, 
        day_start: dayStart});

    if (response.status === 201) {
      return response.data;
    }
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 409) {
        if ("already exists" in error.response.data?.detail ) {
          throw new ResearchAlreadyExistsException('Исследование с таким названием уже существует.');
        }
      }
    }
    throw error; // Повторное выбрасывание ошибки для обработки в submitForm
  }
};

const submitForm = async () => {
    try {
        await createResearch(researchName.value, researchComment.value, approvalRequired.value, dayStart.value);
        emit('submit');
        closeModal();
    } catch (error) {
        if (error instanceof ResearchAlreadyExistsException) {
            alert(error.message);
        return;
        }
        else {
        console.error('Error creating research:', error);
        }
    }
}
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
