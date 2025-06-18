<!-- components/Terminal.vue -->
<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from "vue";
import { useSession, getSession, useWebSocket, useSessionActions } from "@lib/session";
import { Terminal } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import { WebglAddon } from "@xterm/addon-webgl";
import { ClipboardAddon } from "@xterm/addon-clipboard";
import "@xterm/xterm/css/xterm.css";

const props = defineProps<{ show: boolean }>();
const emit = defineEmits<{ close: [] }>();

const terminalContainer = ref<HTMLElement>();
const { session, isConnecting, connectionError } = useSession();
const { stopSession, clearSession } = useSessionActions();
const { createTerminalWebSocket } = useWebSocket();

const isConnected = ref(false);
const fontSize = ref(14);

let terminal: Terminal;
let fitAddon: FitAddon;
let websocket: WebSocket | null = null;
let terminalInitialized = false;

watch(
  () => props.show,
  async (newShow) => {
    if (newShow) {
      await initializeSession();
      await nextTick();
      setTimeout(async () => {
        if (!terminal || !terminalContainer.value?.hasChildNodes()) {
          await initializeTerminal();
        } else {
          refitTerminal();
        }
      }, 100);
    } else {
      cleanup();
    }
  },
);

onMounted(() => {
  if (props.show) initializeSession();
  document.addEventListener("keydown", handleKeydown);
});

onUnmounted(() => {
  cleanup();
  document.removeEventListener("keydown", handleKeydown);
});

async function initializeSession() {
  try {
    await getSession();
  } catch (err) {
    connectionError.value = `Failed to create session: ${err}`;
  }
}

async function initializeTerminal() {
  if (!session.value || !terminalContainer.value) return;

  if (terminal) terminal.dispose();
  terminalContainer.value.innerHTML = "";

  terminal = new Terminal({
    cursorBlink: true,
    fontSize: fontSize.value,
    fontFamily: "monospace",
    theme: {
      background: "#1a1a1a",
      foreground: "#ffffff",
      cursor: "#ffffff",
      selectionForeground: "#3d3d3d",
    },
    convertEol: true,
    scrollback: 1000,
  });

  fitAddon = new FitAddon();
  terminal.loadAddon(fitAddon);
  terminal.loadAddon(new ClipboardAddon());

  try {
    terminal.loadAddon(new WebglAddon());
  } catch { }

  terminal.open(terminalContainer.value);
  await nextTick();
  setTimeout(() => fitAddon.fit(), 100);

  terminal.onData((data) => {
    if (websocket?.readyState === WebSocket.OPEN) {
      websocket.send(JSON.stringify({ type: "input", data }));
    }
  });

  terminal.onResize(({ cols, rows }) => {
    if (websocket?.readyState === WebSocket.OPEN) {
      websocket.send(JSON.stringify({ type: "resize", data: { cols, rows } }));
    }
  });

  await connectWebSocket();
}

async function connectWebSocket() {
  if (!session.value) return;
  try {
    websocket = await createTerminalWebSocket(session.value.id);

    websocket.onopen = () => {
      isConnected.value = true;
      terminal.writeln("\r\n\x1b[32mConnected! Starting session...\x1b[0m\r\n");
      const { cols, rows } = terminal;
      websocket.send(JSON.stringify({ type: "resize", data: { cols, rows } }));
    };

    websocket.onmessage = (event) => {
      if (!terminal) return;
      try {
        const message = JSON.parse(event.data);
        if (message.type === "output") terminal.write(message.data);
        else if (message.type === "error") terminal.writeln(`\r\n\x1b[31mError: ${message.data}\x1b[0m\r\n`);
      } catch (error) {
        console.error("Failed to parse message:", error);
      }
    };

    websocket.onclose = () => {
      isConnected.value = false;
      if (terminal) terminal.writeln("\r\n\x1b[33mConnection closed\x1b[0m\r\n");
    };

    websocket.onerror = () => {
      isConnected.value = false;
      connectionError.value = "WebSocket connection failed";
      if (terminal) terminal.writeln("\r\n\x1b[31mConnection error\x1b[0m\r\n");
    };
  } catch (err) {
    connectionError.value = `Connection failed: ${err}`;
  }
}

function cleanup() {
  if (websocket) {
    websocket.onopen = null;
    websocket.onmessage = null;
    websocket.onclose = null;
    websocket.onerror = null;
    websocket.close();
  }

  websocket = null;
  terminal?.dispose();
  terminal = null;
  isConnected.value = false;
  terminalInitialized = false;
}


async function reconnect() {
  cleanup();
  await initializeSession();
  await nextTick();             // wait for DOM
  await initializeTerminal();   // rebuild XTerm + container + socket
}


function refitTerminal() {
  if (!terminal || !fitAddon) return;
  fitAddon.fit();
  const { cols, rows } = terminal;
  if (cols > 2 && rows > 1 && websocket?.readyState === WebSocket.OPEN) {
    websocket.send(JSON.stringify({ type: "resize", data: { cols, rows } }));
  }
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
    setTimeout(() => {
      fitAddon.fit();
      const { cols, rows } = terminal;
      if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify({ type: "resize", data: { cols, rows } }));
      }
    }, 100);
  }
}

function tmuxCommand(keySequence: string) {
  if (websocket?.readyState !== WebSocket.OPEN) return;
  websocket.send(JSON.stringify({ type: "input", data: "\x02" }));
  for (const ch of keySequence) {
    websocket.send(JSON.stringify({ type: "input", data: ch }));
  }
}

function sendTmuxCommand(command: string) {
  if (websocket?.readyState === WebSocket.OPEN) {
    websocket.send(JSON.stringify({ type: "tmux_command", data: command }));
  }
}

function closePopup() {
  emit("close");
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === "Escape" && props.show) closePopup();
}
</script>

<template>
  <!-- Modal Backdrop -->
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center" style="z-index: 9999"
      @click="closePopup">
      <!-- Modal Content -->
      <div class="bg-zinc-900 rounded-lg shadow-2xl w-[90vw] h-[80vh] max-w-6xl flex flex-col relative"
        style="z-index: 10000" @click.stop>
        <!-- Header with close button -->
        <div class="terminal-header bg-zinc-800 text-white px-2 py-1 rounded-t-lg flex justify-between items-center">
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 rounded-full"
              :class="isConnected ? 'bg-green-500' : isConnecting ? 'bg-yellow-500' : 'bg-red-500'"></div>
            <span class="text-sm font-mono">
              {{ session ? session.id : "No session" }}
            </span>

            <!-- Window Controls -->
            <div class="tmux-controls flex gap-2 ml-4">
              <button @click="tmuxCommand('c')" class="px-1 py-1 text-xs bg-green-600 rounded hover:bg-green-500"
                title="New Window (Ctrl+b, c)">
                +
              </button>
              <button @click="tmuxCommand('p')" class="px-1 py-1 text-xs bg-blue-600 rounded hover:bg-blue-500"
                title="Previous Window (Ctrl+b, p)">
                ←
              </button>
              <button @click="tmuxCommand('n')" class="px-1 py-1 text-xs bg-blue-600 rounded hover:bg-blue-500"
                title="Next Window (Ctrl+b, n)">
                →
              </button>
              <button @click="tmuxCommand('o')" class="px-2 py-1 text-xs bg-blue-600 rounded hover:bg-orange-500"
                title="Switch Pane (Ctrl+b, o)">
                ⧉
              </button>
              <button @click="tmuxCommand('%')" class="px-2 py-1 text-xs bg-purple-600 rounded hover:bg-purple-500"
                title="Split Vertical (Ctrl+b, %)">
                |
              </button>
              <button @click="sendTmuxCommand('kill-pane')"
                class="px-2 py-1 text-xs bg-red-600 rounded hover:bg-red-500" title="Close Pane">
                ×
              </button>
            </div>
          </div>

          <div class="flex gap-2 items-center">
            <!-- Font size controls -->
            <div class="flex items-center gap-1">
              <button @click="decreaseFontSize" :disabled="fontSize <= 8"
                class="px-2 py-1 text-xs bg-gray-600 rounded hover:bg-gray-500 disabled:opacity-50"
                title="Decrease font size">
                -
              </button>
              <span class="text-xs px-1">{{ fontSize }}px</span>
              <button @click="increaseFontSize" :disabled="fontSize >= 24"
                class="px-2 py-1 text-xs bg-gray-600 rounded hover:bg-gray-500 disabled:opacity-50"
                title="Increase font size">
                +
              </button>
            </div>

            <!-- Connection controls -->
            <button @click="reconnect" :disabled="isConnecting"
              class="px-2 py-1 text-xs bg-blue-600 rounded hover:bg-blue-500 disabled:opacity-50">
              {{ isConnecting ? "Connecting..." : isConnected ? "Reconnect" : "Start" }}
            </button>
            <button @click="stopSession" class="px-2 py-1 text-xs bg-red-600 rounded hover:bg-red-500">Stop</button>

            <!-- Close popup button -->
            <button @click="closePopup" class="px-2 py-1 text-xs bg-gray-600 rounded hover:bg-gray-500 ml-2"
              title="Close Terminal (ESC)">
              ✕
            </button>
          </div>
        </div>

        <!-- Terminal content -->
        <div ref="terminalContainer" class="terminal-content bg-black rounded-b-lg flex-1" style="width: 100%"></div>

        <!-- Error display -->
        <div v-if="connectionError" class="mx-2 mb-2 p-2 bg-red-900 text-red-200 rounded text-sm">
          {{ connectionError }}
        </div>

        <div v-if="isConnecting && !session" class="mx-2 mb-2 p-2 bg-yellow-900 text-yellow-200 rounded text-sm">
          Creating new Docker session...
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.terminal-container {
  font-family: "Cascadia Code", "Fira Code", "Monaco", "Menlo", monospace;
}

.terminal-content {
  box-sizing: border-box;
}

.terminal-content :deep(.xterm-viewport) {
  border-radius: 0 0 0.5rem 0.5rem;
}

.terminal-content :deep(.xterm-screen) {
  position: relative;
}

.terminal-content :deep(.xterm-selection-layer) {
  position: absolute;
  pointer-events: none;
}
</style>
