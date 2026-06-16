import json
import os
from producto import Producto


class Inventario:
    ARCHIVO = "inventario.json"
    
    def __init__(self):
        self.productos = {}
        self.cargar()
    
    def cargar(self):
        if os.path.exists(self.ARCHIVO):
            try:
                with open(self.ARCHIVO, "r", encoding="utf-8") as f:
                    contenido = f.read().strip()
                    if not contenido:  # Archivo vacío
                        self.productos = {}
                        return
                    datos = json.loads(contenido)
                    self.productos = {
                        id_prod: Producto.from_dict(prod) 
                        for id_prod, prod in datos.items()
                    }
            except (json.JSONDecodeError, ValueError):
                print("⚠️  Archivo de inventario corrupto. Se creará uno nuevo.")
                self.productos = {}
        else:
            self.productos = {}
    
    def guardar(self):
        with open(self.ARCHIVO, "w", encoding="utf-8") as f:
            json.dump(
                {id_prod: prod.to_dict() for id_prod, prod in self.productos.items()},
                f,
                indent=4,
                ensure_ascii=False
            )
    
    def agregar(self, producto):
        if producto.id_producto in self.productos:
            print(f"⚠️ El producto '{producto.id_producto}' ya existe. Usa 'actualizar'.")
            return False
        self.productos[producto.id_producto] = producto
        self.guardar()
        print(f"✅ Producto '{producto.nombre}' agregado.")
        return True
    
    def actualizar(self, id_producto, cantidad=None, precio=None, nombre=None):
        if id_producto not in self.productos:
            print(f"❌ Producto '{id_producto}' no encontrado.")
            return False
        
        producto = self.productos[id_producto]
        if cantidad is not None:
            producto.cantidad = cantidad
        if precio is not None:
            producto.precio = precio
        if nombre is not None:
            producto.nombre = nombre
        
        producto.ultima_actualizacion = __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.guardar()
        print(f"✅ Producto '{id_producto}' actualizado.")
        return True
    
    def eliminar(self, id_producto):
        if id_producto in self.productos:
            nombre = self.productos[id_producto].nombre
            del self.productos[id_producto]
            self.guardar()
            print(f"✅ Producto '{nombre}' eliminado.")
            return True
        print(f"❌ Producto '{id_producto}' no encontrado.")
        return False
    
    def buscar(self, termino):
        resultados = []
        termino = termino.lower()
        for prod in self.productos.values():
            if (termino in prod.nombre.lower() or 
                termino in prod.categoria.lower() or
                termino in prod.id_producto.lower()):
                resultados.append(prod)
        return resultados
    
    def listar_todos(self):
        if not self.productos:
            print("📭 Inventario vacío.")
            return []
        return list(self.productos.values())
    
    def listar_stock_bajo(self):
        bajos = [p for p in self.productos.values() if p.stock_bajo()]
        return bajos
    
    def listar_por_categoria(self, categoria):
        return [p for p in self.productos.values() if p.categoria.lower() == categoria.lower()]
    
    def valor_inventario_total(self):
        return sum(p.valor_total() for p in self.productos.values())
    
    def resumen(self):
        total_productos = len(self.productos)
        total_items = sum(p.cantidad for p in self.productos.values())
        valor_total = self.valor_inventario_total()
        stock_bajo = len(self.listar_stock_bajo())
        
        print("\n" + "="*50)
        print("📊 RESUMEN DEL INVENTARIO")
        print("="*50)
        print(f"Total de productos distintos: {total_productos}")
        print(f"Total de unidades:            {total_items}")
        print(f"Valor total del inventario:   ${valor_total:,.2f}")
        print(f"Productos con stock bajo:     {stock_bajo}")
        print("="*50 + "\n")