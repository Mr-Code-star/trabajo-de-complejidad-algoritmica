import os
from collections import defaultdict, deque
from graphviz import Graph
from openpyxl import load_workbook, Workbook
import matplotlib.pyplot as plt
import networkx as nx

# --------------------------
# Configuración de rutas
# --------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "../Dataset")

# --------------------------
# UFDS (Union-Find) para comunidades
# --------------------------
class UFDS:
    def __init__(self):
        self.parent = {}
        self.rank = {}
    
    def make_set(self, x):
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
    
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        rx = self.find(x)
        ry = self.find(y)
        
        if rx == ry:
            return
        
        if self.rank[rx] < self.rank[ry]:
            self.parent[rx] = ry
        elif self.rank[rx] > self.rank[ry]:
            self.parent[ry] = rx
        else:
            self.parent[ry] = rx
            self.rank[rx] += 1

# --------------------------
# Utilidades internas
# --------------------------
def _abrir_hoja(path_xlsx: str):
    """
    Abre un .xlsx y devuelve su hoja activa.
    Lanza un error claro si el archivo no existe.
    """
    archivo = os.path.join(DATASET_DIR, path_xlsx)
    if not os.path.exists(archivo):
        raise FileNotFoundError(
            f"No se encontró '{path_xlsx}' en la carpeta Dataset.\n"
            f"Ruta esperada: {archivo}"
        )
    wb = load_workbook(archivo, data_only=True)
    return wb.active

# --------------------------
# Cargar usuarios y posts (desde usuarios.xlsx)
# --------------------------
def cargar_usuarios():
    usuarios = {}
    posts = {}

    ws = _abrir_hoja("usuarios.xlsx")

    for id_, nombre, post in ws.iter_rows(min_row=2, max_col=3, values_only=True):
        if id_ is None:
            continue
        sid = str(id_).strip()
        usuarios[sid] = (nombre or "").strip()
        posts[sid] = (post or "").strip()

    return usuarios, posts

# --------------------------
# Cargar amistades (grafo) desde amistades.xlsx
# --------------------------
def cargar_grafo():
    grafo = defaultdict(list)

    ws = _abrir_hoja("amistades.xlsx")

    for id1, id2 in ws.iter_rows(min_row=2, max_col=2, values_only=True):
        if id1 is None or id2 is None:
            continue
        a, b = str(id1).strip(), str(id2).strip()
        if a == "" or b == "":
            continue
        grafo[a].append(b)
        grafo[b].append(a)  # no dirigido

    return grafo

# --------------------------
# Cargar comunidades desde comunidades.xlsx
# --------------------------
def cargar_comunidades():
    """
    Carga comunidades desde Excel.
    Estructura: id_comunidad | nombre_comunidad | id_usuario
    """
    comunidades = defaultdict(list)  # id_comunidad -> [usuarios]
    nombres_comunidades = {}  # id_comunidad -> nombre
    usuario_comunidad = {}  # id_usuario -> id_comunidad
    
    try:
        ws = _abrir_hoja("comunidades.xlsx")
        
        for id_com, nombre_com, id_user in ws.iter_rows(min_row=2, max_col=3, values_only=True):
            if id_com is None or id_user is None:
                continue
            
            id_com_str = str(id_com).strip()
            id_user_str = str(id_user).strip()
            
            if nombre_com:
                nombres_comunidades[id_com_str] = str(nombre_com).strip()
            
            comunidades[id_com_str].append(id_user_str)
            usuario_comunidad[id_user_str] = id_com_str
            
    except FileNotFoundError:
        # Si el archivo no existe, se creará cuando se agregue la primera comunidad
        pass
    
    return comunidades, nombres_comunidades, usuario_comunidad

# --------------------------
# Guardar comunidades en Excel
# --------------------------
def guardar_comunidades(comunidades, nombres_comunidades):
    """
    Guarda comunidades en Excel.
    """
    archivo = os.path.join(DATASET_DIR, "comunidades.xlsx")
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Comunidades"
    
    # Encabezados
    ws.append(["id_comunidad", "nombre_comunidad", "id_usuario"])
    
    # Datos
    for id_com, usuarios in comunidades.items():
        nombre_com = nombres_comunidades.get(id_com, f"Comunidad {id_com}")
        for usuario in usuarios:
            ws.append([id_com, nombre_com, usuario])
    
    wb.save(archivo)

# --------------------------
# Sistema de comunidades con UFDS
# --------------------------
class SistemaComunidades:
    def __init__(self):
        self.ufds = UFDS()
        self.comunidades, self.nombres_comunidades, self.usuario_comunidad = cargar_comunidades()
        self._inicializar_ufds()
    
    def _inicializar_ufds(self):
        """Inicializa UFDS con los usuarios de las comunidades"""
        for id_com, usuarios in self.comunidades.items():
            for usuario in usuarios:
                self.ufds.make_set(usuario)
                if len(usuarios) > 1:
                    # Unir todos los usuarios de la misma comunidad
                    primer_usuario = usuarios[0]
                    self.ufds.union(primer_usuario, usuario)
    
    def crear_comunidad(self, nombre_comunidad, usuarios):
        """Crea una nueva comunidad"""
        if not usuarios:
            return False, "Debe incluir al menos un usuario"
        
        # Generar nuevo ID de comunidad
        nuevo_id = str(max([int(k) for k in self.comunidades.keys()] + [0]) + 1)
        
        # Agregar usuarios a la comunidad
        self.comunidades[nuevo_id] = usuarios
        self.nombres_comunidades[nuevo_id] = nombre_comunidad
        
        # Actualizar UFDS y mapeo de usuario a comunidad
        for usuario in usuarios:
            self.ufds.make_set(usuario)
            self.usuario_comunidad[usuario] = nuevo_id
            
            # Unir usuarios de la misma comunidad
            if usuario != usuarios[0]:
                self.ufds.union(usuarios[0], usuario)
        
        # Guardar en Excel
        guardar_comunidades(self.comunidades, self.nombres_comunidades)
        
        return True, f"Comunidad '{nombre_comunidad}' creada exitosamente"
    
    def obtener_comunidad_usuario(self, usuario_id):
        """Obtiene la comunidad de un usuario"""
        return self.usuario_comunidad.get(usuario_id)
    
    def obtener_usuarios_comunidad(self, comunidad_id):
        """Obtiene todos los usuarios de una comunidad"""
        return self.comunidades.get(comunidad_id, [])
    
    def obtener_todas_comunidades(self, usuarios_dict):
        """Obtiene todas las comunidades con sus nombres y usuarios"""
        resultado = []
        for id_com, usuarios_lista in self.comunidades.items():
            nombre = self.nombres_comunidades.get(id_com, f"Comunidad {id_com}")
            nombres_usuarios = [usuarios_dict.get(user_id, f"Usuario {user_id}") for user_id in usuarios_lista]
            resultado.append({
                'id': id_com,
                'nombre': nombre,
                'usuarios': usuarios_lista,
                'nombres_usuarios': nombres_usuarios
        })
        return resultado
    
    def son_misma_comunidad(self, usuario1, usuario2):
        """Verifica si dos usuarios están en la misma comunidad"""
        if usuario1 not in self.ufds.parent or usuario2 not in self.ufds.parent:
            return False
        return self.ufds.find(usuario1) == self.ufds.find(usuario2)

# --------------------------
# BFS → camino más corto
# --------------------------
def camino_mas_corto(grafo, inicio, destino):
    cola = deque([(inicio, [inicio])])
    visitados = set([inicio])

    while cola:
        nodo, camino = cola.popleft()
        if nodo == destino:
            return camino
        for vecino in grafo[nodo]:
            if vecino not in visitados:
                visitados.add(vecino)
                cola.append((vecino, camino + [vecino]))
    return None

# --------------------------
# Recomendación de amigos
# --------------------------
def recomendar_amigos(grafo, usuario):
    """Devuelve amigos de amigos que no sean ya amigos directos"""
    directos = set(grafo[usuario])
    sugerencias = set()
    for amigo in directos:
        for amigo_de_amigo in grafo[amigo]:
            if amigo_de_amigo != usuario and amigo_de_amigo not in directos:
                sugerencias.add(amigo_de_amigo)
    return list(sugerencias)

# --------------------------
# Visualización con matplotlib
# --------------------------
def dibujar_grafo(grafo, usuarios, camino=None, archivo="red_social",
                  top_labels=25, seed=42):
    """
    Visualización estética y foco en el camino corto si se provee.
    """
    import numpy as np
    import matplotlib.pyplot as plt
    import networkx as nx

    # --- Construcción del grafo NX -----------------------------------------
    G = nx.Graph()
    for nodo, nombre in usuarios.items():
        G.add_node(nodo, label=nombre)

    # Asegurar que todas las aristas estén en el grafo (ambas direcciones)
    for u, vecinos in grafo.items():
        for v in vecinos:
            G.add_edge(u, v)  # Añadir todas las aristas sin condiciones

    # Layout mejorado
    n = max(len(G), 1)
    k = 3.0 / np.sqrt(n)
    pos = nx.spring_layout(G, seed=seed, k=k, iterations=100)

    # Tamaño de nodo ~ grado (acotado)
    degrees = dict(G.degree())
    node_order = list(G.nodes())
    base_sizes = [max(300, min(300 + 100 * degrees.get(v, 0), 2000)) for v in node_order]

    # --- Dibujo -------------------------------------------------------------
    plt.figure(figsize=(14, 10), dpi=140)
    plt.title("Red Social", fontsize=18, pad=12)

    if not camino:
        # Grafo general
        nx.draw_networkx_edges(G, pos, width=0.8, alpha=0.3, edge_color="gray")

        nx.draw_networkx_nodes(
            G, pos,
            node_size=base_sizes,
            node_color="#b7def1",
            linewidths=1.0,
            edgecolors="#3b7aa0",
        )

        # Etiquetas: solo top por grado
        top_by_degree = sorted(degrees, key=degrees.get, reverse=True)[:top_labels]
        etiquetas = {n: usuarios.get(n, n) for n in top_by_degree if n in G}
        nx.draw_networkx_labels(
            G, pos, labels=etiquetas,
            font_size=9, font_weight="bold",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.9),
        )

    else:
        # ------------------- Modo foco en camino corto ----------------------
        camino = list(camino)
        camino_set = set(camino)
        
        # 1) Primero dibujar aristas fuera del camino - más tenues
        otras_aristas = [(u, v) for (u, v) in G.edges() 
                        if (u not in camino_set or v not in camino_set)]
        nx.draw_networkx_edges(G, pos, edgelist=otras_aristas,
                              width=0.8, alpha=0.15, edge_color="gray", style="dashed")

        # 2) RESALTAR CAMINO - LÍNEAS ROJAS MÁS GRUESAS Y VISIBLES
        # Crear lista de aristas del camino
        edges_camino = []
        for i in range(len(camino)-1):
           
            # Normalizamos ids: str + strip para tolerar espacios/enteros
            u = str(camino[i]).strip()
            v = str(camino[i + 1]).strip()

             # Aseguramos existencia de nodos en G
            if not G.has_node(u) or not G.has_node(v):
                print(f"[AVISO] Nodo faltante en el grafo: {u} o {v}")
                continue

             # Si el grafo quedó con arista en una sola dirección, la añadimos para dibujar
            if not (G.has_edge(u, v) or G.has_edge(v, u)):
                G.add_edge(u, v)

            edges_camino.append((u, v))

        if edges_camino:
            nx.draw_networkx_edges(
                G, pos, 
                edgelist=edges_camino,
                edge_color="#b71c1c",           # Rojo puro
                width=8.0,                  # Más grueso
                alpha=1.0,                  # Completamente opaco
                style="solid"
            )

        # 3) Nodos fuera del camino - tenues
        otros_nodos = [n for n in G.nodes() if n not in camino_set]
        otros_sizes = [base_sizes[node_order.index(n)] for n in otros_nodos]
        nx.draw_networkx_nodes(
            G, pos, nodelist=otros_nodos,
            node_size=otros_sizes,
            node_color="#e0e0e0", 
            edgecolors="#9e9e9e", 
            linewidths=0.8, 
            alpha=0.4
        )

        # 4) Nodos del camino - amarillo brillante
        camino_sizes = [base_sizes[node_order.index(n)] for n in camino]
        nx.draw_networkx_nodes(
            G, pos, nodelist=camino,
            node_size=camino_sizes,
            node_color="#ffeb3b",     # Amarillo más brillante
            edgecolors="#ff9800",     # Borde naranja
            linewidths=2.0,           # Borde más grueso
            alpha=0.9
        )

        # 5) Etiquetas del camino
        etiquetas_camino = {}
        for i, n in enumerate(camino, start=1):
            nombre = usuarios.get(n, n)
            etiquetas_camino[n] = f"{i}. {nombre}"
        
        nx.draw_networkx_labels(
            G, pos, 
            labels=etiquetas_camino, 
            font_size=11, 
            font_weight="bold",
            font_color="#000000",
            bbox=dict(
                boxstyle="round,pad=0.4", 
                fc="yellow",           # Fondo amarillo para mejor contraste
                ec="orange", 
                alpha=0.95,
                lw=2
            )
        )

        # 6) Origen y Destino con colores distintos y muy visibles
        origen, destino = camino[0], camino[-1]
        
        # Origen - Verde brillante
        nx.draw_networkx_nodes(
            G, pos, nodelist=[origen],
            node_color="#4caf50",      # Verde más brillante
            node_size=[base_sizes[node_order.index(origen)] * 1.5],  # Más grande
            edgecolors="#1b5e20",      # Borde verde oscuro
            linewidths=3.0
        )
        
        # Destino - Rojo brillante  
        nx.draw_networkx_nodes(
            G, pos, nodelist=[destino],
            node_color="#f44336",      # Rojo más brillante
            node_size=[base_sizes[node_order.index(destino)] * 1.5],  # Más grande
            edgecolors="#b71c1c",      # Borde rojo oscuro
            linewidths=3.0
        )

    # Leyenda
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color="gray", lw=2, alpha=0.3, label="Amistad"),
        Line2D([0], [0], marker="o", color="w", label="Nodo (tamaño ~ grado)",
               markerfacecolor="#b7def1", markeredgecolor="#3b7aa0", markersize=12),
    ]
    
    if camino:
        legend_elements += [
            Line2D([0], [0], color="red", lw=6, label="Camino más corto"),
            Line2D([0], [0], marker="o", color="w", label="Nodos del camino",
                   markerfacecolor="#ffeb3b", markeredgecolor="#ff9800", markersize=12),
            Line2D([0], [0], marker="o", color="w", label="Origen",
                   markerfacecolor="#4caf50", markeredgecolor="#1b5e20", markersize=12),
            Line2D([0], [0], marker="o", color="w", label="Destino",
                   markerfacecolor="#f44336", markeredgecolor="#b71c1c", markersize=12),
        ]

    plt.legend(handles=legend_elements, loc="upper left", frameon=True, 
               framealpha=0.9, facecolor="white")

    plt.axis("off")
    plt.tight_layout()
    plt.show()
