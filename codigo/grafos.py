import os
from collections import defaultdict, deque
from openpyxl import load_workbook  # <- Excel
import matplotlib.pyplot as plt
import networkx as nx

# --------------------------
# Configuración de rutas
# --------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "../Dataset")

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
# Encabezados esperados: id | nombre | post
# --------------------------
def cargar_usuarios():
    usuarios = {}
    posts = {}

    ws = _abrir_hoja("usuarios.xlsx")

    # Detecta automáticamente la fila de encabezados y comienza en la 2
    for id_, nombre, post in ws.iter_rows(min_row=2, max_col=3, values_only=True):
        if id_ is None:
            continue
        sid = str(id_).strip()
        usuarios[sid] = (nombre or "").strip()
        posts[sid] = (post or "").strip()

    return usuarios, posts

# --------------------------
# Cargar amistades (grafo) desde amistades.xlsx
# Encabezados esperados: id1 | id2
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
# Visualización con Graphviz
# --------------------------
def dibujar_grafo(grafo, usuarios, camino=None, archivo="red_social"):
    g = Graph(format="png", engine="neato")  # layout
    g.attr(overlap="false", size="10")

    colores = ["lightblue", "lightgreen", "lightpink", "yellow", "orange", "violet"]

    # nodos con colores
    for i, nodo in enumerate(usuarios):
        color = colores[i % len(colores)]
        g.node(nodo, usuarios[nodo], shape="circle", style="filled", color=color, fontsize="12")

    # aristas normales
    for nodo, vecinos in grafo.items():
        for v in vecinos:
            if nodo < v:  # evita duplicados
                g.edge(nodo, v, color="gray")

    # resaltar camino
    if camino:
        for i in range(len(camino) - 1):
            g.edge(camino[i], camino[i + 1], color="red", penwidth="3")

    g.render(archivo, view=True)
    try:
        os.remove(archivo)  # limpia el .gv si existe
    except FileNotFoundError:
        pass
import os
from collections import defaultdict, deque
from graphviz import Graph
from openpyxl import load_workbook  # <- Excel

# --------------------------
# Configuración de rutas
# --------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "../Dataset")

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
# Encabezados esperados: id | nombre | post
# --------------------------
def cargar_usuarios():
    usuarios = {}
    posts = {}

    ws = _abrir_hoja("usuarios.xlsx")

    # Detecta automáticamente la fila de encabezados y comienza en la 2
    for id_, nombre, post in ws.iter_rows(min_row=2, max_col=3, values_only=True):
        if id_ is None:
            continue
        sid = str(id_).strip()
        usuarios[sid] = (nombre or "").strip()
        posts[sid] = (post or "").strip()

    return usuarios, posts

# --------------------------
# Cargar amistades (grafo) desde amistades.xlsx
# Encabezados esperados: id1 | id2
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
