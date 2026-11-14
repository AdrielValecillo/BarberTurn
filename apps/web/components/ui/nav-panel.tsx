import Link from "next/link";
import { Icono } from "./icono";
import estilos from "./ui.module.css";

const SECCIONES = [
  { id: "agenda", texto: "Agenda", icono: "calendario" },
  { id: "clientes", texto: "Clientes", icono: "personas" },
  { id: "ajustes", texto: "Ajustes", icono: "ajustes" },
] as const;

/** Barra inferior del panel. Cada pantalla dice cuál es la suya. */
export function NavPanel({ activa }: { activa: (typeof SECCIONES)[number]["id"] }) {
  return (
    <nav className={estilos.nav} aria-label="Secciones del panel">
      {SECCIONES.map((s) => (
        <Link key={s.id} href={`/panel/${s.id}`} aria-current={s.id === activa ? "page" : undefined}>
          <Icono nombre={s.icono} />
          {s.texto}
        </Link>
      ))}
    </nav>
  );
}
