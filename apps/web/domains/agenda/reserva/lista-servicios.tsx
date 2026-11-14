"use client";

import Link from "next/link";
import { useState } from "react";
import { Icono } from "@/components/ui/icono";
import { useDispositivo } from "@/lib/dispositivo";
import { precio } from "@/lib/fechas";
import type { Barberia } from "../api";
import { Continuar, Paso, Resumen, rutaReserva } from "./paso";
import estilos from "./reserva.module.css";

/** Paso 1 (RF-01, RF-02) y "Repetir mi último corte" (RF-09, CU-01 2a). */
export function ListaServicios({ barberia, inicial }: { barberia: Barberia; inicial?: string }) {
  const dispositivo = useDispositivo(barberia.slug);
  const [elegido, setElegido] = useState<string>();

  const ultimoServicio = barberia.servicios.find((s) => s.id === dispositivo?.servicioId);
  const ultimoBarbero = barberia.barberos.find((b) => b.id === dispositivo?.barberoId);
  const servicio = barberia.servicios.find((s) => s.id === (elegido ?? inicial ?? ultimoServicio?.id));

  return (
    <Paso
      barberia={barberia.nombre}
      numero={1}
      titulo="¿Qué te vas a hacer?"
      pie={
        <>
          {servicio && (
            <Resumen texto={`${servicio.nombre}, ${servicio.duracionMin} min`} total={precio(servicio.precioCop)} />
          )}
          <Continuar href={servicio && rutaReserva(barberia.slug, "barbero", { servicio: servicio.id })} />
        </>
      }
    >
      {ultimoServicio && ultimoBarbero && (
        <>
          <Link
            className={estilos.repetir}
            href={rutaReserva(barberia.slug, "hora", { servicio: ultimoServicio.id, barbero: ultimoBarbero.id })}
          >
            <span className={estilos.circulo}>
              <Icono nombre="repetir" />
            </span>
            <span className={estilos.lineas}>
              <strong>Repetir mi último corte</strong>
              {ultimoServicio.nombre} con {ultimoBarbero.nombre}
            </span>
            <span className={estilos.precio}>{precio(ultimoServicio.precioCop)}</span>
          </Link>
          <p className={estilos.rotulo}>O elige otro servicio</p>
        </>
      )}

      <div role="radiogroup" aria-label="Servicio">
        {barberia.servicios.map((s) => (
          <label key={s.id} className={estilos.opcion}>
            <span className={estilos.lineas}>
              <strong>{s.nombre}</strong>
              {s.duracionMin} min
            </span>
            <span className={estilos.precio}>{precio(s.precioCop)}</span>
            <input
              type="radio"
              name="servicio"
              className={estilos.radio}
              checked={servicio?.id === s.id}
              onChange={() => setElegido(s.id)}
            />
          </label>
        ))}
      </div>
    </Paso>
  );
}
