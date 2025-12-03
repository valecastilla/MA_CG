from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
from .agent import *
import json
from .estructuras import *

class Car(CellAgent):
    """
    Agent that moves randomly.
    """
    grafo_mapa = []
    def __init__(self, model, cell, ruta):
        """
        Creates a new random agent.
        Args:
            model: Model reference for the agent
            cell: The initial position of the agent
        """
        super().__init__(model)
        self.cell = cell
        self.estadoMovimiento=""
        self.direccionMovimiento=""
        self.ruta= ruta
        self.debe_eliminarse = False
        print(self.ruta)
        self.nodoactual = ""
        self.indexActual = 0
        self.direction = ""
        self.isNodoFinal = False
        self.nodofinal = GlobalGraph.obtener_nodo_por_id(self.ruta[len(self.ruta) - 1]["nodo_id"])
        print(self.nodofinal)
        self.direcionPatitas=""
        self.estadoAnterior = ""
        self.xf, self.yf=self.ruta[len(self.ruta) - 1]["posicion"]
        self.x, self.y = self.cell.coordinate
        
        # Inicializar la primera dirección
        if len(self.ruta) > 1:
            self.direccionMovimiento = self.ruta[1]["direccion"]
       
    def seguirRuta(self):
      
     xf, yf = self.ruta[len(self.ruta) - 1]["posicion"]
     
     # Validación temprana
     if self.cell is None:
         print("Error: self.cell es None")
         return
         
     next_moves = self.cell.neighborhood
     x, y = self.cell.coordinate
 
     vecinos = {
         "izquierda": None,
         "derecha": None,
         "arriba": None,
         "abajo": None,
         "izquierdaAbajo": None,
         "derechaAbajo": None,
         "derechaArriba": None,
         "izquierdaArriba": None,
     }
 
     for vecino in next_moves:
         if vecino is None:
             continue
 
         cx, cy = vecino.coordinate
 
         if   (cx, cy) == (x - 1, y) and any(isinstance(a, (Road, Destination, Obstacle)) for a in vecino.agents): 
             vecinos["izquierda"] = vecino
         elif (cx, cy) == (x + 1, y) and any(isinstance(a, (Road, Destination, Obstacle)) for a in vecino.agents): 
             vecinos["derecha"] = vecino
         elif (cx, cy) == (x, y + 1) and any(isinstance(a, (Road, Destination, Obstacle)) for a in vecino.agents): 
             vecinos["arriba"] = vecino
         elif (cx, cy) == (x, y - 1) and any(isinstance(a, (Road, Destination, Obstacle)) for a in vecino.agents): 
             vecinos["abajo"] = vecino
         elif (cx, cy) == (x - 1, y - 1) and any(isinstance(a, (Road, Destination, Obstacle)) for a in vecino.agents): 
             vecinos["izquierdaAbajo"] = vecino
         elif (cx, cy) == (x + 1, y - 1) and any(isinstance(a, (Road, Destination, Obstacle)) for a in vecino.agents): 
             vecinos["derechaAbajo"] = vecino
         elif (cx, cy) == (x + 1, y + 1) and any(isinstance(a, (Road, Destination, Obstacle)) for a in vecino.agents): 
             vecinos["derechaArriba"] = vecino
         elif (cx, cy) == (x - 1, y + 1) and any(isinstance(a, (Road, Destination, Obstacle)) for a in vecino.agents): 
             vecinos["izquierdaArriba"] = vecino
     
     arriba = vecinos["arriba"]
     abajo = vecinos["abajo"]
     izquierda = vecinos["izquierda"]
     derecha = vecinos["derecha"]
     arribaIzquierda = vecinos["izquierdaArriba"]
     arribaDerecha = vecinos["derechaArriba"]
     abajoDerecha = vecinos["derechaAbajo"]
     abajoIzquierda = vecinos["izquierdaAbajo"]
     
     # Variable para controlar si el agente debe moverse
     debe_detenerse = False
     
     def tiene_semaforo_rojo(celda):
         """
         Verifica si hay un semáforo en rojo en la celda dada.
         Si encuentra semáforo en rojo, marca debe_detenerse como True.
         """
         nonlocal debe_detenerse  # Para modificar la variable externa
         
         if celda is None:
             return
         
         semaforo = next((a for a in celda.agents if isinstance(a, Traffic_Light)), None)
         
         if semaforo is not None and not semaforo.state:
             
             debe_detenerse = True  # Marca para detener el movimiento
             return
         
         return
     def encontroObstaculo(direccion):
        if direccion == "Arriba":
            if arriba is None:
                return False
            return any(isinstance(a, (Car, Obstacle)) for a in arriba.agents)

        elif direccion == "Abajo":
            if abajo is None:
                return False
            return any(isinstance(a, (Car, Obstacle)) for a in abajo.agents)

        elif direccion == "Derecha":
            if derecha is None:
                return False
            return any(isinstance(a, (Car, Obstacle)) for a in derecha.agents)

        elif direccion == "Izquierda":
            if izquierda is None:
                return False
            return any(isinstance(a, (Car, Obstacle)) for a in izquierda.agents)
     def puedeRebasar(direccion,):
        road = next((a for a in self.cell.agents if isinstance(a, Road)), None)
        direccion_actual= road.direction
       
        if direccion == "Arriba":
            if not any(isinstance(a, (Car, Obstacle)) for a in arribaDerecha.agents) and not any(isinstance(a, (Car, Obstacle)) for a in derecha.agents):
                r= next((a for a in self.arribaDerecha.agents if isinstance(a, Road)), None)
                if r.direction== direccion_actual:
                    return"ArribaDerecha"
            if not any(isinstance(a, (Car, Obstacle)) for a in arribaIzquierda.agents) and not any(isinstance(a, (Car, Obstacle)) for a in izquierda.agents):
                
                return"ArribaIzquierda"
            
            return "NO"

        elif direccion == "Abajo":
            if not any(isinstance(a, (Car, Obstacle)) for a in abajoDerecha.agents) and not any(isinstance(a, (Car, Obstacle)) for a in derecha.agents):
                return"AbajoDerecha"
            if not any(isinstance(a, (Car, Obstacle)) for a in abajoIzquierda.agents) and not any(isinstance(a, (Car, Obstacle)) for a in izquierda.agents):

                return"ArribaIzquierda"
            
            return "NO"

        elif direccion == "Derecha":
            if not any(isinstance(a, (Car, Obstacle)) for a in abajoDerecha.agents) and not any(isinstance(a, (Car, Obstacle)) for a in abajo.agents):
                return"AbajoDerecha"
            if not any(isinstance(a, (Car, Obstacle)) for a in arribaDerecha.agents) and not any(isinstance(a, (Car, Obstacle)) for a in arriba.agents):
                return"ArribaDerecha"
            
            return "NO"

        elif direccion == "Izquierda":
            if not any(isinstance(a, (Car, Obstacle)) for a in abajoIzquierda.agents) and not any(isinstance(a, (Car, Obstacle)) for a in abajo.agents):

                return"AbajoDerecha"
            if not any(isinstance(a, (Car, Obstacle)) for a in arribaIzquierda.agents) and not any(isinstance(a, (Car, Obstacle)) for a in arriba.agents):
                return"ArribaDerecha"
            
            return "NO"

         
     
     def llego():
         print(f"Carro llegó a destino en posición ({xf}, {yf})")
         self.debe_eliminarse = True  
         
     # CAMBIO IMPORTANTE: Estas funciones ya no retornan True/False
     def estado_ARRIBA():
         if encontroObstaculo("Arriba"):
             
             
         tiene_semaforo_rojo(arriba)
         
         
         
         if debe_detenerse:
             print("🛑 Detenido por semáforo en rojo")
             return
             
         if self.isNodoFinal:
             if y == yf:
                 if x > xf:
                     self.direction = "Izquierda"
                     return
                 elif x < xf:
                     self.direction = "Derecha"
                     return
                 else: 
                     llego()
                     return
         
         self.direction = "Arriba"
     
     def estado_ABAJO():
         
         tiene_semaforo_rojo(abajo)
         if debe_detenerse:
             print("🛑 Detenido por semáforo en rojo")
             return
         if encontroObstaculo("Abajo"):
             print("encontroObstaculo")
             
         if self.isNodoFinal:
             if y == yf:
                 if x > xf:
                     self.direction = "Izquierda"
                     return
                 elif x < xf:
                     self.direction = "Derecha"
                     return
                 else: 
                     llego()
                     return
         
         self.direction = "Abajo"
     
     def estado_IZQUIERDA():
         tiene_semaforo_rojo(izquierda)
         if debe_detenerse:
             print("🛑 Detenido por semáforo en rojo")
             return
         if encontroObstaculo("Izquierda"):
             print("encontroObstaculo")
         if self.isNodoFinal:
             if x == xf:
                 if y > yf:
                     self.direction = "Abajo"
                     return
                 elif y < yf:
                     self.direction = "Arriba"
                     return
                 else:
                     llego()
                     return
         
         self.direction = "Izquierda"
     
     def estado_DERECHA():
         tiene_semaforo_rojo(derecha)
         if debe_detenerse:
             print("🛑 Detenido por semáforo en rojo")
             return
         if encontroObstaculo("Derecha"):
             print("encontroObstaculo" )
         if self.isNodoFinal:
             if x == xf:
                 if y > yf:
                     self.direction = "Abajo"
                     return
                 elif y < yf:
                     self.direction = "Arriba"
                     return
                 else:
                     llego()
                     return
         
         self.direction = "Derecha"
     
     def estado_SEMAFORO():
         print("En semáforo")
     
     tabla_estados = {
         "Arriba": estado_ARRIBA,
         "Abajo": estado_ABAJO,
         "Izquierda": estado_IZQUIERDA,
         "Derecha": estado_DERECHA,
         "semaforo": estado_SEMAFORO,
     }
             
     intersection = next((a for a in self.cell.agents if isinstance(a, Intersection)), None)
    
     if intersection is not None:
         print(intersection.idNodoInter)
         for index, nodo in enumerate(self.ruta):
             if nodo.get("nodo_id") == intersection.idNodoInter:
                 self.nodoactual, self.indexActual = nodo, index
                 break
         
         if self.indexActual + 1 < len(self.ruta):
             print(self.ruta[self.indexActual + 1]["direccion"])   
             
             if self.ruta[self.indexActual + 1]["nodo_id"] == self.nodofinal.id:
                 self.isNodoFinal = True
                 print("Llegó al nodo final")
             
             self.direccionMovimiento = self.ruta[self.indexActual + 1]["direccion"]
         else:
             print("Llegó al final de la ruta")
             self.isNodoFinal = True
             return
     
     # Actualizar dirección
     if self.direccionMovimiento in tabla_estados:
         tabla_estados[self.direccionMovimiento]()
     
     # Si debe detenerse (semáforo rojo), NO mover
     if debe_detenerse:
         return  # Salir sin ejecutar move_to()
     
     # Mapeo de direcciones
     direcciones = {
         "Arriba": arriba,
         "Abajo": abajo,
         "Derecha": derecha,
         "Izquierda": izquierda,
         "Arribaderecha": arribaDerecha,
         "Arribaizquierda": arribaIzquierda,
         "Abajoderecha": abajoDerecha,
         "Abajoizquierda": abajoIzquierda
     }
 
     destino = direcciones.get(self.direction)
     
     # Validar que destino no es None antes de mover
     if destino is not None:
         self.move_to(destino)
     else:
         print(f"⚠️ No se encontró celda destino para dirección '{self.direction}'")
         print(f"Posición actual: {self.cell.coordinate}")

    def moverse(self):
        if self.cell is None:
            print("Error: self.cell es None en moverse()")
            return  # evita crash si el agente no tiene celda aún
    
       
            

        self.seguirRuta()

    def move(self):
        self.moverse()
        
    def step(self):
        if self.debe_eliminarse:
            try:
                # Remover de la celda
                if self.cell is not None:
                    self.cell.remove_agent(self)

                # Remover del modelo
                if self in self.model.agents:
                    self.model.agents.remove(self)

                print("✅ Carro eliminado correctamente")
                return  # Salir sin ejecutar move()
            except Exception as e:
                print(f"⚠️ Error al eliminar carro: {e}")
                return
        self.move()