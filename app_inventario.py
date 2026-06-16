
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
import json
import os
import random
from datetime import datetime, timedelta
import webbrowser
import difflib  # Para búsqueda fuzzy
from collections import Counter  # Para contar productos más vendidos

# Configuración
ANCHO = 1280  # Reducido para que quepa en la mayoría de pantallas
ALTO = 800

# Colores tema oscuro mejorado
COLORES = {
    'bg_principal': '#0d1117',
    'bg_panel': '#161b22',
    'bg_tarjeta': '#21262d',
    'bg_hover': '#30363d',
    'borde': '#30363d',
    'borde_activo': '#58a6ff',
    'texto': '#c9d1d9',
    'texto_titulo': '#f0f6fc',
    'texto_secundario': '#8b949e',
    'acento': '#58a6ff',
    'exito': '#3fb950',
    'advertencia': '#d29922',
    'peligro': '#f85149',
    'info': '#58a6ff',
}

class AppInventario:
    def __init__(self, root):
        self.root = root
        self.root.title("🏪 StockMaster Pro - Sistema de Inventario")
        self.root.geometry(f"{ANCHO}x{ALTO}")
        self.root.configure(bg=COLORES['bg_principal'])
        self.root.minsize(1024, 600)  # Tamaño mínimo más razonable

        # Datos
        self.cargar_datos()
        self.imagenes_cache = {}
        self.carrito = []
        self.pagina_actual = 0
        self.productos_por_pagina = 12
        self.vista_actual = "inventario"  # inventario | ventas | dashboard

        # Variables
        self.filtro_categoria = tk.StringVar(value="Todas")
        self.busqueda_texto = tk.StringVar()
        self.metodo_pago = tk.StringVar(value="Efectivo")

        # Crear interfaz
        self.crear_menu_lateral()
        self.crear_panel_contenido()

        # Mostrar dashboard al inicio
        self.mostrar_dashboard()
        
        # Atajos de teclado
        self.root.bind('<F5>', lambda e: self.finalizar_venta() if self.vista_actual == 'ventas' else None)
        self.root.bind('<Escape>', lambda e: self.limpiar_busqueda_venta() if self.vista_actual == 'ventas' else None)

    def cargar_datos(self):
        try:
            with open('productos_1000.json', 'r', encoding='utf-8') as f:
                self.todos_productos = json.load(f)
        except:
            self.todos_productos = []

        self.categorias = sorted(list(set(p['categoria'] for p in self.todos_productos)))
        self.categorias.insert(0, "Todas")
        self.productos_filtrados = self.todos_productos.copy()
        self.producto_seleccionado = None

    def mostrar_toast(self, mensaje, tipo="info", duracion=2000):
        """Muestra una notificacion flotante (Toast).
        tipo: 'info', 'exito', 'advertencia', 'peligro'
        duracion: milisegundos
        """
        colores_toast = {
            'info': (COLORES['acento'], 'white'),
            'exito': (COLORES['exito'], 'white'),
            'advertencia': (COLORES['advertencia'], 'white'),
            'peligro': (COLORES['peligro'], 'white')
        }
        bg, fg = colores_toast.get(tipo, colores_toast['info'])
        
        # Crear ventana flotante
        toast = tk.Toplevel(self.root)
        toast.wm_overrideredirect(True)
        toast.configure(bg=bg)
        
        # Posicionar en la esquina inferior derecha
        ancho_toast = 300
        alto_toast = 50
        x = self.root.winfo_x() + self.root.winfo_width() - ancho_toast - 20
        y = self.root.winfo_y() + self.root.winfo_height() - alto_toast - 20
        toast.geometry(f"{ancho_toast}x{alto_toast}+{x}+{y}")
        
        # Agregar label con el mensaje
        lbl = tk.Label(toast, text=mensaje, font=("Arial", 11, "bold"),
                      bg=bg, fg=fg, wraplength=280, justify="center")
        lbl.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Desaparecer despues de la duracion
        def desaparecer():
            try:
                toast.destroy()
            except:
                pass
        
        toast.after(duracion, desaparecer)

    # ==================== MENU LATERAL ====================
    def crear_menu_lateral(self):
        self.frame_menu = tk.Frame(self.root, bg=COLORES['bg_panel'], width=220)
        self.frame_menu.pack(side=tk.LEFT, fill=tk.Y)
        self.frame_menu.pack_propagate(False)

        # Logo
        tk.Label(self.frame_menu, text="🏪", font=("Arial", 40),
                bg=COLORES['bg_panel'], fg=COLORES['acento']).pack(pady=(20, 5))

        tk.Label(self.frame_menu, text="StockMaster", font=("Arial", 16, "bold"),
                bg=COLORES['bg_panel'], fg=COLORES['texto_titulo']).pack()

        tk.Label(self.frame_menu, text="Pro v3.0", font=("Arial", 9),
                bg=COLORES['bg_panel'], fg=COLORES['texto_secundario']).pack(pady=(0, 20))

        # Separador
        tk.Frame(self.frame_menu, bg=COLORES['borde'], height=1).pack(fill=tk.X, padx=15, pady=5)

        # Botones de navegación
        self.botones_menu = {}
        botones = [
            ("📊 Dashboard", self.mostrar_dashboard),
            ("📦 Inventario", self.mostrar_inventario),
            ("🛒 Punto de Venta", self.mostrar_ventas),
            ("📈 Reportes", self.mostrar_reportes),
            ("⚙️ Configuración", self.mostrar_configuracion),
        ]

        for texto, comando in botones:
            btn = tk.Button(self.frame_menu, text=texto, font=("Arial", 11),
                           bg=COLORES['bg_panel'], fg=COLORES['texto'],
                           activebackground=COLORES['bg_hover'],
                           activeforeground=COLORES['acento'],
                           relief=tk.FLAT, anchor="w", padx=20, pady=12,
                           cursor="hand2", command=comando)
            btn.pack(fill=tk.X, padx=10, pady=2)
            self.botones_menu[texto] = btn

            # Hover efecto
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=COLORES['bg_hover']))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=COLORES['bg_panel']))

        # Separador
        tk.Frame(self.frame_menu, bg=COLORES['borde'], height=1).pack(fill=tk.X, padx=15, pady=10)

        # Info del sistema
        tk.Label(self.frame_menu, text="📅 " + datetime.now().strftime("%d/%m/%Y"),
                font=("Arial", 10), bg=COLORES['bg_panel'],
                fg=COLORES['texto_secundario']).pack(pady=5)

        tk.Label(self.frame_menu, text=f"📦 {len(self.todos_productos)} productos",
                font=("Arial", 10), bg=COLORES['bg_panel'],
                fg=COLORES['texto_secundario']).pack(pady=5)

        # Alertas
        productos_por_vencer = len([p for p in self.todos_productos
                                    if p.get('dias_para_vencer') and p['dias_para_vencer'] <= 30])
        stock_bajo = len([p for p in self.todos_productos if p['cantidad'] <= p['stock_minimo']])

        if productos_por_vencer > 0:
            tk.Label(self.frame_menu, text=f"⚠️ {productos_por_vencer} por vencer",
                    font=("Arial", 10, "bold"), bg=COLORES['bg_panel'],
                    fg=COLORES['peligro']).pack(pady=2)

        if stock_bajo > 0:
            tk.Label(self.frame_menu, text=f"🔴 {stock_bajo} stock bajo",
                    font=("Arial", 10, "bold"), bg=COLORES['bg_panel'],
                    fg=COLORES['advertencia']).pack(pady=2)

    # ==================== PANEL CONTENIDO ====================
    def crear_panel_contenido(self):
        self.frame_contenido = tk.Frame(self.root, bg=COLORES['bg_principal'])
        self.frame_contenido.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def limpiar_contenido(self):
        for widget in self.frame_contenido.winfo_children():
            widget.destroy()

    # ==================== DASHBOARD ====================
    def mostrar_dashboard(self):
        self.limpiar_contenido()
        self.vista_actual = "dashboard"
        self.resaltar_boton("📊 Dashboard")

        # FIX: Envolver todo el dashboard en un Canvas con scrollbar
        # para evitar que el contenido quede cortado en pantallas pequeñas
        canvas_dash = tk.Canvas(self.frame_contenido, bg=COLORES['bg_principal'],
                                highlightthickness=0)
        scrollbar_dash = ttk.Scrollbar(self.frame_contenido, orient="vertical",
                                       command=canvas_dash.yview)
        frame_dash = tk.Frame(canvas_dash, bg=COLORES['bg_principal'])

        frame_dash.bind("<Configure>",
            lambda e: canvas_dash.configure(scrollregion=canvas_dash.bbox("all")))

        canvas_dash.create_window((0, 0), window=frame_dash, anchor="nw")
        canvas_dash.configure(yscrollcommand=scrollbar_dash.set)

        canvas_dash.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_dash.pack(side=tk.RIGHT, fill=tk.Y)

        canvas_dash.bind("<MouseWheel>",
            lambda e: canvas_dash.yview_scroll(int(-1*(e.delta/120)), "units"))
        canvas_dash.bind("<Button-4>",
            lambda e: canvas_dash.yview_scroll(-1, "units"))
        canvas_dash.bind("<Button-5>",
            lambda e: canvas_dash.yview_scroll(1, "units"))

        # Ajustar el ancho del frame interno al canvas
        def _ajustar_ancho(event):
            canvas_dash.itemconfig(canvas_dash.find_withtag("all")[0], width=event.width)
        canvas_dash.bind("<Configure>", _ajustar_ancho)

        # Header
        frame_header = tk.Frame(frame_dash, bg=COLORES['bg_principal'], height=80)
        frame_header.pack(fill=tk.X, padx=25, pady=(20, 10))
        frame_header.pack_propagate(False)

        tk.Label(frame_header, text="📊 Dashboard", font=("Arial", 24, "bold"),
                bg=COLORES['bg_principal'], fg=COLORES['texto_titulo']).pack(side=tk.LEFT, pady=15)

        tk.Label(frame_header, text=f"Bienvenido de vuelta — {datetime.now().strftime('%A %d de %B, %Y')}",
                font=("Arial", 12), bg=COLORES['bg_principal'],
                fg=COLORES['texto_secundario']).pack(side=tk.LEFT, padx=20, pady=20)

        # Tarjetas de resumen
        frame_tarjetas = tk.Frame(frame_dash, bg=COLORES['bg_principal'])
        frame_tarjetas.pack(fill=tk.X, padx=25, pady=10)

        # Calcular métricas
        total_productos = len(self.todos_productos)
        valor_inventario = sum(p['precio'] * p['cantidad'] for p in self.todos_productos)
        stock_bajo = len([p for p in self.todos_productos if p['cantidad'] <= p['stock_minimo']])
        por_vencer = len([p for p in self.todos_productos
                         if p.get('dias_para_vencer') and p['dias_para_vencer'] <= 30])

        # Ventas del día
        hoy = datetime.now().strftime('%Y-%m-%d')
        try:
            with open('ventas.json', 'r', encoding='utf-8') as f:
                todas_ventas = json.load(f)
        except:
            todas_ventas = []
        ventas_hoy = sum(v['total'] for v in todas_ventas if v['fecha'].startswith(hoy))

        tarjetas = [
            ("📦 Productos", str(total_productos), COLORES['acento'], "Total en inventario"),
            ("💰 Valor Inventario", f"${valor_inventario:,.0f}", COLORES['exito'], "Precio × cantidad"),
            ("🛒 Ventas Hoy", f"${ventas_hoy:,.0f}", '#a371f7', "Ingresos del día"),
            ("🔴 Stock Bajo", str(stock_bajo), COLORES['peligro'], "Requieren reposición"),
            ("⚠️ Por Vencer", str(por_vencer), COLORES['advertencia'], "Vencen en 30 días"),
        ]

        for titulo, valor, color, subtitulo in tarjetas:
            self.crear_tarjeta_resumen(frame_tarjetas, titulo, valor, color, subtitulo)

        # Panel inferior: gráfica + listas
        # FIX: Usar grid con pesos para que se adapte al tamaño disponible
        frame_inferior = tk.Frame(frame_dash, bg=COLORES['bg_principal'])
        frame_inferior.pack(fill=tk.BOTH, expand=True, padx=25, pady=10)

        # Configurar grid con pesos iguales para que ambos lados compartan espacio
        frame_inferior.columnconfigure(0, weight=1)  # Gráfica
        frame_inferior.columnconfigure(1, weight=1)  # Stock bajo + por vencer
        frame_inferior.rowconfigure(0, weight=1)

        # --- Gráfica ventas 7 días ---
        frame_grafica = tk.Frame(frame_inferior, bg=COLORES['bg_panel'])
        frame_grafica.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(frame_grafica, text="📈 Ventas — últimos 7 días", font=("Arial", 13, "bold"),
                bg=COLORES['bg_panel'], fg=COLORES['acento']).pack(anchor="w", padx=15, pady=(10, 5))

        # Calcular datos de los últimos 7 días
        dias_labels = []
        dias_valores = []
        for i in range(6, -1, -1):
            dia = datetime.now() - timedelta(days=i)
            clave = dia.strftime('%Y-%m-%d')
            etiqueta = dia.strftime('%d/%m')
            total_dia = sum(v['total'] for v in todas_ventas if v['fecha'].startswith(clave))
            dias_labels.append(etiqueta)
            dias_valores.append(total_dia)

        # Canvas para la gráfica con altura mínima
        canvas_g = tk.Canvas(frame_grafica, bg=COLORES['bg_panel'], highlightthickness=0,
                             height=200)
        canvas_g.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))

        def dibujar_grafica(event=None):
            canvas_g.delete("all")
            w = canvas_g.winfo_width()
            h = canvas_g.winfo_height()
            if w < 10:
                return

            margen_izq = 55
            margen_der = 15
            margen_sup = 20
            margen_inf = 35
            area_w = w - margen_izq - margen_der
            area_h = h - margen_sup - margen_inf

            max_val = max(dias_valores) if max(dias_valores) > 0 else 1
            n = len(dias_valores)
            ancho_barra = (area_w / n) * 0.6
            espacio = area_w / n

            # Líneas de referencia
            for frac in [0.25, 0.5, 0.75, 1.0]:
                y = margen_sup + area_h - int(area_h * frac)
                canvas_g.create_line(margen_izq, y, w - margen_der, y,
                                     fill=COLORES['borde'], dash=(4, 4))
                etiq = f"${max_val * frac:,.0f}"
                canvas_g.create_text(margen_izq - 5, y, text=etiq,
                                     anchor="e", fill=COLORES['texto_secundario'],
                                     font=("Arial", 7))

            # Barras
            for i, (val, lbl) in enumerate(zip(dias_valores, dias_labels)):
                x_centro = margen_izq + espacio * i + espacio / 2
                x0 = x_centro - ancho_barra / 2
                x1 = x_centro + ancho_barra / 2
                altura = int((val / max_val) * area_h) if max_val > 0 else 0
                y0 = margen_sup + area_h - altura
                y1 = margen_sup + area_h

                color_barra = COLORES['acento'] if i < 6 else '#a371f7'
                canvas_g.create_rectangle(x0, y0, x1, y1, fill=color_barra, outline="")

                # Valor encima de la barra
                if val > 0:
                    canvas_g.create_text(x_centro, y0 - 4, text=f"${val:,.0f}",
                                         fill=COLORES['texto'], font=("Arial", 7), anchor="s")

                # Etiqueta fecha
                canvas_g.create_text(x_centro, margen_sup + area_h + 12, text=lbl,
                                     fill=COLORES['texto_secundario'], font=("Arial", 8))

        canvas_g.bind("<Configure>", dibujar_grafica)
        canvas_g.after(100, dibujar_grafica)

        # --- Columna derecha: stock bajo + por vencer ---
        frame_derecha = tk.Frame(frame_inferior, bg=COLORES['bg_principal'])
        frame_derecha.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        # Configurar grid para los dos paneles (stock bajo y por vencer)
        frame_derecha.rowconfigure(0, weight=1)
        frame_derecha.rowconfigure(1, weight=1)
        frame_derecha.columnconfigure(0, weight=1)

        # Productos con stock bajo
        frame_stock = tk.Frame(frame_derecha, bg=COLORES['bg_panel'])
        frame_stock.grid(row=0, column=0, sticky="nsew", pady=(0, 8))

        tk.Label(frame_stock, text="🔴 Stock Bajo", font=("Arial", 13, "bold"),
                bg=COLORES['bg_panel'], fg=COLORES['peligro']).pack(anchor="w", padx=15, pady=8)

        productos_bajos = [p for p in self.todos_productos if p['cantidad'] <= p['stock_minimo']][:6]

        if productos_bajos:
            for p in productos_bajos:
                frame_item = tk.Frame(frame_stock, bg=COLORES['bg_tarjeta'])
                frame_item.pack(fill=tk.X, padx=10, pady=2)

                tk.Label(frame_item, text=f"{p['id']}", font=("Arial", 9, "bold"),
                        bg=COLORES['bg_tarjeta'], fg=COLORES['peligro'], width=8).pack(side=tk.LEFT, padx=8, pady=4)

                tk.Label(frame_item, text=p['nombre'][:22], font=("Arial", 9),
                        bg=COLORES['bg_tarjeta'], fg=COLORES['texto']).pack(side=tk.LEFT, padx=5, pady=4)

                tk.Label(frame_item, text=f"{p['cantidad']}/{p['stock_minimo']}", font=("Arial", 9, "bold"),
                        bg=COLORES['bg_tarjeta'], fg=COLORES['peligro']).pack(side=tk.RIGHT, padx=10, pady=4)
        else:
            tk.Label(frame_stock, text="✅ Sin stock bajo", font=("Arial", 11),
                    bg=COLORES['bg_panel'], fg=COLORES['exito']).pack(pady=15)

        # Productos por vencer
        frame_vencer = tk.Frame(frame_derecha, bg=COLORES['bg_panel'])
        frame_vencer.grid(row=1, column=0, sticky="nsew")

        tk.Label(frame_vencer, text="⚠️ Por Vencer", font=("Arial", 13, "bold"),
                bg=COLORES['bg_panel'], fg=COLORES['advertencia']).pack(anchor="w", padx=15, pady=8)

        productos_vencer = [p for p in self.todos_productos
                           if p.get('dias_para_vencer') and p['dias_para_vencer'] <= 30][:6]

        if productos_vencer:
            for p in productos_vencer:
                frame_item = tk.Frame(frame_vencer, bg=COLORES['bg_tarjeta'])
                frame_item.pack(fill=tk.X, padx=10, pady=2)

                color_dias = COLORES['peligro'] if p['dias_para_vencer'] <= 7 else COLORES['advertencia']

                tk.Label(frame_item, text=f"{p['id']}", font=("Arial", 9, "bold"),
                        bg=COLORES['bg_tarjeta'], fg=color_dias, width=8).pack(side=tk.LEFT, padx=8, pady=4)

                tk.Label(frame_item, text=p['nombre'][:22], font=("Arial", 9),
                        bg=COLORES['bg_tarjeta'], fg=COLORES['texto']).pack(side=tk.LEFT, padx=5, pady=4)

                tk.Label(frame_item, text=f"{p['dias_para_vencer']}d", font=("Arial", 9, "bold"),
                        bg=COLORES['bg_tarjeta'], fg=color_dias).pack(side=tk.RIGHT, padx=10, pady=4)
        else:
            tk.Label(frame_vencer, text="✅ Sin productos por vencer", font=("Arial", 11),
                    bg=COLORES['bg_panel'], fg=COLORES['exito']).pack(pady=15)

    def crear_tarjeta_resumen(self, parent, titulo, valor, color, subtitulo):
        # FIX: Usar minsize en lugar de height fijo para evitar contenido cortado
        frame = tk.Frame(parent, bg=COLORES['bg_panel'], width=250)
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=4)

        # Barra de color superior
        tk.Frame(frame, bg=color, height=4).pack(fill=tk.X)

        tk.Label(frame, text=titulo, font=("Arial", 11),
                bg=COLORES['bg_panel'], fg=COLORES['texto_secundario']).pack(anchor="w", padx=15, pady=(10, 0))

        tk.Label(frame, text=valor, font=("Arial", 28, "bold"),
                bg=COLORES['bg_panel'], fg=color).pack(anchor="w", padx=15)

        tk.Label(frame, text=subtitulo, font=("Arial", 9),
                bg=COLORES['bg_panel'], fg=COLORES['texto_secundario']).pack(anchor="w", padx=15, pady=(0, 10))

    # ==================== INVENTARIO ====================
    def mostrar_inventario(self):
        self.limpiar_contenido()
        self.vista_actual = "inventario"
        self.resaltar_boton("📦 Inventario")
        self.pagina_actual = 0

        # Header
        frame_header = tk.Frame(self.frame_contenido, bg=COLORES['bg_principal'], height=70)
        frame_header.pack(fill=tk.X, padx=25, pady=(15, 5))
        frame_header.pack_propagate(False)

        tk.Label(frame_header, text="📦 Inventario", font=("Arial", 22, "bold"),
                bg=COLORES['bg_principal'], fg=COLORES['texto_titulo']).pack(side=tk.LEFT, pady=12)

        self.lbl_total_inv = tk.Label(frame_header, text=f"{len(self.todos_productos)} productos",
                                     font=("Arial", 11), bg=COLORES['bg_principal'], fg=COLORES['texto_secundario'])
        self.lbl_total_inv.pack(side=tk.LEFT, padx=15, pady=18)

        # Filtros
        tk.Label(frame_header, text="📂", font=("Arial", 12), bg=COLORES['bg_principal'], fg="white").pack(side=tk.LEFT, padx=(30, 2))
        combo_cat = ttk.Combobox(frame_header, textvariable=self.filtro_categoria,
                                values=self.categorias, state="readonly", width=18, font=("Arial", 10))
        combo_cat.pack(side=tk.LEFT, padx=2)
        combo_cat.bind("<<ComboboxSelected>>", lambda e: self.filtrar_inventario())

        tk.Label(frame_header, text="🔍", font=("Arial", 12), bg=COLORES['bg_principal'], fg="white").pack(side=tk.LEFT, padx=(20, 2))
        entry_buscar = tk.Entry(frame_header, textvariable=self.busqueda_texto,
                               font=("Arial", 10), width=25, bg=COLORES['bg_tarjeta'], fg=COLORES['texto'],
                               insertbackground="white", relief=tk.FLAT)
        entry_buscar.pack(side=tk.LEFT, padx=2, ipady=4)
        entry_buscar.bind("<KeyRelease>", lambda e: self.filtrar_inventario())

        btn_reset = tk.Button(frame_header, text="🔄 Limpiar", command=self.resetear_inventario,
                             bg=COLORES['bg_tarjeta'], fg=COLORES['texto'], font=("Arial", 9),
                             activebackground=COLORES['bg_hover'], cursor="hand2", relief=tk.FLAT, padx=10)
        btn_reset.pack(side=tk.LEFT, padx=10)

        # Panel principal dividido
        frame_main = tk.Frame(self.frame_contenido, bg=COLORES['bg_principal'])
        frame_main.pack(fill=tk.BOTH, expand=True, padx=25, pady=5)

        # Lista de productos (izquierda)
        frame_lista = tk.Frame(frame_main, bg=COLORES['bg_panel'], width=500)
        frame_lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        frame_lista.pack_propagate(False)

        # Canvas con scrollbar
        self.canvas_lista = tk.Canvas(frame_lista, bg=COLORES['bg_panel'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=self.canvas_lista.yview)
        self.scrollable_frame = tk.Frame(self.canvas_lista, bg=COLORES['bg_panel'])

        self.scrollable_frame.bind("<Configure>",
            lambda e: self.canvas_lista.configure(scrollregion=self.canvas_lista.bbox("all")))

        self.canvas_lista.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=480)
        self.canvas_lista.configure(yscrollcommand=scrollbar.set)

        self.canvas_lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # FIX: Usar bind en lugar de bind_all para evitar interferencias entre vistas
        self.canvas_lista.bind("<Enter>",
            lambda e: self.canvas_lista.bind_all("<MouseWheel>",
                lambda ev: self.canvas_lista.yview_scroll(int(-1*(ev.delta/120)), "units")))
        self.canvas_lista.bind("<Leave>",
            lambda e: self.canvas_lista.unbind_all("<MouseWheel>"))

        # Panel detalle (derecha)
        frame_detalle = tk.Frame(frame_main, bg=COLORES['bg_panel'], width=700)
        frame_detalle.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))
        frame_detalle.pack_propagate(False)

        self.crear_panel_detalle(frame_detalle)

        # Paginación
        frame_pag = tk.Frame(self.frame_contenido, bg=COLORES['bg_principal'], height=50)
        frame_pag.pack(fill=tk.X, padx=25, pady=5)
        frame_pag.pack_propagate(False)

        self.btn_ant = tk.Button(frame_pag, text="◀ Anterior", command=self.pagina_ant,
                                bg=COLORES['bg_tarjeta'], fg=COLORES['texto'], font=("Arial", 10, "bold"),
                                activebackground=COLORES['bg_hover'], cursor="hand2", relief=tk.FLAT, padx=15)
        self.btn_ant.pack(side=tk.LEFT, padx=10, pady=8)

        self.lbl_pag = tk.Label(frame_pag, text="Página 1", font=("Arial", 11),
                               bg=COLORES['bg_principal'], fg=COLORES['texto'])
        self.lbl_pag.pack(side=tk.LEFT, expand=True)

        self.btn_sig = tk.Button(frame_pag, text="Siguiente ▶", command=self.pagina_sig,
                                bg=COLORES['bg_tarjeta'], fg=COLORES['texto'], font=("Arial", 10, "bold"),
                                activebackground=COLORES['bg_hover'], cursor="hand2", relief=tk.FLAT, padx=15)
        self.btn_sig.pack(side=tk.RIGHT, padx=10, pady=8)

        self.actualizar_lista_inventario()

    def crear_panel_detalle(self, parent):
        """Panel de detalle del producto con scroll"""
        tk.Label(parent, text="📋 Detalle del Producto", font=("Arial", 16, "bold"),
                bg=COLORES['bg_panel'], fg=COLORES['acento']).pack(pady=12)

        # Canvas con scrollbar para todo el contenido
        canvas_det = tk.Canvas(parent, bg=COLORES['bg_panel'], highlightthickness=0)
        scrollbar_det = ttk.Scrollbar(parent, orient="vertical", command=canvas_det.yview)
        frame_scroll = tk.Frame(canvas_det, bg=COLORES['bg_panel'])

        frame_scroll.bind("<Configure>",
            lambda e: canvas_det.configure(scrollregion=canvas_det.bbox("all")))

        canvas_det.create_window((0, 0), window=frame_scroll, anchor="nw")
        canvas_det.configure(yscrollcommand=scrollbar_det.set)

        canvas_det.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_det.pack(side=tk.RIGHT, fill=tk.Y)

        canvas_det.bind("<MouseWheel>",
            lambda e: canvas_det.yview_scroll(int(-1*(e.delta/120)), "units"))

        # Imagen
        self.frame_img_det = tk.Frame(frame_scroll, bg=COLORES['bg_tarjeta'], width=200, height=200,
                                      highlightbackground=COLORES['borde_activo'], highlightthickness=2)
        self.frame_img_det.pack(pady=8)
        self.frame_img_det.pack_propagate(False)

        self.lbl_img_det = tk.Label(self.frame_img_det, bg=COLORES['bg_tarjeta'])
        self.lbl_img_det.pack(expand=True)

        # Estado
        self.lbl_estado_det = tk.Label(frame_scroll, text="", font=("Arial", 11, "bold"),
                                      bg=COLORES['bg_panel'])
        self.lbl_estado_det.pack(pady=5)

        # Barra de stock
        self.canvas_barra = tk.Canvas(frame_scroll, bg=COLORES['bg_tarjeta'], height=16,
                                      width=280, highlightthickness=0)
        self.canvas_barra.pack(pady=4)

        self.lbl_pct = tk.Label(frame_scroll, text="", font=("Arial", 9),
                               bg=COLORES['bg_panel'], fg=COLORES['texto_secundario'])
        self.lbl_pct.pack(pady=(0, 8))

        # Info en grid
        frame_info = tk.Frame(frame_scroll, bg=COLORES['bg_panel'])
        frame_info.pack(fill=tk.X, padx=15, pady=5)

        frame_info.columnconfigure(0, weight=0, minsize=140)
        frame_info.columnconfigure(1, weight=1)

        self.campos_info = {}
        campos = [
            ("🆔 ID", "id"), ("📛 Nombre", "nombre"), ("🏷️ Marca", "marca"),
            ("📂 Categoría", "categoria"), ("📦 Cantidad", "cantidad"),
            ("⚠️ Stock Mínimo", "stock_minimo"), ("💰 Precio Venta", "precio"),
            ("💵 Costo", "costo"), ("📈 Ganancia", "ganancia"),
            ("📊 Margen", "margen"), ("🏢 Proveedor", "proveedor"),
            ("📅 Ingreso", "fecha_ingreso"), ("⏰ Vencimiento", "fecha_vencimiento"),
            ("📍 Ubicación", "ubicacion"), ("🏷️ Código", "codigo_barras"),
            ("⚖️ Peso/Vol", "peso_volumen"), ("🔢 Lote", "lote"),
        ]

        for i, (label, key) in enumerate(campos):
            bg_row = COLORES['bg_tarjeta'] if i % 2 == 0 else COLORES['bg_panel']
            tk.Label(frame_info, text=f"{label}:", font=("Arial", 9, "bold"),
                    bg=bg_row, fg=COLORES['texto_secundario'],
                    anchor="w", padx=5).grid(row=i, column=0, sticky="ew", pady=2)

            lbl_valor = tk.Label(frame_info, text="-", font=("Arial", 9),
                                bg=bg_row, fg=COLORES['texto'], anchor="w", padx=8,
                                wraplength=200)
            lbl_valor.grid(row=i, column=1, sticky="ew", pady=2)
            self.campos_info[key] = lbl_valor

    def filtrar_inventario(self):
        cat = self.filtro_categoria.get()
        busq = self.busqueda_texto.get().lower()

        self.productos_filtrados = []
        for p in self.todos_productos:
            if cat != "Todas" and p['categoria'] != cat:
                continue
            # Búsqueda exacta primero
            if busq:
                nombre_match = busq in p['nombre'].lower()
                id_match = busq in p['id'].lower()
                marca_match = busq in p.get('marca', '').lower()
                
                # Si no hay coincidencia exacta, intentar búsqueda fuzzy
                if not (nombre_match or id_match or marca_match):
                    # Fuzzy search: permite pequeños errores ortográficos
                    nombre_ratio = difflib.SequenceMatcher(None, busq, p['nombre'].lower()).ratio()
                    marca_ratio = difflib.SequenceMatcher(None, busq, p.get('marca', '').lower()).ratio()
                    if nombre_ratio < 0.6 and marca_ratio < 0.6:
                        continue
            self.productos_filtrados.append(p)

        self.pagina_actual = 0
        self.lbl_total_inv.config(text=f"{len(self.productos_filtrados)} productos")
        self.actualizar_lista_inventario()
        if self.productos_filtrados:
            self.seleccionar_producto(self.productos_filtrados[0])

    def resetear_inventario(self):
        self.filtro_categoria.set("Todas")
        self.busqueda_texto.set("")
        self.productos_filtrados = self.todos_productos.copy()
        self.pagina_actual = 0
        self.lbl_total_inv.config(text=f"{len(self.todos_productos)} productos")
        self.actualizar_lista_inventario()
        if self.productos_filtrados:
            self.seleccionar_producto(self.productos_filtrados[0])

    def actualizar_lista_inventario(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        inicio = self.pagina_actual * self.productos_por_pagina
        fin = min(inicio + self.productos_por_pagina, len(self.productos_filtrados))
        productos_pag = self.productos_filtrados[inicio:fin]

        for prod in productos_pag:
            self.crear_tarjeta_inventario(prod)

        total_pag = max(1, (len(self.productos_filtrados) + self.productos_por_pagina - 1) // self.productos_por_pagina)
        self.lbl_pag.config(text=f"Página {self.pagina_actual + 1} de {total_pag}")
        self.btn_ant.config(state=tk.NORMAL if self.pagina_actual > 0 else tk.DISABLED)
        self.btn_sig.config(state=tk.NORMAL if self.pagina_actual < total_pag - 1 else tk.DISABLED)
        self.canvas_lista.yview_moveto(0)

    def crear_tarjeta_inventario(self, prod):
        # Color según estado
        if prod['cantidad'] <= prod['stock_minimo']:
            color_bg = "#2d132c"
            color_borde = COLORES['peligro']
            estado_txt = "🔴 BAJO"
            estado_fg = COLORES['peligro']
        elif prod.get('dias_para_vencer') and prod['dias_para_vencer'] <= 7:
            color_bg = "#2d1f1f"
            color_borde = COLORES['peligro']
            estado_txt = "⚠️ VENCE"
            estado_fg = COLORES['peligro']
        elif prod.get('dias_para_vencer') and prod['dias_para_vencer'] <= 30:
            color_bg = "#2d2418"
            color_borde = COLORES['advertencia']
            estado_txt = "⚡ VENCE"
            estado_fg = COLORES['advertencia']
        else:
            color_bg = COLORES['bg_tarjeta']
            color_borde = COLORES['borde']
            estado_txt = "✅ OK"
            estado_fg = COLORES['exito']

        frame = tk.Frame(self.scrollable_frame, bg=color_bg,
                        highlightbackground=color_borde, highlightthickness=1,
                        cursor="hand2")
        frame.pack(fill=tk.X, padx=6, pady=3)

        frame.bind("<Button-1>", lambda e, p=prod: self.seleccionar_producto(p))
        frame.bind("<Enter>", lambda e, f=frame: f.config(highlightbackground=COLORES['borde_activo'], highlightthickness=2))
        frame.bind("<Leave>", lambda e, f=frame, c=color_borde: f.config(highlightbackground=c, highlightthickness=1))

        # Layout horizontal
        fh = tk.Frame(frame, bg=color_bg)
        fh.pack(fill=tk.X, padx=8, pady=6)

        # Imagen mini
        fi = tk.Frame(fh, bg=color_bg, width=55, height=55)
        fi.pack(side=tk.LEFT, padx=(0, 8))
        fi.pack_propagate(False)

        li = tk.Label(fi, bg=color_bg)
        li.pack(expand=True)

        try:
            ip = f"imagenes_productos/{prod['id']}.png"
            if os.path.exists(ip):
                img = Image.open(ip).resize((50, 50), Image.LANCZOS)
                it = ImageTk.PhotoImage(img)
                li.config(image=it)
                li.image = it
        except:
            li.config(text=prod['nombre'][0].upper(), font=("Arial", 18, "bold"), fg=COLORES['acento'])

        # Info
        finf = tk.Frame(fh, bg=color_bg)
        finf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(finf, text=f"{prod['id']}", font=("Arial", 8, "bold"),
                bg=color_bg, fg=COLORES['acento'], anchor="w").pack(fill=tk.X)

        tk.Label(finf, text=prod['nombre'][:26], font=("Arial", 10, "bold"),
                bg=color_bg, fg=COLORES['texto_titulo'], anchor="w").pack(fill=tk.X)

        fd = tk.Frame(finf, bg=color_bg)
        fd.pack(fill=tk.X, pady=1)

        tk.Label(fd, text=f"📂 {prod['categoria']}", font=("Arial", 8),
                bg=color_bg, fg=COLORES['texto_secundario']).pack(side=tk.LEFT)

        tk.Label(fd, text=f"📦 {prod['cantidad']} uds", font=("Arial", 8),
                bg=color_bg, fg=COLORES['texto_secundario']).pack(side=tk.LEFT, padx=8)

        tk.Label(fd, text=f"⚠️ Min: {prod['stock_minimo']}", font=("Arial", 8),
                bg=color_bg, fg=COLORES['advertencia']).pack(side=tk.LEFT)

        fp = tk.Frame(finf, bg=color_bg)
        fp.pack(fill=tk.X, pady=1)

        tk.Label(fp, text=f"💰 ${prod['precio']:,.2f}", font=("Arial", 9, "bold"),
                bg=color_bg, fg=COLORES['exito']).pack(side=tk.LEFT)

        tk.Label(fp, text=estado_txt, font=("Arial", 8, "bold"),
                bg=color_bg, fg=estado_fg).pack(side=tk.RIGHT)

        # Vencimiento si aplica
        if prod.get('dias_para_vencer') and prod['dias_para_vencer'] <= 30:
            fv = tk.Frame(finf, bg=color_bg)
            fv.pack(fill=tk.X)
            cv = COLORES['peligro'] if prod['dias_para_vencer'] <= 7 else COLORES['advertencia']
            tk.Label(fv, text=f"⏰ Vence en {prod['dias_para_vencer']} días ({prod['fecha_vencimiento']})",
                    font=("Arial", 8, "bold"), bg=color_bg, fg=cv).pack(side=tk.LEFT)

        # Hacer todo clickeable
        for child in [fh, fi, finf, fd, fp]:
            child.bind("<Button-1>", lambda e, p=prod: self.seleccionar_producto(p))
            for w in child.winfo_children():
                w.bind("<Button-1>", lambda e, p=prod: self.seleccionar_producto(p))
                w.config(cursor="hand2")

        # FIX: Botón editar más grande y visible
        btn_editar = tk.Button(frame, text="✏️ Editar",
                               font=("Arial", 9, "bold"),
                               bg=COLORES['acento'], fg="white",
                               relief=tk.FLAT, cursor="hand2",
                               padx=10, pady=4,
                               command=lambda p=prod: self.abrir_editor_producto(p))
        btn_editar.place(relx=1.0, rely=0.0, anchor="ne", x=-6, y=6)

    def seleccionar_producto(self, prod):
        self.producto_seleccionado = prod

        for key, lbl in self.campos_info.items():
            valor = prod.get(key, "-")
            if key == "precio":
                valor = f"${valor:,.2f}"
            elif key == "costo":
                valor = f"${valor:,.2f}"
            elif key == "ganancia":
                valor = f"${valor:,.2f}"
            elif key == "margen":
                valor = f"{valor}%"
            elif key == "cantidad":
                valor = f"{valor} unidades"
            elif key == "fecha_vencimiento":
                if valor:
                    dias = prod.get('dias_para_vencer', 0)
                    valor = f"{valor} ({dias} días)"
                else:
                    valor = "No aplica"
            lbl.config(text=str(valor))

        # Estado
        if prod['cantidad'] <= prod['stock_minimo']:
            self.lbl_estado_det.config(text="🔴 STOCK BAJO - ¡Reponer urgentemente!", fg=COLORES['peligro'])
        elif prod.get('dias_para_vencer') and prod['dias_para_vencer'] <= 7:
            self.lbl_estado_det.config(text=f"⚠️ POR VENCER - {prod['dias_para_vencer']} días restantes", fg=COLORES['peligro'])
        elif prod.get('dias_para_vencer') and prod['dias_para_vencer'] <= 30:
            self.lbl_estado_det.config(text=f"⚡ VENCE PRONTO - {prod['dias_para_vencer']} días", fg=COLORES['advertencia'])
        else:
            self.lbl_estado_det.config(text="✅ STOCK OK - Producto en buen estado", fg=COLORES['exito'])

        # Barra de progreso
        self.canvas_barra.delete("all")
        max_s = max(prod['stock_minimo'] * 3, prod['cantidad'])
        pct = min(100, (prod['cantidad'] / max_s) * 100)

        if pct <= 33:
            cb = COLORES['peligro']
        elif pct <= 66:
            cb = COLORES['advertencia']
        else:
            cb = COLORES['exito']

        ab = int((pct / 100) * 280)
        self.canvas_barra.create_rectangle(0, 0, ab, 18, fill=cb, outline="")
        self.canvas_barra.create_rectangle(0, 0, 280, 18, outline=COLORES['borde'], width=1)
        self.lbl_pct.config(text=f" {prod['cantidad']}/{prod['stock_minimo']} mínimo  ({pct:.0f}%)")

        # Imagen grande
        try:
            ip = f"imagenes_productos/{prod['id']}.png"
            if os.path.exists(ip):
                img = Image.open(ip).resize((220, 220), Image.LANCZOS)
                it = ImageTk.PhotoImage(img)
                self.lbl_img_det.config(image=it)
                self.lbl_img_det.image = it
            else:
                self.lbl_img_det.config(text=f"📦\n{prod['id']}", image="", font=("Arial", 14), fg=COLORES['texto'])
        except:
            self.lbl_img_det.config(text="Error", image="")

    def pagina_ant(self):
        if self.pagina_actual > 0:
            self.pagina_actual -= 1
            self.actualizar_lista_inventario()

    def pagina_sig(self):
        tp = (len(self.productos_filtrados) + self.productos_por_pagina - 1) // self.productos_por_pagina
        if self.pagina_actual < tp - 1:
            self.pagina_actual += 1
            self.actualizar_lista_inventario()

    def abrir_editor_producto(self, prod):
        """Ventana emergente para editar campos esenciales del producto"""
        win = tk.Toplevel(self.root)
        win.title(f"✏️ Editar — {prod['id']}")
        win.geometry("440x430")
        win.configure(bg=COLORES['bg_panel'])
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text=f"✏️ Editar Producto", font=("Arial", 14, "bold"),
                bg=COLORES['bg_panel'], fg=COLORES['acento']).pack(pady=(15, 5))

        tk.Label(win, text=f"{prod['id']} — {prod['nombre'][:35]}", font=("Arial", 10),
                bg=COLORES['bg_panel'], fg=COLORES['texto_secundario']).pack(pady=(0, 12))

        frame_form = tk.Frame(win, bg=COLORES['bg_panel'])
        frame_form.pack(fill=tk.X, padx=25)

        campos = [
            ("Nombre", "nombre", prod.get('nombre', '')),
            ("Precio", "precio", str(prod.get('precio', ''))),
            ("Costo", "costo", str(prod.get('costo', ''))),
            ("Cantidad", "cantidad", str(prod.get('cantidad', ''))),
            ("Stock Mínimo", "stock_minimo", str(prod.get('stock_minimo', ''))),
            ("Proveedor", "proveedor", prod.get('proveedor', '')),
            ("Fecha Vencimiento", "fecha_vencimiento", prod.get('fecha_vencimiento', '') or ''),
        ]

        entradas = {}
        for i, (label, key, valor) in enumerate(campos):
            tk.Label(frame_form, text=f"{label}:", font=("Arial", 10),
                    bg=COLORES['bg_panel'], fg=COLORES['texto_secundario'],
                    anchor="w", width=18).grid(row=i, column=0, sticky="w", pady=4)

            entry = tk.Entry(frame_form, font=("Arial", 10), width=22,
                            bg=COLORES['bg_tarjeta'], fg=COLORES['texto'],
                            insertbackground="white", relief=tk.FLAT)
            entry.insert(0, valor)
            entry.grid(row=i, column=1, sticky="ew", pady=4, padx=(8, 0))
            entradas[key] = entry

        frame_form.columnconfigure(1, weight=1)

        def guardar():
            try:
                nuevo_nombre = entradas['nombre'].get().strip()
                nuevo_precio = float(entradas['precio'].get())
                nuevo_costo = float(entradas['costo'].get()) if entradas['costo'].get().strip() else prod.get('costo', 0)
                nueva_cantidad = int(entradas['cantidad'].get())
                nuevo_minimo = int(entradas['stock_minimo'].get())
                nuevo_proveedor = entradas['proveedor'].get().strip()
                nueva_fecha = entradas['fecha_vencimiento'].get().strip() or None

                if not nuevo_nombre:
                    messagebox.showerror("Error", "El nombre no puede estar vacío.", parent=win)
                    return

                # FIX: Recalcular ganancia y margen al guardar
                nueva_ganancia = round(nuevo_precio - nuevo_costo, 2)
                nuevo_margen = round((nueva_ganancia / nuevo_precio) * 100, 1) if nuevo_precio > 0 else 0

                # FIX: Recalcular dias_para_vencer si se cambió la fecha
                nuevos_dias = None
                if nueva_fecha:
                    try:
                        fecha_dt = datetime.strptime(nueva_fecha, '%Y-%m-%d')
                        nuevos_dias = (fecha_dt - datetime.now()).days
                    except:
                        pass

                # Actualizar en la lista de productos
                for p in self.todos_productos:
                    if p['id'] == prod['id']:
                        p['nombre'] = nuevo_nombre
                        p['precio'] = nuevo_precio
                        p['costo'] = nuevo_costo
                        p['ganancia'] = nueva_ganancia
                        p['margen'] = nuevo_margen
                        p['cantidad'] = nueva_cantidad
                        p['stock_minimo'] = nuevo_minimo
                        p['proveedor'] = nuevo_proveedor
                        p['fecha_vencimiento'] = nueva_fecha
                        if nuevos_dias is not None:
                            p['dias_para_vencer'] = nuevos_dias
                        break

                # Guardar en archivo
                with open('productos_1000.json', 'w', encoding='utf-8') as f:
                    json.dump(self.todos_productos, f, ensure_ascii=False, indent=2)

                win.destroy()
                self.productos_filtrados = self.todos_productos.copy()
                self.actualizar_lista_inventario()
                # Refrescar detalle si es el mismo producto
                if self.producto_seleccionado and self.producto_seleccionado['id'] == prod['id']:
                    self.seleccionar_producto(prod)

            except ValueError:
                messagebox.showerror("Error", "Precio, costo, cantidad y stock mínimo deben ser números.", parent=win)

        frame_btns = tk.Frame(win, bg=COLORES['bg_panel'])
        frame_btns.pack(pady=18)

        tk.Button(frame_btns, text="💾 Guardar", command=guardar,
                 bg=COLORES['exito'], fg="white", font=("Arial", 11, "bold"),
                 relief=tk.FLAT, padx=20, pady=6, cursor="hand2").pack(side=tk.LEFT, padx=8)

        tk.Button(frame_btns, text="Cancelar", command=win.destroy,
                 bg=COLORES['bg_tarjeta'], fg=COLORES['texto'], font=("Arial", 11),
                 relief=tk.FLAT, padx=20, pady=6, cursor="hand2").pack(side=tk.LEFT, padx=8)

    # ==================== PUNTO DE VENTA ====================
    def mostrar_ventas(self):
        self.limpiar_contenido()
        self.vista_actual = "ventas"
        self.resaltar_boton("🛒 Punto de Venta")

        # Header
        frame_header = tk.Frame(self.frame_contenido, bg=COLORES['bg_principal'], height=70)
        frame_header.pack(fill=tk.X, padx=25, pady=(15, 5))
        frame_header.pack_propagate(False)

        tk.Label(frame_header, text="🛒 Punto de Venta", font=("Arial", 22, "bold"),
                bg=COLORES['bg_principal'], fg=COLORES['texto_titulo']).pack(side=tk.LEFT, pady=12)

        # Panel dividido con grid para que sea responsivo
        frame_main = tk.Frame(self.frame_contenido, bg=COLORES['bg_principal'])
        frame_main.pack(fill=tk.BOTH, expand=True, padx=25, pady=5)

        # Configurar grid con pesos iguales para ambos lados
        frame_main.columnconfigure(0, weight=1)  # Izquierda: búsqueda
        frame_main.columnconfigure(1, weight=1)  # Derecha: carrito
        frame_main.rowconfigure(0, weight=1)

        # Izquierda: Buscador de productos
        frame_izq = tk.Frame(frame_main, bg=COLORES['bg_panel'])
        frame_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(frame_izq, text="🔍 Buscar Producto", font=("Arial", 14, "bold"),
                bg=COLORES['bg_panel'], fg=COLORES['acento']).pack(anchor="w", padx=15, pady=10)

        self.entry_venta_buscar = tk.Entry(frame_izq, font=("Arial", 12), width=35,
                                          bg=COLORES['bg_tarjeta'], fg=COLORES['texto'],
                                          insertbackground="white", relief=tk.FLAT)
        self.entry_venta_buscar.pack(padx=15, pady=5, ipady=5)
        self.entry_venta_buscar.bind("<KeyRelease>", lambda e: self.buscar_producto_venta())
        self.entry_venta_buscar.bind("<Return>", lambda e: self.buscar_producto_venta())

        # FIX: Indicación visual del mínimo de caracteres
        self.lbl_hint_buscar = tk.Label(frame_izq, text="Escribe al menos 2 caracteres para buscar",
                                        font=("Arial", 9), bg=COLORES['bg_panel'],
                                        fg=COLORES['texto_secundario'])
        self.lbl_hint_buscar.pack(anchor="w", padx=15)

        # Resultados de búsqueda con scroll
        frame_res_outer = tk.Frame(frame_izq, bg=COLORES['bg_panel'])
        frame_res_outer.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        canvas_res = tk.Canvas(frame_res_outer, bg=COLORES['bg_panel'], highlightthickness=0)
        scrollbar_res = ttk.Scrollbar(frame_res_outer, orient="vertical", command=canvas_res.yview)
        self.frame_resultados_venta = tk.Frame(canvas_res, bg=COLORES['bg_panel'])

        self.frame_resultados_venta.bind("<Configure>",
            lambda e: canvas_res.configure(scrollregion=canvas_res.bbox("all")))

        canvas_res.create_window((0, 0), window=self.frame_resultados_venta, anchor="nw")
        canvas_res.configure(yscrollcommand=scrollbar_res.set)

        canvas_res.grid(row=0, column=0, sticky="nsew")
        scrollbar_res.grid(row=0, column=1, sticky="ns")

        # Configurar grid para frame_res_outer
        frame_res_outer.rowconfigure(0, weight=1)
        frame_res_outer.columnconfigure(0, weight=1)

        # Scroll del mouse solo cuando el cursor está sobre el canvas de resultados
        canvas_res.bind("<Enter>",
            lambda e: canvas_res.bind_all("<MouseWheel>",
                lambda ev: canvas_res.yview_scroll(int(-1*(ev.delta/120)), "units")))
        canvas_res.bind("<Leave>",
            lambda e: canvas_res.unbind_all("<MouseWheel>"))

        # Derecha: Carrito
        frame_der = tk.Frame(frame_main, bg=COLORES['bg_panel'])
        frame_der.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        # FIX: Configurar grid ANTES de agregar widgets para evitar conflicto pack/grid
        frame_der.rowconfigure(0, weight=0)  # Label del título
        frame_der.rowconfigure(1, weight=1)  # Canvas del carrito (expande)
        frame_der.rowconfigure(2, weight=0)  # Totales
        frame_der.rowconfigure(3, weight=0)  # Método de pago
        frame_der.rowconfigure(4, weight=0)  # Botones
        frame_der.columnconfigure(0, weight=1)
        frame_der.columnconfigure(1, weight=0)  # Scrollbar

        # Label del carrito usando grid
        tk.Label(frame_der, text="🛒 Carrito de Compras", font=("Arial", 14, "bold"),
                bg=COLORES['bg_panel'], fg=COLORES['acento']).grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=10)

        # FIX: Canvas con scroll para el carrito (evita parpadeo al reconstruir)
        # Usar grid para que se ajuste correctamente
        canvas_carrito = tk.Canvas(frame_der, bg=COLORES['bg_panel'], highlightthickness=0)
        scrollbar_carrito = ttk.Scrollbar(frame_der, orient="vertical", command=canvas_carrito.yview)
        self.frame_carrito = tk.Frame(canvas_carrito, bg=COLORES['bg_panel'])

        self.frame_carrito.bind("<Configure>",
            lambda e: canvas_carrito.configure(scrollregion=canvas_carrito.bbox("all")))

        canvas_carrito.create_window((0, 0), window=self.frame_carrito, anchor="nw")
        canvas_carrito.configure(yscrollcommand=scrollbar_carrito.set)

        canvas_carrito.grid(row=1, column=0, sticky="nsew", padx=(0, 0))
        scrollbar_carrito.grid(row=1, column=1, sticky="ns")

        # Scroll del mouse solo cuando el cursor está sobre el canvas
        canvas_carrito.bind("<Enter>",
            lambda e: canvas_carrito.bind_all("<MouseWheel>",
                lambda ev: canvas_carrito.yview_scroll(int(-1*(ev.delta/120)), "units")))
        canvas_carrito.bind("<Leave>",
            lambda e: canvas_carrito.unbind_all("<MouseWheel>"))

        # Totales (fuera del canvas para que siempre sean visibles)
        frame_totales = tk.Frame(frame_der, bg=COLORES['bg_tarjeta'])
        frame_totales.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 0))
        frame_totales.columnconfigure(0, weight=1)

        self.lbl_subtotal = tk.Label(frame_totales, text="Subtotal: $0.00", font=("Arial", 11),
                                    bg=COLORES['bg_tarjeta'], fg=COLORES['texto'])
        self.lbl_subtotal.pack(anchor="e", padx=15, pady=1)

        self.lbl_iva = tk.Label(frame_totales, text="IVA (16%): $0.00", font=("Arial", 11),
                               bg=COLORES['bg_tarjeta'], fg=COLORES['texto'])
        self.lbl_iva.pack(anchor="e", padx=15, pady=1)

        self.lbl_total_venta = tk.Label(frame_totales, text="TOTAL: $0.00", font=("Arial", 14, "bold"),
                                       bg=COLORES['bg_tarjeta'], fg=COLORES['exito'])
        self.lbl_total_venta.pack(anchor="e", padx=15, pady=3)

        # Método de pago
        frame_pago = tk.Frame(frame_der, bg=COLORES['bg_panel'])
        frame_pago.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        frame_pago.columnconfigure(1, weight=1)

        tk.Label(frame_pago, text="💳 Método:", font=("Arial", 10),
                bg=COLORES['bg_panel'], fg=COLORES['texto_secundario']).grid(row=0, column=0, sticky="w", padx=5)

        combo_pago = ttk.Combobox(frame_pago, textvariable=self.metodo_pago,
                                 values=["Efectivo", "Tarjeta Débito", "Tarjeta Crédito", "Transferencia"],
                                 state="readonly", width=15, font=("Arial", 9))
        combo_pago.grid(row=0, column=1, sticky="ew", padx=5)

        # Botones
        frame_btns = tk.Frame(frame_der, bg=COLORES['bg_panel'])
        frame_btns.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        frame_btns.columnconfigure(0, weight=1)
        frame_btns.columnconfigure(1, weight=1)

        tk.Button(frame_btns, text="✅ Finalizar Venta", command=self.finalizar_venta,
                 bg=COLORES['exito'], fg="white", font=("Arial", 11, "bold"),
                 relief=tk.FLAT, padx=15, pady=6, cursor="hand2").grid(row=0, column=0, sticky="ew", padx=2)

        tk.Button(frame_btns, text="🗑️ Vaciar Carrito", command=self.vaciar_carrito,
                 bg=COLORES['peligro'], fg="white", font=("Arial", 11, "bold"),
                 relief=tk.FLAT, padx=15, pady=6, cursor="hand2").grid(row=0, column=1, sticky="ew", padx=2)

        self.actualizar_carrito()

    def buscar_producto_venta(self):
        busq = self.entry_venta_buscar.get().lower()

        for widget in self.frame_resultados_venta.winfo_children():
            widget.destroy()

        if len(busq) < 2:
            # FIX: Mostrar hint cuando hay menos de 2 caracteres
            if len(busq) == 1:
                tk.Label(self.frame_resultados_venta,
                        text="Escribe al menos 2 caracteres...",
                        font=("Arial", 10), bg=COLORES['bg_panel'],
                        fg=COLORES['texto_secundario']).pack(pady=10)
            return

        # Búsqueda exacta + fuzzy search
        resultados_exactos = [p for p in self.todos_productos
                     if busq in p['nombre'].lower() or busq in p['id'].lower() or busq in p.get('marca', '').lower()]
        
        # Si hay menos de 5 resultados exactos, agregar fuzzy matches
        if len(resultados_exactos) < 5:
            resultados_fuzzy = []
            for p in self.todos_productos:
                if p not in resultados_exactos:
                    nombre_ratio = difflib.SequenceMatcher(None, busq, p['nombre'].lower()).ratio()
                    marca_ratio = difflib.SequenceMatcher(None, busq, p.get('marca', '').lower()).ratio()
                    if nombre_ratio >= 0.65 or marca_ratio >= 0.65:
                        resultados_fuzzy.append((max(nombre_ratio, marca_ratio), p))
            resultados_fuzzy.sort(reverse=True, key=lambda x: x[0])
            resultados = resultados_exactos + [p for _, p in resultados_fuzzy]
        else:
            resultados = resultados_exactos
        
        resultados = resultados[:10]

        if not resultados:
            tk.Label(self.frame_resultados_venta,
                    text="❌ No se encontraron productos",
                    font=("Arial", 10), bg=COLORES['bg_panel'],
                    fg=COLORES['peligro']).pack(pady=10)
            return

        for p in resultados:
            # Cambiar color del borde si es un match fuzzy
            nombre_ratio = difflib.SequenceMatcher(None, busq, p['nombre'].lower()).ratio()
            es_fuzzy = nombre_ratio >= 0.65 and nombre_ratio < 1.0
            borde_color = COLORES['advertencia'] if es_fuzzy else COLORES['borde']
            
            frame = tk.Frame(self.frame_resultados_venta, bg=COLORES['bg_tarjeta'],
                            highlightbackground=borde_color, highlightthickness=1)
            frame.pack(fill=tk.X, padx=5, pady=3)

            tk.Label(frame, text=f"{p['id']}", font=("Arial", 9, "bold"),
                    bg=COLORES['bg_tarjeta'], fg=COLORES['acento'], width=8).pack(side=tk.LEFT, padx=8, pady=5)

            tk.Label(frame, text=p['nombre'][:30], font=("Arial", 10),
                    bg=COLORES['bg_tarjeta'], fg=COLORES['texto']).pack(side=tk.LEFT, padx=5, pady=5)

            tk.Label(frame, text=f"${p['precio']:,.2f}", font=("Arial", 10, "bold"),
                    bg=COLORES['bg_tarjeta'], fg=COLORES['exito']).pack(side=tk.LEFT, padx=10, pady=5)

            # Stock disponible
            color_stock = COLORES['peligro'] if p['cantidad'] <= p['stock_minimo'] else COLORES['texto_secundario']
            tk.Label(frame, text=f"Stock: {p['cantidad']}", font=("Arial", 9),
                    bg=COLORES['bg_tarjeta'], fg=color_stock).pack(side=tk.LEFT, padx=5, pady=5)
            
            # Indicador de fuzzy match
            if es_fuzzy:
                tk.Label(frame, text="⚠️ Aproximado", font=("Arial", 8),
                        bg=COLORES['bg_tarjeta'], fg=COLORES['advertencia']).pack(side=tk.LEFT, padx=5, pady=5)

            btn = tk.Button(frame, text="➕ Agregar", command=lambda prod=p: self.agregar_al_carrito(prod),
                           bg=COLORES['acento'], fg="white", font=("Arial", 9, "bold"),
                           relief=tk.FLAT, padx=10, cursor="hand2")
            btn.pack(side=tk.RIGHT, padx=8, pady=5)

    def agregar_al_carrito(self, prod):
        # Buscar si ya está en el carrito
        for item in self.carrito:
            if item['id'] == prod['id']:
                if item['cantidad'] < prod['cantidad']:
                    item['cantidad'] += 1
                    self.mostrar_toast(f"✅ {prod['nombre']} (+1)", tipo="exito", duracion=1500)
                else:
                    self.mostrar_toast(f"⚠️ Solo hay {prod['cantidad']} unidades", tipo="advertencia", duracion=2000)
                self.actualizar_carrito()
                return

        # Agregar nuevo
        if prod['cantidad'] > 0:
            self.carrito.append({
                'id': prod['id'],
                'nombre': prod['nombre'],
                'precio': prod['precio'],
                'cantidad': 1,
                'stock_disponible': prod['cantidad']
            })
            self.mostrar_toast(f"✅ {prod['nombre']} agregado al carrito", tipo="exito", duracion=1500)
            self.actualizar_carrito()
        else:
            self.mostrar_toast("❌ Sin stock disponible", tipo="peligro", duracion=2000)

    def actualizar_carrito(self):
        """Reconstruye el carrito completo. Usado al agregar/quitar items."""
        # Limpiar referencias de widgets de items anteriores
        self._widgets_carrito = {}

        for widget in self.frame_carrito.winfo_children():
            widget.destroy()

        if not self.carrito:
            tk.Label(self.frame_carrito, text="🛒 El carrito está vacío", font=("Arial", 12),
                    bg=COLORES['bg_panel'], fg=COLORES['texto_secundario']).pack(pady=30)
            self.lbl_subtotal.config(text="Subtotal: $0.00")
            self.lbl_iva.config(text="IVA (16%): $0.00")
            self.lbl_total_venta.config(text="TOTAL: $0.00")
            return

        # Headers
        frame_headers = tk.Frame(self.frame_carrito, bg=COLORES['bg_panel'])
        frame_headers.pack(fill=tk.X, padx=5, pady=2)

        tk.Label(frame_headers, text="Producto", font=("Arial", 9, "bold"),
                bg=COLORES['bg_panel'], fg=COLORES['texto_secundario'], width=25, anchor="w").pack(side=tk.LEFT)
        tk.Label(frame_headers, text="Precio", font=("Arial", 9, "bold"),
                bg=COLORES['bg_panel'], fg=COLORES['texto_secundario'], width=12).pack(side=tk.LEFT)
        tk.Label(frame_headers, text="Cant", font=("Arial", 9, "bold"),
                bg=COLORES['bg_panel'], fg=COLORES['texto_secundario'], width=6).pack(side=tk.LEFT)
        tk.Label(frame_headers, text="Total", font=("Arial", 9, "bold"),
                bg=COLORES['bg_panel'], fg=COLORES['texto_secundario'], width=12).pack(side=tk.LEFT)

        # Items — guardar referencias a los labels para actualización sin parpadeo
        for item in self.carrito:
            frame_item = tk.Frame(self.frame_carrito, bg=COLORES['bg_tarjeta'])
            frame_item.pack(fill=tk.X, padx=5, pady=2)

            tk.Label(frame_item, text=item['nombre'][:22], font=("Arial", 10),
                    bg=COLORES['bg_tarjeta'], fg=COLORES['texto'], width=25, anchor="w").pack(side=tk.LEFT, padx=5, pady=4)

            tk.Label(frame_item, text=f"${item['precio']:,.2f}", font=("Arial", 10),
                    bg=COLORES['bg_tarjeta'], fg=COLORES['texto'], width=12).pack(side=tk.LEFT, pady=4)

            # Cantidad con botones
            fc = tk.Frame(frame_item, bg=COLORES['bg_tarjeta'])
            fc.pack(side=tk.LEFT, pady=4)

            tk.Button(fc, text="-", command=lambda i=item: self.cambiar_cantidad(i, -1),
                     bg=COLORES['bg_hover'], fg=COLORES['texto'], font=("Arial", 8, "bold"),
                     relief=tk.FLAT, width=2, cursor="hand2").pack(side=tk.LEFT)

            # FIX: Guardar referencia al label de cantidad por ID del producto
            lbl_cant = tk.Label(fc, text=str(item['cantidad']), font=("Arial", 10, "bold"),
                    bg=COLORES['bg_tarjeta'], fg=COLORES['acento'], width=3)
            lbl_cant.pack(side=tk.LEFT)

            tk.Button(fc, text="+", command=lambda i=item: self.cambiar_cantidad(i, 1),
                     bg=COLORES['bg_hover'], fg=COLORES['texto'], font=("Arial", 8, "bold"),
                     relief=tk.FLAT, width=2, cursor="hand2").pack(side=tk.LEFT)

            total_item = item['precio'] * item['cantidad']
            # FIX: Guardar referencia al label de total por ID del producto
            lbl_total_item = tk.Label(frame_item, text=f"${total_item:,.2f}", font=("Arial", 10, "bold"),
                    bg=COLORES['bg_tarjeta'], fg=COLORES['exito'], width=12)
            lbl_total_item.pack(side=tk.LEFT, pady=4)

            # Guardar referencias indexadas por ID del producto
            self._widgets_carrito[item['id']] = {
                'lbl_cant': lbl_cant,
                'lbl_total': lbl_total_item
            }

            tk.Button(frame_item, text="🗑️", command=lambda i=item: self.quitar_del_carrito(i),
                     bg=COLORES['peligro'], fg="white", font=("Arial", 8),
                     relief=tk.FLAT, cursor="hand2").pack(side=tk.RIGHT, padx=5)

        # Calcular totales
        subtotal = sum(item['precio'] * item['cantidad'] for item in self.carrito)
        iva = subtotal * 0.16
        total = subtotal + iva

        self.lbl_subtotal.config(text=f"Subtotal: ${subtotal:,.2f}")
        self.lbl_iva.config(text=f"IVA (16%): ${iva:,.2f}")
        self.lbl_total_venta.config(text=f"TOTAL: ${total:,.2f}")

    def cambiar_cantidad(self, item, delta):
        """FIX: Actualiza solo los labels del item sin reconstruir todo el carrito.
        Esto elimina el parpadeo al presionar + o -."""
        nueva_cant = item['cantidad'] + delta
        if nueva_cant > 0 and nueva_cant <= item['stock_disponible']:
            item['cantidad'] = nueva_cant
            # Actualizar solo los widgets de este item (sin parpadeo)
            widgets = getattr(self, '_widgets_carrito', {}).get(item['id'])
            if widgets:
                widgets['lbl_cant'].config(text=str(nueva_cant))
                total_item = item['precio'] * nueva_cant
                widgets['lbl_total'].config(text=f"${total_item:,.2f}")
                # Recalcular y actualizar totales generales
                subtotal = sum(i['precio'] * i['cantidad'] for i in self.carrito)
                iva = subtotal * 0.16
                total = subtotal + iva
                self.lbl_subtotal.config(text=f"Subtotal: ${subtotal:,.2f}")
                self.lbl_iva.config(text=f"IVA (16%): ${iva:,.2f}")
                self.lbl_total_venta.config(text=f"TOTAL: ${total:,.2f}")
            else:
                # Fallback: reconstruir si no hay referencia
                self.actualizar_carrito()
        elif nueva_cant <= 0:
            self.quitar_del_carrito(item)
        elif nueva_cant > item['stock_disponible']:
            messagebox.showwarning("Stock", f"Máximo {item['stock_disponible']} unidades")

    def quitar_del_carrito(self, item):
        self.carrito.remove(item)
        self.actualizar_carrito()

    def vaciar_carrito(self):
        if self.carrito:
            if messagebox.askyesno("Confirmar", "¿Vaciar el carrito?"):
                self.carrito = []
                self.actualizar_carrito()

    def limpiar_busqueda_venta(self):
        """Limpia el buscador de productos en Punto de Venta (atajo Esc)"""
        if self.vista_actual == 'ventas':
            self.entry_venta_buscar.delete(0, tk.END)
            for widget in self.frame_resultados_venta.winfo_children():
                widget.destroy()

    def finalizar_venta(self):
        if not self.carrito:
            self.mostrar_toast("❌ Carrito vacío", tipo="peligro", duracion=2000)
            return

        subtotal = sum(item['precio'] * item['cantidad'] for item in self.carrito)
        iva = subtotal * 0.16
        total = subtotal + iva

        # Confirmar
        msg = f"Total a pagar: ${total:,.2f}\n\nMétodo: {self.metodo_pago.get()}\n\n¿Confirmar venta?"
        if not messagebox.askyesno("Confirmar Venta", msg):
            return

        # Descontar stock
        for item in self.carrito:
            for p in self.todos_productos:
                if p['id'] == item['id']:
                    p['cantidad'] -= item['cantidad']
                    break

        # Guardar venta
        venta = {
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'productos': self.carrito.copy(),
            'subtotal': subtotal,
            'iva': iva,
            'total': total,
            'metodo_pago': self.metodo_pago.get()
        }

        try:
            with open('ventas.json', 'r', encoding='utf-8') as f:
                ventas = json.load(f)
        except:
            ventas = []

        ventas.append(venta)

        with open('ventas.json', 'w', encoding='utf-8') as f:
            json.dump(ventas, f, ensure_ascii=False, indent=2)

        # Guardar inventario actualizado
        with open('productos_1000.json', 'w', encoding='utf-8') as f:
            json.dump(self.todos_productos, f, ensure_ascii=False, indent=2)

        self.mostrar_toast(f"✅ Venta de ${total:,.2f} registrada", tipo="exito", duracion=2000)

        self.carrito = []
        self.actualizar_carrito()
        self.entry_venta_buscar.delete(0, tk.END)
        # Limpiar resultados de búsqueda
        for widget in self.frame_resultados_venta.winfo_children():
            widget.destroy()

    # ==================== REPORTES ====================
    def mostrar_reportes(self):
        self.limpiar_contenido()
        self.vista_actual = "reportes"
        self.resaltar_boton("📈 Reportes")

        # Scroll para reportes
        canvas_rep = tk.Canvas(self.frame_contenido, bg=COLORES['bg_principal'], highlightthickness=0)
        scrollbar_rep = ttk.Scrollbar(self.frame_contenido, orient="vertical", command=canvas_rep.yview)
        frame_rep = tk.Frame(canvas_rep, bg=COLORES['bg_principal'])

        frame_rep.bind("<Configure>",
            lambda e: canvas_rep.configure(scrollregion=canvas_rep.bbox("all")))

        canvas_rep.create_window((0, 0), window=frame_rep, anchor="nw")
        canvas_rep.configure(yscrollcommand=scrollbar_rep.set)

        canvas_rep.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_rep.pack(side=tk.RIGHT, fill=tk.Y)

        canvas_rep.bind("<MouseWheel>",
            lambda e: canvas_rep.yview_scroll(int(-1*(e.delta/120)), "units"))

        def _ajustar_ancho_rep(event):
            canvas_rep.itemconfig(canvas_rep.find_withtag("all")[0], width=event.width)
        canvas_rep.bind("<Configure>", _ajustar_ancho_rep)

        frame_header = tk.Frame(frame_rep, bg=COLORES['bg_principal'], height=70)
        frame_header.pack(fill=tk.X, padx=25, pady=(15, 5))
        frame_header.pack_propagate(False)

        tk.Label(frame_header, text="📈 Reportes y Estadísticas", font=("Arial", 22, "bold"),
                bg=COLORES['bg_principal'], fg=COLORES['texto_titulo']).pack(side=tk.LEFT, pady=12)

        # Cargar ventas
        try:
            with open('ventas.json', 'r', encoding='utf-8') as f:
                ventas = json.load(f)
        except:
            ventas = []

        # Métricas
        frame_metrics = tk.Frame(frame_rep, bg=COLORES['bg_principal'])
        frame_metrics.pack(fill=tk.X, padx=25, pady=10)

        total_ventas = len(ventas)
        ingresos_total = sum(v['total'] for v in ventas)
        productos_vendidos = sum(sum(item['cantidad'] for item in v['productos']) for v in ventas)

        metricas = [
            ("🛒 Ventas Realizadas", str(total_ventas), COLORES['acento']),
            ("💰 Ingresos Totales", f"${ingresos_total:,.2f}", COLORES['exito']),
            ("📦 Productos Vendidos", str(productos_vendidos), COLORES['advertencia']),
        ]

        for titulo, valor, color in metricas:
            f = tk.Frame(frame_metrics, bg=COLORES['bg_panel'], width=300, height=100)
            f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8)
            f.pack_propagate(False)
            tk.Frame(f, bg=color, height=3).pack(fill=tk.X)
            tk.Label(f, text=titulo, font=("Arial", 11), bg=COLORES['bg_panel'], fg=COLORES['texto_secundario']).pack(pady=(10, 0))
            tk.Label(f, text=valor, font=("Arial", 24, "bold"), bg=COLORES['bg_panel'], fg=color).pack()

        # Historial de ventas
        frame_historial = tk.Frame(frame_rep, bg=COLORES['bg_panel'])
        frame_historial.pack(fill=tk.X, padx=25, pady=15)

        tk.Label(frame_historial, text="📋 Historial de Ventas", font=("Arial", 16, "bold"),
                bg=COLORES['bg_panel'], fg=COLORES['acento']).pack(anchor="w", padx=15, pady=10)

        if ventas:
            for v in reversed(ventas[-20:]):
                fv = tk.Frame(frame_historial, bg=COLORES['bg_tarjeta'])
                fv.pack(fill=tk.X, padx=10, pady=3)

                tk.Label(fv, text=f"📅 {v['fecha']}", font=("Arial", 10, "bold"),
                        bg=COLORES['bg_tarjeta'], fg=COLORES['acento'], width=20).pack(side=tk.LEFT, padx=8, pady=6)

                productos_txt = ", ".join([f"{item['nombre'][:15]} (x{item['cantidad']})" for item in v['productos'][:3]])
                if len(v['productos']) > 3:
                    productos_txt += f" +{len(v['productos'])-3} más"

                tk.Label(fv, text=productos_txt, font=("Arial", 10),
                        bg=COLORES['bg_tarjeta'], fg=COLORES['texto']).pack(side=tk.LEFT, padx=5, pady=6)

                tk.Label(fv, text=f"${v['total']:,.2f}", font=("Arial", 11, "bold"),
                        bg=COLORES['bg_tarjeta'], fg=COLORES['exito']).pack(side=tk.RIGHT, padx=10, pady=6)

                tk.Label(fv, text=f"💳 {v['metodo_pago']}", font=("Arial", 9),
                        bg=COLORES['bg_tarjeta'], fg=COLORES['texto_secundario']).pack(side=tk.RIGHT, padx=5, pady=6)
        else:
            tk.Label(frame_historial, text="No hay ventas registradas", font=("Arial", 12),
                    bg=COLORES['bg_panel'], fg=COLORES['texto_secundario']).pack(pady=30)

    # ==================== CONFIGURACIÓN ====================
    def mostrar_configuracion(self):
        self.limpiar_contenido()
        self.vista_actual = "configuracion"
        self.resaltar_boton("⚙️ Configuración")

        frame_header = tk.Frame(self.frame_contenido, bg=COLORES['bg_principal'], height=70)
        frame_header.pack(fill=tk.X, padx=25, pady=(15, 5))
        frame_header.pack_propagate(False)

        tk.Label(frame_header, text="⚙️ Configuración", font=("Arial", 22, "bold"),
                bg=COLORES['bg_principal'], fg=COLORES['texto_titulo']).pack(side=tk.LEFT, pady=12)

        frame_config = tk.Frame(self.frame_contenido, bg=COLORES['bg_panel'])
        frame_config.pack(fill=tk.BOTH, expand=True, padx=25, pady=15)

        # Info del sistema
        tk.Label(frame_config, text="ℹ️ Información del Sistema", font=("Arial", 14, "bold"),
                bg=COLORES['bg_panel'], fg=COLORES['acento']).pack(anchor="w", padx=15, pady=10)

        info_items = [
            ("Versión", "StockMaster Pro v3.0"),
            ("Productos", str(len(self.todos_productos))),
            ("Categorías", str(len(self.categorias) - 1)),
            ("Última actualización", datetime.now().strftime('%d/%m/%Y %H:%M')),
        ]

        for label, valor in info_items:
            f = tk.Frame(frame_config, bg=COLORES['bg_tarjeta'])
            f.pack(fill=tk.X, padx=10, pady=3)
            tk.Label(f, text=f"{label}:", font=("Arial", 11, "bold"),
                    bg=COLORES['bg_tarjeta'], fg=COLORES['texto_secundario'], width=20, anchor="w").pack(side=tk.LEFT, padx=10, pady=6)
            tk.Label(f, text=valor, font=("Arial", 11),
                    bg=COLORES['bg_tarjeta'], fg=COLORES['texto']).pack(side=tk.LEFT, padx=5, pady=6)

        # Botones de acción
        tk.Label(frame_config, text="🛠️ Acciones", font=("Arial", 14, "bold"),
                bg=COLORES['bg_panel'], fg=COLORES['acento']).pack(anchor="w", padx=15, pady=(20, 10))

        frame_btns = tk.Frame(frame_config, bg=COLORES['bg_panel'])
        frame_btns.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(frame_btns, text="💾 Guardar Inventario", command=self.guardar_inventario,
                 bg=COLORES['acento'], fg="white", font=("Arial", 11, "bold"),
                 relief=tk.FLAT, padx=20, pady=8, cursor="hand2").pack(side=tk.LEFT, padx=5)

        tk.Button(frame_btns, text="🔄 Recargar Datos", command=self.recargar_datos,
                 bg=COLORES['bg_tarjeta'], fg=COLORES['texto'], font=("Arial", 11, "bold"),
                 relief=tk.FLAT, padx=20, pady=8, cursor="hand2").pack(side=tk.LEFT, padx=5)

    def guardar_inventario(self):
        with open('productos_1000.json', 'w', encoding='utf-8') as f:
            json.dump(self.todos_productos, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("✅ Guardado", "Inventario guardado correctamente")

    def recargar_datos(self):
        self.cargar_datos()
        messagebox.showinfo("✅ Recargado", "Datos recargados correctamente")
        if self.vista_actual == "inventario":
            self.mostrar_inventario()
        elif self.vista_actual == "dashboard":
            self.mostrar_dashboard()

    def resaltar_boton(self, texto):
        for t, btn in self.botones_menu.items():
            if t == texto:
                btn.config(bg=COLORES['bg_hover'], fg=COLORES['acento'])
            else:
                btn.config(bg=COLORES['bg_panel'], fg=COLORES['texto'])


if __name__ == "__main__":
    root = tk.Tk()
    app = AppInventario(root)
    root.mainloop()
