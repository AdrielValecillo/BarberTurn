"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, useTransition, type FormEvent } from "react";
import { Boton } from "@/components/ui/boton";
import { Campo } from "@/components/ui/campo";
import { Icono } from "@/components/ui/icono";
import { guardarDispositivo, useDispositivo } from "@/lib/dispositivo";
import { claveDia, fechaConHoy, hora, precio } from "@/lib/fechas";
import { normalizarTelefono } from "@/lib/telefono";
import { crearCita, PRIMERO, type Barberia, type Barbero, type Servicio } from "../api";
import { Paso, rutaReserva } from "./paso";
import estilos from "./reserva.module.css";

type Props = {
  barberia: Barberia;
  servicio: Servicio;
  /** El que atiende; con "el primero disponible" es el que asignó la API. */
  barbero: Barbero;
  eligioPrimero: boolean;
  inicio: string;
  hoy: string;
};

/** Paso 4 (RF-05 a RF-07): resumen, nombre y WhatsApp. Sin cuenta. */
export function FormularioDatos({ barberia, servicio, barbero, eligioPrimero, inicio, hoy }: Props) {
  const router = useRouter();
  const dispositivo = useDispositivo(barberia.slug);
  const [error, setError] = useState<{ telefono?: string; general?: string }>({});
  const [aceptaPolitica, setAceptaPolitica] = useState(false);
  const [enviando, enviar] = useTransition();
  const seleccion = { servicio: servicio.id, barbero: barbero.id, inicio };
  const volverAHora = { servicio: servicio.id, barbero: eligioPrimero ? PRIMERO : barbero.id };

  function confirmar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    const datos = new FormData(evento.currentTarget);
    const nombre = String(datos.get("nombre")).trim();
    const telefono = normalizarTelefono(String(datos.get("telefono")));
    if (!telefono) {
      setError({ telefono: "Escribe un celular de 10 dígitos, por ejemplo 300 123 4567." });
      return;
    }
    if (!aceptaPolitica) return; // el botón ya está deshabilitado; esto lo confirma para el tipo
    setError({});
    enviar(async () => {
      try {
        const resultado = await crearCita({
          slug: barberia.slug,
          servicioId: servicio.id,
          barberoId: barbero.id,
          inicio,
          nombre,
          telefono,
          aceptaPolitica: true,
          avisosProximoCorte: datos.get("proximo_corte") === "on",
        });
        if ("token" in resultado) {
          guardarDispositivo(barberia.slug, { nombre, telefono, servicioId: servicio.id, barberoId: barbero.id });
          router.push(rutaReserva(barberia.slug, "listo", { ...seleccion, token: resultado.token }));
        } else if (resultado.codigo === "turno_ocupado") {
          // 9a: el formulario se rellena desde el dispositivo, así que guardar ahí conserva nombre y teléfono.
          // El último corte ("Repetir mi último corte", RF-09) sigue siendo el de la última reserva que salió bien.
          guardarDispositivo(barberia.slug, {
            nombre,
            telefono,
            servicioId: dispositivo?.servicioId ?? servicio.id,
            barberoId: dispositivo?.barberoId ?? barbero.id,
          });
          router.push(
            rutaReserva(barberia.slug, "hora", {
              ...volverAHora,
              fecha: claveDia(new Date(inicio), barberia.zona),
              ocupado: "1",
            }),
          );
        } else if (resultado.codigo === "telefono_invalido") {
          setError({ telefono: resultado.mensaje });
        } else {
          setError({ general: resultado.mensaje }); // 9b, 9c y los demás: el mensaje de la API
        }
      } catch {
        setError({ general: "No pudimos guardar tu reserva. Revisa tu conexión e inténtalo de nuevo." });
      }
    });
  }

  return (
    <Paso
      barberia={barberia.nombre}
      numero={4}
      titulo="Último paso"
      atras={rutaReserva(barberia.slug, "hora", volverAHora)}
      pie={
        <>
          {error.general && (
            <p className={estilos.legal} role="alert">
              {error.general}
            </p>
          )}
          <p className={estilos.legal}>No necesitas crear una cuenta.</p>
          <Boton type="submit" form="datos" disabled={enviando || !aceptaPolitica}>
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
        {/* RF-06: obligatoria y desmarcada; sin ella no se puede confirmar. */}
        <label className={estilos.casilla}>
          <input
            type="checkbox"
            name="politica"
            required
            checked={aceptaPolitica}
            onChange={(e) => setAceptaPolitica(e.target.checked)}
          />
          <span className={estilos.lineas}>
            <strong>
              Acepto la{" "}
              <Link href="/privacidad" target="_blank">
                política de tratamiento de datos
              </Link>
            </strong>
            Para agendar tu cita y enviarte los avisos por WhatsApp.
          </span>
        </label>
        {/* RF-07: opcional y desmarcada. */}
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
