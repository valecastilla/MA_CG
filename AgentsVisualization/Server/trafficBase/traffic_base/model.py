from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
from .agent import *
import json
from .estructuras import *
from .car import Car
from .peticion import *

class CityModel(Model):
 
    def __init__(self, N, seed=42):
        self.grafo_calles=[]
        self.grafo = {}
        self.nodo_counter= 0
        self.coche=False
        self.nodos = []
        
        

        super().__init__(seed=seed)

        dataDictionary = json.load(open("city_files/mapDictionary.json"))
        self.spawnClock=5
        self.num_agents = N
        self.traffic_lights = []

        with open("city_files/2025_base.txt") as baseFile:
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

                    if col in ["v", "^", ">", "<", "1", "2","3","4"]:
                            
                     
                        if col == "1":
                            agent = Road(self, cell, dataDictionary["<"])
                            agent.char = "<"
                            agent = Intersection(self, cell)
                            
                        elif col == "3":
                            agent = Road(self, cell, dataDictionary[">"])
                            agent.char = ">"
                            agent = Intersection(self, cell)
                        elif col == "2":
                            agent = Road(self, cell, dataDictionary["^"])
                            agent.char = "^"
                            agent = Intersection(self, cell)
                        elif col == "4":
                            agent = Road(self, cell, dataDictionary["v"])
                            agent.char = "v"
                            agent = Intersection(self, cell)
                        else:
                            
                            agent = Road(self, cell, dataDictionary[col])
                            agent.char = col   
                        
                        
                       
                    elif col in ["1", "2","3","4"]:
                         agent = Intersection(self, cell)
                    elif col in ["5", "6", "7", "8"]:
                        
                        traffic_light = Traffic_Light(
                            self,
                            cell,
                            True,
                            (dataDictionary["s"]),
                        )
                        self.traffic_lights.append(traffic_light)
                        


    
                        if col == "5":
                            agent = Road(self, cell, dataDictionary["<"])
                            agent.char = "<"
                           
                            
                        elif col == "6":
                            agent = Road(self, cell, dataDictionary[">"])
                            agent.char = ">"
                           
                        elif col == "7":
                            agent = Road(self, cell, dataDictionary["^"])
                            agent.char = "^"
                        elif col == "8":
                            agent = Road(self, cell, dataDictionary["v"])
                            agent.char = "v"
                            
                        

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
           
            GlobalGraph.setNodosFinales()
    
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
                        
                        # Sincronizar el ID del nodo con el destino
                        destino.idNodo(self.nodo_counter)
                        
                        self.nodo_counter += 1
                       
                    
                
    
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
    
                        # Marcar todas las intersecciones del grupo como nodo y sincronizar el ID
                        for pos in grupo_intersecciones:
                            inter_cell = self.grid[pos]
                            inter = next((a for a in inter_cell.agents if isinstance(a, Intersection)), None)
                            if inter:
                                inter.isNodo = True
                                inter.idNodo(self.nodo_counter)  # Sincronizar el ID del nodo
    
                        # Agregar nodo a la lista
                        self.nodos.append(nodo)
    
                        # Agregar al grafo usando todas las posiciones del grupo
                        for pos in grupo_intersecciones:
                            self.grafo[pos] = nodo
    
                        # Incrementar contador
                        self.nodo_counter += 1
    
                    
                        
    
        
        
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
        
       
        direcciones = [
            (0, 1, "Arriba"),
            (0, -1, "Abajo"),
            (1, 0, "Derecha"),
            (-1, 0, "Izquierda")
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
        posiciones = [(0,0),(self.width-2 ,self.height-1), (0,self.height-1), (self.width-2 ,0)]

        if self.steps % stepsSpawm != 0:
            return

        print("==Huevos en pantalla")
        print(DatosGlobales.huevosEnPantalla)
        print("==Huevos que llegaron")
        print(DatosGlobales.huevosLlegaron)
        print("==Huevos que han aparecido")
        print(DatosGlobales.aparcionhuevos)
   
        todas_ocupadas = True
        for pos in posiciones:
            x, y = pos
            cell = self.grid[(x, y)]
            carros_en_celda = [agent for agent in cell.agents if isinstance(agent, Car)]
            if len(carros_en_celda) == 0:
                todas_ocupadas = False
                break

        if todas_ocupadas:
            self.running = False
            return

        for pos in posiciones:
            x, y = pos
            cell = self.grid[(x, y)]

            carros_en_celda = [agent for agent in cell.agents if isinstance(agent, Car)]
            if carros_en_celda:
                continue
            
            tiene_road = any(isinstance(agent, Road) for agent in cell.agents)
            if not tiene_road:
                continue
            
   
            ruta = GlobalGraph.obtenerRutaAleatoria(cell)
            car = Car(self, cell, ruta)
            DatosGlobales.sumarHuevos()


    def crearConexionesNodos(self):
    
        direcciones_road = {
            '<': (-1, 0),  # Izquierda
            '>': (1, 0),   # Derecha
            '^': (0, 1),   # Arriba
            'v': (0, -1)   # Abajo
        }
        
       
        vector_a_nombre = {
            (-1, 0): 'Izquierda',
            (1, 0): 'Derecha',
            (0, 1): 'Arriba',
            (0, -1): 'Abajo'
        }
    
        #crear nodo en lista
        for nodo_origen in self.nodos:
            #si es final no tiene hijops
            if nodo_origen.esDetino:
                continue
            
            conexiones_encontradas = set()  #conexiones dupli
    
            
            posiciones_origen = nodo_origen.intersecciones if hasattr(nodo_origen, 'intersecciones') else [nodo_origen.posicion]
    
            
            for pos_origen in posiciones_origen:
                ox, oy = pos_origen
    
                #dentro del gridd
                if not (0 <= ox < self.width and 0 <= oy < self.height):
                    continue
                
                cell_origen = self.grid[(ox, oy)]
    
                #busca vecinos nods
                for vecino in cell_origen.neighborhood:
                    vx, vy = vecino.coordinate
    
                    road = next((a for a in vecino.agents if isinstance(a, Road)), None)
    
                    if road is None:
                        continue
                    
                    
                    direccion_char = road.char if hasattr(road, 'char') else road.direction
    
                    if direccion_char not in direcciones_road:
                        continue
                    
                    dx_carretera, dy_carretera = direcciones_road[direccion_char]
                    dx_hacia_vecino = vx - ox
                    dy_hacia_vecino = vy - oy
    
                
                    if dx_hacia_vecino != 0:
                        dx_hacia_vecino = dx_hacia_vecino // abs(dx_hacia_vecino)
                    if dy_hacia_vecino != 0:
                        dy_hacia_vecino = dy_hacia_vecino // abs(dy_hacia_vecino)
    
                    if (dx_carretera == -dx_hacia_vecino and dx_hacia_vecino != 0) or \
                       (dy_carretera == -dy_hacia_vecino and dy_hacia_vecino != 0):
                        continue
                    
             
                    direccion_inicial = vector_a_nombre.get((dx_carretera, dy_carretera), None)
                    
                    if direccion_inicial is None:
                        continue
                    
                    #seguir camino
                    cx, cy = vx, vy
                    pasos = 1
                    max_pasos = max(self.width, self.height) * 2
    
                    while pasos < max_pasos:
                        #limites
                        if not (0 <= cx < self.width and 0 <= cy < self.height):
                            break
                        
                        current_cell = self.grid[(cx, cy)]
    
                        
                        destino = next((a for a in current_cell.agents if isinstance(a, Destination)), None)
                        if destino is not None:
                            #nodo por posi
                            nodo_destino = next(
                                (n for n in self.nodos 
                                 if n.esDetino and n.posicion == (cx, cy)), 
                                None
                            )
    
                            if nodo_destino and nodo_destino.id not in conexiones_encontradas:
                                conexiones_encontradas.add(nodo_destino.id)
                                if not hasattr(nodo_origen, 'conexiones'):
                                    nodo_origen.conexiones = []
    
                                nodo_origen.conexiones.append({
                                    'nodo_id': nodo_destino.id,
                                    'posicion': nodo_destino.posicion,
                                    'direccion': direccion_inicial,  
                                    'desde': pos_origen,
                                    'distancia': pasos
                                })
                            break
                        
                        #buscar destinos en los costados
                        for dx_adj, dy_adj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                            adj_x, adj_y = cx + dx_adj, cy + dy_adj
    
                            #limites
                            if not (0 <= adj_x < self.width and 0 <= adj_y < self.height):
                                continue
                            
                            adj_cell = self.grid[(adj_x, adj_y)]
                            destino_adj = next((a for a in adj_cell.agents if isinstance(a, Destination)), None)
    
                            if destino_adj is not None:
                                
                                nodo_destino = next(
                                    (n for n in self.nodos 
                                     if n.esDetino and n.posicion == (adj_x, adj_y)), 
                                    None
                                )
    
                                if nodo_destino and nodo_destino.id not in conexiones_encontradas:
                                    conexiones_encontradas.add(nodo_destino.id)
                                    if not hasattr(nodo_origen, 'conexiones'):
                                        nodo_origen.conexiones = []
    
                                    nodo_origen.conexiones.append({
                                        'nodo_id': nodo_destino.id,
                                        'posicion': nodo_destino.posicion,
                                        'direccion': direccion_inicial,  
                                        'desde': pos_origen,
                                        'distancia': pasos + 1 
                                    })
    
                   
                        interseccion = next((a for a in current_cell.agents if isinstance(a, Intersection)), None)
                        if interseccion is not None and interseccion.isNodo:
                            #nodo a grafo
                            if (cx, cy) in self.grafo:
                                nodo_destino = self.grafo[(cx, cy)]
    
                                #no conectar nodo con el mismo nond
                                if nodo_destino.id != nodo_origen.id and nodo_destino.id not in conexiones_encontradas:
                                    conexiones_encontradas.add(nodo_destino.id)
    
                                    if not hasattr(nodo_origen, 'conexiones'):
                                        nodo_origen.conexiones = []
    
                                    nodo_origen.conexiones.append({
                                        'nodo_id': nodo_destino.id,
                                        'posicion': nodo_destino.posicion,
                                        'direccion': direccion_inicial, 
                                        'desde': pos_origen,
                                        'distancia': pasos
                                    })
                            break
                        
                        
                        hay_obstaculo = any(isinstance(a, Obstacle) for a in current_cell.agents)
                        if hay_obstaculo:
                            break
                        
                        #crear nuevo cmaino
                        current_road = next((a for a in current_cell.agents if isinstance(a, Road)), None)
    
                        if current_road is None:
                            break
                        
                        
                        current_dir = current_road.char if hasattr(current_road, 'char') else current_road.direction
    
                        if current_dir not in direcciones_road:
                            break
                        
                        #seguir direciones de carretera
                        dx_carretera, dy_carretera = direcciones_road[current_dir]
                        cx += dx_carretera
                        cy += dy_carretera
                        pasos += 1
    
        #nodos impresio
        for nodo in self.nodos:
            tipo = "DESTINO" if nodo.esDetino else "INTERSECCIÓN"
            num_conexiones = len(nodo.conexiones) if hasattr(nodo, 'conexiones') else 0
           
            GlobalGraph.agregar_nodo(nodo)
    
        total_conexiones = sum(len(n.conexiones) if hasattr(n, 'conexiones') else 0 for n in self.nodos)
        

    def step(self):
        if self.steps % 5 != 0:
            data = {
                "year": 2025,
                "classroom": 302,
                "name": "Confis",
                "current_cars": DatosGlobales.huevosEnPantalla,
                "total_arrived": DatosGlobales.huevosLlegaron,
                "attempt_number": 5
            }

            resp = validate_attempt(data)
            print("Response:", resp)
           
            
        
        self.crearAutos(self.spawnClock)
       
        self.agents.shuffle_do("step")
    
