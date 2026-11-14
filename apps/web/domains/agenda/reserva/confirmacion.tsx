"use client";

import { EnlaceBoton } from "@/components/ui/boton";
import { Icono } from "@/components/ui/icono";
import { Contenido, Encabezado, Pantalla } from "@/components/ui/piezas";
import { useDispositivo } from "@/lib/dispositivo";
import { fechaConHoy, hora, partesHora } from "@/lib/fechas";
import type { Barberia, Barbero, Servicio } from "../api";
import estilos from "./reserva.module.css";

type Props = { barberia: Barberia; servicio: Servicio; barbero: Barbero; inicio: string; token: string; hoy: string };

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const DOS_HORAS = 2 * 60 * 60_000;

/** Confirmación (RF-08, CU-01 paso 10): resumen, calendario, mapa y cómo se verá el recordatorio. */
export function Confirmacion({ barberia, servicio, barbero, inicio, token, hoy }: Props) {
  const nombre = useDispositivo(barberia.slug)?.nombre.split(" ")[0];
  const { reloj, periodo } = partesHora(inicio, barberia.zona);
  const mapa = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${barberia.nombre}, ${barberia.direccion}`)}`;

  return (
    <Pantalla>
      <Encabezado titulo={barberia.nombre} />
      <Contenido>
        <div className={estilos.exito}>
          <span className={estilos.circulo}>
            <Icono nombre="check" />
          </span>
          <h1>Reserva confirmada</h1>
        </div>
        <p className={estilos.nota}>Te enviamos los detalles por WhatsApp.</p>

        <div className={estilos.tiquete}>
          <p className={estilos.horaGrande}>
            {reloj} <span>{periodo}</span>
          </p>
          <strong>{fechaConHoy(inicio, hoy, barberia.zona)}</strong>
          <hr />
          <p>
            {servicio.nombre} con {barbero.nombre}
            <small>
              {barberia.direccion}, {barberia.nombre}
            </small>
          </p>
        </div>

        <div className={estilos.acciones}>
          {/* El .ics lo genera la API (F1.08). */}
          <EnlaceBoton variante="secundario" href={`${API}/public/citas/${token}/calendario.ics`}>
            <Icono nombre="calendario" />
            Agregar a mi calendario
          </EnlaceBoton>
          <EnlaceBoton variante="secundario" href={mapa} target="_blank" rel="noopener">
            <Icono nombre="ubicacion" />
            Cómo llegar
          </EnlaceBoton>
        </div>

        <p className={estilos.rotulo}>Así te lo recordamos 2 horas antes</p>
        <div className={estilos.burbuja}>
          <p>
            Hola{nombre ? ` ${nombre}` : ""}, te recordamos tu cita de hoy a las {hora(inicio, barberia.zona)} con{" "}
            {barbero.nombre} en {barberia.nombre}. ¿Nos confirmas?
          </p>
          <small>{hora(new Date(Date.parse(inicio) - DOS_HORAS), barberia.zona)}</small>
        </div>
        {/* Muestra de los botones del mensaje de WhatsApp: aquí no hacen nada. */}
        <div className={estilos.respuestas} aria-hidden="true">
          <span>Confirmo</span>
          <span>Reagendar</span>
          <span>Cancelar</span>
        </div>

        <EnlaceBoton variante="texto" href={`/c/${token}`}>
          Ver mis citas
        </EnlaceBoton>
      </Contenido>
    </Pantalla>
  );
}
