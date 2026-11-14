import { expect, test } from "vitest";
import { formatoTelefono, normalizarTelefono } from "../../lib/telefono";

test.each([
  ["300 123 4567", "+573001234567"],
  ["3001234567", "+573001234567"],
  ["+57 300-123-4567", "+573001234567"],
  ["573001234567", "+573001234567"],
])("CU-01: %s es un celular válido", (texto, esperado) => {
  expect(normalizarTelefono(texto)).toBe(esperado);
});

test.each(["", "300 123 456", "30012345678", "601 123 4567", "abc"])(
  "CU-01 8a: %j no es un celular válido",
  (texto) => {
    expect(normalizarTelefono(texto)).toBeNull();
  },
);

test("formato para mostrar", () => {
  expect(formatoTelefono("+573105550182")).toBe("+57 310 555 0182");
});
