<!-- components/RunButton.vue -->
<script setup lang="ts">
import { ref } from "vue";
import { getSession, useSession, SESSION_KEY, BACKEND_HTTP_URL } from "@lib/session";

type RunButtonProps = {
  cmd?: string;
};

const props = withDefaults(defineProps<RunButtonProps>(), {});

const session = useSession();
const output = ref<string | null>(null);
const isRunning = ref(false);
const isConnecting = ref(false);

async function runCommand() {
  if (!session.value) return;

  isRunning.value = true;
  output.value = "Running...";

  const res = await fetch(`${BACKEND_HTTP_URL}/run?sess=${session.value.id}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ cmd: props.cmd }),
  });

  const respJson = await res.json();
  output.value = respJson.output;
  isRunning.value = false;
}

async function stopSession() {
  if (!session.value) return;

  await fetch(`${BACKEND_HTTP_URL}/session?sess=${session.value.id}`, {
    method: "DELETE",
  });

  clearOutput();
  localStorage.removeItem(SESSION_KEY);
  session.value = null;
}

async function clearOutput() {
  output.value = null;
}

const out = ref<HTMLElement | null>(null);
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
      <button v-else @click="stopSession" class="px-1 py-1 text-xs text-mono bg-red-600 rounded hover:bg-red-500">
        Stop
      </button>
      <button
        v-if="cmd && session"
        @click="runCommand"
        :disabled="isRunning || !session"
        class="px-1 py-1 text-xs text-mono bg-blue-600 rounded hover:bg-blue-500"
      >
        Run
      </button>
    </div>
    <!-- End Connection Bar -->
    <div v-if="cmd">
      <div class="my-2 font-mono text-sm">
        Command: <code>{{ cmd }}</code>
      </div>
      <!-- <div v-if="output" class="bg-zinc-900 rounded max-h-80 overflow-auto text-xs whitespace-pre-wrap"> -->
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
