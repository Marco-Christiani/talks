<script setup lang="ts">
import { ref, onMounted } from "vue";

const props = defineProps<{
  cmd: string;
}>();

type Session = {
  id: string;
  port: number;
};

const session = ref<Session | null>(null);
const output = ref("");
const isRunning = ref(false);
const isConnected = ref(false);
const isConnecting = ref(false);

const SESSION_KEY = "docker-session";

onMounted(async () => {
  const saved = localStorage.getItem(SESSION_KEY);
  if (saved) {
    try {
      const parsed: Session = JSON.parse(saved);
      const check = await fetch(
        `http://localhost:5000/session?sess=${parsed.id}`,
      );
      if (check.ok) {
        isConnected.value = true;
        session.value = parsed;
        output.value = `Reconnected to existing session ${parsed.id}`;
      } else {
        isConnected.value = false;
        localStorage.removeItem(SESSION_KEY);
      }
    } catch {
      isConnected.value = false;
      localStorage.removeItem(SESSION_KEY);
    }
  }
});

async function ensureSession() {
  if (session.value) return;

  isConnecting.value = true;
  try {
    const res = await fetch("http://localhost:5000/session?wait=true", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    const data = await res.json();
    if (!res.ok) {
      isConnected.value = false;
      console.log(data);
      alert("Failed to create session");
    } else {
      session.value = data;
      localStorage.setItem(SESSION_KEY, JSON.stringify(data));
      isConnected.value = true;
    }
    output.value = "";
  } finally {
    isConnecting.value = false;
  }
}

async function runCommand() {
  await ensureSession();
  if (!session.value) return;

  isRunning.value = true;
  output.value = "Running...";

  const res = await fetch(
    `http://localhost:5000/run?sess=${session.value.id}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cmd: props.cmd }),
    },
  );

  output.value = await res.text();
  isRunning.value = false;
}

async function stopSession() {
  if (!session.value) return;
  await fetch(`http://localhost:5000/session?sess=${session.value.id}`, {
    method: "DELETE",
  });
  output.value += `\nSession ${session.value.id} stopped`;
  localStorage.removeItem(SESSION_KEY);
  session.value = null;
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
      Connected: <code>{{ session.id }}@{{ session.port }}</code>
    </div>
    <div class="flex gap-2 mb-2">
      <button
        @click="runCommand"
        :disabled="isRunning"
        class="px-3 py-1 bg-blue-600 rounded hover:bg-blue-500"
      >
        Run
      </button>
      <button
        @click="stopSession"
        class="px-3 py-1 bg-red-600 rounded hover:bg-red-500"
      >
        Stop Session
      </button>
    </div>
    <pre
      class="bg-black text-green-400 p-2 rounded max-h-64 overflow-auto text-xs whitespace-pre-wrap"
      >{{ output }}</pre
    >
  </div>
</template>
