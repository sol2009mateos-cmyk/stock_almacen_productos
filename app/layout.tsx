import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "StockMaster Pro",
  description: "Sistema de inventario y punto de venta",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es-AR">
      <body className="bg-gray-50 min-h-screen">{children}</body>
    </html>
  );
}
