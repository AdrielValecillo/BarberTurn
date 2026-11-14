import type { Metadata, Viewport } from "next";
import { Barlow, Barlow_Condensed } from "next/font/google";
import "./globals.css";

const texto = Barlow({ subsets: ["latin"], weight: ["400", "500", "600", "700"], variable: "--fuente-texto" });
const titulos = Barlow_Condensed({ subsets: ["latin"], weight: "700", variable: "--fuente-titulos" });

export const metadata: Metadata = {
  title: "Turnero",
  description: "Reserva tu turno en la barbería y recibe recordatorios por WhatsApp.",
};

export const viewport: Viewport = { themeColor: "#15532e" };

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="es-CO" className={`${texto.variable} ${titulos.variable}`}>
      <body>{children}</body>
    </html>
  );
}
