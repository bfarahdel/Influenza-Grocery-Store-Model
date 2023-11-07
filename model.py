import math
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import SingleGrid
from mesa.visualization.UserParam import UserSettableParameter
import numpy as np
import random


model_params = {
    "n_adults": UserSettableParameter("number", "Adults (Max. 100)", 40, 0, 100, 1),
    "n_elderly": UserSettableParameter("number", "Elderly (Max. 100)", 40, 0, 100, 1),
    "n_children": UserSettableParameter("number", "Children (Max. 100)", 40, 0, 100, 1),
    "init_infected": UserSettableParameter(
        "number", "Initial Infected (Max. 400)", 1, 0, 400, 1
    ),
    "transmission": UserSettableParameter(
        "slider", "Transmission Probability", 0.75, 0, 1, 0.05
    ),
    "infection_period": UserSettableParameter(
        "slider", "Infection Period", 20, 0, 100, 1
    ),
    "immunity_period": UserSettableParameter(
        "slider", "Immunity Period", 100, 0, 100, 10
    ),
    "width": 50,
    "height": 50,
}


class Agent(Agent):
    """Agents in the SIR model"""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type = "agent"
        self.age = None
        self.transmission = self.model.transmission
        self.infected = False
        self.immune = False
        self.recovery_steps = 0
        self.immunity_steps = 0
        if self.infected:
            self.recovery_steps = self.model.infection_period

    def move(self):
        if self.type != "wall":
            # Move agent to a random cell in the radius of 1, if there is no empty cell, agent stays in place
            possible_steps = self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=False
            )
            new_x, new_y = self.random.choice(possible_steps)
            while self.model.grid.is_cell_empty((new_x, new_y)) == False:
                new_x, new_y = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, (new_x, new_y))

    def new_infected(self):
        # Infected or immune agents cannot become infected
        if self.infected | self.immune:
            return None
        pos = tuple([int(self.pos[0]), int(self.pos[1])])
        # Checks if any of agents in the neighborhood with radius of 1 are infected
        neighbors = self.model.grid.get_neighbors(pos, moore=True, include_center=False)
        infected_neighbors = [a.infected for a in neighbors]
        # If any of the agents in the neighborhood are infected, the agent has a probability of getting infected
        if True in infected_neighbors:
            if random.random() < self.transmission:
                self.infected = True

        # Once infected, consider recovery
        if self.infected:
            self.recovery_steps = self.model.infection_period

    def new_recovered(self):
        if self.recovery_steps == 1:
            self.infected = False
            self.immune = True
            # Following recovery, consider immunity period
            self.immunity_steps = self.model.immunity_period
        if self.recovery_steps > 0:
            self.recovery_steps += -1

    def new_susceptible(self):
        # Following immunity, agent becomes susceptible
        if self.immunity_steps == 1:
            self.immune = False
        if self.immunity_steps > 0:
            self.immunity_steps = self.immunity_steps - 1

    def step(self):
        self.move()
        self.new_infected()
        self.new_recovered()
        self.new_susceptible()


class Wall(Agent):
    def __init__(self, pos, model, agent_type):
        super().__init__(pos, model)
        self.pos = pos
        self.type = agent_type


class SIR(Model):
    """An SIR (Susceptible, Infected, Removed) Agent-based model"""

    def __init__(
        self,
        n_adults,
        n_elderly,
        n_children,
        width,
        height,
        init_infected,
        transmission,
        infection_period,
        immunity_period,
    ):
        self.n_adults = n_adults
        self.n_elderly = n_elderly
        self.n_children = n_children
        self.n_agents = n_adults + n_elderly + n_children
        self.grid = SingleGrid(width, height, True)
        self.init_infected = init_infected
        self.transmission = transmission
        self.infection_period = infection_period
        self.immunity_period = immunity_period
        self.schedule = RandomActivation(self)
        self.running = True

        # 4 walls that run from (10,10) to (10,40), (20, 10) to (20,40), (30, 10) to (30,40), (40, 10) to (40,40)
        walls = (
            [(10, y) for y in range(10, 41)]
            + [(20, y) for y in range(10, 41)]
            + [(30, y) for y in range(10, 41)]
            + [(40, y) for y in range(10, 41)]
        )

        for pos in walls:
            agent_type = "wall"
            agent = Wall(pos, self, agent_type)
            self.grid.position_agent(agent, pos[0], pos[1])
            self.schedule.add(agent)

        ###############
        # Create agents
        ###############
        # Boolean array to represent if an agent is initially infected or not
        infected_arr = np.array(
            [True] * self.init_infected + [False] * (self.n_agents - self.init_infected)
        )
        # Array of age groups
        adult_arr = np.array(["adult"] * self.n_adults)
        elderly_arr = np.array(["elderly"] * self.n_elderly)
        children_arr = np.array(["children"] * self.n_children)

        # Concatentate age arrays
        age_arr = np.concatenate((adult_arr, elderly_arr, children_arr))

        # Shuffle arrays to randomize the initial agents
        np.random.shuffle(infected_arr)
        np.random.shuffle(age_arr)

        for i in range(self.n_agents):
            a = Agent(i, self)
            self.schedule.add(a)
            a.infected = infected_arr[i]
            a.age = age_arr[i]

            # Place agent on a random cell that is not occupied
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            while self.grid.is_cell_empty((x, y)) == False:
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        self.datacollector = DataCollector(
            {
                "Susceptible": "susceptible",
                "Infected": "infected",
                "Recovered": "immune",
            }
        )

    @property
    def susceptible(self):
        agents = self.schedule.agents
        susceptible = [not (a.immune | a.infected) for a in agents if a.type != "wall"]
        return int(np.sum(susceptible))

    @property
    def infected(self):
        agents = self.schedule.agents
        infected = [a.infected for a in agents if a.type != "wall"]
        return int(np.sum(infected))

    @property
    def immune(self):
        agents = self.schedule.agents
        immune = [a.immune for a in agents if a.type != "wall"]
        return int(np.sum(immune))

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
