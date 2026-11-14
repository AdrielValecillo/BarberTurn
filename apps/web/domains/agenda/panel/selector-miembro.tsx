"use client";

import { useRouter } from "next/navigation";
import { Icono } from "@/components/ui/icono";
import { Avatar } from "@/components/ui/piezas";
import estilos from "./panel.module.css";

type Props = { equipo: { id: string; nombre: string }[]; actual: string; dia: string };

/** El dueño elige de qué barbero ve la agenda (RF-37). */
export function SelectorMiembro({ equipo, actual, dia }: Props) {
  const router = useRouter();
  return (
    <label className={estilos.selector}>
      <Avatar nombre={equipo.find((m) => m.id === actual)?.nombre ?? ""} />
      <select
        aria-label="Barbero"
        value={actual}
        onChange={(evento) => router.push(`/panel/agenda?fecha=${dia}&miembro=${evento.target.value}`)}
      >
        {equipo.map((m) => (
          <option key={m.id} value={m.id}>
            {m.nombre}
          </option>
        ))}
      </select>
      <Icono nombre="abajo" tamano={20} />
    </label>
  );
}
