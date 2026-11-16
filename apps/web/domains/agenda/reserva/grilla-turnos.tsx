"use client";

import Link from "next/link";
import { useState } from "react";
import {
  deClave,
  diaSemanaCorto,
  fechaConHoy,
  fechaHoraCorta,
  franja,
  partesHora,
  precio,
  sumarDias,
} from "@/lib/fechas";
import { PRIMERO, type Barberia, type Barbero, type Servicio, type Turno } from "../api";
import { Continuar, Paso, Resumen, rutaReserva } from "./paso";
import estilos from "./reserva.module.css";

type Props = {
  barberia: Barberia;
  servicio: Servicio;
  /** Sin barbero es "El primero disponible". */
  barbero?: Barbero;
  dia: string;
  hoy: string;
  turnos: Turno[];
  /** CU-01 9a: el turno elegido se ocupó mientras llenaba los datos. */
  ocupado?: boolean;
};

const DIAS_VISIBLES = 14;
const FRANJAS = ["Mañana", "Tarde", "Noche"];

/** Paso 3 (RF-04): próximos días y turnos libres del día elegido, en mañana, tarde y noche. */
export function GrillaTurnos({ barberia, servicio, barbero, dia, hoy, turnos, ocupado }: Props) {
  const [inicio, setInicio] = useState<string>();
  const elegido = turnos.find((t) => t.inicio === inicio);
  const seleccion = { servicio: servicio.id, barbero: barbero?.id ?? PRIMERO };
  const quien = barbero ? `con ${barbero.nombre}` : "con el primero disponible";

  return (
    <Paso
      barberia={barberia.nombre}
      numero={3}
      titulo="¿A qué hora?"
      subtitulo={`${servicio.nombre} ${quien}, ${servicio.duracionMin} min`}
      atras={rutaReserva(barberia.slug, "barbero", seleccion)}
      pie={
        <>
          <Resumen
            texto={elegido ? fechaHoraCorta(elegido.inicio, hoy, barberia.zona) : "Elige una hora"}
            total={precio(servicio.precioCop)}
          />
          <Continuar
            href={
              elegido &&
              rutaReserva(barberia.slug, "datos", {
                servicio: servicio.id,
                barbero: elegido.barberoId,
                inicio: elegido.inicio,
                // Para que "atrás" y el 9a vuelvan a "el primero disponible" y no al barbero asignado.
                eleccion: barbero ? undefined : PRIMERO,
              })
            }
          />
        </>
      }
    >
      <nav className={estilos.dias} aria-label="Día">
        {Array.from({ length: DIAS_VISIBLES }, (_, i) => sumarDias(hoy, i)).map((clave) => (
          <Link
            key={clave}
            className={estilos.dia}
            href={rutaReserva(barberia.slug, "hora", { ...seleccion, fecha: clave })}
            // Cambiar de día no suma historial: "atrás" vuelve al barbero.
            replace
            scroll={false}
            aria-current={clave === dia ? "date" : undefined}
            aria-label={fechaConHoy(deClave(clave), hoy, "UTC")}
          >
            {clave === hoy ? "Hoy" : diaSemanaCorto(deClave(clave), "UTC")}
            <strong>{Number(clave.slice(8))}</strong>
          </Link>
        ))}
      </nav>

      {ocupado && (
        <p className={estilos.nota} role="alert">
          Ese horario se acaba de ocupar. Elige otra hora.
        </p>
      )}

      {turnos.length === 0 && <p className={estilos.nota}>No hay turnos libres este día. Prueba con otro.</p>}

      {FRANJAS.map((nombre) => {
        const deLaFranja = turnos.filter((t) => franja(t.inicio, barberia.zona) === nombre);
        if (deLaFranja.length === 0) return null;
        return (
          <div key={nombre} role="radiogroup" aria-label={nombre}>
            <p className={estilos.rotulo}>{nombre}</p>
            <div className={estilos.turnos}>
              {deLaFranja.map((t) => {
                const { reloj, periodo } = partesHora(t.inicio, barberia.zona);
                return (
                  <label key={t.inicio} className={estilos.turno}>
                    <input
                      type="radio"
                      name="turno"
                      checked={t.inicio === inicio}
                      onChange={() => setInicio(t.inicio)}
                    />
                    <strong>{reloj}</strong> {periodo}
                  </label>
                );
              })}
            </div>
          </div>
        );
      })}

      {turnos.length > 0 && (
        <p className={estilos.nota}>
          Solo ves las horas en que {barbero ? `${barbero.nombre} tiene` : "hay un barbero con"} los{" "}
          {servicio.duracionMin} minutos libres.
        </p>
      )}
    </Paso>
  );
}
