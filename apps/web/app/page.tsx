import { EnlaceBoton } from "@/components/ui/boton";
import { Contenido, Pantalla } from "@/components/ui/piezas";

export default function Home() {
  return (
    <Pantalla>
      <Contenido>
        <h1 style={{ padding: "2rem 0 0.5rem" }}>Turnero</h1>
        <p style={{ paddingBottom: "1.5rem" }}>Reservas y recordatorios por WhatsApp para barberías.</p>
        {/* Accesos a las pantallas con datos de demostración mientras no haya página comercial. */}
        <div style={{ display: "grid", gap: "0.75rem" }}>
          <EnlaceBoton href="/b/barberia-norte">Reservar en Barbería Norte</EnlaceBoton>
          <EnlaceBoton variante="secundario" href="/panel/agenda">
            Panel del barbero
          </EnlaceBoton>
        </div>
      </Contenido>
    </Pantalla>
  );
}
