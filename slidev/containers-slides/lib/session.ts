// lib/session.ts
//
// Usage - Basic
//
// import { onMounted } from 'vue';
// import { getSession } from '@lib/session';
//
// onMounted(async () => {
//   const sess = await getSession();
//   console.log("Got session", sess);
// });
//
// Usage - Reactive
// const session = useSession();
// watchEffect(() => {
//   console.log("session changed", session.value);
// })
//
// Usage - Commands
// const { runCommand, stopSession, clearSession } = useSessionActions();
// await runCommand('ls -la');
// await stopSession();

import { ref, computed } from 'vue';

export interface Session {
  id: string;
}

export interface CommandResult {
  output: string;
  exitCode?: number;
  error?: string;
}

// Detect env
const isDevelopment = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";

// Backend configuration
export const BACKEND_CONFIG = {
  // Development: local backend
  development: {
    host: "127.0.0.1:5000",
    httpUrl: "http://127.0.0.1:5000",
    wsUrl: "ws://127.0.0.1:5000"
  },
  // Production: cloud backend via API subdomain
  production: {
    host: "api.docker-workshop.com",
    httpUrl: "https://api.docker-workshop.com",
    wsUrl: "wss://api.docker-workshop.com"
  }
};

// Active configuration based on environment
const activeConfig = isDevelopment ? BACKEND_CONFIG.development : BACKEND_CONFIG.production;

export const BACKEND_HOST = activeConfig.host;
export const BACKEND_HTTP_URL = activeConfig.httpUrl;
export const BACKEND_WS_URL = activeConfig.wsUrl;
export const SESSION_KEY = "docker-session";

// Global state
const session = ref<Session | null>(null);
const isConnecting = ref(false);
const connectionError = ref<string | null>(null);
let inFlight: Promise<Session> | null = null;

// Environment info for debugging
export const ENV_INFO = computed(() => ({
  environment: isDevelopment ? 'development' : 'production',
  hostname: window.location.hostname,
  backendUrl: BACKEND_HTTP_URL,
  wsUrl: BACKEND_WS_URL
}));

// Request helpers with proper headers and error handling
async function apiRequest(endpoint: string, options: RequestInit = {}): Promise<Response> {
  const url = `${BACKEND_HTTP_URL}${endpoint}`;

  const defaultHeaders = {
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0',
    'Content-Type': 'application/json'
  };

  const response = await fetch(url, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers
    }
  });

  if (!response.ok) {
    const errorText = await response.text().catch(() => response.statusText);
    throw new Error(`API request failed (${response.status}): ${errorText}`);
  }

  return response;
}

// Session management
export function useSession() {
  return {
    session: session,
    isConnecting: isConnecting,
    connectionError: connectionError,
    envInfo: ENV_INFO
  };
}

export async function getSession(): Promise<Session> {
  if (session.value) return session.value;

  isConnecting.value = true;
  connectionError.value = null;

  try {
    // Try to restore from localStorage
    const cached = localStorage.getItem(SESSION_KEY);
    if (cached) {
      const parsed: Session = JSON.parse(cached);

      // Verify session is still valid
      try {
        const response = await apiRequest(`/session?sess=${parsed.id}`);
        if (response.ok) {
          session.value = parsed;
          isConnecting.value = false;
          return parsed;
        }
      } catch (error) {
        console.warn('Cached session invalid, creating new one');
      }

      localStorage.removeItem(SESSION_KEY);
    }

    // Create new session if no valid cached session
    if (!inFlight) {
      inFlight = apiRequest('/session?wait=true', {
        method: 'POST'
      })
        .then(async (res) => {
          const sess: Session = await res.json();
          session.value = sess;
          localStorage.setItem(SESSION_KEY, JSON.stringify(sess));
          return sess;
        })
        .catch((error) => {
          connectionError.value = error.message;
          throw error;
        })
        .finally(() => {
          inFlight = null;
          isConnecting.value = false;
        });
    }

    return await inFlight;
  } catch (error) {
    isConnecting.value = false;
    connectionError.value = error instanceof Error ? error.message : 'Unknown error';
    throw error;
  }
}

export async function clearSession(): Promise<void> {
  localStorage.removeItem(SESSION_KEY);
  session.value = null;
  connectionError.value = null;
}

// Session actions
export function useSessionActions() {
  const runCommand = async (cmd: string): Promise<CommandResult> => {
    const currentSession = session.value || await getSession();

    try {
      const response = await apiRequest(`/run?sess=${currentSession.id}`, {
        method: 'POST',
        body: JSON.stringify({ cmd })
      });

      const result = await response.json();
      return {
        output: result.output || '',
        exitCode: result.exitCode,
        error: result.error
      };
    } catch (error) {
      return {
        output: '',
        error: error instanceof Error ? error.message : 'Command execution failed'
      };
    }
  };

  const stopSession = async (): Promise<void> => {
    if (!session.value) return;

    try {
      await apiRequest(`/session?sess=${session.value.id}`, {
        method: 'DELETE'
      });
    } catch (error) {
      console.warn('Error stopping session:', error);
      // Continue with cleanup even if API call fails
    } finally {
      await clearSession();
    }
  };

  const restartSession = async (): Promise<Session> => {
    await stopSession();
    return await getSession();
  };

  const checkSessionHealth = async (): Promise<boolean> => {
    if (!session.value) return false;

    try {
      const response = await apiRequest(`/session?sess=${session.value.id}`);
      return response.ok;
    } catch (error) {
      return false;
    }
  };

  return {
    runCommand,
    stopSession,
    restartSession,
    clearSession,
    checkSessionHealth
  };
}

// WebSocket utilities
export function useWebSocket() {
  const createWebSocket = (sessionId: string, path: string = '/ws'): WebSocket => {
    // Add cache busting for development
    const timestamp = isDevelopment ? `&t=${Date.now()}` : '';
    const wsUrl = `${BACKEND_WS_URL}${path}?sess=${sessionId}${timestamp}`;

    const ws = new WebSocket(wsUrl);

    ws.addEventListener('error', (error) => {
      console.error('WebSocket error:', error);
      connectionError.value = 'WebSocket connection failed';
    });

    return ws;
  };

  const createTerminalWebSocket = async (sessionId?: string): Promise<WebSocket> => {
    const targetSessionId = sessionId || (await getSession()).id;
    return createWebSocket(targetSessionId, '/ws');
  };

  return {
    createWebSocket,
    createTerminalWebSocket
  };
}

// Debugging utilities
export function debugSession() {
  console.group('Session Debug Info');
  console.log('Environment:', ENV_INFO.value);
  console.log('Current session:', session.value);
  console.log('Is connecting:', isConnecting.value);
  console.log('Connection error:', connectionError.value);
  console.log('Cached session:', localStorage.getItem(SESSION_KEY));
  console.groupEnd();
}

// Auto-cleanup on page unload
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', () => {
    // Note: We don't call stopSession here as it's async and may not complete
    // Sessions should have server-side timeouts for cleanup
  });
}
