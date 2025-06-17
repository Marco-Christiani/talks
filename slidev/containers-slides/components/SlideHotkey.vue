<!-- components/TerminalToggle.vue -->
<template>
  <button
    class="fixed bottom-4 right-4 z-50 px-3 py-1 bg-black text-white rounded"
    @click="toggle"
  >
    <template v-if="isTargetSlide">
      <slot name="target">Back</slot>
    </template>
    <template v-else>
      <slot>Terminal</slot>
    </template>
  </button>
</template>

<script setup lang="ts">
import { ref, watchEffect, onMounted, onBeforeUnmount } from "vue";
import { useNav } from "@slidev/client";
import { useMagicKeys } from "@vueuse/core";

type SlideHotkeyProps = {
  route?: string;
  hotkey?: string; // e.g., "ctrl+."
};

const props = withDefaults(defineProps<SlideHotkeyProps>(), {
  route: "terminal",
  hotkey: "ctrl+.",
});

const nav = useNav();
const isTargetSlide = ref(false);

const targetSlideRoute = props.route;

if (window.__prevSlideNum === undefined) window.__prevSlideNum = 1;

watchEffect(() => {
  const routeAlias =
    nav.currentSlideRoute.value?.meta.slide?.frontmatter.routeAlias || "1";
  isTargetSlide.value = routeAlias === targetSlideRoute;
  if (!isTargetSlide.value) {
    window.__prevSlideNum = nav.currentPage.value;
    console.log(`Setting prevSlide to ${window.__prevSlideNum}`);
  }
});

function toggle(): void {
  if (isTargetSlide.value) {
    if (window.__prevSlideNum === undefined)
      return console.warn("No previous slide number recorded.");
    nav.go(window.__prevSlideNum);
  } else {
    nav.go(targetSlideRoute);
  }
}

function parseHotkey(hotkey: string): [string[], string] {
  const parts = hotkey.toLowerCase().split("+");
  const key = parts.pop()!;
  return [parts, key];
}

const keys = useMagicKeys();

function setupHotkey(): void {
  const [mods, key] = parseHotkey(props.hotkey);
  watchEffect(() => {
    const mainPressed = keys[key]?.value;
    const modifiersPressed = mods.every((mod) => keys[mod]?.value);
    if (mainPressed && modifiersPressed) {
      toggle();
    }
  });
}

onMounted(() => {
  if (!window.__terminalKeyBindRegistered) {
    setupHotkey();
    window.__terminalKeyBindRegistered = true;
  }
});
</script>
