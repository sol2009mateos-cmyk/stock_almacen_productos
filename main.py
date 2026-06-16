from stock import Inventario
from producto import Producto


def mostrar_menu():
    print("\n" + "="*50)
    print("   🏪 SISTEMA DE INVENTARIO - STOCK TIENDA")
    print("="*50)
    print("1. ➕ Agregar producto")
    print("2. 📋 Listar todos los productos")
    print("3. 🔍 Buscar producto")
    print("4. ✏️  Actualizar producto")
    print("5. 🗑️  Eliminar producto")
    print("6. ⚠️  Ver productos con stock bajo")
    print("7. 📂 Listar por categoría")
    print("8. 📊 Ver resumen")
    print("9. 💰 Ver valor del inventario")
    print("0. 🚪 Salir")
    print("="*50)


def agregar_producto(inv):
    print("\n--- AGREGAR PRODUCTO ---")
    id_prod = input("ID del producto: ").strip().upper()
    nombre = input("Nombre: ").strip()
    categoria = input("Categoría: ").strip()
    
    try:
        cantidad = int(input("Cantidad en stock: "))
        precio = float(input("Precio unitario: $"))
        minimo = input("Stock mínimo (default 5): ").strip()
        minimo = int(minimo) if minimo else 5
    except ValueError:
        print("❌ Error: Ingresa números válidos.")
        return
    
    producto = Producto(id_prod, nombre, categoria, cantidad, precio, minimo)
    inv.agregar(producto)


def listar_productos(inv):
    productos = inv.listar_todos()
    if not productos:
        return
    
    print("\n--- LISTA DE PRODUCTOS ---")
    print(f"{'ID':<10} {'Nombre':<20} {'Cat.':<15} {'Cant':<6} {'Precio':<10} {'Estado'}")
    print("-" * 80)
    for p in sorted(productos, key=lambda x: x.id_producto):
        estado = "⚠️ BAJO" if p.stock_bajo() else "✅ OK"
        print(f"{p.id_producto:<10} {p.nombre:<20} {p.categoria:<15} {p.cantidad:<6} ${p.precio:<9.2f} {estado}")
    print("-" * 80)


def buscar_producto(inv):
    termino = input("\n🔍 Ingresa término de búsqueda: ").strip()
    resultados = inv.buscar(termino)
    
    if not resultados:
        print("❌ No se encontraron productos.")
        return
    
    print(f"\n✅ {len(resultados)} resultado(s) encontrado(s):")
    for p in resultados:
        print(f"  → {p}")


def actualizar_producto(inv):
    id_prod = input("\nID del producto a actualizar: ").strip().upper()
    
    if id_prod not in inv.productos:
        print("❌ Producto no encontrado.")
        return
    
    print(f"Producto actual: {inv.productos[id_prod]}")
    print("Deja en blanco si no quieres cambiar ese campo.")
    
    cantidad = input("Nueva cantidad: ").strip()
    precio = input("Nuevo precio: ").strip()
    nombre = input("Nuevo nombre: ").strip()
    
    inv.actualizar(
        id_prod,
        cantidad=int(cantidad) if cantidad else None,
        precio=float(precio) if precio else None,
        nombre=nombre if nombre else None
    )


def stock_bajo(inv):
    bajos = inv.listar_stock_bajo()
    if not bajos:
        print("\n✅ No hay productos con stock bajo.")
        return
    
    print(f"\n⚠️  {len(bajos)} PRODUCTO(S) CON STOCK BAJO:")
    for p in bajos:
        print(f"  → {p.nombre}: {p.cantidad} unidades (mín: {p.minimo})")


def listar_por_categoria(inv):
    categoria = input("\nIngresa la categoría: ").strip()
    productos = inv.listar_por_categoria(categoria)
    
    if not productos:
        print(f"❌ No hay productos en la categoría '{categoria}'.")
        return
    
    print(f"\n📂 Productos en '{categoria}':")
    for p in productos:
        print(f"  → {p}")


def main():
    inv = Inventario()
    
    # Datos de ejemplo (solo la primera vez)
    if not inv.productos:
        print("🆕 Inventario vacío. ¿Deseas agregar datos de ejemplo? (s/n)")
        if input().lower().startswith('s'):
            inv.agregar(Producto("P001", "Coca Cola 600ml", "Bebidas", 50, 18.50, 10))
            inv.agregar(Producto("P002", "Sabritas Original", "Snacks", 8, 15.00, 5))
            inv.agregar(Producto("P003", "Galletas María", "Galletas", 25, 12.00, 5))
            inv.agregar(Producto("P004", "Agua Embotellada 1L", "Bebidas", 3, 10.00, 10))
            print("✅ Datos de ejemplo cargados.\n")
    
    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción: ").strip()
        
        if opcion == "1":
            agregar_producto(inv)
        elif opcion == "2":
            listar_productos(inv)
        elif opcion == "3":
            buscar_producto(inv)
        elif opcion == "4":
            actualizar_producto(inv)
        elif opcion == "5":
            id_prod = input("ID del producto a eliminar: ").strip().upper()
            inv.eliminar(id_prod)
        elif opcion == "6":
            stock_bajo(inv)
        elif opcion == "7":
            listar_por_categoria(inv)
        elif opcion == "8":
            inv.resumen()
        elif opcion == "9":
            print(f"\n💰 Valor total del inventario: ${inv.valor_inventario_total():,.2f}")
        elif opcion == "0":
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción no válida.")


if __name__ == "__main__":
    main()