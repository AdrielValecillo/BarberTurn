import type { Tono } from "@/components/ui/piezas";
import type { EstadoCita } from "../api";

/** Cómo se muestra cada estado de RN-08 en el panel. */
export const ESTADOS: Record<EstadoCita, { etiqueta: string; tono: Tono; cerrada: boolean }> = {
  pendiente: { etiqueta: "Sin confirmar", tono: "ambar", cerrada: false },
  confirmada: { etiqueta: "Confirmada", tono: "verde", cerrada: false },
  atendida: { etiqueta: "Atendido", tono: "gris", cerrada: true },
  no_asistio: { etiqueta: "No vino", tono: "rojo", cerrada: true },
  cancelada: { etiqueta: "Cancelada", tono: "gris", cerrada: true },
};
