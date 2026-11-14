import type { ComponentProps } from "react";
import estilos from "./ui.module.css";

type Props = {
  id: string;
  etiqueta: string;
  ayuda?: string;
  error?: string;
  /** Texto fijo antes del campo, como "+57". */
  prefijo?: string;
} & ComponentProps<"input">;

export function Campo({ id, etiqueta, ayuda, error, prefijo, ...input }: Props) {
  const nota = error ?? ayuda;
  return (
    <div className={estilos.campo}>
      <label htmlFor={id}>{etiqueta}</label>
      <div className={estilos.campoFila}>
        {prefijo && <span className={estilos.prefijo}>{prefijo}</span>}
        <input id={id} aria-invalid={!!error} aria-describedby={nota ? `${id}-nota` : undefined} {...input} />
      </div>
      {nota && (
        <p id={`${id}-nota`} className={error ? estilos.error : estilos.ayuda} role={error ? "alert" : undefined}>
          {nota}
        </p>
      )}
    </div>
  );
}
