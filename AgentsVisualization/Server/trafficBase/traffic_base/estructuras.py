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
        """Agrega un nodo a la lista global"""
        GlobalGraph.nodos.append(nodo)
    
    @staticmethod
    def limpiar():
        """Limpia el grafo y la lista de nodos"""
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
        """
        Calcula la dirección desde pos_origen hacia pos_destino.
        
        Args:
            pos_origen: Tupla (x, y) del punto de origen
            pos_destino: Tupla (x, y) del punto de destino
            
        Returns:
            String con la dirección: 'Norte', 'Sur', 'Este', 'Oeste', 
            'Noreste', 'Noroeste', 'Sureste', 'Suroeste', o 'Misma posición'
        """
        ox, oy = pos_origen
        dx, dy = pos_destino
        
        # Calcular diferencia
        diff_x = dx - ox
        diff_y = dy - oy
        
        # Determinar dirección principal
        if diff_x == 0 and diff_y > 0:
            return "Arriba"
        elif diff_x == 0 and diff_y < 0:
            return "Abajo"
        elif diff_x > 0 and diff_y == 0:
            return "Derecha"
        elif diff_x < 0 and diff_y == 0:
            return "Izquierda"
        elif diff_x > 0 and diff_y > 0:
            return "ArribaDerecha"
        elif diff_x < 0 and diff_y > 0:
            return "ArribaIzquierda"
        elif diff_x > 0 and diff_y < 0:
            return "AbajoDerecha"
        elif diff_x < 0 and diff_y < 0:
            return "AbajoIzquierda"
        else:
            return "Misma posición"
    @staticmethod
    def setNodosFinales ():
        for nodo in GlobalGraph.nodos:
         
            if (nodo.esDetino):
                GlobalGraph.nodosDestino.append(nodo)
            
        
      
    @staticmethod
    def agregar_direccion_a_conexiones():
        """
        Agrega la dirección a todas las conexiones existentes de todos los nodos.
        Debe llamarse DESPUÉS de crear todos los nodos y sus conexiones.
        """
        print("\n=== AGREGANDO DIRECCIONES A CONEXIONES ===")
        
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
                
                print(f"Nodo {nodo.id} -> Nodo {conexion['nodo_id']}: {direccion}")
        
        
    
    @staticmethod
    def obtener_direccion_entre_nodos(nodo_origen_id, nodo_destino_id):
        """
        Calcula la dirección directa entre dos nodos (sin seguir ruta)
        
        Args:
            nodo_origen_id: ID del nodo de origen
            nodo_destino_id: ID del nodo de destino
            
        Returns:
            String con la dirección o None si algún nodo no existe
        """
        nodo_origen = GlobalGraph.obtener_nodo_por_id(nodo_origen_id)
        nodo_destino = GlobalGraph.obtener_nodo_por_id(nodo_destino_id)
        
        if nodo_origen is None or nodo_destino is None:
            return None
        
        return GlobalGraph.calcular_direccion(nodo_origen.posicion, nodo_destino.posicion)
    
    @staticmethod
    def obtener_siguiente_nodo_y_direccion(nodo_actual_id, nodo_destino_id):
        """
        Obtiene el siguiente nodo en la ruta y la dirección para llegar a él
        
        Args:
            nodo_actual_id: ID del nodo actual
            nodo_destino_id: ID del nodo destino final
            
        Returns:
            Diccionario con:
            {
                'siguiente_nodo_id': int,
                'direccion': str,
                'posicion': tuple,
                'distancia': int
            }
            o None si no hay ruta
        """
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
        """Imprime información del grafo"""
        print("\n=== GRAFO GLOBAL ===")
        print(f"Total de nodos: {len(GlobalGraph.nodos)}")
        print(f"Total de entradas en grafo: {len(GlobalGraph.grafo)}")
        
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
        """Busca un nodo por su ID"""
        for nodo in GlobalGraph.nodos:
            if nodo.id == nodo_id:
                return nodo
        return None
    
    @staticmethod
    def obtener_nodo_por_posicion(posicion):
        """Busca un nodo por su posición"""
        # Primero buscar en el diccionario grafo
        if posicion in GlobalGraph.grafo:
            return GlobalGraph.grafo[posicion]
        
        # Si no está, buscar en la lista de nodos
        for nodo in GlobalGraph.nodos:
            if nodo.posicion == posicion:
                return nodo
        return None
    
    @staticmethod
    def encontrar_nodo_mas_cercano(posicion_actual):
        """
        Encuentra el nodo más cercano a una posición dada
        
        Args:
            posicion_actual: Tupla (x, y) de la posición actual
            
        Returns:
            Nodo más cercano o None si no hay nodos
        """
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
        
        print(f"Se encontraron {nNodos} Nodos")
        return nNodos
    
    @staticmethod
    def crearConexiones():
        print("Creando conexiones...")
    
    @staticmethod
    def buscar_ruta_bfs(nodo_origen_id, nodo_destino_id):
        """
        Busca la ruta más corta entre dos nodos usando BFS (Búsqueda por Anchura)
        
        Args:
            nodo_origen_id: ID del nodo de inicio
            nodo_destino_id: ID del nodo de destino
            
        Returns:
            Lista de diccionarios con información de cada paso:
            [{'nodo_id': int, 'posicion': tuple, 'direccion': str}, ...]
            o None si no hay ruta
        """
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
        """
        Busca e imprime la ruta entre dos nodos con direcciones
        
        Args:
            nodo_origen_id: ID del nodo de inicio
            nodo_destino_id: ID del nodo de destino
            
        Returns:
            Lista con la ruta detallada o None si no existe
        """
        print(f"\n=== BÚSQUEDA DE RUTA ===")
        print(f"Origen: Nodo {nodo_origen_id}")
        print(f"Destino: Nodo {nodo_destino_id}")
        
        ruta = GlobalGraph.buscar_ruta_bfs(nodo_origen_id, nodo_destino_id)
        print(f"\n===  RUTA ===")
        print(ruta)        
        if ruta is None:
            print(f"\n❌ NO SE PUEDE llegar del nodo {nodo_origen_id} al nodo {nodo_destino_id}")
            print("No existe una ruta que conecte estos nodos.")
        else:
            print(f"\n✓ RUTA ENCONTRADA (longitud: {len(ruta)} nodos):")
            
            # Imprimir resumen simple
            ruta_ids = " -> ".join(str(paso['nodo_id']) for paso in ruta)
            print(f"Secuencia: {ruta_ids}")
            
            # Imprimir detalles paso a paso
            print("\n📍 Detalles de la ruta:")
            for i, paso in enumerate(ruta):
                if i == 0:
                    print(f"  {i+1}. Inicio en Nodo {paso['nodo_id']} (posición {paso['posicion']})")
                else:
                    direccion = paso['direccion']
                    distancia = paso.get('distancia', 'N/A')
                    print(f"  {i+1}. Ir hacia el {direccion} → Nodo {paso['nodo_id']} (posición {paso['posicion']})")
                    print(f"      Distancia desde nodo anterior: {distancia} pasos")
            
            # Calcular distancia total
            distancia_total = sum(paso.get('distancia', 0) for paso in ruta[1:])
            print(f"\n📏 Distancia total: {distancia_total} pasos")
        
        return ruta
    
    @staticmethod
    def obtener_siguiente_direccion(nodo_actual_id, nodo_destino_id):
        """
        Obtiene solo la dirección hacia el siguiente nodo en la ruta más corta
        
        Args:
            nodo_actual_id: ID del nodo actual
            nodo_destino_id: ID del nodo destino final
            
        Returns:
            String con la dirección (Norte, Sur, Este, Oeste, etc.) o None
        """
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