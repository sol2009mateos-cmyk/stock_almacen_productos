export interface Producto {
  id: number;
  nombre: string;
  categoria: string;
  marca: string | null;
  precio_costo: number;
  precio_venta: number;
  stock: number;
  codigo_barras: string | null;
  created_at: string;
  updated_at: string;
}

export interface Config {
  id: number;
  nombre_negocio: string;
  direccion: string | null;
  cuit: string | null;
  iva_porcentaje: number;
  comprobante_prefijo: string;
  comprobante_numero_actual: number;
  banco_nombre: string | null;
  banco_cbu: string | null;
  banco_alias: string | null;
}

export interface Favorito {
  id: number;
  slot: number;
  producto_id: number | null;
}

export interface Venta {
  id: number;
  numero_comprobante: string;
  fecha: string;
  metodo_pago: "efectivo" | "tarjeta" | "transferencia";
  cuotas: number | null;
  monto_recibido: number | null;
  vuelto: number | null;
  referencia_transferencia: string | null;
  subtotal: number;
  iva_total: number;
  total: number;
}

export interface VentaItem {
  id: number;
  venta_id: number;
  producto_id: number | null;
  nombre_producto: string;
  cantidad: number;
  precio_unitario: number;
  subtotal: number;
}
