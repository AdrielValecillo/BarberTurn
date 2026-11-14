import Link from "next/link";
import type { ComponentProps } from "react";
import estilos from "./ui.module.css";

type Estilo = {
  variante?: "primario" | "secundario" | "texto";
  compacto?: boolean;
  peligro?: boolean;
};

const clases = ({ variante = "primario", compacto, peligro }: Estilo) =>
  [estilos.boton, estilos[variante], compacto && estilos.compacto, peligro && estilos.peligro].filter(Boolean).join(" ");

export function Boton({ variante, compacto, peligro, ...resto }: Estilo & ComponentProps<"button">) {
  return <button type="button" {...resto} className={clases({ variante, compacto, peligro })} />;
}

/** Mismo aspecto que Boton, pero navega: rutas internas, wa.me, tel: o mapas. */
export function EnlaceBoton({ variante, compacto, peligro, ...resto }: Estilo & ComponentProps<typeof Link>) {
  return <Link {...resto} className={clases({ variante, compacto, peligro })} />;
}
