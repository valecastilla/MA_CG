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
        if puntoPartida is None:
            raise RuntimeError("No hay punto de partida (Intersection) en la celda.")
        idPartida = puntoPartida.idNodoInter

        if not GlobalGraph.nodosDestino:
            raise RuntimeError("No hay nodos destino disponibles en GlobalGraph.nodosDestino.")

        # Intentar destinos aleatorios hasta encontrar una ruta o agotar la lista
        while GlobalGraph.nodosDestino:
            nodoDestino = random.choice(GlobalGraph.nodosDestino)
            idNodoDestino = nodoDestino.id

            ruta = GlobalGraph.buscar_ruta_bfs(idPartida, idNodoDestino)
            if ruta is not None:
                return ruta

            # Si no hay ruta, quitar ese destino de la lista para no intentar otra vez
            try:
                GlobalGraph.nodosDestino.remove(nodoDestino)
            except ValueError:
                pass

        # Si se agotaron todos los destinos sin éxito, lanzar error (no se retorna None)
        raise RuntimeError("No se encontró ruta a ningún destino disponible.")

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
    def buscar_ruta_bfs(nodo_origen_id, nodo_destino_id):
       
        #bbtener los nodos
        nodo_origen = GlobalGraph.obtener_nodo_por_id(nodo_origen_id)
        nodo_destino = GlobalGraph.obtener_nodo_por_id(nodo_destino_id)
        
        #asmbos nodos existan
        if nodo_origen is None:
            return None
        
        if nodo_destino is None:
            return None
        
        #si dieccion y destino son iguales
        if nodo_origen_id == nodo_destino_id:
            return [{
                'nodo_id': nodo_origen_id,
                'posicion': nodo_origen.posicion,
                'direccion': None
            }]
        
   
        cola = deque([(nodo_origen, [{
            'nodo_id': nodo_origen_id,
            'posicion': nodo_origen.posicion,
            'direccion': None  
        }])])
        
        # Set de nodos visitados
        visitados = {nodo_origen_id}
        
        # BFS
        while cola:
            nodo_actual, camino = cola.popleft()
            
            #explorar vecinos
            conexiones = nodo_actual.conexiones if hasattr(nodo_actual, 'conexiones') else []
            
            for conn in conexiones:
                vecino_id = conn['nodo_id']
                
                #ecitar si ya existe este nodo
                if vecino_id in visitados:
                    continue
                
                #marcar vis
                visitados.add(vecino_id)
                
                #Oobtener la dirección hacia vec

                if 'direccion' in conn and conn['direccion'] != 'Desconocida':
                    direccion = conn['direccion']
                else:
                    
                    direccion = GlobalGraph.calcular_direccion(
                        nodo_actual.posicion,
                        conn['posicion']
                    )
                
                nuevo_paso = {
                    'nodo_id': vecino_id,
                    'posicion': conn['posicion'],
                    'direccion': direccion,
                    'distancia': conn.get('distancia', 0)
                }
                
                #nuevo camino
                nuevo_camino = camino + [nuevo_paso]
                
                # Si llegamos al destino regresar camino
                if vecino_id == nodo_destino_id:
                    return nuevo_camino
                
                
                vecino = GlobalGraph.obtener_nodo_por_id(vecino_id)
                if vecino:
                    cola.append((vecino, nuevo_camino))
        #none no se encontró la ruta
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
        self.intersecciones = []  # Lista de posiciones de intersecciones del nodo
        self.vecinos = []
        self.x = 0
        self.y = 0
        self.esDetino = False
        self.isNodo = True

class DatosGlobales:
    aparcionhuevos=0
    huevosLlegaron= 0
    huevosEnPantalla= 0
    
    @staticmethod
    def restarHuevos():
        DatosGlobales.huevosLlegaron+=1
        DatosGlobales.huevosEnPantalla-=1
      
    @staticmethod
    def sumarHuevos():
        DatosGlobales.aparcionhuevos+=1
        DatosGlobales.huevosEnPantalla+=1