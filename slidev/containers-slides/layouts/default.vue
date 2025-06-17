<!-- layouts/default.vue -->
<template>
  <div class="slidev-layout default">
    <slot />

    <div class="absolute bottom-4 right-4 z-50">
      <TerminalButton />
    </div>
  </div>
</template>

<script setup lang="ts">
import TerminalButton from '../components/TerminalButton.vue'
</script>
