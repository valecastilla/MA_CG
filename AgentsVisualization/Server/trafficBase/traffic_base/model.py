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
        self.nodo_counter= 0
        self.nodo_counter= 0
        self.nodos = []
        
        

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
            
            
        
            # Goes through each character in the map file and creates the corresponding agent.
            for r, row in enumerate(lines):
                for c, col in enumerate(row):

                    cell = self.grid[(c, self.height - r - 1)]

                    if col in ["v", "^", ">", "<", "←", "↑","→","↓"]:
                            
                     
                        if col == "←":
                            agent = Road(self, cell, dataDictionary["<"])
                            agent.char = "<"
                            agent = Intersection(self, cell)
                            
                        elif col == "→":
                            agent = Road(self, cell, dataDictionary[">"])
                            agent.char = ">"
                            agent = Intersection(self, cell)
                        elif col == "↑":
                            agent = Road(self, cell, dataDictionary["^"])
                            agent.char = "^"
                            agent = Intersection(self, cell)
                        elif col == "↓":
                            agent = Road(self, cell, dataDictionary["v"])
                            agent.char = "v"
                            agent = Intersection(self, cell)
                        else:
                            
                            agent = Road(self, cell, dataDictionary[col])
                            agent.char = col   
                        
                        
                       
                    elif col in ["←", "↑","→","↓"]:
                         agent = Intersection(self, cell)
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
                        agent = Tierra(self, cell,)
                    elif col == "I":
                        agent = Intersection(self, cell)

                    elif col == "D":
                        agent = Destination(self, cell)
                        agent.direction = col 
                        self.grafo_calles.append(agent)
                        agent = Tierra(self, cell,)
            self.crearNodos()
            self.crearConexionesNodos()
    def crearNodos(self):
        #Crea nodos agrupando intersecciones que existan de un mismo grupo creando nodo unicos 
        nNodos = 0
        intersecciones_visitadas = set()  # Revisa nodos que ya se hayan creado

        # Iterar por todas las celdas del mapa
        for x in range(self.width):
            for y in range(self.height):
                # Si ya visitamos esta celda, continuar
                if (x, y) in intersecciones_visitadas:
                    continue
                
                
                cell = self.grid[(x, y)]
                
                

                # Buscar si hay una intersección en la celda
                interseccion = next((a for a in cell.agents if isinstance(a, Intersection)), None)
                destino = next((a for a in cell.agents if isinstance(a, Destination)), None)
                if destino is not None and destino.esNodo== False:
                        nNodos += 1
                        

                        # Crear el nodo con ID único
                        nodo = Nodo()
                        nodo.id = self.nodo_counter
                        nodo.posicion = (destino.cell.coordinate)  # coordenadas del nodo
                        nodo.esDetino = True
                        self.nodos.append(nodo)
                        self.nodo_counter += 1
                        print(f"Nodo {nodo.id} creado agrupando {len(grupo_intersecciones)} intersecciones")
                        print(f"  Posiciones: {grupo_intersecciones}")
                        print(f"  Centro: ({int(centro_x)}, {int(centro_y)})")
                        print(f"  Vecinos: {len(vecinos_inmediatos)}")
                        print(f"  Es Destino: {nodo.esDetino}")
                        
                      
                    
                

                if interseccion is not None:
                    # Encontrar grupos de intersecciones
                    grupo_intersecciones = self.encontrarGrupoIntersecciones(x, y, intersecciones_visitadas)

                    # Marcar todas como visitadas
                    for pos in grupo_intersecciones:
                        intersecciones_visitadas.add(pos)

                    # Calcular el centro del grupo (promedio de posiciones)
                    centro_x = sum(pos[0] for pos in grupo_intersecciones) / len(grupo_intersecciones)
                    centro_y = sum(pos[1] for pos in grupo_intersecciones) / len(grupo_intersecciones)

                    # Buscar vecinos desde todas las intersecciones del grupo
                    vecinos_inmediatos = self.buscarVecinosDelGrupo(grupo_intersecciones, intersecciones_visitadas)

                    # Solo crear nodo si tiene vecinos (al menos 1 conexión saliente)
                    if len(vecinos_inmediatos) >= 1:
                        nNodos += 1

                        # Crear el nodo con ID único
                        nodo = Nodo()
                        nodo.id = self.nodo_counter
                        nodo.posicion = (int(centro_x), int(centro_y))  # Posición central del grupo
                        nodo.intersecciones = list(grupo_intersecciones)  # Todas las intersecciones del grupo
                        nodo.vecinos = vecinos_inmediatos

                        # Marcar todas las intersecciones del grupo como nodo
                        for pos in grupo_intersecciones:
                            inter_cell = self.grid[pos]
                            inter = next((a for a in inter_cell.agents if isinstance(a, Intersection)), None)
                            if inter:
                                inter.isNodo = True

                        # Agregar nodo a la lista
                        self.nodos.append(nodo)

                        # Agregar al grafo usando todas las posiciones del grupo
                        for pos in grupo_intersecciones:
                            self.grafo[pos] = nodo

                        # Incrementar contador
                        self.nodo_counter += 1

                        print(f"Nodo {nodo.id} creado agrupando {len(grupo_intersecciones)} intersecciones")
                        print(f"  Posiciones: {grupo_intersecciones}")
                        print(f"  Centro: ({int(centro_x)}, {int(centro_y)})")
                        print(f"  Vecinos: {len(vecinos_inmediatos)}")
                        print(f"  Es Destino: {nodo.esDetino}")

        print(f"\n=== RESUMEN ===")
        print(f"Se encontraron {nNodos} Nodos (grupos de intersecciones)")
        print(f"Total de nodos en lista: {len(self.nodos)}")

        return nNodos

    def encontrarGrupoIntersecciones(self, x, y, visitadas):
        
       #Enceuntra las interesciones que rodean a un nodo, para encontrar grupos de interescciones

        grupo = set()
        por_visitar = [(x, y)]
        
        while por_visitar:
            cx, cy = por_visitar.pop()
            
            # Si ya está en el grupo o visitada, continuar
            if (cx, cy) in grupo or (cx, cy) in visitadas:
                continue
            
            # Verificar si está dentro del grid para no buscar intersecciones fuera del grid
            if not (0 <= cx < self.width and 0 <= cy < self.height):
                continue
            
            # Verificar si hay una intersección
            cell = self.grid[(cx, cy)]
            interseccion = next((a for a in cell.agents if isinstance(a, Intersection)), None)
            
            if interseccion is not None:
                # Agregar al grupo
                grupo.add((cx, cy))
                
                # Buscar vecinos adyacentes (4 direcciones)
                direcciones = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                for dx, dy in direcciones:
                    nx, ny = cx + dx, cy + dy
                    if (nx, ny) not in grupo:
                        por_visitar.append((nx, ny))
        
        return grupo
    
    def buscarVecinosDelGrupo(self, grupo_intersecciones, todas_visitadas):
        
        #Busca los vecinos (otros grupos de intersecciones) para crear nodos unicos
        
        vecinos = []
        vecinos_encontrados = set()  # Crear nodos únicos, se evitan repetidos con el set
        
        # Direcciones: Norte, Sur, Este, Oeste
        direcciones = [
            (0, 1, "Norte"),
            (0, -1, "Sur"),
            (1, 0, "Este"),
            (-1, 0, "Oeste")
        ]
        
        # Para cada intersección del grupo
        for gx, gy in grupo_intersecciones:
            # Buscar en cada dirección
            for dx, dy, nombre_dir in direcciones:
                nx, ny = gx + dx, gy + dy
                
                # Si la celda de al aldo es del grupo ya no buscar
                if (nx, ny) in grupo_intersecciones:
                    continue
                
                # Buscar en esta dirección hasta encontrar otro grupo
                while 0 <= nx < self.width and 0 <= ny < self.height:
                    vecino_cell = self.grid[(nx, ny)]
                    
                    # Verificar si hay una intersección
                    vecino_interseccion = next(
                        (a for a in vecino_cell.agents if isinstance(a, Intersection)), 
                        None
                    )
                    
                    if vecino_interseccion is not None:
                        # Si se encuentra otra intersección de otro grupo crear id unico
                      
                        clave_vecino = (nx, ny)
                        
                        if clave_vecino not in vecinos_encontrados:
                            vecinos_encontrados.add(clave_vecino)
                            vecinos.append({
                                'posicion': (nx, ny),
                                'direccion': nombre_dir,
                                'distancia': abs(nx - gx) + abs(ny - gy),
                                'desde': (gx, gy)
                            })
                        break
                    
                    # Verificar si hay un obstáculo
                    hay_obstaculo = any(isinstance(a, Obstacle) for a in vecino_cell.agents)
                    if hay_obstaculo:
                        break
                    
                    # Verificar si hay una carretera
                    hay_carretera = any(isinstance(a, Road) for a in vecino_cell.agents)
                    if not hay_carretera:
                        break
                    
                    # Continuar en la misma dirección
                    nx += dx
                    ny += dy
        
        return vecinos
    
    def crearAutos(self, stepsSpawm):
        posiciones = [(0,0), (23,23), (0,23), (23,0)]
        
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
    def crearConexionesNodos(self):
        """
        Crea las conexiones entre nodos siguiendo el sentido de las carreteras.
        Un nodo puede conectarse a otro si siguiendo el flujo de tráfico (dirección de Roads)
        se puede llegar desde una posición del nodo origen a una posición del nodo destino.
        """
        print("\n=== CREANDO CONEXIONES ENTRE NODOS ===\n")

        # Mapeo de direcciones de Road a vectores de movimiento
        direcciones_road = {
            '<': (-1, 0),  # Izquierda
            '>': (1, 0),   # Derecha
            '^': (0, 1),   # Arriba
            'v': (0, -1)   # Abajo
        }

        # Para cada nodo en la lista
        for nodo_origen in self.nodos:
            # Los nodos destino son finales, no tienen conexiones salientes
            if nodo_origen.esDetino:
                continue
            
            conexiones_encontradas = set()  # Evitar conexiones duplicadas

            # Obtener posiciones del nodo origen
            posiciones_origen = nodo_origen.intersecciones if hasattr(nodo_origen, 'intersecciones') else [nodo_origen.posicion]

            # Desde cada posición del nodo origen
            for pos_origen in posiciones_origen:
                ox, oy = pos_origen

                # Verificar que la posición esté en el grid
                if not (0 <= ox < self.width and 0 <= oy < self.height):
                    continue
                
                cell_origen = self.grid[(ox, oy)]

                # Buscar todas las Roads adyacentes desde esta intersección
                for vecino in cell_origen.neighborhood:
                    vx, vy = vecino.coordinate

                    # Buscar si hay una Road en esta celda vecina
                    road = next((a for a in vecino.agents if isinstance(a, Road)), None)

                    if road is None:
                        continue
                    
                    # Obtener la dirección de la carretera
                    direccion_char = road.char if hasattr(road, 'char') else road.direction

                    if direccion_char not in direcciones_road:
                        continue
                    
                    # Verificar que podemos entrar a esta carretera desde nuestra posición
                    # La carretera debe estar en la dirección correcta desde el origen
                    dx_carretera, dy_carretera = direcciones_road[direccion_char]

                    # Calcular hacia dónde está el vecino desde nuestra posición
                    dx_hacia_vecino = vx - ox
                    dy_hacia_vecino = vy - oy

                    # Normalizar (solo nos importa la dirección, no la magnitud)
                    if dx_hacia_vecino != 0:
                        dx_hacia_vecino = dx_hacia_vecino // abs(dx_hacia_vecino)
                    if dy_hacia_vecino != 0:
                        dy_hacia_vecino = dy_hacia_vecino // abs(dy_hacia_vecino)

                    # La carretera debe ir en la misma dirección que queremos ir
                    # o al menos no ir en dirección contraria
                    if (dx_carretera == -dx_hacia_vecino and dx_hacia_vecino != 0) or \
                       (dy_carretera == -dy_hacia_vecino and dy_hacia_vecino != 0):
                        # La carretera va en sentido contrario
                        continue
                    
                    # Ahora seguimos el camino desde esta carretera
                    cx, cy = vx, vy
                    pasos = 1
                    max_pasos = max(self.width, self.height) * 2

                    while pasos < max_pasos:
                        # Verificar límites
                        if not (0 <= cx < self.width and 0 <= cy < self.height):
                            break
                        
                        current_cell = self.grid[(cx, cy)]

                        # Verificar si encontramos un nodo destino
                        destino = next((a for a in current_cell.agents if isinstance(a, Destination)), None)
                        if destino is not None:
                            # Buscar el nodo correspondiente
                            nodo_destino = next((n for n in self.nodos if n.posicion == (cx, cy) and n.esDetino), None)
                            if nodo_destino and nodo_destino.id not in conexiones_encontradas and nodo_destino.id != nodo_origen.id:
                                conexiones_encontradas.add(nodo_destino.id)
                                if not hasattr(nodo_origen, 'conexiones'):
                                    nodo_origen.conexiones = []
                                nodo_origen.conexiones.append({
                                    'nodo_id': nodo_destino.id,
                                    'posicion': nodo_destino.posicion,
                                    'desde': pos_origen,
                                    'distancia': pasos
                                })
                            break
                        
                        # Verificar si encontramos una intersección (otro nodo)
                        interseccion = next((a for a in current_cell.agents if isinstance(a, Intersection)), None)
                        if interseccion is not None and interseccion.isNodo:
                            # Buscar el nodo correspondiente en el grafo
                            if (cx, cy) in self.grafo:
                                nodo_destino = self.grafo[(cx, cy)]

                                # Evitar conectar el nodo consigo mismo
                                if nodo_destino.id != nodo_origen.id and nodo_destino.id not in conexiones_encontradas:
                                    conexiones_encontradas.add(nodo_destino.id)

                                    # Agregar la conexión
                                    if not hasattr(nodo_origen, 'conexiones'):
                                        nodo_origen.conexiones = []

                                    nodo_origen.conexiones.append({
                                        'nodo_id': nodo_destino.id,
                                        'posicion': nodo_destino.posicion,
                                        'desde': pos_origen,
                                        'distancia': pasos
                                    })
                            break
                        
                        # Verificar si hay un obstáculo
                        hay_obstaculo = any(isinstance(a, Obstacle) for a in current_cell.agents)
                        if hay_obstaculo:
                            break
                        
                        # Buscar la carretera actual
                        current_road = next((a for a in current_cell.agents if isinstance(a, Road)), None)

                        if current_road is None:
                            break
                        
                        # Obtener la dirección de la carretera actual
                        current_dir = current_road.char if hasattr(current_road, 'char') else current_road.direction

                        if current_dir not in direcciones_road:
                            break
                        
                        # Seguir en la dirección que indica la carretera
                        dx_carretera, dy_carretera = direcciones_road[current_dir]

                        # Avanzar en esa dirección
                        cx += dx_carretera
                        cy += dy_carretera
                        pasos += 1

        # Imprimir resumen de conexiones
        print("\n=== RESUMEN DE CONEXIONES ===\n")
        for nodo in self.nodos:
            tipo = "DESTINO" if nodo.esDetino else "INTERSECCIÓN"
            num_conexiones = len(nodo.conexiones) if hasattr(nodo, 'conexiones') else 0

            print(f"Nodo {nodo.id} ({tipo}) en {nodo.posicion}:")
            print(f"  Conexiones: {num_conexiones}")

            if hasattr(nodo, 'conexiones') and nodo.conexiones:
                for conn in nodo.conexiones:
                    print(f"    -> Nodo {conn['nodo_id']} en {conn['posicion']} (distancia: {conn['distancia']})")
            else:
                print(f"    (Sin conexiones salientes)")
            print()

        print(f"Total de nodos: {len(self.nodos)}")
        total_conexiones = sum(len(n.conexiones) if hasattr(n, 'conexiones') else 0 for n in self.nodos)
        print(f"Total de conexiones: {total_conexiones}\n")

    def step(self):
        
        self.crearAutos(self.spawnClock)
        """Advance the model by one step."""
        self.agents.shuffle_do("step")
    
