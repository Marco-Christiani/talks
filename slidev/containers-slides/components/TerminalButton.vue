<!-- components/TerminalButton.vue -->
<script setup lang="ts">
import { ref } from 'vue';
import TerminalPopup from './Terminal.vue';

const showTerminal = ref(false);

function openTerminal() {
  showTerminal.value = true;
}

function closeTerminal() {
  showTerminal.value = false;
}
</script>

<template>
  <div>
    <!-- Terminal Button -->
    <button @click="openTerminal"
      class="inline-flex px-2 py-2 bg-gray-700 hover:bg-blue-500 text-white rounded-lg transition-colors duration-200 shadow-md hover:shadow-lg"
      title="Open Terminal">
      <MdiTerminalLine />
    </button>

    <!-- Terminal Popup -->
    <TerminalPopup :show="showTerminal" @close="closeTerminal" />
  </div>
</template>
