// shortcut: avisos de demostración con el contenido del diseño; pasa a la API cuando exista
// el historial de avisos de una cita (F3.11).
import { claveDia, sumarDias } from "@/lib/fechas";

export type Aviso = {
  texto: string;
  cuando: string;
  /** Algo salió distinto a lo esperado (sin respuesta, no entregado): se resalta. */
  atencion: boolean;
};

export async function obtenerAvisos(citaId: string): Promise<Aviso[]> {
  void citaId;
  const hoy = claveDia(new Date());
  const en = (dias: number, hhmm: string) => new Date(`${sumarDias(hoy, dias)}T${hhmm}:00-05:00`).toISOString();
  return [
    { texto: "Reservó desde el enlace y recibió la confirmación", cuando: en(-3, "20:12"), atencion: false },
    { texto: "Recordatorio del día anterior: leído, sin respuesta", cuando: en(-1, "15:00"), atencion: true },
    { texto: "Recordatorio de 2 horas antes: leído, sin respuesta", cuando: en(0, "13:00"), atencion: true },
  ];
}
