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
        print(self.ruta)
        self.nodoactual = ""
        self.indexActual =0
        self.isNodoFinal=False
        self.nodofinal=GlobalGraph.obtener_nodo_por_id(self.ruta[len(self.ruta) - 1]["nodo_id"])
        print(self.nodofinal)
      
      
    
    def seguirRuta(self):
        intersection = next((a for a in self.cell.agents if isinstance(a, Intersection)), None)
       
        if intersection!= None:
            print(intersection.idNodoInter)
            for index, nodo in enumerate(self.ruta):
                
                if nodo.get("nodo_id") == intersection.idNodoInter:
                    self.nodoactual, self.indexActual= nodo, index
            print("direccion:")
            print("index")


            print(self.ruta[self.indexActual + 1]["direccion"])   
            self.direccionMovimiento=self.ruta[self.indexActual + 1]["direccion"]
            

        
    def moverse(self):
        # Actualizar dirección según la ruta
        self.seguirRuta()

        if not self.direccionMovimiento:
            return  # no hay más nodos

        # Mapa de tus direcciones → desplazamientos reales
        mapeo = {
            "Arriba": (0, 1),
            "Abajo": (0, -1),
            "Izquierda": (-1, 0),
            "Derecha": (1, 0),

            # diagonales si las usas
            "ArribaIzquierda": (-1, 1),
            "ArribaDerecha": (1, 1),
            "AbajoIzquierda": (-1, -1),
            "AbajoDerecha": (1, -1)
        }

        dxdy = mapeo.get(self.direccionMovimiento)

        if dxdy is None:
            print("Dirección no reconocida:", self.direccionMovimiento)
            return

        x, y = self.cell.coordinate
        dx, dy = dxdy
        coord_destino = (x + dx, y + dy)

        # Buscar la celda destino
        try:
            destino = self.model.grid[coord_destino]
        except Exception:
            print("Destino fuera del grid:", coord_destino)
            return

        # Obstáculos
        if any(isinstance(a, Obstacle) for a in destino.agents):
            return

        # Otro carro
        if any(isinstance(a, Car) for a in destino.agents):
            return

        # Todo OK → mover
        self.move_to(destino)

            
    def move(self):
        self.moverse()
        
    def step(self):
        self.move()