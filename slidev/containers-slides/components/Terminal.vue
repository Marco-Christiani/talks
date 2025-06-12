<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from "vue";
import { Terminal } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import { WebglAddon } from "@xterm/addon-webgl";
import "@xterm/xterm/css/xterm.css";

const props = defineProps<{
  sessionId?: string;
  sessionPort?: number;
}>();

type Session = {
  id: string;
  port: number;
};

const terminalContainer = ref<HTMLElement>();
const session = ref<Session | null>(null);
const isConnected = ref(false);
const isConnecting = ref(false);
const connectionError = ref("");
const fontSize = ref(14);

let terminal: Terminal;
let fitAddon: FitAddon;
let websocket: WebSocket | null = null;
let resizeObserver: ResizeObserver | null = null;

const SESSION_KEY = "docker-session";

onMounted(async () => {
  await initializeSession();
  await initializeTerminal();
});

onUnmounted(() => {
  cleanup();
});

function cleanup() {
  if (websocket) {
    websocket.close();
    websocket = null;
  }
  isConnected.value = false;
}

async function initializeSession() {
  // If session info is provided via props, use it
  if (props.sessionId && props.sessionPort) {
    session.value = { id: props.sessionId, port: props.sessionPort };
    return;
  }

  // Otherwise, try to restore from localStorage or create new
  const saved = localStorage.getItem(SESSION_KEY);
  if (saved) {
    try {
      const parsed: Session = JSON.parse(saved);
      const check = await fetch(
        `http://localhost:5000/session?sess=${parsed.id}`,
      );
      if (check.ok) {
        session.value = parsed;
        return;
      } else {
        localStorage.removeItem(SESSION_KEY);
      }
    } catch {
      localStorage.removeItem(SESSION_KEY);
    }
  }

  // Create new session
  await createNewSession();
}

async function createNewSession() {
  isConnecting.value = true;
  connectionError.value = "";

  try {
    const res = await fetch("http://localhost:5000/session?wait=true", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });

    if (!res.ok) {
      throw new Error(`Failed to create session: ${res.statusText}`);
    }

    const data = await res.json();
    session.value = data;
    localStorage.setItem(SESSION_KEY, JSON.stringify(data));
  } catch (error) {
    connectionError.value = `Failed to create session: ${error}`;
  } finally {
    isConnecting.value = false;
  }
}

async function initializeTerminal() {
  if (!session.value || !terminalContainer.value) return;

  terminal = new Terminal({
    cursorBlink: true,
    fontSize: fontSize.value,
    fontFamily: "monospace", // Use system monospace for consistent metrics
    theme: {
      background: "#1a1a1a",
      foreground: "#ffffff",
      cursor: "#ffffff",
      selectionForeground: "#3d3d3d",
    },
    allowTransparency: false,
    convertEol: true,
    scrollback: 1000,
    // lineHeight: 1.0, // Let xterm calculate line height automatically
  });

  fitAddon = new FitAddon();
  terminal.loadAddon(fitAddon);

  try {
    const webglAddon = new WebglAddon();
    terminal.loadAddon(webglAddon);
  } catch {
    // WebGL not supported, fallback to canvas renderer
  }

  terminal.open(terminalContainer.value);

  // Single fit after DOM is ready
  await nextTick();
  setTimeout(() => {
    fitAddon.fit();
  }, 100);

  // Handle terminal input
  terminal.onData((data) => {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      websocket.send(
        JSON.stringify({
          type: "input",
          data: data,
        }),
      );
    }
  });

  // Handle terminal resize
  terminal.onResize(({ cols, rows }) => {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      websocket.send(
        JSON.stringify({
          type: "resize",
          data: { cols, rows },
        }),
      );
    }
  });

  // Simple resize handling
  window.addEventListener("resize", () => {
    setTimeout(() => fitAddon.fit(), 100);
  });

  await connectWebSocket();
}

async function connectWebSocket() {
  if (!session.value) return;

  isConnecting.value = true;
  connectionError.value = "";

  try {
    const wsUrl = `ws://localhost:${session.value.port}/terminal`;
    websocket = new WebSocket(wsUrl);

    websocket.onopen = () => {
      isConnected.value = true;
      isConnecting.value = false;
      terminal.writeln("\r\n\x1b[32mTerminal connected!\x1b[0m\r\n");

      // Send initial terminal size
      const { cols, rows } = terminal;
      websocket?.send(
        JSON.stringify({
          type: "resize",
          data: { cols, rows },
        }),
      );
    };

    websocket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.type === "output" && message.data) {
          terminal.write(message.data);
        } else if (message.type === "error") {
          terminal.writeln(`\r\n\x1b[31mError: ${message.data}\x1b[0m\r\n`);
        }
      } catch (error) {
        console.error("Failed to parse WebSocket message:", error);
      }
    };

    websocket.onclose = () => {
      isConnected.value = false;
      terminal.writeln("\r\n\x1b[33mConnection closed\x1b[0m\r\n");
    };

    websocket.onerror = (error) => {
      isConnected.value = false;
      isConnecting.value = false;
      connectionError.value = "WebSocket connection failed";
      terminal.writeln("\r\n\x1b[31mConnection error\x1b[0m\r\n");
    };
  } catch (error) {
    isConnecting.value = false;
    connectionError.value = `Connection failed: ${error}`;
  }
}

async function reconnect() {
  cleanup();
  await connectWebSocket();
}

async function stopSession() {
  if (!session.value) return;

  try {
    await fetch(`http://localhost:5000/session?sess=${session.value.id}`, {
      method: "DELETE",
    });
    terminal.writeln(
      `\r\n\x1b[33mSession ${session.value.id} stopped\x1b[0m\r\n`,
    );
  } catch (error) {
    terminal.writeln(`\r\n\x1b[31mFailed to stop session: ${error}\x1b[0m\r\n`);
  }

  localStorage.removeItem(SESSION_KEY);
  session.value = null;
  cleanup();
}

function increaseFontSize() {
  if (fontSize.value < 24) {
    fontSize.value += 1;
    updateFontSize();
  }
}

function decreaseFontSize() {
  if (fontSize.value > 8) {
    fontSize.value -= 1;
    updateFontSize();
  }
}

function updateFontSize() {
  if (terminal) {
    terminal.options.fontSize = fontSize.value;
    // Simple font size update
    setTimeout(() => {
      fitAddon.fit();
      // Send updated size to backend
      const { cols, rows } = terminal;
      if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(
          JSON.stringify({
            type: "resize",
            data: { cols, rows },
          }),
        );
      }
    }, 100);
  }
}
</script>

<template>
  <div class="terminal-container">
    <div
      class="terminal-header bg-zinc-800 text-white p-2 rounded-t-lg flex justify-between items-center"
    >
      <div class="flex items-center gap-2">
        <div
          class="w-3 h-3 rounded-full"
          :class="
            isConnected
              ? 'bg-green-500'
              : isConnecting
                ? 'bg-yellow-500'
                : 'bg-red-500'
          "
        ></div>
        <span class="text-sm font-mono">
          {{ session ? `${session.id}:${session.port}` : "No session" }}
        </span>
      </div>
      <div class="flex gap-2">
        <div class="flex items-center gap-1">
          <button
            @click="decreaseFontSize"
            :disabled="fontSize <= 8"
            class="px-2 py-1 text-xs bg-gray-600 rounded hover:bg-gray-500 disabled:opacity-50"
            title="Decrease font size"
          >
            A-
          </button>
          <span class="text-xs px-1">{{ fontSize }}px</span>
          <button
            @click="increaseFontSize"
            :disabled="fontSize >= 24"
            class="px-2 py-1 text-xs bg-gray-600 rounded hover:bg-gray-500 disabled:opacity-50"
            title="Increase font size"
          >
            A+
          </button>
        </div>
        <button
          @click="reconnect"
          :disabled="isConnecting"
          class="px-2 py-1 text-xs bg-blue-600 rounded hover:bg-blue-500 disabled:opacity-50"
        >
          {{ isConnecting ? "Connecting..." : "Reconnect" }}
        </button>
        <button
          @click="stopSession"
          class="px-2 py-1 text-xs bg-red-600 rounded hover:bg-red-500"
        >
          Stop
        </button>
      </div>
    </div>

    <div
      ref="terminalContainer"
      class="terminal-content bg-black rounded-b-lg"
      style="height: 400px; width: 100%"
    ></div>

    <div
      v-if="connectionError"
      class="mt-2 p-2 bg-red-900 text-red-200 rounded text-sm"
    >
      {{ connectionError }}
    </div>

    <div
      v-if="isConnecting && !session"
      class="mt-2 p-2 bg-yellow-900 text-yellow-200 rounded text-sm"
    >
      Creating new Docker session...
    </div>
  </div>
</template>

<style scoped>
.terminal-container {
  font-family: "Cascadia Code", "Fira Code", "Monaco", "Menlo", monospace;
}

.terminal-content {
  /* Ensure consistent box-sizing */
  box-sizing: border-box;
}

.terminal-content :deep(.xterm-viewport) {
  border-radius: 0 0 0.5rem 0.5rem;
}

/* Ensure xterm elements have proper positioning */
.terminal-content :deep(.xterm-screen) {
  position: relative;
}

.terminal-content :deep(.xterm-selection-layer) {
  position: absolute;
  pointer-events: none;
}
</style>
