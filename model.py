from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import SingleGrid
from mesa.visualization.UserParam import UserSettableParameter
import numpy as np
import random


model_params = {
    "n_adults": UserSettableParameter("number", "Adults (Max. 100)", 70, 0, 100, 1),
    "n_elderly": UserSettableParameter("number", "Elderly (Max. 100)", 70, 0, 100, 1),
    "n_children": UserSettableParameter("number", "Children (Max. 100)", 70, 0, 100, 1),
    "init_infected": UserSettableParameter(
        "number", "Initial Infected (Max. 400)", 5, 0, 400, 1
    ),
    "contact_aa": UserSettableParameter(
        "number", "Contact Rate (Adult-Adult)", 5, 0, 1, 1
    ),
    "contact_ac": UserSettableParameter(
        "number", "Contact Rate (Adult-Child)", 5, 0, 1, 1
    ),
    "contact_ae": UserSettableParameter(
        "number", "Contact Rate (Adult-Elder)", 5, 0, 1, 1
    ),
    "contact_cc": UserSettableParameter(
        "number", "Contact Rate (Child-Child)", 10, 0, 1, 1
    ),
    "contact_ce": UserSettableParameter(
        "number", "Contact Rate (Child-Elder)", 10, 0, 1, 1
    ),
    "contact_ca": UserSettableParameter(
        "number", "Contact Rate (Child-Adult)", 10, 0, 1, 1
    ),
    "contact_ee": UserSettableParameter(
        "number", "Contact Rate (Elder-Elder)", 1, 0, 1, 1
    ),
    "contact_ec": UserSettableParameter(
        "number", "Contact Rate (Elder-Child)", 1, 0, 1, 1
    ),
    "contact_ea": UserSettableParameter(
        "number", "Contact Rate (Elder-Adult)", 1, 0, 1, 1
    ),
    "transmission": UserSettableParameter(
        "slider", "Transmission Probability", 0.7, 0, 1, 0.05
    ),
    "infection_period": UserSettableParameter(
        "slider", "Infection Period", 25, 0, 100, 1
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
        self.contact_aa = self.model.contact_aa
        self.contact_ac = self.model.contact_ac
        self.contact_ae = self.model.contact_ae
        self.contact_cc = self.model.contact_cc
        self.contact_ce = self.model.contact_ce
        self.contact_ca = self.model.contact_ca
        self.contact_ee = self.model.contact_ee
        self.contact_ec = self.model.contact_ec
        self.contact_ea = self.model.contact_ea
        self.contact_matrix = {
            "adult": {
                "adult": self.model.contact_aa,
                "child": self.model.contact_ac,
                "elder": self.model.contact_ae,
            },
            "child": {
                "adult": self.model.contact_ca,
                "child": self.model.contact_cc,
                "elder": self.model.contact_ce,
            },
            "elder": {
                "adult": self.model.contact_ea,
                "child": self.model.contact_ec,
                "elder": self.model.contact_ee,
            },
        }
        self.transmission = self.model.transmission
        self.infected = False
        self.immune = False
        self.recovery_steps = 0
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
        if self.infected | self.immune | (self.type == "wall"):
            return None
        pos = tuple([int(self.pos[0]), int(self.pos[1])])
        # Checks if any of agents in the neighborhood with radius of 1 are infected
        neighbors = self.model.grid.get_neighbors(pos, moore=True, include_center=False)
        contact_rate = 0
        infection = False
        for a in neighbors:
            if a.infected:
                infection = True
                if self.contact_matrix[self.age][a.age] > contact_rate:
                    contact_rate = self.contact_matrix[self.age][a.age]

        # If any of the agents in the neighborhood are infected, the agent has a probability of getting infected
        if infection:
            for _ in range(contact_rate):
                if random.random() < self.transmission * contact_rate:
                    self.infected = True

        # Once infected, consider recovery based on infection period
        if self.infected:
            self.recovery_steps = self.model.infection_period

    def new_recovered(self):
        if self.recovery_steps == 1:
            self.infected = False
            self.immune = True
        if self.recovery_steps > 0:
            self.recovery_steps += -1

    def step(self):
        self.move()
        self.new_infected()
        self.new_recovered()


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
        contact_aa,
        contact_ac,
        contact_ae,
        contact_cc,
        contact_ce,
        contact_ca,
        contact_ee,
        contact_ec,
        contact_ea,
        transmission,
        infection_period,
    ):
        self.n_adults = n_adults
        self.n_elderly = n_elderly
        self.n_children = n_children
        self.n_agents = n_adults + n_elderly + n_children
        self.grid = SingleGrid(width, height, True)
        self.init_infected = init_infected
        self.contact_aa = contact_aa
        self.contact_ac = contact_ac
        self.contact_ae = contact_ae
        self.contact_cc = contact_cc
        self.contact_ce = contact_ce
        self.contact_ca = contact_ca
        self.contact_ee = contact_ee
        self.contact_ec = contact_ec
        self.contact_ea = contact_ea
        self.contact_matrix = {
            "adult": {
                "adult": self.contact_aa,
                "child": self.contact_ac,
                "elder": self.contact_ae,
            },
            "child": {
                "adult": self.contact_ca,
                "child": self.contact_cc,
                "elder": self.contact_ce,
            },
            "elder": {
                "adult": self.contact_ea,
                "child": self.contact_ec,
                "elder": self.contact_ee,
            },
        }
        self.transmission = transmission
        self.infection_period = infection_period
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
        elder_arr = np.array(["elder"] * self.n_elderly)
        child_arr = np.array(["child"] * self.n_children)

        # Concatentate age arrays
        age_arr = np.concatenate((adult_arr, elder_arr, child_arr))

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
                "Susceptible Adults": "susceptible_adults",
                "Susceptible Children": "susceptible_children",
                "Susceptible Elderly": "susceptible_elderly",
                "Infected Adults": "infected_adults",
                "Infected Children": "infected_children",
                "Infected Elderly": "infected_elderly",
                "Recovered Adults": "immune_adults",
                "Recovered Children": "immune_children",
                "Recovered Elderly": "immune_elderly",
            }
        )

    @property
    def susceptible_adults(self):
        agents = self.schedule.agents
        susceptible = [not (a.immune | a.infected) & (a.age == "adult") for a in agents]
        return int(np.sum(susceptible))

    @property
    def susceptible_children(self):
        agents = self.schedule.agents
        susceptible = [not (a.immune | a.infected) & (a.age == "child") for a in agents]
        return int(np.sum(susceptible))

    @property
    def susceptible_elderly(self):
        agents = self.schedule.agents
        susceptible = [not (a.immune | a.infected) & (a.age == "elder") for a in agents]
        return int(np.sum(susceptible))

    @property
    def infected_adults(self):
        agents = self.schedule.agents
        infected = [a.infected & (a.age == "adult") for a in agents]
        return int(np.sum(infected))

    @property
    def infected_children(self):
        agents = self.schedule.agents
        infected = [a.infected & (a.age == "child") for a in agents]
        return int(np.sum(infected))

    @property
    def infected_elderly(self):
        agents = self.schedule.agents
        infected = [a.infected & (a.age == "elder") for a in agents]
        return int(np.sum(infected))

    @property
    def immune_adults(self):
        agents = self.schedule.agents
        immune = [a.immune & (a.age == "adult") for a in agents]
        return int(np.sum(immune))

    @property
    def immune_children(self):
        agents = self.schedule.agents
        immune = [a.immune & (a.age == "child") for a in agents]
        return int(np.sum(immune))

    @property
    def immune_elderly(self):
        agents = self.schedule.agents
        immune = [a.immune & (a.age == "elder") for a in agents]
        return int(np.sum(immune))

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
