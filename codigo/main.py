import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from grafos import (cargar_grafo, cargar_usuarios, camino_mas_corto, 
                   recomendar_amigos, dibujar_grafo, SistemaComunidades)

# --------------------------
# Cargar datos
# --------------------------
usuarios, posts = cargar_usuarios()
grafo = cargar_grafo()
sistema_comunidades = SistemaComunidades()

# --------------------------
# Funciones
# --------------------------
def buscar_camino():
    u1 = combo_user1.get()
    u2 = combo_user2.get()

    if not u1 or not u2:
        messagebox.showwarning("Error", "Debes seleccionar dos usuarios.")
        return

    id1 = next((k for k,v in usuarios.items() if v == u1), None)
    id2 = next((k for k,v in usuarios.items() if v == u2), None)

    camino = camino_mas_corto(grafo, id1, id2)

    if camino:
        nombres = [usuarios[i] for i in camino]
        messagebox.showinfo("Camino encontrado", " → ".join(nombres))
        dibujar_grafo(grafo, usuarios, camino)
    else:
        messagebox.showerror("Sin conexión", "No existe un camino entre esos usuarios.")

def mostrar_recomendaciones():
    u = combo_user1.get()
    if not u:
        messagebox.showwarning("Error", "Selecciona un usuario primero.")
        return

    idu = next((k for k,v in usuarios.items() if v == u), None)
    sugerencias = recomendar_amigos(grafo, idu)

    if sugerencias:
        nombres = [usuarios[s] for s in sugerencias]
        messagebox.showinfo("Recomendaciones", f"Amigos sugeridos para {u}:\n" + "\n".join(nombres))
    else:
        messagebox.showinfo("Recomendaciones", f"No hay sugerencias para {u}.")

def mostrar_feed():
    u = combo_user1.get()
    if not u:
        messagebox.showwarning("Error", "Selecciona un usuario primero.")
        return

    idu = next((k for k,v in usuarios.items() if v == u), None)
    ventana_feed = tk.Toplevel(ventana)
    ventana_feed.title(f"Feed de {u}")
    ventana_feed.geometry("400x300")

    tk.Label(ventana_feed, text=f"📸 Publicaciones de {u}", font=("Arial", 14, "bold")).pack(pady=10)

    # mostrar el post desde usuarios.csv
    post = posts.get(idu, "Este usuario aún no tiene publicaciones...")
    tk.Message(ventana_feed, text=post, width=350, font=("Arial", 12)).pack(pady=10)

def crear_comunidad():
    """Interfaz para crear una nueva comunidad"""
    ventana_comunidad = tk.Toplevel(ventana)
    ventana_comunidad.title("Crear Nueva Comunidad")
    ventana_comunidad.geometry("400x500")
    ventana_comunidad.configure(bg="white")
    
    tk.Label(ventana_comunidad, text="Crear Nueva Comunidad", 
             font=("Arial", 16, "bold"), bg="white").pack(pady=10)
    
    # Nombre de la comunidad
    tk.Label(ventana_comunidad, text="Nombre de la comunidad:", 
             bg="white", font=("Arial", 10)).pack(pady=5)
    entry_nombre = tk.Entry(ventana_comunidad, width=30, font=("Arial", 10))
    entry_nombre.pack(pady=5)
    
    # Lista de usuarios seleccionables
    tk.Label(ventana_comunidad, text="Selecciona usuarios:", 
             bg="white", font=("Arial", 10)).pack(pady=10)
    
    frame_usuarios = tk.Frame(ventana_comunidad, bg="white")
    frame_usuarios.pack(pady=10, fill="both", expand=True)
    
    # Listbox con scrollbar
    listbox = tk.Listbox(frame_usuarios, selectmode=tk.MULTIPLE, height=10)
    scrollbar = tk.Scrollbar(frame_usuarios, orient=tk.VERTICAL)
    
    for nombre in usuarios.values():
        listbox.insert(tk.END, nombre)
    
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    
    listbox.pack(side=tk.LEFT, fill="both", expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def confirmar_creacion():
        nombre_comunidad = entry_nombre.get().strip()
        selecciones = listbox.curselection()
        
        if not nombre_comunidad:
            messagebox.showwarning("Error", "Debes ingresar un nombre para la comunidad.")
            return
        
        if not selecciones:
            messagebox.showwarning("Error", "Debes seleccionar al menos un usuario.")
            return
        
        # Obtener IDs de usuarios seleccionados
        usuarios_seleccionados = []
        for idx in selecciones:
            nombre_usuario = listbox.get(idx)
            id_usuario = next((k for k,v in usuarios.items() if v == nombre_usuario), None)
            if id_usuario:
                usuarios_seleccionados.append(id_usuario)
        
        # Crear comunidad
        exito, mensaje = sistema_comunidades.crear_comunidad(nombre_comunidad, usuarios_seleccionados)
        
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            ventana_comunidad.destroy()
        else:
            messagebox.showerror("Error", mensaje)
    
    tk.Button(ventana_comunidad, text="Crear Comunidad", 
              command=confirmar_creacion, bg="#4CAF50", fg="white",
              font=("Arial", 12)).pack(pady=20)

def ver_comunidades():
    """Muestra todas las comunidades creadas"""
    comunidades = sistema_comunidades.obtener_todas_comunidades(usuarios)
    
    ventana_comunidades = tk.Toplevel(ventana)
    ventana_comunidades.title("Comunidades Existentes")
    ventana_comunidades.geometry("500x400")
    ventana_comunidades.configure(bg="white")
    
    tk.Label(ventana_comunidades, text="Comunidades Existentes", 
             font=("Arial", 16, "bold"), bg="white").pack(pady=10)
    
    if not comunidades:
        tk.Label(ventana_comunidades, text="No hay comunidades creadas aún.", 
                 bg="white", font=("Arial", 12)).pack(pady=20)
        return
    
    # Frame con scrollbar para las comunidades
    frame_principal = tk.Frame(ventana_comunidades, bg="white")
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
    
    # Mostrar cada comunidad
    for i, com in enumerate(comunidades):
        frame_com = tk.Frame(scrollable_frame, bg="#f0f0f0", relief=tk.RAISED, bd=1)
        frame_com.pack(fill="x", pady=5, padx=10)
        
        tk.Label(frame_com, text=f"🏠 {com['nombre']}", 
                 font=("Arial", 12, "bold"), bg="#f0f0f0").pack(anchor="w", pady=(5,0), padx=10)
        
        usuarios_text = ", ".join([usuarios.get(user_id, f"Usuario {user_id}") for user_id in com['usuarios']])
        tk.Label(frame_com, text=f"Miembros: {usuarios_text}", 
                 font=("Arial", 10), bg="#f0f0f0", wraplength=400).pack(anchor="w", pady=(0,5), padx=10)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

# --------------------------
# Interfaz principal
# --------------------------
ventana = tk.Tk()
ventana.title("Mini Red Social")
ventana.geometry("500x500")
ventana.configure(bg="white")

# Título
tk.Label(ventana, text=" Mini Red Social", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

# Selección de usuarios
frame = tk.Frame(ventana, bg="white")
frame.pack(pady=10)

tk.Label(frame, text="Usuario 1:", bg="white").grid(row=0, column=0, padx=5, pady=5)
combo_user1 = ttk.Combobox(frame, values=list(usuarios.values()), width=20)
combo_user1.grid(row=0, column=1)

tk.Label(frame, text="Usuario 2:", bg="white").grid(row=1, column=0, padx=5, pady=5)
combo_user2 = ttk.Combobox(frame, values=list(usuarios.values()), width=20)
combo_user2.grid(row=1, column=1)

# Botones principales
tk.Button(ventana, text=" Buscar camino más corto", command=buscar_camino, bg="#4CAF50", fg="white").pack(pady=5)
tk.Button(ventana, text=" Recomendar amigos", command=mostrar_recomendaciones, bg="#2196F3", fg="white").pack(pady=5)
tk.Button(ventana, text=" Ver feed de Usuario 1", command=mostrar_feed, bg="#FF9800", fg="white").pack(pady=5)

# Separador para funcionalidades de comunidades
tk.Label(ventana, text="Gestión de Comunidades", font=("Arial", 12, "bold"), bg="white").pack(pady=(20,10))

tk.Button(ventana, text=" Crear Nueva Comunidad", command=crear_comunidad, bg="#9C27B0", fg="white").pack(pady=5)
tk.Button(ventana, text=" Ver Todas las Comunidades", command=ver_comunidades, bg="#673AB7", fg="white").pack(pady=5)

# Botón salir
tk.Button(ventana, text=" Salir", command=ventana.quit, bg="#f44336", fg="white").pack(pady=20)

ventana.mainloop()