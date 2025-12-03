from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
from .agent import *
import json
from .agent import *
class GlobalGraph:
    grafo = {}

    def imprimir():
        for nodo in GlobalGraph.grafo:
            print(nodo)
            print(GlobalGraph.grafo[nodo].direccion)
            print(GlobalGraph.grafo[nodo].conexiones)
    def crearNodos(celdas):
        
        nNodos=0
        nodo =Nodo()
        for celda in celdas:
            interseccion = next((a for a in celda.agents if isinstance(a, Intersection)), None)
            if interseccion!= None:
                nNodos+=1
        
        print("se encontraron")
        print(nNodos)
        print("Nodos")
            
        
    def crearConexiones():
        print()

#
class Nodo():

   def __init__(self):
       self.conexiones= []
       self.conexiones_dirigidas=[]
       self.x = 0
       self.y = 0
       self.esDetino = False

       
   
#            

#class Nodo():
#
#    def __init__(self):
#        self.conexiones = []
#        self.conexiones_dirigidas = []
#        self.x = 0
#        self.y = 0
#        self.direccion = ""
#
#    def crear_crear_conexiones(self, direccion,  cell):
#        self.direccion= direccion
#        # Reglas basadas exactamente en tus comentarios
#        reglas = {
#            "Left": [
#                (-1, 0),   # izquierda
#                (0, 1),    # arriba
#                (0, -1),   # abajo
#                (-1, 1),   # arriba izquierda
#                (-1, -1),  # abajo izquierda
#            ],
#            "Right": [
#                (1, 0),     # derecha
#                (0, 1),     # arriba
#                (0, -1),    # abajo
#                (1, 1),     # arriba derecha
#                (1, -1),    # abajo derecha
#            ],
#            "Up": [
#                (0, 1),     # arriba
#                (-1, 0),    # izquierda
#                (1, 0),     # derecha
#                (-1, 1),    # arriba izquierda
#                (1, 1),     # arriba derecha
#            ],
#            "Down": [
#                (0, -1),    # abajo
#                (-1, 0),    # izquierda
#                (1, 0),     # derecha
#                (-1, -1),   # abajo izquierda
#                (1, -1),    # abajo derecha
#            ]
#        }
#
#        permitidos = reglas[direccion]
#
#        cx, cy = cell.coordinate
#
#        for vecino in cell.neighborhood:
#            vx, vy = vecino.coordinate
#
#            dx = vx - cx
#            dy = vy - cy
#
#            # Solo conectamos si el vector está permitido por las reglas
#            if (dx, dy) in permitidos:
#                self.conexiones.append((vx, vy))
#                self.conexiones_dirigidas.append((vx, vy))
#
#        # Guardar nodo en el grafo
#        GlobalGraph.grafo[(cx, cy)] = self
#            
#            
#            
#        
#        