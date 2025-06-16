<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from "vue";
  import { BACKEND_URL, getSession, SESSION_KEY, useSession } from '@lib/session';
import { Terminal } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import { WebglAddon } from "@xterm/addon-webgl";
import { ClipboardAddon } from "@xterm/addon-clipboard";
import "@xterm/xterm/css/xterm.css";

const terminalContainer = ref<HTMLElement>();
const session = useSession();
const isConnected = ref(false);
const isConnecting = ref(false);
const connectionError = ref("");
const fontSize = ref(14);
const showHelp = ref(false);

let terminal: Terminal;
let fitAddon: FitAddon;
let websocket: WebSocket | null = null;


onMounted(async () => {
  await initializeSession();
  observeTerminalVisibility();
});


function observeTerminalVisibility() {
  if (!terminalContainer.value) return;

  const observer = new IntersectionObserver(async ([entry]) => {
    if (entry.isIntersecting) {
      if (!terminal) {
        await initializeTerminal(); // safe to call once
      } else {
        setTimeout(refitTerminal, 50); // DOM might have resized
      }
    }
  }, {
    root: null, // default to viewport
    threshold: 0.1,
  });

  observer.observe(terminalContainer.value);
  onUnmounted(() => observer.disconnect());
}

function refitTerminal() {
  if (!terminal || !fitAddon) return;

  fitAddon.fit();

  const { cols, rows } = terminal;
  if (cols > 2 && rows > 1 && websocket && websocket.readyState === WebSocket.OPEN) {
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
  isConnected.value = false;
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

let terminalInitialized = false;

async function initializeTerminal() {
  if (terminalInitialized || !session.value || !terminalContainer.value) return;
  terminalInitialized = true;

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

  // Attach to resize event
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
        } else if (message.type == "message" && message.data == "ready"){
          showMessage( 
          "This terminal supports multiple tabs and split panes using tmux, you may use standard keybinds to navigate or use the buttons/mouse."
          );
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
    await fetch(`${BACKEND_URL}/session?sess=${session.value.id}`, {
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
    // First send the Ctrl+B prefix
    websocket.send(
      JSON.stringify({
        type: "input",
        data: "\x02",
      }),
    );

    // Then send each character separately
    for (const ch of keySequence) {
      // Delay
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
      data: command, // e.g. "split-window -h"
    }),
  );
}


const infoMessage = ref<string | null>(null);
let timeout: number | null = null;

function showMessage(msg: string, durationMs = 5000) {
  infoMessage.value = msg;

  if (timeout !== null) {
    clearTimeout(timeout);
  }

  timeout = window.setTimeout(() => {
    infoMessage.value = null;
  }, durationMs);
}

function onAfterLeave() {
  timeout = null;
}
</script>

<template>
  <div class="terminal-container">
    <transition name="fade-message" @after-leave="onAfterLeave">
      <div v-if="infoMessage"
          class="absolute top-4 right-0 bg-zinc-800 text-white w-1/2 text-xs px-4 py-2 rounded shadow-md pointer-events-none z-50">
        {{ infoMessage }}
      </div>
    </transition>

    <div class="terminal-header bg-zinc-800 text-white px-2 py-1 rounded-t-lg flex justify-between items-center">
      <div class="flex items-center gap-2">
        <div class="w-3 h-3 rounded-full"
          :class="isConnected ? 'bg-green-500' : isConnecting ? 'bg-yellow-500' : 'bg-red-500' "
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
            <MdiAdd />
          </button>
          <button
            @click="tmuxCommand('p')"
            class="px-1 py-1 text-xs bg-blue-600 rounded hover:bg-blue-500"
            title="Previous Window (Ctrl+b, p)"
          >
            <MdiArrowLeft />
          </button>
          <button
            @click="tmuxCommand('n')"
            class="px-1 py-1 text-xs bg-blue-600 rounded hover:bg-blue-500"
            title="Next Window (Ctrl+b, n)"
          >
            <MdiArrowRight />
          </button>

          <!-- Pane controls -->
          <button
            @click="tmuxCommand('o')"
            class="px-2 py-1 text-xs bg-blue-600 rounded hover:bg-orange-500"
            title="Switch Pane (Ctrl+b, o)"
          >
            <MdiWindowRestore />
            <!-- <MdiAlignVerticalDistribute /> -->
            <!-- <MdiDragVerticalVariant /> -->
          </button>
          <button
            @click="tmuxCommand('%')"
            class="px-2 py-1 text-xs bg-purple-600 rounded hover:bg-purple-500"
            title="Split Vertical (Ctrl+b, %)"
          >
            <MdiAlignHorizontalDistribute />
          </button>
          <!-- <button @click="tmuxCommand('\"')"
                  class="px-2 py-1 text-xs bg-purple-600 rounded hover:bg-purple-500"
                  title="Split Horizontal (Ctrl+b, \")">
            ⬒
          </button> -->

          <!-- Close pane -->
          <!-- <button
            @click="tmuxCommand('xy\r')"
            class="px-2 py-1 text-xs bg-red-600 rounded hover:bg-red-500"
            title="Close Pane (Ctrl+b, x)"
          >
            <MdiClose />
          </button> -->
          <!-- <button onclick='sendTmuxCommand("split-window -h")'>
            Split Horizontally
          </button> -->
          <button @click="sendTmuxCommand('kill-pane')">
            <MdiClose />
          </button>
        </div>
      </div>
      <div class="flex gap-2">
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
        <button
          @click="reconnect"
          :disabled="isConnecting"
          class="px-2 py-1 text-xs bg-blue-600 rounded hover:bg-blue-500 disabled:opacity-50"
        >
          {{ isConnecting ? "Connecting..." : (isConnected ? "Reconnect" : "Start") }}
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
      style="height: 100%; width: 100%"
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

    <!-- <button -->
    <!--   @click="showHelp = true" -->
    <!--   class="mt-2 px-1 py-1 text-sm bg-blue-600 rounded hover:blue-500" -->
    <!-- > -->
    <!--   Help -->
    <!-- </button> -->
    <!-- <div
      v-if="showHelp"
      class="help-overlay absolute inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 text-black"
    >
      <div class="bg-white p-6 rounded-lg max-w-md">
        <h3 class="font-bold mb-4">Terminal Shortcuts</h3>
        <div class="space-y-2 text-md">
          <div><kbd>Ctrl+T</kbd> - New tab</div>
          <div><kbd>Ctrl+PageUp/PageDown</kbd> - Switch tabs</div>
          <div><kbd>Ctrl+Alt+→</kbd> - Split right</div>
          <div><kbd>Ctrl+Alt+↓</kbd> - Split down</div>
          <div><kbd>Ctrl+W</kbd> - Close current pane/tab</div>
        </div>
        <button
          @click="showHelp = false"
          class="mt-4 px-4 py-2 bg-blue-500 text-white rounded"
        >
          Got it!
        </button>
      </div>
    </div> -->
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

.fade-message-enter-active,
.fade-message-leave-active {
  transition: opacity 0.5s ease, transform 0.5s ease;
}

.fade-message-enter-from,
.fade-message-leave-to {
  opacity: 0;
  transform: translateX(100px);
}

.fade-message-enter-to,
.fade-message-leave-from {
  opacity: 1;
  transform: translateX(0);
}
</style>
