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

#
class Nodo():

   def __init__(self, direccion):
       self.conexiones= []
       self.conexiones_dirigidas=[]
       self.x = 0
       self.y = 0
       self.direccion =direccion

       
   def crear_crear_conexiones(self,  cell):
       #for celula in celulas:
       #    for agente in 
       #
       direccion=self.direccion
       cx, cy = cell.coordinate
       
       direcciones = {
               "Right": (1, 0),
               "Left": (-1, 0),
               "Up":   (0, 1),
               "Down": (0, -1),
               "ArribaDerecha": (1,1),
               "ArribaIzquierda": (-1,1),
               "AbajoIzquierda": (-1,-1),
               "AbajoDerecha": (1,-1)
               
           }
       
       
       for vecino in cell.neighborhood:
          vx, vy = vecino.coordinate
          dx = vx - cx
          dy = vy - cy
          road = next((a for a in vecino.agents if isinstance(a, Road)), None)

            # Si NO hay ROAD, saltamos este vecino
          if road is None:
            print("no hay calle")
            continue
          else:
              print("calle tipo")
              print(road.direction)
        
              if direccion == "Left":
                  if( (dx,dy) == direcciones["Left"]):
                      if road.direction == "Up" or  "Down" or "Left":
                          self.conexiones.append((vx,vy))
            
           
       
      # if (direccion =="Left"):
      #     print()
      #     #Conectar en izquierda si
      #     #Arriba, Abajo, Izquierda
      #     
      #     #Conectar Abajo
      #     #Abajo, Izquierda, Derecha
      #     
      #     #Conectar Arriba 
      #     #Izquierda, Derecha, Arriba
      #     
      #     #Conectar ARRIBA IZQUIERDA
      #     #Izquierda Arriba
      #     
      #     #Conectar Abajo IZUQIERDO 
      #     #Izquierda Abajo
      #     
      # elif (direccion =="Right"):
      #     print()
      #     #Conectar derecha
      #     #Arriba Abajo, Derecha
      #     
      #     #Conectar Abajo
      #     #Abajo, Izquierda, Derecha
      #     
      #     #Conectar Arriba 
      #     #Izquierda, Derecha, Arriba
      #     
      #     #Conectar ARRIBA DERECHA
      #     #Derecha ARRIBA
      #     
      #     #Conectar Abajo DERECHA
      #     #Derecha ABAJO
      # elif (direccion =="Up"):
      #     print()
      #     #Conectar en izquierda si
      #     #Arriba, Abajo, Izquierda
      #     
      #     #Conectar derecha
      #     #Arriba Abajo, Derecha
      #     
      #     #Conectar Arriba 
      #     #Izquierda, Derecha, Arriba
      #     
      #       
      #     #Conectar ARRIBA DERECHA
      #     #Dercha Arriba
      #     
      #     
      #     #Conectar ARRIBA IZQUIERDA
      #     #Izquierda Arriba
      #     
      #     
      # elif (direccion =="Down"):
      #     print()
      #     #Conectar en izquierda si
      #     #Arriba, Abajo, Izquierda
      #     
      #     #Conectar derecha
      #     #Arriba Abajo, Derecha
      #     
      #     #Conectar Abajo 
      #     #Izquierda, Derecha, Abajo
      #     
      #     #Conectar ABAJO DERECHA
      #     #Derecha Abajo
      #     
      #     
      #     #Conectar ABAJO IZQUIERDA
      #     #Izquierda Abajo
      #
           

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