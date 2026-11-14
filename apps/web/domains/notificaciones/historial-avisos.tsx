import { Icono } from "@/components/ui/icono";
import { fechaHoraCorta } from "@/lib/fechas";
import type { Aviso } from "./api";
import estilos from "./avisos.module.css";

/** Avisos enviados de una cita (RF-26, RF-42). */
export function HistorialAvisos({ avisos, hoy }: { avisos: Aviso[]; hoy: string }) {
  if (avisos.length === 0) return null;
  return (
    <section>
      <h2 className={estilos.titulo}>Avisos enviados</h2>
      <ol className={estilos.avisos}>
        {avisos.map((aviso) => (
          <li key={aviso.cuando}>
            <span className={`${estilos.marca} ${aviso.atencion ? estilos.atencion : ""}`}>
              <Icono nombre={aviso.atencion ? "alerta" : "check"} tamano={18} />
            </span>
            <p>
              {aviso.texto}
              <small>{fechaHoraCorta(aviso.cuando, hoy)}</small>
            </p>
          </li>
        ))}
      </ol>
    </section>
  );
}
