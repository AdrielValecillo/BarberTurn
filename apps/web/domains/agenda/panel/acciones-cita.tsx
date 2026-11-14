"use client";

import { useState } from "react";
import { Boton } from "@/components/ui/boton";
import estilos from "./panel.module.css";

/** Acciones de CU-08 (RF-27) sobre una cita que sigue abierta. */
export function AccionesCita() {
  // shortcut: los botones solo avisan; cambian el estado cuando exista POST /panel/citas/{id}/acciones (F2.03).
  const [aviso, setAviso] = useState(false);
  const pendiente = () => setAviso(true);
  return (
    <>
      {aviso && (
        <p className={estilos.tenue} role="status">
          Esta acción todavía no está conectada a la API (paso F2.03 del plan).
        </p>
      )}
      <Boton onClick={pendiente}>Marcar como atendida</Boton>
      <div className={estilos.tres}>
        <Boton variante="secundario" compacto onClick={pendiente}>
          Reagendar
        </Boton>
        <Boton variante="secundario" compacto onClick={pendiente}>
          No vino
        </Boton>
        <Boton variante="secundario" compacto peligro onClick={pendiente}>
          Cancelar
        </Boton>
      </div>
    </>
  );
}
