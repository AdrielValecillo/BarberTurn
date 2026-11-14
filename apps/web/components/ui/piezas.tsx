import Link from "next/link";
import type { ReactNode } from "react";
import { Icono } from "./icono";
import estilos from "./ui.module.css";

/** Columna de celular centrada. Dentro van Encabezado, Contenido y Pie. */
export function Pantalla({ children }: { children: ReactNode }) {
  return <div className={estilos.pantalla}>{children}</div>;
}

export function Contenido({ children }: { children: ReactNode }) {
  return <main className={estilos.contenido}>{children}</main>;
}

/** Pie fijo abajo con la acción principal. */
export function Pie({ children }: { children: ReactNode }) {
  return <footer className={estilos.pie}>{children}</footer>;
}

export function Encabezado({ titulo, atras }: { titulo: string; atras?: string }) {
  return (
    <header className={estilos.encabezado}>
      {atras && (
        <Link href={atras} className={estilos.atras} aria-label="Volver">
          <Icono nombre="atras" tamano={28} />
        </Link>
      )}
      <p>{titulo}</p>
    </header>
  );
}

export function BarraPasos({ actual, total }: { actual: number; total: number }) {
  return (
    <div className={estilos.pasos}>
      <p>
        Paso {actual} de {total}
      </p>
      <div aria-hidden="true">
        {Array.from({ length: total }, (_, i) => (
          <span key={i} className={i < actual ? estilos.hecho : undefined} />
        ))}
      </div>
    </div>
  );
}

export type Tono = "gris" | "verde" | "ambar" | "amarillo" | "rojo";

export function Chip({ tono = "gris", children }: { tono?: Tono; children: ReactNode }) {
  return <span className={`${estilos.chip} ${estilos[tono]}`}>{children}</span>;
}

/** Iniciales: "Andrea Martínez" → "AM", "Carlos" → "CA". */
export function Avatar({ nombre, claro }: { nombre: string; claro?: boolean }) {
  const palabras = nombre.trim().split(/\s+/);
  const iniciales = palabras.length > 1 ? palabras[0][0] + palabras[1][0] : nombre.trim().slice(0, 2);
  return (
    <span className={`${estilos.avatar} ${claro ? estilos.claro : ""}`} aria-hidden="true">
      {iniciales.toUpperCase()}
    </span>
  );
}

/** Pantalla de solo texto: un título y una explicación. */
export function Mensaje({ titulo, children, volver }: { titulo: string; children: ReactNode; volver?: string }) {
  return (
    <Pantalla>
      {volver && <Encabezado titulo={titulo} atras={volver} />}
      <Contenido>
        <div className={estilos.mensaje}>
          <h1>{titulo}</h1>
          <p>{children}</p>
        </div>
      </Contenido>
    </Pantalla>
  );
}

/** Pantallas del plan (doc 06) que todavía no existen: evita enlaces rotos. */
export function Pendiente({ titulo, paso, volver }: { titulo: string; paso: string; volver: string }) {
  return (
    <Mensaje titulo={titulo} volver={volver}>
      Esta pantalla todavía no está construida (paso {paso} del plan).
    </Mensaje>
  );
}
