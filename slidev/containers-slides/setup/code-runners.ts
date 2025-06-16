import { defineCodeRunnersSetup } from "@slidev/types";
import { getSession, BACKEND_HTTP_URL } from "@lib/session";


export default defineCodeRunnersSetup(() => {
  async function run(code: string, lang: "sh" | "bash" | "python") {
    const session = await getSession();

    if (lang === "python") {
      code = `python3 -c ${JSON.stringify(code)}`;
    }

    const res = await fetch(`${BACKEND_HTTP_URL}/run?sess=${session.id}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cmd: code }),
    });

    const output = await res.text();
    return {
      text: output,
      class: "text-green-400",
      highlightLang: "text",
    };
  }

  return {
    sh: (code: string) => run(code, "sh"),
    bash: (code: string) => run(code, "bash"),
    python: (code: string) => run(code, "python"),
  };
});
