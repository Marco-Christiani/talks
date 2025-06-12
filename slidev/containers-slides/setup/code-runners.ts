import { defineCodeRunnersSetup } from "@slidev/types";

const BACKEND_URL = "http://localhost:5000";
const SESSION_KEY = "docker-session";

interface Session {
  id: string;
  port: number;
}

async function getSession(): Promise<Session> {
  const cached = localStorage.getItem(SESSION_KEY);
  if (cached) {
    const parsed = JSON.parse(cached);
    const res = await fetch(`${BACKEND_URL}/session?sess=${parsed.id}`);
    if (res.ok) return parsed;
    localStorage.removeItem(SESSION_KEY);
  }

  const res = await fetch(`${BACKEND_URL}/session?wait=true`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) throw new Error("Failed to create Docker session");
  const session = await res.json();
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
  return session;
}

export default defineCodeRunnersSetup(() => {
  async function run(code: string, lang: "sh" | "bash" | "python") {
    const session = await getSession();

    if (lang == "bash" || lang == "sh") {
    } else if (lang == "python") {
      code = `python3 -c ${JSON.stringify(code)}`;
    }

    const res = await fetch(`${BACKEND_URL}/run?sess=${session.id}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cmd: code }),
    });

    const output = await res.text();
    return {
      text: output,
      class: "text-green-400",
      highlightLang: "shell",
    };
  }

  return {
    async sh(code: string) {
      return run(code, "sh");
    },

    async bash(code: string) {
      return run(code, "bash");
    },

    async python(code: string) {
      return run(code, "python");
    },
  };
});
