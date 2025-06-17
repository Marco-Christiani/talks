
<template>
  <div ref="termRef" class="xterm-container" />
</template>


<script setup>
import { ref, onMounted } from 'vue'
import { Terminal } from '@xterm/xterm'
import { FitAddon } from '@xterm/addon-fit'
import { WebglAddon } from '@xterm/addon-webgl'
import '@xterm/xterm/css/xterm.css'

const termRef = ref(null)
// const term = new Terminal()
const term = new Terminal({
  fontSize: 12,
  cursorBlink: false,
  cursorStyle: 'block',
  // theme: {
  //   background: '#000000',
  //   foreground: '#00FF00',
  // },
  fontFamily: 'JetBrainsMono Nerd Font, FiraCode Nerd Font, Menlo, monospace',
})
const fitAddon = new FitAddon()
term.loadAddon(fitAddon)

onMounted(() => {
  const container = termRef.value
  if (!container) return

  term.open(container)
  fitAddon.fit()
  term.focus()

  // try {
  //   const webgl = new WebglAddon()
  //   term.loadAddon(webgl)
  //   console.log('WebGL renderer loaded')
  // } catch (err) {
  //   console.warn('WebGL renderer unavailable:', err)
  // }

  const socket = new WebSocket('ws://localhost:3000')
  socket.addEventListener('message', (event) => {
    term.write(event.data)
  })
  term.onData((data) => {
    socket.send(data)
  })
})
</script>