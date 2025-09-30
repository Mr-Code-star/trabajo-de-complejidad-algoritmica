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
def dibujar_grafo(grafo, usuarios, camino=None, archivo="red_social"):
    G = nx.Graph()

    # Agregar nodos con etiquetas (nombre del usuario)
    for nodo, nombre in usuarios.items():
        G.add_node(nodo, label=nombre)

    # Agregar aristas (amistades)
    for nodo, vecinos in grafo.items():
        for v in vecinos:
            if not G.has_edge(nodo, v):
                G.add_edge(nodo, v)

    # Posiciones de los nodos
    pos = nx.spring_layout(G, seed=42)

    # Dibujar nodos
    nx.draw_networkx_nodes(G, pos, node_size=1000, node_color="lightblue")

    # Dibujar aristas
    nx.draw_networkx_edges(G, pos, edge_color="gray")

    # Resaltar camino más corto en rojo
    if camino:
        edges_camino = list(zip(camino, camino[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=edges_camino, edge_color="red", width=3)

    # Dibujar etiquetas con los nombres
    etiquetas = {nodo: usuarios[nodo] for nodo in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=etiquetas, font_size=10, font_weight="bold")

    plt.title("Red Social")
    plt.axis("off")
    plt.show()
