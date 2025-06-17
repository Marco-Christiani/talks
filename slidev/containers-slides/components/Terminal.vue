<!-- components/Terminal.vue -->
<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from "vue";
import {
  BACKEND_HTTP_URL,
  getSession,
  SESSION_KEY,
  useSession,
} from "@lib/session";
import { Terminal } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import { WebglAddon } from "@xterm/addon-webgl";
import { ClipboardAddon } from "@xterm/addon-clipboard";
import "@xterm/xterm/css/xterm.css";

const props = defineProps<{
  show: boolean;
}>();

const emit = defineEmits<{
  close: [];
}>();

const terminalContainer = ref<HTMLElement>();
const session = useSession();
const isConnected = ref(false);
const isConnecting = ref(false);
const connectionError = ref("");
const fontSize = ref(14);

let terminal: Terminal;
let fitAddon: FitAddon;
let websocket: WebSocket | null = null;
let terminalInitialized = false;

// Watch for popup visibility changes
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
      // Clean up when closing
      cleanup();
    }
  },
);

onMounted(async () => {
  if (props.show) {
    await initializeSession();
  }
});

function refitTerminal() {
  if (!terminal || !fitAddon) return;

  fitAddon.fit();

  const { cols, rows } = terminal;
  if (
    cols > 2 &&
    rows > 1 &&
    websocket &&
    websocket.readyState === WebSocket.OPEN
  ) {
    websocket.send(
      JSON.stringify({
        type: "resize",
        data: { cols, rows },
      }),
    );
  }
}

onUnmounted(() => {
  cleanup();
});

function cleanup() {
  if (websocket) {
    websocket.close();
    websocket = null;
  }
  if (terminal) {
    terminal.dispose();
    terminal = null;
  }
  isConnected.value = false;
  terminalInitialized = false;
}

async function initializeSession() {
  isConnecting.value = true;
  connectionError.value = "";

  try {
    await getSession();
  } catch (err) {
    connectionError.value = `Failed to create session: ${err}`;
  } finally {
    isConnecting.value = false;
  }
}

async function initializeTerminal() {
  if (!session.value || !terminalContainer.value) return;

  // Clear any existing terminal content
  if (terminal) {
    terminal.dispose();
  }

  // Clear the container
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
    allowTransparency: false,
    convertEol: true,
    scrollback: 1000,
  });

  fitAddon = new FitAddon();
  terminal.loadAddon(fitAddon);

  const clipAddon = new ClipboardAddon();
  terminal.loadAddon(clipAddon);

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

  await connectWebSocket();
}

async function connectWebSocket() {
  if (!session.value) return;

  isConnecting.value = true;
  connectionError.value = "";

  try {
    const wsUrl =
      window.location.hostname === "localhost" ||
      window.location.hostname === "127.0.0.1"
        ? `ws://127.0.0.1:5000/ws?sess=${session.value.id}`
        : `wss://${window.location.hostname}/ws?sess=${session.value.id}`;

    websocket = new WebSocket(wsUrl);

    websocket.onopen = () => {
      isConnected.value = true;
      isConnecting.value = false;
      terminal.writeln("\r\n\x1b[32mConnected! Starting session...\x1b[0m\r\n");

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
  await initializeSession();
  await connectWebSocket();
}

async function stopSession() {
  if (!session.value) return;

  try {
    await fetch(`${BACKEND_HTTP_URL}/session?sess=${session.value.id}`, {
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
    setTimeout(() => {
      fitAddon.fit();
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

function tmuxCommand(keySequence: string) {
  if (websocket && websocket.readyState === WebSocket.OPEN) {
    websocket.send(
      JSON.stringify({
        type: "input",
        data: "\x02",
      }),
    );

    for (const ch of keySequence) {
      setTimeout(() => {
        fitAddon.fit();
      }, 100);

      websocket.send(
        JSON.stringify({
          type: "input",
          data: ch,
        }),
      );
    }
  }
}

function sendTmuxCommand(command: string) {
  websocket.send(
    JSON.stringify({
      type: "tmux_command",
      data: command,
    }),
  );
}

function closePopup() {
  emit("close");
}

// Handle ESC key to close popup
function handleKeydown(event: KeyboardEvent) {
  if (event.key === "Escape" && props.show) {
    closePopup();
  }
}

onMounted(() => {
  document.addEventListener("keydown", handleKeydown);
});

onUnmounted(() => {
  document.removeEventListener("keydown", handleKeydown);
});
</script>

<template>
  <!-- Modal Backdrop -->
  <Teleport to="body">
    <div
      v-if="show"
      class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center"
      style="z-index: 9999"
      @click="closePopup"
    >
      <!-- Modal Content -->
      <div
        class="bg-zinc-900 rounded-lg shadow-2xl w-[90vw] h-[80vh] max-w-6xl flex flex-col relative"
        style="z-index: 10000"
        @click.stop
      >
        <!-- Header with close button -->
        <div
          class="terminal-header bg-zinc-800 text-white px-2 py-1 rounded-t-lg flex justify-between items-center"
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

            <!-- Window Controls -->
            <div class="tmux-controls flex gap-2 ml-4">
              <button
                @click="tmuxCommand('c')"
                class="px-1 py-1 text-xs bg-green-600 rounded hover:bg-green-500"
                title="New Window (Ctrl+b, c)"
              >
                +
              </button>
              <button
                @click="tmuxCommand('p')"
                class="px-1 py-1 text-xs bg-blue-600 rounded hover:bg-blue-500"
                title="Previous Window (Ctrl+b, p)"
              >
                ←
              </button>
              <button
                @click="tmuxCommand('n')"
                class="px-1 py-1 text-xs bg-blue-600 rounded hover:bg-blue-500"
                title="Next Window (Ctrl+b, n)"
              >
                →
              </button>
              <button
                @click="tmuxCommand('o')"
                class="px-2 py-1 text-xs bg-blue-600 rounded hover:bg-orange-500"
                title="Switch Pane (Ctrl+b, o)"
              >
                ⧉
              </button>
              <button
                @click="tmuxCommand('%')"
                class="px-2 py-1 text-xs bg-purple-600 rounded hover:bg-purple-500"
                title="Split Vertical (Ctrl+b, %)"
              >
                |
              </button>
              <button
                @click="sendTmuxCommand('kill-pane')"
                class="px-2 py-1 text-xs bg-red-600 rounded hover:bg-red-500"
                title="Close Pane"
              >
                ×
              </button>
            </div>
          </div>

          <div class="flex gap-2 items-center">
            <!-- Font size controls -->
            <div class="flex items-center gap-1">
              <button
                @click="decreaseFontSize"
                :disabled="fontSize <= 8"
                class="px-2 py-1 text-xs bg-gray-600 rounded hover:bg-gray-500 disabled:opacity-50"
                title="Decrease font size"
              >
                -
              </button>
              <span class="text-xs px-1">{{ fontSize }}px</span>
              <button
                @click="increaseFontSize"
                :disabled="fontSize >= 24"
                class="px-2 py-1 text-xs bg-gray-600 rounded hover:bg-gray-500 disabled:opacity-50"
                title="Increase font size"
              >
                +
              </button>
            </div>

            <!-- Connection controls -->
            <button
              @click="reconnect"
              :disabled="isConnecting"
              class="px-2 py-1 text-xs bg-blue-600 rounded hover:bg-blue-500 disabled:opacity-50"
            >
              {{
                isConnecting
                  ? "Connecting..."
                  : isConnected
                    ? "Reconnect"
                    : "Start"
              }}
            </button>
            <button
              @click="stopSession"
              class="px-2 py-1 text-xs bg-red-600 rounded hover:bg-red-500"
            >
              Stop
            </button>

            <!-- Close popup button -->
            <button
              @click="closePopup"
              class="px-2 py-1 text-xs bg-gray-600 rounded hover:bg-gray-500 ml-2"
              title="Close Terminal (ESC)"
            >
              ✕
            </button>
          </div>
        </div>

        <!-- Terminal content -->
        <div
          ref="terminalContainer"
          class="terminal-content bg-black rounded-b-lg flex-1"
          style="width: 100%"
        ></div>

        <!-- Error display -->
        <div
          v-if="connectionError"
          class="mx-2 mb-2 p-2 bg-red-900 text-red-200 rounded text-sm"
        >
          {{ connectionError }}
        </div>

        <div
          v-if="isConnecting && !session"
          class="mx-2 mb-2 p-2 bg-yellow-900 text-yellow-200 rounded text-sm"
        >
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
