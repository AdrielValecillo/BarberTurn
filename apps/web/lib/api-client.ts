import type { paths } from "@turnero/api-types";
import createClient from "openapi-fetch";

// Cliente HTTP base de la API, tipado con el OpenAPI generado (make gen-types).
export const api = createClient<paths>({
  baseUrl: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
});
