<!-- components/TerminalToggle.vue -->
<template>
  <button class="fixed bottom-4 right-4 z-50 px-3 py-1 bg-black text-white rounded"
          @click="toggle">
    {{ isTerminal ? 'Back' : 'Term' }}
  </button>
</template>

<script setup>
import { useNav } from '@slidev/client'
import { ref, watchEffect } from 'vue'

const nav = useNav()
const terminalRoute = 'terminal'
const isTerminal = ref(false)

// Use global to persist the previous slide number across route changes.
if (window.__prevSlideNum === undefined) {
  window.__prevSlideNum = 1
}
if (window.__terminalKeyBindRegistered === undefined) {
  window.__terminalKeyBindRegistered = false
}

watchEffect(() => {
  const route = nav.currentSlideRoute.value?.meta.slide?.frontmatter.routeAlias || '1';
  isTerminal.value = route === terminalRoute
  if (!isTerminal.value) {
    window.__prevSlideNum = nav.currentPage.value
    console.log(`setting prevSlide to ${window.__prevSlideNum}`)
  }
})
 
function toggle() {
  if (isTerminal.value) {
    if (window.__prevSlideNum === undefined) {
      console.log('no prev slide num')
      return
    }
    console.log(`going back to ${window.__prevSlideNum}`)
    nav.go(window.__prevSlideNum)
  } else {
    nav.go(terminalRoute)
  }
}

import { onMounted, onBeforeUnmount } from 'vue'

function handleKey(e) {
  if ((e.ctrlKey || e.metaKey) && e.key === '.') {
    console.log(isTerminal.value)
    e.preventDefault()
    toggle()
  }
}

onMounted(() => {
  if (!window.__terminalKeyBindRegistered) {
    window.addEventListener('keydown', handleKey)
    window.__terminalKeyBindRegistered = true
  }
})
onBeforeUnmount(() => window.removeEventListener('keydown', handleKey))
</script>