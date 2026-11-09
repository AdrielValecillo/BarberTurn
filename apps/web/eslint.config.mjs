import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const dominios = ["agenda", "barberias", "clientes", "notificaciones"];

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Un dominio no importa componentes de otro; lo compartido sube a components/ui/ (doc 11).
  ...dominios.map((dominio) => ({
    files: [`domains/${dominio}/**/*.{ts,tsx}`],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: dominios.filter((d) => d !== dominio).map((d) => `@/domains/${d}/**`),
              message: "Un dominio no importa a otro: sube lo compartido a components/ui/.",
            },
          ],
        },
      ],
    },
  })),
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
  ]),
]);

export default eslintConfig;
