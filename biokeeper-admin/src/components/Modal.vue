<template>
    <div class="modal-overlay">
      <!--  @click.self="closeModal"> -->
      <div class="modal">
        <header class="modal-header">
          <h2>{{ title }}</h2>
          <button @click="closeModal">X</button>
        </header>
        <div class="modal-body">
          <slot></slot>
        </div>
        <footer class="modal-footer">
          <slot name="footer" ></slot>
        </footer>
      </div>
    </div>
  </template>
  
  <script lang="ts" setup>
  const {title} = defineProps<{
    title: string;
  }>();
  
  const emit = defineEmits(['close']);
  
  const closeModal = () => {
    emit('close');
  };
  </script>
  
  <style scoped>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .modal {
    background: white;
    padding: 1em;
    border-radius: 5px;
    max-width: 500px;
    width: 100%;
  }

  .modal-footer {
    margin-top: 10px;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }


</style>
  