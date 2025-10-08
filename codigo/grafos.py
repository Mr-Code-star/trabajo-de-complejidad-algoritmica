import os
import matplotlib.pyplot as plt
from collections import defaultdict, deque
from openpyxl import load_workbook, Workbook
import math
import tkinter as tk
from tkinter import Canvas
import random


# Configuracion de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "../Dataset")

# UFDS para comunidades
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


# Utilidades internas
def _abrir_hoja(path_xlsx: str):
    """ABRE ARCHIVO EXCEL"""
    archivo = os.path.join(DATASET_DIR, path_xlsx)
    if not os.path.exists(archivo):
        raise FileNotFoundError(
            f"No se encontro '{path_xlsx}' en la carpeta Dataset.\n"
            f"Ruta esperada: {archivo}"
        )
    wb = load_workbook(archivo, data_only=True)
    return wb.active


# Cargar usuarios y posts desde usuarios.xlsx
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


# Cargar amistades desde amistades.xlsx
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


# Cargar comunidades desde comunidades.xlsx
def cargar_comunidades():
    """Cargar comunidades desde Excel."""
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
        # Si el archivo no existe se crea cuando se agregue una comunidad
        pass
    
    return comunidades, nombres_comunidades, usuario_comunidad


# Guardar comunidades en Excel
def guardar_comunidades(comunidades, nombres_comunidades):
    """Guarda comunidades en Excel."""
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


# Sistema de comunidades con UFDS
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
            nombres_usuarios = [usuarios_dict.get(user_id, f"Usuario {user_id}") 
                              for user_id in usuarios_lista]
            resultado.append({
                'id': id_com,
                'nombre': nombre,
                'usuarios': usuarios_lista,
                'nombres_usuarios': nombres_usuarios
            })
        return resultado
    
    def son_misma_comunidad(self, usuario1, usuario2):
        """Verifica si dos usuarios estan en la misma comunidad"""
        if usuario1 not in self.ufds.parent or usuario2 not in self.ufds.parent:
            return False
        return self.ufds.find(usuario1) == self.ufds.find(usuario2)


# BFS para el camino mas corto
def camino_mas_corto(grafo, inicio, destino):
    """Encuentra el camino más corto usando BFS"""
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


# Recomendacion de amigos
def recomendar_amigos(grafo, usuario):
    """Devuelve amigos de amigos que no sean ya amigos directos"""
    directos = set(grafo[usuario])
    sugerencias = set()
    for amigo in directos:
        for amigo_de_amigo in grafo[amigo]:
            if amigo_de_amigo != usuario and amigo_de_amigo not in directos:
                sugerencias.add(amigo_de_amigo)
    return list(sugerencias)


# Calcular grado de cada nodo
def calcular_grados(grafo):
    """Calcula el grado de cada nodo en el grafo"""
    grados = {}
    for nodo, vecinos in grafo.items():
        grados[nodo] = len(vecinos)
    # Asegurar que todos los nodos aislados tengan grado 0
    for nodo in grafo:
        if nodo not in grados:
            grados[nodo] = 0
    return grados


# Obtener subgrafo relevante (vecindario de N saltos)
def obtener_subgrafo(grafo, nodos_centrales, saltos=2):
    """
    Obtiene un subgrafo que incluye los nodos centrales y sus vecinos hasta N saltos.
    
    Args:
        grafo: grafo completo
        nodos_centrales: lista de nodos centrales para el subgrafo
        saltos: número de saltos desde los nodos centrales
    
    Returns:
        subgrafo: diccionario con solo los nodos relevantes
        nodos_incluidos: conjunto de nodos en el subgrafo
    """
    nodos_incluidos = set(nodos_centrales)
    nodos_por_explorar = set(nodos_centrales)
    
    for _ in range(saltos):
        nuevos_nodos = set()
        for nodo in nodos_por_explorar:
            if nodo in grafo:
                vecinos = grafo[nodo]
                nuevos_nodos.update(vecinos)
        nodos_incluidos.update(nuevos_nodos)
        nodos_por_explorar = nuevos_nodos - nodos_incluidos
    
    # Crear subgrafo
    subgrafo = defaultdict(list)
    for nodo in nodos_incluidos:
        if nodo in grafo:
            for vecino in grafo[nodo]:
                if vecino in nodos_incluidos:
                    subgrafo[nodo].append(vecino)
    
    return subgrafo, nodos_incluidos


# Clase para visualización interactiva en Canvas
class VisualizadorGrafo:
    def __init__(self, canvas, grafo, usuarios, ancho=800, alto=600):
        self.canvas = canvas
        self.grafo = grafo
        self.usuarios = usuarios
        self.ancho = ancho
        self.alto = alto
        self.posiciones = {}
        self.nodos_dibujados = {}
        self.aristas_dibujadas = []
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        
    def limpiar(self):
        """Limpia el canvas"""
        self.canvas.delete("all")
        self.nodos_dibujados = {}
        self.aristas_dibujadas = []
        
    def calcular_layout_fuerza(self, nodos, iteraciones=50):
        """
        Calcula las posiciones usando un algoritmo de fuerza simplificado.
        """
        # Inicializar posiciones aleatoriamente
        posiciones = {}
        for nodo in nodos:
            posiciones[nodo] = [
                random.uniform(100, self.ancho - 100),
                random.uniform(100, self.alto - 100)
            ]
        
        # Parámetros del algoritmo
        k = math.sqrt((self.ancho * self.alto) / len(nodos)) if len(nodos) > 0 else 100
        c_rep = k * k  # Constante de repulsión
        c_spring = 1.0  # Constante del resorte
        damping = 0.9  # Factor de amortiguación
        
        for _ in range(iteraciones):
            fuerzas = {nodo: [0, 0] for nodo in nodos}
            
            # Fuerzas de repulsión entre todos los nodos
            nodos_lista = list(nodos)
            for i, nodo1 in enumerate(nodos_lista):
                for nodo2 in nodos_lista[i+1:]:
                    dx = posiciones[nodo2][0] - posiciones[nodo1][0]
                    dy = posiciones[nodo2][1] - posiciones[nodo1][1]
                    dist = math.sqrt(dx*dx + dy*dy)
                    
                    if dist > 0:
                        # Fuerza de repulsión
                        f_rep = c_rep / (dist * dist)
                        fx = (dx / dist) * f_rep
                        fy = (dy / dist) * f_rep
                        
                        fuerzas[nodo1][0] -= fx
                        fuerzas[nodo1][1] -= fy
                        fuerzas[nodo2][0] += fx
                        fuerzas[nodo2][1] += fy
            
            # Fuerzas de atracción para nodos conectados
            for nodo in nodos:
                if nodo in self.grafo:
                    for vecino in self.grafo[nodo]:
                        if vecino in nodos:
                            dx = posiciones[vecino][0] - posiciones[nodo][0]
                            dy = posiciones[vecino][1] - posiciones[nodo][1]
                            dist = math.sqrt(dx*dx + dy*dy)
                            
                            if dist > 0:
                                # Fuerza del resorte
                                f_spring = c_spring * math.log(dist / k)
                                fx = (dx / dist) * f_spring
                                fy = (dy / dist) * f_spring
                                
                                fuerzas[nodo][0] += fx * 0.5
                                fuerzas[nodo][1] += fy * 0.5
            
            # Actualizar posiciones
            for nodo in nodos:
                posiciones[nodo][0] += fuerzas[nodo][0] * damping
                posiciones[nodo][1] += fuerzas[nodo][1] * damping
                
                # Mantener dentro de los límites
                posiciones[nodo][0] = max(50, min(self.ancho - 50, posiciones[nodo][0]))
                posiciones[nodo][1] = max(50, min(self.alto - 50, posiciones[nodo][1]))
        
        return posiciones
    
    def dibujar_grafo(self, subgrafo=None, camino=None, nodos_destacados=None):
        """
        Dibuja el grafo en el canvas.
        
        Args:
            subgrafo: si se proporciona, solo dibuja este subgrafo
            camino: lista de nodos que forman un camino para destacar
            nodos_destacados: conjunto de nodos para destacar
        """
        self.limpiar()
        
        grafo_a_dibujar = subgrafo if subgrafo else self.grafo
        
        # Obtener todos los nodos del grafo
        nodos = set()
        for nodo in grafo_a_dibujar:
            nodos.add(nodo)
            nodos.update(grafo_a_dibujar[nodo])
        
        if not nodos:
            return
        
        # Calcular posiciones
        self.posiciones = self.calcular_layout_fuerza(nodos)
        
        # Dibujar aristas primero (para que queden detrás de los nodos)
        aristas_dibujadas = set()
        for nodo in grafo_a_dibujar:
            for vecino in grafo_a_dibujar[nodo]:
                arista = tuple(sorted([nodo, vecino]))
                if arista not in aristas_dibujadas and vecino in self.posiciones:
                    aristas_dibujadas.add(arista)
                    
                    x1, y1 = self.posiciones[nodo]
                    x2, y2 = self.posiciones[vecino]
                    
                    # Determinar color de la arista
                    color = "#cccccc"
                    ancho = 1
                    
                    if camino:
                        # Verificar si la arista está en el camino
                        for i in range(len(camino) - 1):
                            if (camino[i] == nodo and camino[i+1] == vecino) or \
                               (camino[i] == vecino and camino[i+1] == nodo):
                                color = "#ff4444"
                                ancho = 3
                                break
                    
                    linea = self.canvas.create_line(
                        x1, y1, x2, y2,
                        fill=color, width=ancho, tags="arista"
                    )
                    self.aristas_dibujadas.append(linea)
        
        # Dibujar nodos
        for nodo in nodos:
            if nodo in self.posiciones:
                x, y = self.posiciones[nodo]
                
                # Determinar color y tamaño del nodo
                color = "#64b5f6"
                radio = 20
                color_texto = "black"
                
                if camino:
                    if nodo == camino[0]:  # Origen
                        color = "#4caf50"
                        radio = 25
                        color_texto = "white"
                    elif nodo == camino[-1]:  # Destino
                        color = "#f44336"
                        radio = 25
                        color_texto = "white"
                    elif nodo in camino:  # En el camino
                        color = "#ffd54f"
                        radio = 22
                
                if nodos_destacados and nodo in nodos_destacados:
                    radio = 25
                    if not camino or nodo not in camino:
                        color = "#9c27b0"
                        color_texto = "white"
                
                # Dibujar círculo del nodo
                circulo = self.canvas.create_oval(
                    x - radio, y - radio,
                    x + radio, y + radio,
                    fill=color, outline="white", width=2,
                    tags=("nodo", f"nodo_{nodo}")
                )
                
                # Dibujar nombre del nodo
                nombre = self.usuarios.get(nodo, f"ID: {nodo}")
                # Truncar nombre si es muy largo
                if len(nombre) > 12:
                    nombre = nombre[:10] + "..."
                
                texto = self.canvas.create_text(
                    x, y,
                    text=nombre,
                    font=("Arial", 9, "bold"),
                    fill=color_texto,
                    tags=("texto", f"texto_{nodo}")
                )
                
                self.nodos_dibujados[nodo] = (circulo, texto)
                
                # Agregar tooltip con nombre completo
                self.agregar_tooltip(nodo, circulo)
    
    def agregar_tooltip(self, nodo_id, elemento):
        """Agrega un tooltip al pasar el mouse sobre un nodo"""
        nombre_completo = self.usuarios.get(nodo_id, f"Usuario {nodo_id}")
        grado = len(self.grafo.get(nodo_id, []))
        
        def mostrar_tooltip(event):
            x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx() + 10
            y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty() - 30
            
            self.canvas.delete("tooltip")
            
            # Crear tooltip
            rect = self.canvas.create_rectangle(
                x, y, x + 150, y + 40,
                fill="#333333", outline="#555555",
                tags="tooltip"
            )
            
            texto = f"{nombre_completo}\nConexiones: {grado}"
            self.canvas.create_text(
                x + 75, y + 20,
                text=texto,
                fill="white",
                font=("Arial", 9),
                tags="tooltip"
            )
        
        def ocultar_tooltip(event):
            self.canvas.delete("tooltip")
        
        self.canvas.tag_bind(elemento, "<Enter>", mostrar_tooltip)
        self.canvas.tag_bind(elemento, "<Leave>", ocultar_tooltip)


# Análisis del grafo
def analizar_grafo(grafo, usuarios):
    """
    Analiza las propiedades del grafo sin usar NetworkX
    """
    # Calcular grados
    grados = calcular_grados(grafo)
    
    # Estadísticas básicas
    num_nodos = len(usuarios)
    num_aristas = sum(len(vecinos) for vecinos in grafo.values()) // 2
    
    if grados:
        grado_promedio = sum(grados.values()) / len(grados)
        grado_max = max(grados.values())
        grado_min = min(grados.values())
        
        # Encontrar nodos más conectados
        nodos_mas_conectados = sorted(grados.items(), 
                                     key=lambda x: x[1], 
                                     reverse=True)[:5]
    else:
        grado_promedio = 0
        grado_max = 0
        grado_min = 0
        nodos_mas_conectados = []
    
    # Calcular densidad
    densidad = (2 * num_aristas) / (num_nodos * (num_nodos - 1)) if num_nodos > 1 else 0
    
    return {
        'num_nodos': num_nodos,
        'num_aristas': num_aristas,
        'grado_promedio': grado_promedio,
        'grado_max': grado_max,
        'grado_min': grado_min,
        'densidad': densidad,
        'nodos_mas_conectados': nodos_mas_conectados
    }


# Funciones auxiliares para visualización simplificada (mantener compatibilidad)
def dibujar_grafo_graphviz(*args, **kwargs):
    """Función mantenida por compatibilidad pero ya no usada"""
    return "Visualización integrada en la interfaz"

def dibujar_grafo_comunidades(*args, **kwargs):
    """Función mantenida por compatibilidad pero ya no usada"""
    return "Visualización integrada en la interfaz"
