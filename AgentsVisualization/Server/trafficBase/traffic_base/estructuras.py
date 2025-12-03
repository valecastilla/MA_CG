from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
from .agent import *
import json
from collections import deque
import random

class GlobalGraph:
    grafo = {}
    nodos = []  # Lista global de todos los nodos
    nodosDestino =[]
    
    @staticmethod
    def agregar_nodo(nodo):
        GlobalGraph.nodos.append(nodo)
    
    @staticmethod
    def limpiar():
        GlobalGraph.grafo = {}
        GlobalGraph.nodos = []
    @staticmethod
    def obtenerRutaAleatoria(cell):
        
         puntoPartida = next((a for a in cell.agents if isinstance(a, Intersection)), None)
         idPartida = puntoPartida.idNodoInter
         nodoDestino=random.choice(GlobalGraph.nodosDestino)
         
         idNodoDestino = nodoDestino.id
         print("=========Id inicio")
         return GlobalGraph.imprimir_ruta(idPartida, idNodoDestino)
         
         
    
    @staticmethod
    def calcular_direccion(pos_origen, pos_destino):
       
        ox, oy = pos_origen
        dx, dy = pos_destino
        
        # Calcular diferencia
        diff_x = dx - ox
        diff_y = dy - oy
        
        
        if diff_x == 0 and diff_y > 0:
            return "Arriba"
        elif diff_x == 0 and diff_y < 0:
            return "Abajo"
        elif diff_x > 0 and diff_y == 0:
            return "Derecha"
        elif diff_x < 0 and diff_y == 0:
            return "Izquierda"
        elif diff_x == 0 and diff_y == 0:
            return "Misma posición"
        else:
    
            if abs(diff_x) > abs(diff_y):
          
                return "Derecha" if diff_x > 0 else "Izquierda"
            else:
               
                return "Arriba" if diff_y > 0 else "Abajo"
    
    @staticmethod
    def setNodosFinales ():
        for nodo in GlobalGraph.nodos:
         
            if (nodo.esDetino):
                GlobalGraph.nodosDestino.append(nodo)
            
        
      
    @staticmethod
    def agregar_direccion_a_conexiones():
      

        
        for nodo in GlobalGraph.nodos:
            if not hasattr(nodo, 'conexiones') or not nodo.conexiones:
                continue
            
            for conexion in nodo.conexiones:
                # Si la conexión ya tiene dirección, saltarla
                if 'direccion' in conexion and conexion['direccion'] != 'Desconocida':
                    continue
                
                # Calcular la dirección desde el nodo actual al nodo destino
                direccion = GlobalGraph.calcular_direccion(
                    nodo.posicion,
                    conexion['posicion']
                )
                
                # Agregar la dirección a la conexión
                conexion['direccion'] = direccion
                
             
        
    
    @staticmethod
    def obtener_direccion_entre_nodos(nodo_origen_id, nodo_destino_id):
    
        nodo_origen = GlobalGraph.obtener_nodo_por_id(nodo_origen_id)
        nodo_destino = GlobalGraph.obtener_nodo_por_id(nodo_destino_id)
        
        if nodo_origen is None or nodo_destino is None:
            return None
        
        return GlobalGraph.calcular_direccion(nodo_origen.posicion, nodo_destino.posicion)
    
    @staticmethod
    def obtener_siguiente_nodo_y_direccion(nodo_actual_id, nodo_destino_id):
  
        ruta = GlobalGraph.buscar_ruta_bfs(nodo_actual_id, nodo_destino_id)
        
        if ruta is None or len(ruta) < 2:
            return None
        
        # El segundo elemento de la ruta es el siguiente paso
        siguiente_paso = ruta[1]
        
        return {
            'siguiente_nodo_id': siguiente_paso['nodo_id'],
            'direccion': siguiente_paso['direccion'],
            'posicion': siguiente_paso['posicion'],
            'distancia': siguiente_paso.get('distancia', 0)
        }
    
    @staticmethod
    def imprimir():
       
        
        for nodo in GlobalGraph.nodos:
            tipo = "DESTINO" if nodo.esDetino else "INTERSECCIÓN"
            print(f"\nNodo {nodo.id} ({tipo}):")
            print(f"  Posición: {nodo.posicion}")
            if hasattr(nodo, 'intersecciones'):
                print(f"  Intersecciones: {len(nodo.intersecciones)}")
            if hasattr(nodo, 'conexiones'):
                print(f"  Conexiones: {len(nodo.conexiones)}")
                for conn in nodo.conexiones:
                    direccion_texto = f" hacia el {conn['direccion']}" if 'direccion' in conn else ""
                    print(f"    -> Nodo {conn['nodo_id']} en {conn['posicion']}{direccion_texto}")
                    print(f"       Distancia: {conn['distancia']} pasos")
    
    @staticmethod
    def obtener_nodo_por_id(nodo_id):
       
        for nodo in GlobalGraph.nodos:
            if nodo.id == nodo_id:
                return nodo
        return None
    
    @staticmethod
    def obtener_nodo_por_posicion(posicion):
        if posicion in GlobalGraph.grafo:
            return GlobalGraph.grafo[posicion]
        for nodo in GlobalGraph.nodos:
            if nodo.posicion == posicion:
                return nodo
        return None
    
    @staticmethod
    def encontrar_nodo_mas_cercano(posicion_actual):
       
        if not GlobalGraph.nodos:
            return None
        
        x, y = posicion_actual
        nodo_cercano = None
        distancia_minima = float('inf')
        
        for nodo in GlobalGraph.nodos:
            nx, ny = nodo.posicion
            distancia = abs(nx - x) + abs(ny - y)  # Distancia Manhattan
            
            if distancia < distancia_minima:
                distancia_minima = distancia
                nodo_cercano = nodo
        
        return nodo_cercano
    
    @staticmethod
    def crearNodos(celdas):
        nNodos = 0
        for celda in celdas:
            interseccion = next((a for a in celda.agents if isinstance(a, Intersection)), None)
            if interseccion is not None:
                nNodos += 1
        
     
        return nNodos
    
    @staticmethod
    def crearConexiones():
        print("Creando conexiones...")
    
    @staticmethod
    def buscar_ruta_bfs(nodo_origen_id, nodo_destino_id):
       
        # Obtener los nodos
        nodo_origen = GlobalGraph.obtener_nodo_por_id(nodo_origen_id)
        nodo_destino = GlobalGraph.obtener_nodo_por_id(nodo_destino_id)
        
        # Verificar que ambos nodos existan
        if nodo_origen is None:
            print(f"Error: No se encontró el nodo origen con ID {nodo_origen_id}")
            return None
        
        if nodo_destino is None:
            print(f"Error: No se encontró el nodo destino con ID {nodo_destino_id}")
            return None
        
        # Caso especial: origen y destino son el mismo
        if nodo_origen_id == nodo_destino_id:
            return [{
                'nodo_id': nodo_origen_id,
                'posicion': nodo_origen.posicion,
                'direccion': None
            }]
        
        # Cola para BFS: cada elemento es una tupla (nodo_actual, camino_hasta_ahora)
        # camino_hasta_ahora es una lista de diccionarios con nodo_id, posicion y direccion
        cola = deque([(nodo_origen, [{
            'nodo_id': nodo_origen_id,
            'posicion': nodo_origen.posicion,
            'direccion': None  # El primer nodo no tiene dirección de llegada
        }])])
        
        # Set de nodos visitados
        visitados = {nodo_origen_id}
        
        # BFS
        while cola:
            nodo_actual, camino = cola.popleft()
            
            # Explorar vecinos/conexiones
            conexiones = nodo_actual.conexiones if hasattr(nodo_actual, 'conexiones') else []
            
            for conn in conexiones:
                vecino_id = conn['nodo_id']
                
                # Si ya visitamos este nodo, lo ignoramos
                if vecino_id in visitados:
                    continue
                
                # Marcar como visitado
                visitados.add(vecino_id)
                
                # Obtener la dirección hacia este vecino
                # Si no existe en la conexión, calcularla
                if 'direccion' in conn and conn['direccion'] != 'Desconocida':
                    direccion = conn['direccion']
                else:
                    # Calcular la dirección sobre la marcha
                    direccion = GlobalGraph.calcular_direccion(
                        nodo_actual.posicion,
                        conn['posicion']
                    )
                
                # Crear nuevo paso en el camino
                nuevo_paso = {
                    'nodo_id': vecino_id,
                    'posicion': conn['posicion'],
                    'direccion': direccion,
                    'distancia': conn.get('distancia', 0)
                }
                
                # Crear nuevo camino
                nuevo_camino = camino + [nuevo_paso]
                
                # Si llegamos al destino, retornar el camino
                if vecino_id == nodo_destino_id:
                    return nuevo_camino
                
                # Agregar a la cola para explorar
                vecino = GlobalGraph.obtener_nodo_por_id(vecino_id)
                if vecino:
                    cola.append((vecino, nuevo_camino))
        
        # Si salimos del while sin encontrar ruta
        return None
    
    @staticmethod
    def imprimir_ruta(nodo_origen_id, nodo_destino_id):
       
        
        ruta = GlobalGraph.buscar_ruta_bfs(nodo_origen_id, nodo_destino_id)
        #print(ruta)        
        if ruta is None:
            print("no hay ruta entre estos nodos")
        else:
            return ruta
    
    @staticmethod
    def obtener_siguiente_direccion(nodo_actual_id, nodo_destino_id):
      
        info = GlobalGraph.obtener_siguiente_nodo_y_direccion(nodo_actual_id, nodo_destino_id)
        return info['direccion'] if info else None


class Nodo():
    def __init__(self):
        self.id = None
        self.posicion = None
        self.conexiones = []
        self.conexiones_dirigidas = []
        self.intersecciones = []  # Lista de posiciones de intersecciones que forman este nodo
        self.vecinos = []
        self.x = 0
        self.y = 0
        self.esDetino = False
        self.isNodo = True


# ============================================
# INSTRUCCIONES PARA USAR EN CityModel:
# ============================================
# 
# En tu método crearConexionesNodos(), al FINAL (después del último print),
# agrega esta línea:
#
#     GlobalGraph.agregar_direccion_a_conexiones()
#
# Esto calculará y agregará las direcciones a todas las conexiones que creaste.
# El método buscar_ruta_bfs ya está actualizado para calcular direcciones
# sobre la marcha si no existen, así que funcionará de ambas formas.