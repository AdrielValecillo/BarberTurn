"use client";

import { useRouter } from "next/navigation";
import { useState, useTransition, type FormEvent } from "react";
import { Boton } from "@/components/ui/boton";
import { Campo } from "@/components/ui/campo";
import { Icono } from "@/components/ui/icono";
import { guardarDispositivo, useDispositivo } from "@/lib/dispositivo";
import { fechaConHoy, hora, precio } from "@/lib/fechas";
import { normalizarTelefono } from "@/lib/telefono";
import { crearCita, type Barberia, type Barbero, type Servicio } from "../api";
import { Paso, rutaReserva } from "./paso";
import estilos from "./reserva.module.css";

type Props = { barberia: Barberia; servicio: Servicio; barbero: Barbero; inicio: string; hoy: string };

/** Paso 4 (RF-05 a RF-07): resumen, nombre y WhatsApp. Sin cuenta. */
export function FormularioDatos({ barberia, servicio, barbero, inicio, hoy }: Props) {
  const router = useRouter();
  const dispositivo = useDispositivo(barberia.slug);
  const [error, setError] = useState<{ telefono?: string; general?: string }>({});
  const [enviando, enviar] = useTransition();
  const seleccion = { servicio: servicio.id, barbero: barbero.id, inicio };

  function confirmar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    const datos = new FormData(evento.currentTarget);
    const nombre = String(datos.get("nombre")).trim();
    const telefono = normalizarTelefono(String(datos.get("telefono")));
    if (!telefono) {
      setError({ telefono: "Escribe un celular de 10 dígitos, por ejemplo 300 123 4567." });
      return;
    }
    setError({});
    enviar(async () => {
      try {
        const { token } = await crearCita({
          slug: barberia.slug,
          servicioId: servicio.id,
          barberoId: barbero.id,
          inicio,
          nombre,
          telefono,
          avisosProximoCorte: datos.get("proximo_corte") === "on",
        });
        guardarDispositivo(barberia.slug, { nombre, telefono, servicioId: servicio.id, barberoId: barbero.id });
        router.push(rutaReserva(barberia.slug, "listo", { ...seleccion, token }));
      } catch {
        // shortcut: un solo mensaje; "Ese horario se acaba de ocupar" (9a), el máximo de citas (9b)
        // y el límite por IP (9c) se distinguen cuando exista POST /public/citas (F1.05).
        setError({ general: "No pudimos guardar tu reserva. Inténtalo de nuevo." });
      }
    });
  }

  return (
    <Paso
      barberia={barberia.nombre}
      numero={4}
      titulo="Último paso"
      atras={rutaReserva(barberia.slug, "hora", { servicio: servicio.id, barbero: barbero.id })}
      pie={
        <>
          {error.general && (
            <p className={estilos.legal} role="alert">
              {error.general}
            </p>
          )}
          <p className={estilos.legal}>
            No necesitas crear una cuenta. Al confirmar aceptas la política de tratamiento de datos.
          </p>
          <Boton type="submit" form="datos" disabled={enviando}>
            {enviando ? "Reservando…" : "Confirmar reserva"}
          </Boton>
        </>
      }
    >
      <ul className={estilos.detalles}>
        <li>
          <Icono nombre="tijeras" />
          {servicio.nombre} con {barbero.nombre}
        </li>
        <li>
          <Icono nombre="calendario" />
          <strong>
            {fechaConHoy(inicio, hoy, barberia.zona)}, {hora(inicio, barberia.zona)}
          </strong>
        </li>
        <li>
          <Icono nombre="ubicacion" />
          {barberia.direccion}
        </li>
        <li>
          <Icono nombre="billete" />
          {precio(servicio.precioCop)}, pagas en la barbería
        </li>
      </ul>

      {/* La clave vuelve a montar los campos cuando llegan los datos guardados en el dispositivo (RF-09). */}
      <form id="datos" key={dispositivo ? "guardado" : "nuevo"} className={estilos.formulario} onSubmit={confirmar}>
        <Campo
          id="nombre"
          name="nombre"
          etiqueta="Tu nombre"
          placeholder="Ej. Juan Pérez"
          autoComplete="name"
          maxLength={80}
          required
          defaultValue={dispositivo?.nombre}
        />
        <Campo
          id="telefono"
          name="telefono"
          etiqueta="Tu WhatsApp"
          prefijo="+57"
          type="tel"
          inputMode="numeric"
          placeholder="300 123 4567"
          autoComplete="tel-national"
          required
          defaultValue={dispositivo?.telefono.replace("+57", "")}
          ayuda="Ahí te llegan la confirmación y el recordatorio."
          error={error.telefono}
        />
        <label className={estilos.casilla}>
          <input type="checkbox" name="proximo_corte" />
          <span className={estilos.lineas}>
            <strong>Avísame cuando me toque el próximo corte</strong>
            Lo puedes desactivar cuando quieras.
          </span>
        </label>
      </form>
    </Paso>
  );
}
