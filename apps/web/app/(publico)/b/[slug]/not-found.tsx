import { Mensaje } from "@/components/ui/piezas";

// CU-01 1a: la barbería no existe o está suspendida (RN-16).
export default function NoDisponible() {
  return (
    <Mensaje titulo="Esta barbería no está disponible">
      Revisa el enlace o escríbele a tu barbería para pedir uno nuevo.
    </Mensaje>
  );
}
