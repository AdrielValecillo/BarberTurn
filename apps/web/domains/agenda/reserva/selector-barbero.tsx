"use client";

import { useState } from "react";
import { Icono } from "@/components/ui/icono";
import { Avatar, Chip } from "@/components/ui/piezas";
import { useDispositivo } from "@/lib/dispositivo";
import { cuandoCorto, precio } from "@/lib/fechas";
import { PRIMERO, type Barberia, type Servicio } from "../api";
import { Continuar, Paso, Resumen, rutaReserva } from "./paso";
import estilos from "./reserva.module.css";

type Props = { barberia: Barberia; servicio: Servicio; inicial?: string; hoy: string };

/** Paso 2 (RF-03): un barbero o "El primero disponible" (RN-05), cada uno con su próximo turno. */
export function SelectorBarbero({ barberia, servicio, inicial, hoy }: Props) {
  const dispositivo = useDispositivo(barberia.slug);
  const [elegido, setElegido] = useState<string>();

  const ultimo = barberia.barberos.find((b) => b.id === dispositivo?.barberoId)?.id;
  const seleccion = elegido ?? inicial ?? ultimo;
  const barbero = barberia.barberos.find((b) => b.id === seleccion);
  const valido = barbero || seleccion === PRIMERO;
  // Las fechas ISO en UTC se ordenan igual que el texto.
  const masCercano = barberia.barberos.map((b) => b.proximoTurno).filter((t) => t !== null).sort()[0];
  const cuando = (turno: string | null) => (turno ? cuandoCorto(turno, hoy, barberia.zona) : "sin turnos por ahora");

  return (
    <Paso
      barberia={barberia.nombre}
      numero={2}
      titulo="¿Con quién?"
      atras={rutaReserva(barberia.slug, "", { servicio: servicio.id })}
      pie={
        <>
          <Resumen
            texto={barbero ? `${servicio.nombre} con ${barbero.nombre}` : `${servicio.nombre}, ${servicio.duracionMin} min`}
            total={precio(servicio.precioCop)}
          />
          <Continuar
            href={valido ? rutaReserva(barberia.slug, "hora", { servicio: servicio.id, barbero: seleccion }) : undefined}
          />
        </>
      }
    >
      <div role="radiogroup" aria-label="Barbero">
        <label className={`${estilos.opcion} ${estilos.tarjeta}`}>
          <span className={estilos.circulo}>
            <Icono nombre="reloj" />
          </span>
          <span className={estilos.lineas}>
            <strong>El primero disponible</strong>
            Turno más cercano: {cuando(masCercano ?? null)}
          </span>
          <input
            type="radio"
            name="barbero"
            className={estilos.radio}
            checked={seleccion === PRIMERO}
            onChange={() => setElegido(PRIMERO)}
          />
        </label>

        <p className={estilos.rotulo}>O elige tu barbero</p>

        {barberia.barberos.map((b) => (
          <label key={b.id} className={estilos.opcion}>
            <Avatar nombre={b.nombre} />
            <span className={estilos.lineas}>
              <strong>{b.nombre}</strong>
              {b.id === ultimo && <Chip tono="amarillo">Te atendió la última vez</Chip>}
              Próximo turno: {cuando(b.proximoTurno)}
            </span>
            <input
              type="radio"
              name="barbero"
              className={estilos.radio}
              checked={seleccion === b.id}
              onChange={() => setElegido(b.id)}
            />
          </label>
        ))}
      </div>
    </Paso>
  );
}
