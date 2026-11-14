// Celulares de Colombia: +57 y 10 dígitos que empiezan por 3. La API vuelve a validar al reservar.

/** Devuelve el número en E.164 ("+573001234567") o null si no es un celular válido. */
export function normalizarTelefono(texto: string): string | null {
  const digitos = texto.replace(/\D/g, "").replace(/^57(?=3\d{9}$)/, "");
  return /^3\d{9}$/.test(digitos) ? `+57${digitos}` : null;
}

/** "+573105550182" → "+57 310 555 0182" */
export function formatoTelefono(e164: string): string {
  const m = /^\+57(\d{3})(\d{3})(\d{4})$/.exec(e164);
  return m ? `+57 ${m[1]} ${m[2]} ${m[3]}` : e164;
}
