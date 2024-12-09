<template>
    <Modal :title="title" @close="closeModal">
      <div>
        <label for="qrCount">Количество QR-кодов:</label>
        <input type="number" id="qrCount" v-model="qrCount" min="1" />
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

class QrCodeAmountException extends Error {
  constructor(message: string) {
    super(message);
    this.name = "QrCodeAmountException";
  }
}

const emit = defineEmits(['close', 'submit']);

const qrCount = ref<number>(1);

const closeModal = () => {
    emit('close');
};

const createKit = async (qrCount: number) => {
  try {
    const response = await coreClient.post('/kits', { n_qrs: qrCount });

    if (response.status === 201) {
      return response.data;
    }

  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 409) {
        if (error.response.data?.detail === 'Number of QRS should be positive') {
          throw new QrCodeAmountException('Количество QR-кодов не может быть меньше 1.');
        }
        if (error.response.data?.detail === 'Number of QRS should be less than 100') {
          throw new QrCodeAmountException('Количество QR-кодов не может быть больше 100.');
        }
      }
    }
    throw error; // Повторное выбрасывание ошибки для обработки в submitForm
  }
};

const submitForm = async () => {
  try {
    await createKit(qrCount.value);
    emit('submit');
    closeModal();
  } catch (error) {
    if (error instanceof QrCodeAmountException) {
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
