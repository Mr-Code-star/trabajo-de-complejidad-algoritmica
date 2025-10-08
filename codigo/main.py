import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, Canvas, Frame
import os
from grafos import (cargar_grafo, cargar_usuarios, camino_mas_corto, 
                   recomendar_amigos, obtener_subgrafo,
                   SistemaComunidades, analizar_grafo, 
                   VisualizadorGrafo, calcular_grados)


# Cargar los datos
usuarios, posts = cargar_usuarios()
grafo = cargar_grafo()
sistema_comunidades = SistemaComunidades()


# Clase principal de la aplicación
class RedSocialApp:
    def __init__(self, root):
        self.root = root
        self.root.title(" Mini Red Social")
        self.root.geometry("1200x700")
        self.root.configure(bg="white")
        
        # Variables
        self.visualizador = None
        self.canvas_grafo = None
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Inicializar visualización
        self.inicializar_visualizacion()
    
    def crear_interfaz(self):
        """Crea la interfaz principal con dos paneles"""
        
        # Frame principal con dos columnas
        main_frame = Frame(self.root, bg="white")
        main_frame.pack(fill="both", expand=True)
        
        # Panel izquierdo - Controles
        self.panel_izquierdo = Frame(main_frame, bg="white", width=400)
        self.panel_izquierdo.pack(side="left", fill="y", padx=10, pady=10)
        self.panel_izquierdo.pack_propagate(False)
        
        # Panel derecho - Visualización
        self.panel_derecho = Frame(main_frame, bg="#f0f0f0", relief=tk.SUNKEN, bd=2)
        self.panel_derecho.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Crear controles en panel izquierdo
        self.crear_controles()
        
        # Crear área de visualización en panel derecho
        self.crear_area_visualizacion()
    
    def crear_controles(self):
        """Crea los controles en el panel izquierdo"""
        
        # Título
        tk.Label(self.panel_izquierdo, text=" Mini Red Social", 
                 font=("Arial", 16, "bold"), bg="white").pack(pady=10)
        
        # Frame para selección de usuarios
        frame_usuarios = tk.Frame(self.panel_izquierdo, bg="white")
        frame_usuarios.pack(pady=10, fill="x", padx=20)
        
        tk.Label(frame_usuarios, text="Usuario 1:", bg="white", 
                font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.combo_user1 = ttk.Combobox(frame_usuarios, values=list(usuarios.values()), width=25)
        self.combo_user1.grid(row=0, column=1, padx=5)
        
        tk.Label(frame_usuarios, text="Usuario 2:", bg="white", 
                font=("Arial", 10)).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.combo_user2 = ttk.Combobox(frame_usuarios, values=list(usuarios.values()), width=25)
        self.combo_user2.grid(row=1, column=1, padx=5)
        
        # Separador
        tk.Frame(self.panel_izquierdo, height=2, bg="#e0e0e0").pack(fill="x", pady=10)
        
        # Sección de Búsqueda y Análisis
        tk.Label(self.panel_izquierdo, text=" Búsqueda y Análisis", 
                font=("Arial", 12, "bold"), bg="white").pack(pady=5)
        
        frame_busqueda = tk.Frame(self.panel_izquierdo, bg="white")
        frame_busqueda.pack(pady=5)
        
        tk.Button(frame_busqueda, text=" Buscar camino", 
                 command=self.buscar_camino, bg="#4CAF50", fg="white",
                 font=("Arial", 10), width=20).pack(pady=3)
        
        tk.Button(frame_busqueda, text=" Recomendar amigos", 
                 command=self.mostrar_recomendaciones, bg="#2196F3", fg="white",
                 font=("Arial", 10), width=20).pack(pady=3)
        
        tk.Button(frame_busqueda, text=" Ver feed", 
                 command=self.mostrar_feed, bg="#FF9800", fg="white",
                 font=("Arial", 10), width=20).pack(pady=3)
        
        # Separador
        tk.Frame(self.panel_izquierdo, height=2, bg="#e0e0e0").pack(fill="x", pady=10)
        
        # Sección de Visualización
        tk.Label(self.panel_izquierdo, text=" Opciones de Visualización", 
                font=("Arial", 12, "bold"), bg="white").pack(pady=5)
        
        frame_visual = tk.Frame(self.panel_izquierdo, bg="white")
        frame_visual.pack(pady=5)
        
        # Slider para controlar el alcance de visualización
        tk.Label(frame_visual, text="Alcance de visualización:", 
                bg="white", font=("Arial", 10)).pack()
        
        self.alcance_var = tk.IntVar(value=2)
        self.slider_alcance = tk.Scale(frame_visual, from_=1, to=4, 
                                      orient=tk.HORIZONTAL, 
                                      variable=self.alcance_var,
                                      command=self.actualizar_visualizacion,
                                      bg="white", length=200)
        self.slider_alcance.pack(pady=5)
        
        tk.Button(frame_visual, text=" Ver grafo completo", 
                 command=self.visualizar_grafo_completo, bg="#00BCD4", fg="white",
                 font=("Arial", 10), width=20).pack(pady=3)
        
        tk.Button(frame_visual, text=" Ver vecindario", 
                 command=self.visualizar_vecindario, bg="#9C27B0", fg="white",
                 font=("Arial", 10), width=20).pack(pady=3)
        
        tk.Button(frame_visual, text=" Ver comunidades", 
                 command=self.visualizar_comunidades, bg="#673AB7", fg="white",
                 font=("Arial", 10), width=20).pack(pady=3)
        
        # Separador
        tk.Frame(self.panel_izquierdo, height=2, bg="#e0e0e0").pack(fill="x", pady=10)
        
        # Sección de Comunidades
        tk.Label(self.panel_izquierdo, text=" Gestión de Comunidades", 
                font=("Arial", 12, "bold"), bg="white").pack(pady=5)
        
        frame_comunidades = tk.Frame(self.panel_izquierdo, bg="white")
        frame_comunidades.pack(pady=5)
        
        tk.Button(frame_comunidades, text=" Crear comunidad", 
                 command=self.crear_comunidad, bg="#E91E63", fg="white",
                 font=("Arial", 10), width=20).pack(pady=3)
        
        tk.Button(frame_comunidades, text=" Ver comunidades", 
                 command=self.ver_comunidades, bg="#9E9E9E", fg="white",
                 font=("Arial", 10), width=20).pack(pady=3)
        
        # Botón de estadísticas
        tk.Button(self.panel_izquierdo, text=" Ver Estadísticas", 
                 command=self.mostrar_estadisticas, bg="#607D8B", fg="white",
                 font=("Arial", 10), width=20).pack(pady=10)
    
    def crear_area_visualizacion(self):
        """Crea el área de visualización del grafo"""
        
        # Título del panel
        tk.Label(self.panel_derecho, text=" Visualización del Grafo", 
                font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=5)
        
        # Frame para controles de zoom
        control_frame = tk.Frame(self.panel_derecho, bg="#f0f0f0")
        control_frame.pack(fill="x", padx=10)
        
        tk.Button(control_frame, text="+", command=self.zoom_in,
                 font=("Arial", 10), width=3).pack(side="left", padx=2)
        tk.Button(control_frame, text="-", command=self.zoom_out,
                 font=("Arial", 10), width=3).pack(side="left", padx=2)
        tk.Button(control_frame, text="🔎", command=self.reset_view,
                 font=("Arial", 10), width=3).pack(side="left", padx=2)
        
        self.info_label = tk.Label(control_frame, text="", bg="#f0f0f0", font=("Arial", 9))
        self.info_label.pack(side="right", padx=10)
        
        # Canvas para el grafo
        self.canvas_grafo = Canvas(self.panel_derecho, bg="white", highlightthickness=1)
        self.canvas_grafo.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Bind eventos del mouse para arrastrar
        self.canvas_grafo.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas_grafo.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas_grafo.bind("<MouseWheel>", self.on_mouse_wheel)
        
        self.drag_data = {"x": 0, "y": 0}
    
    def inicializar_visualizacion(self):
        """Inicializa el visualizador del grafo"""
        if self.canvas_grafo:
            # Obtener dimensiones del canvas
            self.root.update()
            ancho = self.canvas_grafo.winfo_width()
            alto = self.canvas_grafo.winfo_height()
            
            # Crear visualizador
            self.visualizador = VisualizadorGrafo(
                self.canvas_grafo, grafo, usuarios, 
                ancho if ancho > 100 else 600, 
                alto if alto > 100 else 400
            )
            
            # Mostrar vista inicial limitada
            self.visualizar_vecindario()
    
    def actualizar_visualizacion(self, *args):
        """Actualiza la visualización cuando cambia el slider de alcance"""
        if self.combo_user1.get():
            self.visualizar_vecindario()
    
    def buscar_camino(self):
        """Busca y visualiza el camino más corto entre dos usuarios"""
        u1 = self.combo_user1.get()
        u2 = self.combo_user2.get()
        
        if not u1 or not u2:
            messagebox.showwarning("Error", "Debes seleccionar dos usuarios.")
            return
        
        if u1 == u2:
            messagebox.showwarning("Error", "Selecciona dos usuarios diferentes.")
            return
        
        id1 = next((k for k,v in usuarios.items() if v == u1), None)
        id2 = next((k for k,v in usuarios.items() if v == u2), None)
        
        camino = camino_mas_corto(grafo, id1, id2)
        
        if camino:
            # Obtener subgrafo del camino y sus vecinos
            alcance = self.alcance_var.get()
            subgrafo, nodos = obtener_subgrafo(grafo, camino, saltos=alcance)
            
            # Visualizar
            if self.visualizador:
                self.visualizador.dibujar_grafo(subgrafo, camino=camino)
            
            # Actualizar información
            self.info_label.config(text=f"Camino: {len(camino)-1} saltos | Nodos mostrados: {len(nodos)}")
            
            # Mostrar ventana con detalles
            self.mostrar_detalle_camino(camino)
        else:
            messagebox.showerror("Sin conexión", 
                               f" No existe un camino entre {u1} y {u2}.")
    
    def mostrar_detalle_camino(self, camino):
        """Muestra una ventana con los detalles del camino"""
        ventana = tk.Toplevel(self.root)
        ventana.title("Camino Más Corto")
        ventana.geometry("350x300")
        ventana.configure(bg="white")
        
        tk.Label(ventana, text=" Camino Encontrado", 
                font=("Arial", 14, "bold"), bg="white").pack(pady=10)
        
        frame = tk.Frame(ventana, bg="white")
        frame.pack(fill="both", expand=True, padx=20)
        
        texto = tk.Text(frame, height=10, width=35, font=("Arial", 10))
        texto.pack(fill="both", expand=True)
        
        for i, nodo_id in enumerate(camino):
            nombre = usuarios.get(nodo_id, f"Usuario {nodo_id}")
            if i == 0:
                texto.insert(tk.END, f" {i+1}. {nombre} (Origen)\n")
            elif i == len(camino) - 1:
                texto.insert(tk.END, f" {i+1}. {nombre} (Destino)\n")
            else:
                texto.insert(tk.END, f" {i+1}. {nombre}\n")
        
        texto.insert(tk.END, f"\n Distancia: {len(camino)-1} saltos")
        texto.config(state=tk.DISABLED)
    
    def mostrar_recomendaciones(self):
        """Muestra recomendaciones de amigos y las visualiza"""
        u = self.combo_user1.get()
        if not u:
            messagebox.showwarning("Error", "Selecciona un usuario primero.")
            return
        
        idu = next((k for k,v in usuarios.items() if v == u), None)
        sugerencias = recomendar_amigos(grafo, idu)
        
        if sugerencias:
            # Visualizar el usuario, sus amigos y las sugerencias
            nodos_centrales = [idu] + list(grafo[idu]) + sugerencias[:10]
            subgrafo, nodos = obtener_subgrafo(grafo, nodos_centrales, saltos=1)
            
            if self.visualizador:
                self.visualizador.dibujar_grafo(subgrafo, nodos_destacados=set(sugerencias))
            
            self.info_label.config(text=f"Recomendaciones para {u}: {len(sugerencias)} sugerencias")
            
            # Mostrar lista de recomendaciones
            self.mostrar_lista_recomendaciones(u, sugerencias)
        else:
            messagebox.showinfo("Recomendaciones", 
                              f"No hay sugerencias de amigos para {u}.")
    
    def mostrar_lista_recomendaciones(self, usuario, sugerencias):
        """Muestra la lista de recomendaciones en una ventana"""
        ventana = tk.Toplevel(self.root)
        ventana.title(f"Recomendaciones para {usuario}")
        ventana.geometry("300x400")
        ventana.configure(bg="white")
        
        tk.Label(ventana, text=f" Amigos sugeridos", 
                font=("Arial", 14, "bold"), bg="white").pack(pady=10)
        
        frame = tk.Frame(ventana, bg="white")
        frame.pack(fill="both", expand=True, padx=20)
        
        listbox = tk.Listbox(frame, font=("Arial", 10))
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
        
        for i, s in enumerate(sugerencias, 1):
            listbox.insert(tk.END, f"{i}. {usuarios[s]}")
        
        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        
        listbox.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Label(ventana, text=f"Total: {len(sugerencias)} sugerencias", 
                bg="white", font=("Arial", 9)).pack(pady=10)
    
    def mostrar_feed(self):
        """Muestra el feed del usuario seleccionado"""
        u = self.combo_user1.get()
        if not u:
            messagebox.showwarning("Error", "Selecciona un usuario primero.")
            return
        
        idu = next((k for k,v in usuarios.items() if v == u), None)
        
        # Visualizar el usuario y sus conexiones directas
        nodos_centrales = [idu]
        subgrafo, nodos = obtener_subgrafo(grafo, nodos_centrales, saltos=1)
        
        if self.visualizador:
            self.visualizador.dibujar_grafo(subgrafo, nodos_destacados={idu})
        
        self.info_label.config(text=f"Feed de {u} - {len(grafo.get(idu, []))} amigos")
        
        # Mostrar ventana del feed
        ventana = tk.Toplevel(self.root)
        ventana.title(f"Feed de {u}")
        ventana.geometry("400x300")
        ventana.configure(bg="white")
        
        tk.Label(ventana, text=f" Publicaciones de {u}", 
                font=("Arial", 14, "bold"), bg="white").pack(pady=10)
        
        frame_post = tk.Frame(ventana, bg="#f5f5f5", relief=tk.RAISED, bd=1)
        frame_post.pack(padx=20, pady=10, fill="both", expand=True)
        
        post = posts.get(idu, "Este usuario aún no tiene publicaciones...")
        
        texto = tk.Text(frame_post, wrap=tk.WORD, font=("Arial", 10), 
                       bg="#f5f5f5", relief=tk.FLAT)
        texto.pack(padx=10, pady=10, fill="both", expand=True)
        texto.insert(tk.END, post)
        texto.config(state=tk.DISABLED)
    
    def visualizar_grafo_completo(self):
        """Visualiza el grafo completo (limitado a los nodos más conectados)"""
        # Para grafos grandes, mostrar solo los nodos más conectados
        grados = calcular_grados(grafo)
        nodos_importantes = sorted(grados.items(), key=lambda x: x[1], reverse=True)
        
        # Tomar los 30 nodos más conectados
        max_nodos = min(30, len(nodos_importantes))
        nodos_centrales = [nodo for nodo, _ in nodos_importantes[:max_nodos//3]]
        
        subgrafo, nodos = obtener_subgrafo(grafo, nodos_centrales, saltos=2)
        
        if self.visualizador:
            self.visualizador.dibujar_grafo(subgrafo)
        
        self.info_label.config(text=f"Vista general - {len(nodos)} nodos más relevantes")
    
    def visualizar_vecindario(self):
        """Visualiza el vecindario del usuario seleccionado"""
        u = self.combo_user1.get()
        if not u:
            # Si no hay usuario seleccionado, mostrar nodos aleatorios
            import random
            if usuarios:
                nodos_centrales = random.sample(list(usuarios.keys()), 
                                              min(5, len(usuarios)))
            else:
                return
        else:
            idu = next((k for k,v in usuarios.items() if v == u), None)
            nodos_centrales = [idu]
        
        alcance = self.alcance_var.get()
        subgrafo, nodos = obtener_subgrafo(grafo, nodos_centrales, saltos=alcance)
        
        if self.visualizador:
            self.visualizador.dibujar_grafo(subgrafo)
        
        nombre = u if u else "Vista inicial"
        self.info_label.config(text=f"Vecindario de {nombre} - {len(nodos)} nodos")
    
    def visualizar_comunidades(self):
        """Visualiza las comunidades en el grafo"""
        comunidades_data = sistema_comunidades.obtener_todas_comunidades(usuarios)
        
        if not comunidades_data:
            messagebox.showinfo("Info", "No hay comunidades creadas aún.")
            return
        
        # Obtener todos los nodos de las comunidades
        nodos_comunidades = set()
        for com in comunidades_data:
            nodos_comunidades.update(com['usuarios'])
        
        subgrafo, nodos = obtener_subgrafo(grafo, list(nodos_comunidades), saltos=1)
        
        # Crear un conjunto de nodos por comunidad para destacarlos con colores
        if self.visualizador:
            self.visualizador.dibujar_grafo(subgrafo)
        
        self.info_label.config(text=f"Vista de {len(comunidades_data)} comunidades - {len(nodos)} nodos")
    
    def crear_comunidad(self):
        """Interfaz para crear una nueva comunidad"""
        ventana = tk.Toplevel(self.root)
        ventana.title("Crear Nueva Comunidad")
        ventana.geometry("350x450")
        ventana.configure(bg="white")
        
        tk.Label(ventana, text=" Crear Nueva Comunidad", 
                font=("Arial", 14, "bold"), bg="white").pack(pady=10)
        
        tk.Label(ventana, text="Nombre de la comunidad:", 
                bg="white", font=("Arial", 10)).pack(pady=5)
        entry_nombre = tk.Entry(ventana, width=30, font=("Arial", 10))
        entry_nombre.pack(pady=5)
        
        tk.Label(ventana, text="Selecciona usuarios:", 
                bg="white", font=("Arial", 10)).pack(pady=10)
        
        frame_usuarios = tk.Frame(ventana, bg="white")
        frame_usuarios.pack(pady=10, fill="both", expand=True)
        
        listbox = tk.Listbox(frame_usuarios, selectmode=tk.MULTIPLE, height=10)
        scrollbar = tk.Scrollbar(frame_usuarios, orient=tk.VERTICAL)
        
        for nombre in usuarios.values():
            listbox.insert(tk.END, nombre)
        
        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        
        listbox.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def confirmar():
            nombre_com = entry_nombre.get().strip()
            selecciones = listbox.curselection()
            
            if not nombre_com:
                messagebox.showwarning("Error", "Ingresa un nombre para la comunidad.")
                return
            
            if not selecciones:
                messagebox.showwarning("Error", "Selecciona al menos un usuario.")
                return
            
            usuarios_sel = []
            for idx in selecciones:
                nombre_usuario = listbox.get(idx)
                id_usuario = next((k for k,v in usuarios.items() if v == nombre_usuario), None)
                if id_usuario:
                    usuarios_sel.append(id_usuario)
            
            exito, mensaje = sistema_comunidades.crear_comunidad(nombre_com, usuarios_sel)
            
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                ventana.destroy()
                self.visualizar_comunidades()
            else:
                messagebox.showerror("Error", mensaje)
        
        tk.Button(ventana, text=" Crear Comunidad", 
                 command=confirmar, bg="#4CAF50", fg="white",
                 font=("Arial", 11)).pack(pady=15)
    
    def ver_comunidades(self):
        """Muestra todas las comunidades creadas"""
        comunidades = sistema_comunidades.obtener_todas_comunidades(usuarios)
        
        ventana = tk.Toplevel(self.root)
        ventana.title("Comunidades Existentes")
        ventana.geometry("450x400")
        ventana.configure(bg="white")
        
        tk.Label(ventana, text=" Comunidades Existentes", 
                font=("Arial", 14, "bold"), bg="white").pack(pady=10)
        
        if not comunidades:
            tk.Label(ventana, text="No hay comunidades creadas aún.", 
                    bg="white", font=("Arial", 11)).pack(pady=20)
        else:
            frame_principal = tk.Frame(ventana, bg="white")
            frame_principal.pack(fill="both", expand=True, padx=20, pady=10)
            
            canvas = tk.Canvas(frame_principal, bg="white")
            scrollbar = tk.Scrollbar(frame_principal, orient=tk.VERTICAL, command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="white")
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            for i, com in enumerate(comunidades):
                frame_com = tk.Frame(scrollable_frame, bg="#f0f0f0", relief=tk.RAISED, bd=1)
                frame_com.pack(fill="x", pady=5, padx=10)
                
                tk.Label(frame_com, text=f" {com['nombre']}", 
                        font=("Arial", 11, "bold"), bg="#f0f0f0").pack(anchor="w", pady=(5,0), padx=10)
                
                usuarios_text = ", ".join(com['nombres_usuarios'][:5])
                if len(com['nombres_usuarios']) > 5:
                    usuarios_text += f"... (+{len(com['nombres_usuarios'])-5} más)"
                
                tk.Label(frame_com, text=f"Miembros: {usuarios_text}", 
                        font=("Arial", 9), bg="#f0f0f0", wraplength=380).pack(anchor="w", pady=(0,5), padx=10)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas del grafo"""
        stats = analizar_grafo(grafo, usuarios)
        
        ventana = tk.Toplevel(self.root)
        ventana.title("Estadísticas de la Red")
        ventana.geometry("400x450")
        ventana.configure(bg="white")
        
        tk.Label(ventana, text=" Estadísticas de la Red", 
                font=("Arial", 14, "bold"), bg="white").pack(pady=10)
        
        frame = tk.Frame(ventana, bg="#f5f5f5", relief=tk.RAISED, bd=1)
        frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        texto_stats = f"""
     ESTADÍSTICAS GENERALES
    
    • Número de usuarios: {stats['num_nodos']}
    • Número de conexiones: {stats['num_aristas']}
    • Grado promedio: {stats['grado_promedio']:.2f}
    • Grado máximo: {stats['grado_max']}
    • Grado mínimo: {stats['grado_min']}
    • Densidad del grafo: {stats['densidad']:.4f}
    
     TOP 5 USUARIOS MÁS CONECTADOS:
    """
        
        for i, (nodo_id, grado) in enumerate(stats['nodos_mas_conectados'][:5], 1):
            nombre = usuarios.get(nodo_id, f"Usuario {nodo_id}")
            texto_stats += f"\n    {i}. {nombre}: {grado} conexiones"
        
        texto = tk.Text(frame, wrap=tk.WORD, font=("Arial", 10), 
                       bg="#f5f5f5", relief=tk.FLAT)
        texto.pack(padx=10, pady=10, fill="both", expand=True)
        texto.insert(tk.END, texto_stats)
        texto.config(state=tk.DISABLED)
    
    # Funciones de navegación del canvas
    def on_mouse_press(self, event):
        """Guarda la posición inicial del mouse"""
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
    
    def on_mouse_drag(self, event):
        """Arrastra el canvas"""
        delta_x = event.x - self.drag_data["x"]
        delta_y = event.y - self.drag_data["y"]
        self.canvas_grafo.move("all", delta_x, delta_y)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
    
    def on_mouse_wheel(self, event):
        """Zoom con la rueda del mouse"""
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def zoom_in(self):
        """Aumenta el zoom"""
        self.canvas_grafo.scale("all", 
                                self.canvas_grafo.winfo_width()/2, 
                                self.canvas_grafo.winfo_height()/2, 
                                1.2, 1.2)
    
    def zoom_out(self):
        """Disminuye el zoom"""
        self.canvas_grafo.scale("all", 
                                self.canvas_grafo.winfo_width()/2, 
                                self.canvas_grafo.winfo_height()/2, 
                                0.8, 0.8)
    
    def reset_view(self):
        """Resetea la vista"""
        self.canvas_grafo.delete("all")
        self.visualizar_vecindario()


# Función principal
if __name__ == "__main__":
    root = tk.Tk()
    app = RedSocialApp(root)
    root.mainloop()
