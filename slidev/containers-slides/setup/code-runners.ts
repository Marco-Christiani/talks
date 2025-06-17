// setup/code-runners.ts
import { defineCodeRunnersSetup } from "@slidev/types";
import { useNav } from '@slidev/client'
import { getSession, BACKEND_HTTP_URL } from "@lib/session";
const { currentPage } = useNav()

const getWorkspaceId = () => `slide-${currentPage.value}`


export default defineCodeRunnersSetup(() => {
  async function runCode(code: string, language: string) {
    const session = await getSession();
    const workspaceId = getWorkspaceId()

    // Check if this is a file write
    const isFileWrite = code.trim().startsWith('# file:');

    let finalCmd = code;

    // Handle language-specific execution for non-file write ops
    if (!isFileWrite) {
      switch (language) {
        case "python":
          finalCmd = `python3 -c ${JSON.stringify(code)}`;
          break;
        case "node":
        case "javascript":
          finalCmd = `node -e ${JSON.stringify(code)}`;
          break;
        case "bash":
        case "sh":
          // Use as-is
          break;
        default:
          // For other languages, assume they can be executed directly
          break;
      }
    }

    const res = await fetch(`${BACKEND_HTTP_URL}/run?sess=${session.id}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        cmd: finalCmd,
        workspace_id: workspaceId,
      }),
    });

    const result = await res.json();

    return {
      text: result.output,
      class: result.exit_code === 0 ? "text-green-400" : "text-red-400",
      highlightLang: "text",
    };
  }

  return {
    // File operations
    file: (code: string) => runCode(code, "file"),

    // Language runners
    sh: (code: string) => runCode(code, "sh"),
    bash: (code: string) => runCode(code, "bash"),
    python: (code: string, ctx) => {
      console.log(ctx.options)
      return runCode(code, "python")
    },
    javascript: (code: string) => runCode(code, "javascript"),
    node: (code: string) => runCode(code, "node"),
    dockerfile: (code: string) => runCode(code, "dockerfile"),

    // Generic runner
    run: (code: string) => runCode(code, "sh"),
  };
});
