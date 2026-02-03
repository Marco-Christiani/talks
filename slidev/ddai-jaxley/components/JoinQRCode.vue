<script setup lang="ts">
import { onMounted, onBeforeUnmount, computed, ref, watch } from 'vue'
import QRCode from 'qrcode'

const props = withDefaults(defineProps<{
  url?: string
  size?: number
  fg?: string
  bg?: string
  label?: string
  labelPosition?: 'top' | 'bottom' | 'left' | 'right'
  labelClass?: string
}>(), {
  url: undefined,
  size: 220,
  // fg: 'var(--slidev-theme-text)',
  fg: '#000000',
  bg: '#00000000',
  label: undefined,
  labelPosition: 'bottom',
  labelClass: 'text-sm opacity-70',
})

const resolvedUrl = ref('')
const svg = ref('')
const labelText = computed(() => {
  if (props.label === undefined)
    return resolvedUrl.value
  return props.label.replace(/\{url\}/g, resolvedUrl.value)
})
const containerClass = computed(() => {
  switch (props.labelPosition) {
    case 'top': return 'flex-col-reverse'
    case 'left': return 'flex-row-reverse'
    case 'right': return 'flex-row'
    default: return 'flex-col'
  }
})

function pickUrl() {
  if (props.url)
    return props.url
  if (typeof window === 'undefined')
    return ''
  const current = new URL(window.location.href)
  return current.searchParams.get('join') || current.origin
}

let observer: MutationObserver | undefined

async function render() {
  resolvedUrl.value = pickUrl()
  if (!resolvedUrl.value)
    return
  const root = typeof window !== 'undefined' ? getComputedStyle(document.documentElement) : null
  const resolveColor = (value: string) => {
    if (!root)
      return value
    if (value.startsWith('var(')) {
      const name = value.slice(4, -1).trim()
      const resolved = root.getPropertyValue(name).trim()
      return resolved || value
    }
    if (value.startsWith('--')) {
      const resolved = root.getPropertyValue(value).trim()
      return resolved || value
    }
    return value
  }
  svg.value = await QRCode.toString(resolvedUrl.value, {
    type: 'svg',
    margin: 1,
    width: props.size,
    color: {
      dark: resolveColor(props.fg),
      light: resolveColor(props.bg),
    },
  })
}

onMounted(() => {
  // Defer one frame so CSS variables are ready.
  requestAnimationFrame(() => {
    render()
  })
  // Re-render when theme class changes (light/dark toggle).
  if (typeof MutationObserver !== 'undefined') {
    observer = new MutationObserver(() => render())
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })
  }
})

onBeforeUnmount(() => {
  observer?.disconnect()
})
watch(() => props.url, render)
</script>

<template>
  <div :class="['inline-flex items-center gap-3', containerClass]">
    <div v-html="svg" />
    <div v-if="labelText" :class="labelClass">
      {{ labelText }}
    </div>
  </div>
</template>
