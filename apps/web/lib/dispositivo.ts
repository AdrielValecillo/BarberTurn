import { useMemo, useSyncExternalStore } from "react";

// "Repetir mi último corte" (RF-09): se guarda solo en este dispositivo, por barbería.
// Nunca se consulta el historial de alguien a partir de un teléfono escrito.

export type DatosDispositivo = {
  nombre: string;
  telefono: string; // E.164
  servicioId: string;
  barberoId: string;
};

const clave = (slug: string) => `turnero:${slug}`;

export function guardarDispositivo(slug: string, datos: DatosDispositivo) {
  try {
    localStorage.setItem(clave(slug), JSON.stringify(datos));
  } catch {
    // Sin almacenamiento (modo privado): la reserva sigue, solo no habrá "repetir".
  }
}

function leer(slug: string) {
  try {
    return localStorage.getItem(clave(slug));
  } catch {
    return null;
  }
}

function suscribir(avisar: () => void) {
  window.addEventListener("storage", avisar);
  return () => window.removeEventListener("storage", avisar);
}

/** Datos de la última reserva hecha en este dispositivo; null en el servidor y si no hay. */
export function useDispositivo(slug: string): DatosDispositivo | null {
  const crudo = useSyncExternalStore(
    suscribir,
    () => leer(slug),
    () => null,
  );
  return useMemo(() => {
    try {
      return crudo ? (JSON.parse(crudo) as DatosDispositivo) : null;
    } catch {
      return null;
    }
  }, [crudo]);
}
