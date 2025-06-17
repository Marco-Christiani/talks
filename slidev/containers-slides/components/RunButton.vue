<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getSession, useSession, SESSION_KEY, BACKEND_HTTP_URL } from "@lib/session";

const props = defineProps<{
  cmd: string;
}>();

const session = useSession();
const output = ref("");
const isRunning = ref(false);
const isConnected = ref(false);
const isConnecting = ref(false);

onMounted(async () => {
  isConnecting.value = true;
  try {
    await getSession();
    isConnected.value = true;
    output.value = `Connected to session ${session.value?.id}`;
  } catch (err) {
    isConnected.value = false;
    output.value = `Failed to connect: ${err}`;
    console.error(err);
  } finally {
    isConnecting.value = false;
  }
});

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

  output.value += `\nSession ${session.value.id} stopped`;
  localStorage.removeItem(SESSION_KEY);
  session.value = null;
  isConnected.value = false;
}
</script>

<template>
  <div class="p-2 bg-zinc-800 rounded-lg text-white text-left">
    <div class="mb-2 font-mono text-sm">
      Command: <code>{{ cmd }}</code>
    </div>
    <div class="mb-2 text-sm text-yellow-400" v-if="isConnecting">
      <CarbonCircleDash />
      Connecting to Docker sandbox...
    </div>
    <div class="mb-2 text-sm text-green-400" v-else-if="session">
      Connected: <code>{{ session.id }}</code>
    </div>
    <div class="flex gap-2 mb-2">
      <button @click="runCommand" :disabled="isRunning" class="px-3 py-1 bg-blue-600 rounded hover:bg-blue-500">
        Run
      </button>
      <button @click="stopSession" class="px-3 py-1 bg-red-600 rounded hover:bg-red-500">
        Stop Session
      </button>
    </div>
    <pre class="bg-black text-green-400 p-2 rounded max-h-64 overflow-auto text-xs whitespace-pre-wrap">{{ output }}
    </pre>
  </div>
</template>
