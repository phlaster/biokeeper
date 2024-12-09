<template>
    <Modal :title="title" @close="closeModal">
      <p>{{ message }}</p>
      <button @click="confirmAction">Confirm</button>
      <button @click="closeModal">Cancel</button>
    </Modal>
  </template>
  
  <script lang="ts" setup>
  import Modal from '../Modal.vue';
  
  const {title, message} = defineProps<{
    title: string;
    message: string;
  }>();
  
  const emit = defineEmits(['close', 'confirm']);
  
  const closeModal = () => {
    emit('close');
  };
  
  const confirmAction = () => {
    emit('confirm');
    closeModal();
  };
  </script>
  