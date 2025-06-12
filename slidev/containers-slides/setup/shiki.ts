/* ./setup/shiki.ts */
import { defineShikiSetup } from "@slidev/types";

export default defineShikiSetup(() => {
  return {
    langs: [
      "bash",
      "zsh",
      "yaml",
      "docker",
      "markdown",
      "python",
      import("@shikijs/langs/hcl"),
      import("@shikijs/langs/dockerfile"),
    ],
  };
});
