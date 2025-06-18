/* ./setup/shiki.ts */
import { defineShikiSetup } from "@slidev/types";

export default defineShikiSetup(() => {
  return {
    langs: [
      "bash",
      "zsh",
      "yaml",
      "docker",
      "dockerfile",
      "markdown",
      "python",
      "hcl",
    ],
  };
});
