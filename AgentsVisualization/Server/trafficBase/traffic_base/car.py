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
    def __init__(self, model, cell):
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
        
    def moverse(self):
        # Validar que self.cell no sea None
        if self.cell is None:
            print("ERROR: Car.cell es None, no se puede mover")
            return
        
        # Buscar el objeto Road en la celda actual
        road = next((a for a in self.cell.agents if isinstance(a, Road)), None)
        
        if road is None:
            print(f"WARNING: No se encontró Road en la celda {self.cell.coordinate}")
            return
        
        # Obtener la dirección usando el carácter guardado en char
        # Los caracteres son: "^" (arriba), "v" (abajo), "<" (izquierda), ">" (derecha)
        direccion_char = getattr(road, 'char', None)
        
        if direccion_char is None:
            print(f"WARNING: Road sin atributo 'char' en {self.cell.coordinate}")
            return
        
        self.direccionMovimiento = direccion_char
        
        # Obtener vecinos de la celda actual
        x, y = self.cell.coordinate
        
        # Mapear el carácter de dirección a coordenadas del vecino destino
        mapeo_direccion = {
            "^": (x, y + 1),      # arriba
            "v": (x, y - 1),      # abajo
            "<": (x - 1, y),      # izquierda
            ">": (x + 1, y)       # derecha
        }
        
        # Obtener coordenada destino
        coord_destino = mapeo_direccion.get(direccion_char)
        
        if coord_destino is None:
            print(f"WARNING: Dirección '{direccion_char}' no reconocida en {self.cell.coordinate}")
            return
        
        # Buscar la celda destino en el grid
        destino = None
        try:
            destino = self.model.grid[coord_destino]
        except (KeyError, IndexError):
            print(f"WARNING: Coordenada destino {coord_destino} fuera del grid")
            return
        
        if destino is None:
            print(f"WARNING: No existe celda en coordenada {coord_destino}")
            return
        
        # Verificar si hay un obstáculo en el destino
        tiene_obstaculo = any(isinstance(a, Obstacle) for a in destino.agents)
        if tiene_obstaculo:
            # print(f"INFO: Obstáculo en {destino.coordinate}, esperando")
            return
        
        # Verificar si hay otro carro en el destino
        tiene_carro = any(isinstance(a, Car) for a in destino.agents)
        if tiene_carro:
            # print(f"INFO: Carro en {destino.coordinate}, esperando")
            return
        
        # Si todo está bien, moverse
        self.move_to(destino)
            
    def move(self):
        self.moverse()
        
    def step(self):
        self.move()