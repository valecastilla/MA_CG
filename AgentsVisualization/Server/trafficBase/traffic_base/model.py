from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
from .agent import *
import json
from .estructuras import *
from .car import Car

class CityModel(Model):
    """
    Creates a model based on a city map.

    Args:
        N: Number of agents in the simulation
        seed: Random seed for the model
    """
  
    def __init__(self, N, seed=42):
        self.grafo_calles=[]
        self.grafo = {}
        
        

        super().__init__(seed=seed)

        # Load the map dictionary. The dictionary maps the characters in the map file to the corresponding agent.
        dataDictionary = json.load(open("city_files/mapDictionary.json"))
        self.spawnClock=10
        self.num_agents = N
        self.traffic_lights = []

        # Load the map file. The map file is a text file where each character represents an agent.
        with open("city_files/2022_base.txt") as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0])
            self.height = len(lines)
            
            self.grid = OrthogonalMooreGrid(
                [self.width, self.height], capacity=100, torus=False
            )
            
            
            pr= 0
            # Goes through each character in the map file and creates the corresponding agent.
            for r, row in enumerate(lines):
                for c, col in enumerate(row):

                    cell = self.grid[(c, self.height - r - 1)]

                    if col in ["v", "^", ">", "<"]:
                        agent = Road(self, cell, dataDictionary[col])
                        agent.char = col   
                        
                        self.grafo_calles.append(agent)
                        if pr< 3:
                            nodo =Nodo(dataDictionary[col])
                            #nodo.crear_crear_conexiones(cell)
                            self
                        if pr ==3:
                            GlobalGraph.imprimir()
                        pr +=1

                    elif col in ["S", "s"]:
                        agent = Traffic_Light(
                            self,
                            cell,
                            False if col == "S" else True,
                            int(dataDictionary[col]),
                        )
                        agent = Road(self, cell, dataDictionary[col]) 
                        self.traffic_lights.append(agent)

                    elif col == "#":
                        agent = Obstacle(self, cell)
                    elif col == "I":
                        agent = Intersection(self, cell)

                    elif col == "D":
                        agent = Destination(self, cell)
                        agent.direction = col 
                        self.grafo_calles.append(agent)

         
       
    def crearAutos(self, stepsSpawm):
        posiciones = [(0,0), (23,24), (0,24), (23,0)]
        
        if self.steps % stepsSpawm != 0:
            return
        
        for pos in posiciones:
            x, y = pos
            cell = self.grid[(x, y)]
            
            # Verificar si ya hay un carro en esta posición
            tiene_carro = any(isinstance(agent, Car) for agent in cell.agents)
            
            if tiene_carro:
                # Solo imprimir info, no detener la simulación
                print(f"INFO: Ya hay un auto en {pos}, saltando spawn")
                continue  # Continuar con la siguiente posición
            
            # Verificar que haya una Road en esta posición
            tiene_road = any(isinstance(agent, Road) for agent in cell.agents)
            
            if not tiene_road:
                print(f"WARNING: No hay Road en {pos}, no se puede crear auto")
                continue
            
            # Crear el carro
            print(f"Creando auto en: {pos}")
            car = Car(self, cell)
            cell.add_agent(car)
        
    def step(self):
        
        self.crearAutos(self.spawnClock)
        """Advance the model by one step."""
        self.agents.shuffle_do("step")
    
