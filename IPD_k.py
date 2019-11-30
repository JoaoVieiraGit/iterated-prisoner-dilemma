from __future__ import division
import pyafai
import numpy as np
import simcx


class Agent(pyafai.Agent):
    def __init__(self, x, y, n=50):
        super(Agent, self).__init__()

        self.x = x
        self.y = y

        self.points = np.array([[3, 0], [5, 1]])

        self.value = 0
        self.point_counter = 0

        self.body = pyafai.Object(x, y)

    def update(self, delta):
        pass

    def _think(self, delta):
        if self.cur_step > self.k:
            self.value = 1
        self.cur_step += 1
        if self.value == 1:
            self.body.set_colour((255,0,0))

    def cooperate(self):
        pass


class Rect(Agent):
    def __init__(self, x, y, colour, size=20):
        super(Rect, self).__init__(x, y,10)

        shape = pyafai.shapes.Rect(size, size/2, color=('c3B', colour))
        self.body.add_shape(shape)


class Circle(Agent):
    def __init__(self, x, y, colour, size=20):
        super(Circle, self).__init__(x, y, 10)

        shape = pyafai.shapes.Circle(size/2, 0, color=('c3B', colour))
        self.body.add_shape(shape)


class Square(Agent):
    def __init__(self, x, y, colour, size=20, n=100):
        self.k = np.random.randint(0, int(n))
        self.cur_step = 0
        self.size = size
        self.x = x
        self.y = y
        self.colour = colour
        self.value = 0
        self.n = n

        super(Square, self).__init__(x, y, 10)

        shape = pyafai.shapes.Rect(size, size, color=('c3B', colour))
        self.body.add_shape(shape)

        self.add_perception(Player_Neighbours())
        self._players = self._perceptions['player_neighbours']

    def update(self, delta):
        self.cur_step+=1
        self._players.update(self)
        if self.cur_step > self.k:
            self.value = 1
            shape = pyafai.shapes.Rect(self.size, self.size, color=('c3B', (255,0,0)))
            self.body.add_shape(shape)
        if self.cur_step == self.n and 0 < self.x < 19 and 0 < self.y < 19:
            print(self.k, self._players.print_total())

    def set_colour(self, colour):
        print("updating square")
        self.colour = colour

    def defect(self):
        self.value = 1
        shape = pyafai.shapes.Rect(self.size, self.size, color=('c3B', (255,0,0)))
        self.body.add_shape(shape)



class Triangle(Agent):
    def __init__(self, x, y, colour, size=20):
        super(Triangle, self).__init__(x, y, 10)

        shape = pyafai.shapes.Triangle(-size/2, -size/2, size/2, -size/2, 0, size/2, color=('c3B', colour))
        self.body.add_shape(shape)


class Player_Neighbours(pyafai.Perception):
    def __init__(self):
        self.total = 0
        self.points = np.array([[3, 0], [5, 1]])

        super(Player_Neighbours, self).__init__(float, 'player_neighbours')

    def update(self, agent):
        neighbours = agent.world.get_neighbours(agent.body.x, agent.body.y)
        count = 0
        for obj in neighbours:
            self.total+=self.points[int(agent.value)][int(obj.agent.value)]
            if obj.agent.value == 1:
                count += 1
                if count > 3:
                    agent.defect()

    def print_total(self):
        return self.total


class PolygonWorld(pyafai.World2DGrid):
    def __init__(self, width, height, cell, n=100):
        self.width = width
        self.height = height
        self.time_over = n
        self.cur_step = 0
        super(PolygonWorld, self).__init__(width, height, cell, n)

        types = (Square, Triangle, Circle, Rect)
        n = len(types)

        for y in range(height):
            for x in range(width):
                agent = types[0](x, y, [0, 255, 0], size=cell * 0.6)
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

