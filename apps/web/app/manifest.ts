import type { MetadataRoute } from "next";

// PWA del panel (ADR-0004). La reserva pública no se instala: solo el panel.
export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Turnero",
    short_name: "Turnero",
    description: "Agenda de la barbería",
    start_url: "/panel/agenda",
    scope: "/panel",
    display: "standalone",
    lang: "es-CO",
    background_color: "#ffffff",
    theme_color: "#111827",
    icons: [
      { src: "/iconos/icon-192.png", sizes: "192x192", type: "image/png" },
      { src: "/iconos/icon-512.png", sizes: "512x512", type: "image/png" },
    ],
  };
}
