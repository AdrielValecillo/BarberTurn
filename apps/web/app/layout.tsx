import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Turnero",
  description: "Reserva tu turno en la barbería y recibe recordatorios por WhatsApp.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="es-CO">
      <body>{children}</body>
    </html>
  );
}
