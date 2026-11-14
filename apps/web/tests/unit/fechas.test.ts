import { expect, test } from "vitest";
import {
  claveDia,
  cuandoCorto,
  fechaConHoy,
  fechaHoraCorta,
  fechaLarga,
  franja,
  hora,
  precio,
  rangoHoras,
  sumarDias,
} from "../../lib/fechas";

// Las horas llevan espacios duros para no partirse; aquí se comparan como texto normal.
const plano = (texto: string) => texto.replace(/\u00a0/g, " ");

// Sábado 7 de noviembre de 2026, 5:15 p. m. en Bogotá (UTC-5).
const cita = "2026-11-07T22:15:00Z";

test("RNF-13: horas, fechas y precios en español de Colombia", () => {
  expect(plano(hora(cita))).toBe("5:15 p. m.");
  expect(fechaLarga(cita)).toBe("sábado 7 de noviembre");
  expect(precio(35000)).toBe("$35.000");
});

test("RNF-12: el día se calcula en la zona de la barbería, no en UTC", () => {
  // 11:30 p. m. del sábado en Bogotá ya es domingo en UTC.
  expect(claveDia("2026-11-08T04:30:00Z")).toBe("2026-11-07");
  expect(claveDia("2026-11-08T04:30:00Z", "UTC")).toBe("2026-11-08");
});

test("textos relativos a hoy", () => {
  expect(fechaConHoy(cita, "2026-11-07")).toBe("Hoy, sábado 7 de noviembre");
  expect(fechaConHoy(cita, "2026-11-06")).toBe("Sábado 7 de noviembre");
  expect(plano(cuandoCorto(cita, "2026-11-07"))).toBe("hoy 5:15 p. m.");
  expect(plano(cuandoCorto("2026-11-09T14:00:00Z", "2026-11-07"))).toBe("lun 9:00 a. m.");
  expect(plano(fechaHoraCorta("2026-11-05T01:12:00Z", "2026-11-07"))).toBe("Miércoles 4 de nov., 8:12 p. m.");
  expect(plano(fechaHoraCorta(cita, "2026-11-07"))).toBe("Hoy, 5:15 p. m.");
});

test("rangos, franjas y días", () => {
  expect(plano(rangoHoras("2026-11-07T20:45:00Z", cita))).toBe("3:45 a 5:15 p. m.");
  expect(plano(rangoHoras("2026-11-07T16:00:00Z", "2026-11-07T18:00:00Z"))).toBe("11:00 a. m. a 1:00 p. m.");
  expect(franja("2026-11-07T16:59:00Z")).toBe("Mañana");
  expect(franja(cita)).toBe("Tarde");
  expect(franja("2026-11-07T23:00:00Z")).toBe("Noche");
  expect(sumarDias("2026-11-30", 1)).toBe("2026-12-01");
});
