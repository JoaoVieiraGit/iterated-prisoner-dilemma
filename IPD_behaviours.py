from __future__ import division
import pyafai
import numpy as np
import simcx


class Agent(pyafai.Agent):
    def __init__(self, x, y, n=50):
        super(Agent, self).__init__()

        self.x = x
        self.y = y

        self.value = 0
        self.point_counter = 0

        self.body = pyafai.Object(x, y)


class Player_Neighbours(pyafai.Perception):
    def __init__(self):
        self.total = 0
        self.points = np.array([[3, 0], [5, 1]])
        self.temp_count=0

        self.to_defect_next = 0
        self.action_in_two = np.array([0,0])
        self.has_checked = 0

        super(Player_Neighbours, self).__init__(float, 'player_neighbours')

    def update(self, agent):

        if self.has_checked == 0:
            neighbours = agent.world.get_neighbours(agent.body.x, agent.body.y)

            if agent.type == 0:
                count = 0
                for obj in neighbours:
                    self.total+=self.points[int(agent.value)][int(obj.agent.value)]
                    if obj.agent.value == 1:
                        count += 1
                if count > 2:
                    self.to_defect_next = 1
                else:
                    self.to_defect_next = 0

            elif agent.type == 1:
                self.temp_count+=1
                count = 0

                for obj in neighbours:
                    self.total+=self.points[int(agent.value)][int(obj.agent.value)]
                    if self.points[int(agent.value)][int(obj.agent.value)] > 2:
                        count+=1
                if self.temp_count > 1:
                    if count < 4:
                        if agent.value == 1:
                            self.to_defect_next = 0
                        else:
                            self.to_defect_next = 1

            elif agent.type == 2:
                for obj in neighbours:
                    self.total+=self.points[int(agent.value)][int(obj.agent.value)]
                i = np.random.randint(2)
                if i == 0:
                    self.to_defect_next = 0
                if i == 1:
                    self.to_defect_next = 1

            elif agent.type == 3:
                count = 0
                for obj in neighbours:
                    self.total+=self.points[int(agent.value)][int(obj.agent.value)]
                    if obj.agent.value == 1:
                        count += 1
                if count > 2:
                    self.to_defect_next = 0
                else:
                    self.to_defect_next = 1

            self.has_checked = 1

        else:
            if self.to_defect_next == 1:
                agent.defect()
            else:
                agent.cooperate()
            self.has_checked = 0


    def print_total(self):
        return self.total


class Polygon(Agent):
    def __init__(self, x, y, colour, type, size=20, n=100):

        self.type = type

        self.cur_step = 0
        self.size = size
        self.x = x
        self.y = y
        self.colour = colour
        self.value = 0
        self.n = n

        super(Polygon, self).__init__(x, y, 10)

        self.add_perception(Player_Neighbours())
        self._players = self._perceptions['player_neighbours']

        if self.type == 0:
            shape = pyafai.shapes.Rect(size, size, color=('c3B', colour))
            self.body.add_shape(shape)
        elif self.type == 1:
            shape = pyafai.shapes.Triangle(-size/2, -size/2, size/2, -size/2, 0, size/2, color=('c3B', (0,255,0)))
            self.body.add_shape(shape)
        elif self.type == 2:
            shape = pyafai.shapes.Circle(size/2, 0, color=('c3B', colour))
            self.body.add_shape(shape)
        elif self.type == 3:
            self.value = 1
            shape = pyafai.shapes.Rect(size, size/2, color=('c3B', (255,0,0)))
            self.body.add_shape(shape)


    def update(self, delta):
        self.cur_step+=1
        self._players.update(self)
        if self.cur_step == self.n and 0 < self.x < 19 and 0 < self.y < 19:
            print(self.type, self._players.print_total())

    def defect(self):
        self.value = 1
        if self.type == 0:
            shape = pyafai.shapes.Rect(self.size, self.size, color=('c3B', (255,0,0)))
            self.body.add_shape(shape)
        elif self.type == 1:
            shape = pyafai.shapes.Triangle(-self.size/2, -self.size/2, self.size/2, -self.size/2, 0, self.size/2, color=('c3B', (255,0,0)))
            self.body.add_shape(shape)
        elif self.type == 2:
            shape = pyafai.shapes.Circle(self.size/2, 0, color=('c3B', (255,0,0)))
            self.body.add_shape(shape)
        elif self.type == 3:
            shape = pyafai.shapes.Rect(self.size, self.size/2, color=('c3B', (255,0,0)))
            self.body.add_shape(shape)

    def cooperate(self):
        self.value = 0
        if self.type == 0:
            shape = pyafai.shapes.Rect(self.size, self.size, color=('c3B', (0,255,0)))
            self.body.add_shape(shape)
        elif self.type == 1:
            shape = pyafai.shapes.Triangle(-self.size/2, -self.size/2, self.size/2, -self.size/2, 0, self.size/2, color=('c3B', (0,255,0)))
            self.body.add_shape(shape)
        elif self.type == 2:
            shape = pyafai.shapes.Circle(self.size/2, 0, color=('c3B', (0,255,0)))
            self.body.add_shape(shape)
        elif self.type == 3:
            shape = pyafai.shapes.Rect(self.size, self.size/2, color=('c3B', (0,255,0)))
            self.body.add_shape(shape)


class PolygonWorld(pyafai.World2DGrid):
    def __init__(self, width, height, cell, n=50):
        self.width = width
        self.height = height
        self.time_over = n
        self.cur_step = 0
        super(PolygonWorld, self).__init__(width, height, cell, n)

        for y in range(height):
            for x in range(width):
                i = np.random.choice(int(4))
                agent = Polygon(x, y, [0, 255, 0], i, size=int(cell * 0.6))
                self.add_agent(agent)
                agent._update_perceptions()

    def add_agent(self, agent):
        super(PolygonWorld, self).add_agent(agent)

    def update(self, delta):
        self.cur_step+=1
        if self.cur_step < self.time_over:
            super(PolygonWorld, self).update(delta)
        else:
            quit()



def setup():
    world = PolygonWorld(20, 20, 30, 200)
    sim = simcx.PyafaiSimulator(world)
    vis = simcx.PyafaiVisual(sim)
    display = simcx.Display()

    display.add_simulator(sim)
    display.add_visual(vis, 0, 0)

if __name__ == '__main__':
    setup()
    simcx.run()

