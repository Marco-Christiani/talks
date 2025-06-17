// lib/session.ts
//
// Usage
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
//const session = useSession();
// watchEffect(() => {
//   console.log("session changed", session.value);
// })
import { ref } from 'vue';

export interface Session {
  id: string;
}

export const BACKEND_HOST =
  (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
    ? "127.0.0.1:5000"
    : "docker-workshop.com";
export const BACKEND_HTTP_URL =
  (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
    ? `http://${BACKEND_HOST}`
    : `https://${BACKEND_HOST}`;
export const SESSION_KEY = "docker-session";

const session = ref<Session | null>(null);
let inFlight: Promise<Session> | null = null;

export function useSession() {
  return session;
}

export async function getSession(): Promise<Session> {
  if (session.value) return session.value;

  const cached = localStorage.getItem(SESSION_KEY);
  if (cached) {
    const parsed: Session = JSON.parse(cached);
    const res = await fetch(`${BACKEND_HTTP_URL}/session?sess=${parsed.id}`);
    if (res.ok) {
      session.value = parsed;
      return parsed;
    }
    localStorage.removeItem(SESSION_KEY);
  }

  if (!inFlight) {
    inFlight = fetch(`${BACKEND_HTTP_URL}/session?wait=true`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    })
      .then(async (res) => {
        if (!res.ok) throw new Error("Failed to create Docker session");
        const sess: Session = await res.json();
        session.value = sess;
        localStorage.setItem(SESSION_KEY, JSON.stringify(sess));
        return sess;
      })
      .finally(() => {
        inFlight = null;
      });
  }

  return inFlight;
};
