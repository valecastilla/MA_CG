from mesa.discrete_space import CellAgent, FixedAgent


class Traffic_Light(FixedAgent):
 
    def __init__(self, model, cell, state = False, timeToChange = 20):

        super().__init__(model)
       
        self.cell = cell
        self.state = state
        self.timeToChange = timeToChange

    def step(self):

        if self.model.steps % self.timeToChange == 0:
            self.state = not self.state

class Destination(FixedAgent):

    def __init__(self, model, cell):
       
        super().__init__(model)
        self.cell = cell
        self.esNodo= False
        self.idNodoInter= ""
    def idNodo(self,id):
       self.idNodoInter = id
    

class Obstacle(FixedAgent):

    def __init__(self, model, cell):
      
        super().__init__(model)
        self.cell = cell

class Tierra(FixedAgent):

    def __init__(self, model, cell):
       
        super().__init__(model)
        self.cell = cell

class Intersection(FixedAgent):

    def __init__(self, model, cell):
        self.isNodo=False
    
        super().__init__(model)
        self.cell = cell
        self.idNodoInter= ""
    def idNodo(self,id):
       self.idNodoInter = id
    

class Road(FixedAgent):
    def __init__(self, model, cell, direction= "Left"):
   
        super().__init__(model)
        self.cell = cell
        self.direction = direction
