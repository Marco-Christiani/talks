<!-- components/RunButton.vue -->
<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useSession, useSessionActions, getSession } from "@lib/session";

const props = withDefaults(defineProps<{ cmd?: string }>(), {});

const { session, isConnecting } = useSession();
const { runCommand, stopSession, clearSession } = useSessionActions();

const output = ref<string | null>(null);
const isRunning = ref(false);
const out = ref<HTMLElement | null>(null);

async function execute() {
  if (!props.cmd) return;
  isRunning.value = true;
  output.value = "Running...";

  try {
    const result = await runCommand(props.cmd);
    output.value = result.error ? `Error: ${result.error}` : result.output;
  } catch (err) {
    output.value = `Unexpected error: ${err}`;
  } finally {
    isRunning.value = false;
  }
}

async function stopAndClear() {
  await stopSession();
  clearOutput();
}

function clearOutput() {
  output.value = null;
}

onMounted(async () => {
  try {
    await getSession();
  } catch (err) {
    console.warn("Session unavailable:", err);
  }
});
</script>

<template>
  <div class="my-2 p-1 bg-zinc-800 rounded-lg text-white text-left">
    <!-- Connection Bar -->
    <div class="flex items-center gap-2 bg-zinc-800 text-white px-2 rounded-t-lg">
      <div
        class="w-3 h-3 rounded-full"
        :class="session ? 'bg-green-500' : isConnecting ? 'bg-yellow-500' : 'bg-red-500'"
      ></div>
      <span class="text-sm font-mono">
        {{ session ? session.id : "No session" }}
      </span>
      <div v-if="isConnecting" class="text-sm text-yellow-400">Connecting to Docker sandbox...</div>
      <button
        @click="getSession"
        v-if="!isConnecting && !session"
        class="px-1 py-1 text-xs text-mono bg-green-600 rounded"
      >
        Connect
      </button>
      <button v-else @click="stopAndClear" class="px-1 py-1 text-xs text-mono bg-red-600 rounded hover:bg-red-500">
        Stop
      </button>
      <button
        v-if="cmd && session"
        @click="execute"
        :disabled="isRunning || !session"
        class="px-1 py-1 text-xs text-mono bg-blue-600 rounded hover:bg-blue-500"
      >
        Run
      </button>
    </div>
    <!-- Output -->
    <div v-if="cmd">
      <div class="my-2 font-mono text-sm">
        Command: <code>{{ cmd }}</code>
      </div>
      <div
        v-if="output"
        ref="out"
        class="bg-zinc-900 rounded text-xs whitespace-pre-wrap overflow-auto resize-y"
        style="min-height: 4rem; max-height: calc(100vh - 8rem); resize: vertical"
      >
        <div @click="clearOutput" class="inline-block p-1"><MdiClearOctagonOutline /></div>
        <pre class="text-green-400 px-2">{{ output }}</pre>
      </div>
    </div>
  </div>
</template>
