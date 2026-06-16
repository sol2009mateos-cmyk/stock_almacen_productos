import json
from datetime import datetime


class Producto:
    def __init__(self, id_producto, nombre, categoria, cantidad, precio, minimo=5):
        self.id_producto = id_producto
        self.nombre = nombre
        self.categoria = categoria
        self.cantidad = cantidad
        self.precio = precio
        self.minimo = minimo  # Stock mínimo para alerta
        self.ultima_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self):
        return {
            "id_producto": self.id_producto,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "cantidad": self.cantidad,
            "precio": self.precio,
            "minimo": self.minimo,
            "ultima_actualizacion": self.ultima_actualizacion
        }
    
    @classmethod
    def from_dict(cls, data):
        producto = cls(
            data["id_producto"],
            data["nombre"],
            data["categoria"],
            data["cantidad"],
            data["precio"],
            data.get("minimo", 5)
        )
        producto.ultima_actualizacion = data.get("ultima_actualizacion", "")
        return producto
    
    def stock_bajo(self):
        return self.cantidad <= self.minimo
    
    def valor_total(self):
        return self.cantidad * self.precio
    
    def __str__(self):
        estado = "⚠️ STOCK BAJO" if self.stock_bajo() else "✅ OK"
        return f"[{self.id_producto}] {self.nombre} | Cant: {self.cantidad} | ${self.precio:.2f} | {estado}"