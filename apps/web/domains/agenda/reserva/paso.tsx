import type { ReactNode } from "react";
import { Boton, EnlaceBoton } from "@/components/ui/boton";
import { BarraPasos, Contenido, Encabezado, Pantalla, Pie } from "@/components/ui/piezas";
import estilos from "./reserva.module.css";

/** El estado de la reserva viaja en la URL para que "atrás" y recargar funcionen (doc 10 §4). */
export function rutaReserva(slug: string, paso: string, query: Record<string, string | undefined> = {}) {
  const q = new URLSearchParams(Object.entries(query).filter((par): par is [string, string] => !!par[1]));
  return `/b/${slug}${paso && `/${paso}`}${q.size ? `?${q}` : ""}`;
}

type Props = {
  barberia: string;
  numero: number;
  titulo: string;
  subtitulo?: string;
  atras?: string;
  children: ReactNode;
  pie: ReactNode;
};

/** Marco común de los 4 pasos: encabezado, barra de avance, pregunta y pie con la acción. */
export function Paso({ barberia, numero, titulo, subtitulo, atras, children, pie }: Props) {
  return (
    <Pantalla>
      <Encabezado titulo={barberia} atras={atras} />
      <Contenido>
        <BarraPasos actual={numero} total={4} />
        <div className={estilos.cabeza}>
          <h1>{titulo}</h1>
          {subtitulo && <p>{subtitulo}</p>}
        </div>
        {children}
      </Contenido>
      <Pie>{pie}</Pie>
    </Pantalla>
  );
}

export function Resumen({ texto, total }: { texto: string; total: string }) {
  return (
    <p className={estilos.resumen}>
      <span>{texto}</span>
      <strong>{total}</strong>
    </p>
  );
}

/** Sin destino (nada elegido todavía) queda deshabilitado. */
export function Continuar({ href }: { href?: string }) {
  return href ? <EnlaceBoton href={href}>Continuar</EnlaceBoton> : <Boton disabled>Continuar</Boton>;
}
