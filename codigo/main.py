import tkinter as tk
from tkinter import ttk, messagebox
from grafos import cargar_grafo, cargar_usuarios, camino_mas_corto, recomendar_amigos, dibujar_grafo

# --------------------------
# Cargar datos
# --------------------------
usuarios, posts = cargar_usuarios()
grafo = cargar_grafo()

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


# --------------------------
# Interfaz estilo red social
# --------------------------
ventana = tk.Tk()
ventana.title("Mini Red Social")
ventana.geometry("500x450")
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

# Botones
tk.Button(ventana, text=" Buscar camino más corto", command=buscar_camino, bg="#4CAF50", fg="white").pack(pady=10)
tk.Button(ventana, text=" Recomendar amigos", command=mostrar_recomendaciones, bg="#2196F3", fg="white").pack(pady=10)
tk.Button(ventana, text=" Ver feed de Usuario 1", command=mostrar_feed, bg="#FF9800", fg="white").pack(pady=10)
tk.Button(ventana, text=" Salir", command=ventana.quit, bg="#f44336", fg="white").pack(pady=20)

ventana.mainloop()
