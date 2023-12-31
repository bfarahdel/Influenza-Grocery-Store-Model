from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import SingleGrid
from mesa.visualization.UserParam import UserSettableParameter
import numpy as np
import random


model_params = {
    "n_adults": UserSettableParameter("slider", "Adults", 28, 0, 100, 1),
    "n_children": UserSettableParameter("slider", "Children", 28, 0, 100, 1),
    "n_elderly": UserSettableParameter("slider", "Elderly", 28, 0, 100, 1),
    "n_pregnant": UserSettableParameter("slider", "Pregnant", 28, 0, 100, 1),
    "infect_adults": UserSettableParameter(
        "number", "Initial Infected Adults", 7, 0, 100, 1
    ),
    "infect_children": UserSettableParameter(
        "number", "Initial Infected Children", 7, 0, 100, 1
    ),
    "infect_elderly": UserSettableParameter(
        "number", "Initial Infected Elderly", 7, 0, 100, 1
    ),
    "infect_pregnant": UserSettableParameter(
        "number", "Initial Infected Pregnant", 7, 0, 100, 1
    ),
    "infection_period": UserSettableParameter(
        "slider", "Infection Period", 20, 0, 100, 1
    ),
    "v_adults": UserSettableParameter("number", "Vaccinated Adults", 0, 0, 100, 1),
    "v_children": UserSettableParameter("number", "Vaccinated Children", 0, 0, 100, 1),
    "v_elderly": UserSettableParameter("number", "Vaccinated Elderly", 0, 0, 100, 1),
    "v_pregnant": UserSettableParameter("number", "Vaccinated Pregnant", 0, 0, 100, 1),
    "fatal_adults": UserSettableParameter(
        "number", "Fatality Risk in Adults (%)", 0.02, 0, 100, 0.1
    ),
    "fatal_children": UserSettableParameter(
        "number", "Fatality Risk in Children (%)", 0.002, 0, 100, 0.1
    ),
    "fatal_elderly": UserSettableParameter(
        "number", "Fatality Risk in Elderly (%)", 0.009, 0, 100, 0.1
    ),
    "fatal_pregnant": UserSettableParameter(
        "number", "Fatality Risk in Pregnant (%)", 6, 0, 100, 0.1
    ),
    "transmission": UserSettableParameter(
        "number", "Transmission Probability", 0.03, 0, 1, 0.01
    ),
    "contact_aa": UserSettableParameter(
        "number", "Contact Rate (Adult-Adult)", 10, 0, 100, 1
    ),
    "contact_ac": UserSettableParameter(
        "number", "Contact Rate (Adult-Child)", 3, 0, 100, 1
    ),
    "contact_ae": UserSettableParameter(
        "number", "Contact Rate (Adult-Elder)", 1, 0, 100, 1
    ),
    "contact_cc": UserSettableParameter(
        "number", "Contact Rate (Child-Child)", 6, 0, 100, 1
    ),
    "contact_ce": UserSettableParameter(
        "number", "Contact Rate (Child-Elder)", 1, 0, 100, 1
    ),
    "contact_ca": UserSettableParameter(
        "number", "Contact Rate (Child-Adult)", 6, 0, 100, 1
    ),
    "contact_ee": UserSettableParameter(
        "number", "Contact Rate (Elder-Elder)", 2, 0, 100, 1
    ),
    "contact_ec": UserSettableParameter(
        "number", "Contact Rate (Elder-Child)", 1, 0, 100, 1
    ),
    "contact_ea": UserSettableParameter(
        "number", "Contact Rate (Elder-Adult)", 5, 0, 100, 1
    ),
    "width": 50,
    "height": 50,
}


class Agent(Agent):
    """Agents in the SIR model"""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type = "agent"
        self.strata = None
        self.contact_aa = self.model.contact_aa
        self.contact_ac = self.model.contact_ac
        self.contact_ae = self.model.contact_ae
        self.contact_cc = self.model.contact_cc
        self.contact_ce = self.model.contact_ce
        self.contact_ca = self.model.contact_ca
        self.contact_ee = self.model.contact_ee
        self.contact_ec = self.model.contact_ec
        self.contact_ea = self.model.contact_ea
        self.contact_matrix = self.model.contact_matrix
        self.transmission = self.model.transmission
        self.infected = False
        self.recovered = False
        self.dead = False
        if self.infected:
            self.recovery_steps = self.model.infection_period
        else:
            self.recovery_steps = 0
        self.fatality = self.model.fatality

    def move(self):
        if self.type != "wall":
            if not self.dead:
                # Move agent to a random cell in the radius of 1, if there is no empty cell, agent stays in place
                possible_steps = self.model.grid.get_neighborhood(
                    self.pos, moore=True, include_center=False
                )
                new_x, new_y = self.random.choice(possible_steps)
                while self.model.grid.is_cell_empty((new_x, new_y)) == False:
                    new_x, new_y = self.random.choice(possible_steps)
                self.model.grid.move_agent(self, (new_x, new_y))

    def new_infected(self):
        # Fatality rate
        if self.infected:
            if self.strata == "adult":
                if self.fatality == None:
                    self.fatality = random.random() < self.model.fatal_adults / 100
                elif self.fatality == True:
                    self.dead = True
                    self.infected = False
                    self.recovery_steps = 0
                    self.model.grid.remove_agent(self)
                else:
                    self.fatality = False
            if self.strata == "child":
                if self.fatality == None:
                    self.fatality = random.random() < self.model.fatal_children / 100
                elif self.fatality == True:
                    self.dead = True
                    self.infected = False
                    self.recovery_steps = 0
                    self.model.grid.remove_agent(self)
                else:
                    self.fatality = False
            if self.strata == "elder":
                if self.fatality == None:
                    self.fatality = random.random() < self.model.fatal_elderly / 100
                elif self.fatality == True:
                    self.dead = True
                    self.infected = False
                    self.recovery_steps = 0
                    self.model.grid.remove_agent(self)
                else:
                    self.fatality = False
            if self.strata == "pregnant":
                if self.fatality == None:
                    self.fatality = random.random() < self.model.fatal_pregnant / 100
                elif self.fatality == True:
                    self.dead = True
                    self.infected = False
                    self.recovery_steps = 0
                    self.model.grid.remove_agent(self)
                else:
                    self.fatality = False

        # Cases when the agent cannot be infected
        if self.infected | self.recovered | self.dead | (self.type == "wall"):
            return None
        pos = tuple([int(self.pos[0]), int(self.pos[1])])
        # Checks if any of agents in the neighborhood with radius of 1 are infected
        neighbors = self.model.grid.get_neighbors(pos, moore=True, include_center=False)
        contact_rate = 0
        infection = False
        for a in neighbors:
            if a.infected:
                infection = True
                if self.contact_matrix[self.strata][a.strata] > contact_rate:
                    contact_rate = self.contact_matrix[self.strata][a.strata]

        # If any of the agents in the neighborhood are infected, the agent has a probability of getting infected
        if infection:
            if random.random() < self.transmission * contact_rate:
                self.infected = True
                self.recovery_steps = self.model.infection_period

    def new_recovered(self):
        if self.type != "wall":
            if self.recovery_steps == 1:
                self.infected = False
                self.recovered = True
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
    """
    This is an age-structured SIR (Susceptible, Infected, Removed) Agent-based model of influenza A/H1N1 in an artificial Grocery Store.
    First, set the parameters on the left panel. If any of the parameters were changed, click the "Reset" button. Otherwise, click the "Start" button.
    """

    def __init__(
        self,
        n_adults,
        n_elderly,
        n_children,
        n_pregnant,
        infection_period,
        transmission,
        v_adults,
        v_elderly,
        v_children,
        v_pregnant,
        infect_adults,
        infect_children,
        infect_elderly,
        infect_pregnant,
        fatal_adults,
        fatal_children,
        fatal_elderly,
        fatal_pregnant,
        contact_aa,
        contact_ac,
        contact_ae,
        contact_cc,
        contact_ce,
        contact_ca,
        contact_ee,
        contact_ec,
        contact_ea,
        width,
        height,
    ):
        self.n_adults = n_adults
        self.n_elderly = n_elderly
        self.n_children = n_children
        self.n_pregnant = n_pregnant
        self.n_agents = n_adults + n_elderly + n_children + n_pregnant
        self.v_adults = v_adults
        self.v_elderly = v_elderly
        self.v_children = v_children
        self.v_pregnant = v_pregnant
        self.grid = SingleGrid(width, height, True)
        self.infect_adults = infect_adults
        self.infect_children = infect_children
        self.infect_elderly = infect_elderly
        self.infect_pregnant = infect_pregnant
        self.fatal_adults = fatal_adults
        self.fatal_children = fatal_children
        self.fatal_elderly = fatal_elderly
        self.fatal_pregnant = fatal_pregnant
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
                "pregnant": self.contact_aa,
            },
            "child": {
                "adult": self.contact_ca,
                "child": self.contact_cc,
                "elder": self.contact_ce,
                "pregnant": self.contact_ca,
            },
            "elder": {
                "adult": self.contact_ea,
                "child": self.contact_ec,
                "elder": self.contact_ee,
                "pregnant": self.contact_ea,
            },
            "pregnant": {
                "adult": self.contact_aa,
                "child": self.contact_ac,
                "elder": self.contact_ae,
                "pregnant": self.contact_aa,
            },
        }
        self.infection_period = infection_period
        self.transmission = transmission
        self.fatality = None
        self.schedule = RandomActivation(self)
        self.running = True

        # Create aisles
        walls = (
            [(10, y) for y in range(10, 23)]
            + [(10, y) for y in range(28, 41)]
            + [(20, y) for y in range(10, 23)]
            + [(20, y) for y in range(28, 41)]
            + [(30, y) for y in range(10, 23)]
            + [(30, y) for y in range(28, 41)]
            + [(40, y) for y in range(10, 23)]
            + [(40, y) for y in range(28, 41)]
        )

        for pos in walls:
            agent_type = "wall"
            agent = Wall(pos, self, agent_type)
            self.grid.position_agent(agent, pos[0], pos[1])
            self.schedule.add(agent)

        ###############
        # Create agents
        ###############
        # Array of population strata
        adult_arr = np.array(["adult"] * self.n_adults)
        elder_arr = np.array(["elder"] * self.n_elderly)
        child_arr = np.array(["child"] * self.n_children)
        pregnant_arr = np.array(["pregnant"] * self.n_pregnant)

        # Concatentate strata arrays
        strata_arr = np.concatenate((adult_arr, elder_arr, child_arr, pregnant_arr))

        # Boolean array to represent if an agent is initially vaccinated or not where infected_arr is False
        vaccinated_adults = np.array(
            [True] * self.v_adults + [False] * (self.n_adults - self.v_adults)
        )
        vaccinated_elderly = np.array(
            [True] * self.v_elderly + [False] * (self.n_elderly - self.v_elderly)
        )
        vaccinated_children = np.array(
            [True] * self.v_children + [False] * (self.n_children - self.v_children)
        )
        vaccinated_pregnant = np.array(
            [True] * self.v_pregnant + [False] * (self.n_pregnant - self.v_pregnant)
        )

        # Randomize initially vaccinated agents
        np.random.shuffle(vaccinated_adults)
        np.random.shuffle(vaccinated_elderly)
        np.random.shuffle(vaccinated_children)
        np.random.shuffle(vaccinated_pregnant)

        # Concatenate vaccinated arrays in the same order as age array
        vaccinated_arr = np.concatenate(
            (
                vaccinated_adults,
                vaccinated_elderly,
                vaccinated_children,
                vaccinated_pregnant,
            )
        )

        # Initially infect each strata
        unvaccinated_adults = np.where(vaccinated_adults == False)[0]
        unvaccinated_elderly = np.where(vaccinated_elderly == False)[0]
        unvaccinated_children = np.where(vaccinated_children == False)[0]
        unvaccinated_pregnant = np.where(vaccinated_pregnant == False)[0]

        # Randomly infect agents
        init_inf_adults = np.random.choice(
            unvaccinated_adults, size=self.infect_adults, replace=False
        )
        init_inf_elderly = np.random.choice(
            unvaccinated_elderly, size=self.infect_elderly, replace=False
        )
        init_inf_children = np.random.choice(
            unvaccinated_children, size=self.infect_children, replace=False
        )
        init_inf_pregnant = np.random.choice(
            unvaccinated_pregnant, size=self.infect_pregnant, replace=False
        )

        # Boolean arrays to represent if an agent is initially infected or not
        infected_adults_arr = np.array([False] * self.n_adults)
        infected_elderly_arr = np.array([False] * self.n_elderly)
        infected_children_arr = np.array([False] * self.n_children)
        infected_pregnant_arr = np.array([False] * self.n_pregnant)

        # Set infected agents to True
        infected_adults_arr[init_inf_adults] = True
        infected_elderly_arr[init_inf_elderly] = True
        infected_children_arr[init_inf_children] = True
        infected_pregnant_arr[init_inf_pregnant] = True

        # Concatenate infected arrays in the same order as age array
        infected_arr = np.concatenate(
            (
                infected_adults_arr,
                infected_elderly_arr,
                infected_children_arr,
                infected_pregnant_arr,
            )
        )

        for i in range(self.n_agents):
            a = Agent(i, self)
            self.schedule.add(a)
            a.infected = infected_arr[i]
            if a.infected:
                a.recovery_steps = self.infection_period
            a.strata = strata_arr[i]
            a.recovered = vaccinated_arr[i]

            # Place agent on a random cell that is not occupied
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            while self.grid.is_cell_empty((x, y)) == False:
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        self.datacollector = DataCollector(
            {
                "Total Susceptible": "total_susceptible",
                "Total Infected": "total_infected",
                "Total Recovered": "total_recovered",
                "Total Dead": "total_dead",
                "Susceptible Adults": "susceptible_adults",
                "Susceptible Children": "susceptible_children",
                "Susceptible Elderly": "susceptible_elderly",
                "Infected Adults": "infected_adults",
                "Infected Children": "infected_children",
                "Infected Elderly": "infected_elderly",
                "Recovered Adults": "recovered_adults",
                "Recovered Children": "recovered_children",
                "Recovered Elderly": "recovered_elderly",
                "Susceptible Pregnant": "susceptible_pregnant",
                "Infected Pregnant": "infected_pregnant",
                "Recovered Pregnant": "recovered_pregnant",
                "Dead Adults": "dead_adults",
                "Dead Children": "dead_children",
                "Dead Elderly": "dead_elderly",
                "Dead Pregnant": "dead_pregnant",
            }
        )

    @property
    def susceptible_adults(self):
        agents = self.schedule.agents
        susceptible = []
        for a in agents:
            if a.strata == "adult":
                # If other strata has a population of 0
                if a.recovered == 1.0:
                    a.recovered = True
                else:
                    a.recovered = False
                if a.infected == 1.0:
                    a.infected = True
                else:
                    a.infected = False
                if a.dead == 1.0:
                    a.dead = True
                else:
                    a.dead = False
                # If agent is not recovered, infected, or a wall
                if not (a.recovered | a.infected | a.dead | (a.type == "wall")):
                    susceptible.append(True)
        return int(np.sum(susceptible))

    @property
    def susceptible_children(self):
        agents = self.schedule.agents
        susceptible = []
        for a in agents:
            if a.strata == "child":
                # If other strata has a population of 0
                if a.recovered == 1.0:
                    a.recovered = True
                else:
                    a.recovered = False
                if a.infected == 1.0:
                    a.infected = True
                else:
                    a.infected = False
                if a.dead == 1.0:
                    a.dead = True
                else:
                    a.dead = False
                # If agent is not recovered, infected, or a wall
                if not (a.recovered | a.infected | a.dead | (a.type == "wall")):
                    susceptible.append(True)
        return int(np.sum(susceptible))

    @property
    def susceptible_elderly(self):
        agents = self.schedule.agents
        susceptible = []
        for a in agents:
            if a.strata == "elder":
                # If other strata has a population of 0
                if a.recovered == 1.0:
                    a.recovered = True
                else:
                    a.recovered = False
                if a.infected == 1.0:
                    a.infected = True
                else:
                    a.infected = False
                if a.dead == 1.0:
                    a.dead = True
                else:
                    a.dead = False
                # If agent is not recovered, infected, or a wall
                if not (a.recovered | a.infected | a.dead | (a.type == "wall")):
                    susceptible.append(True)
        return int(np.sum(susceptible))

    @property
    def susceptible_pregnant(self):
        agents = self.schedule.agents
        susceptible = []
        for a in agents:
            if a.strata == "pregnant":
                # If other strata has a population of 0
                if a.recovered == 1.0:
                    a.recovered = True
                else:
                    a.recovered = False
                if a.infected == 1.0:
                    a.infected = True
                else:
                    a.infected = False
                if a.dead == 1.0:
                    a.dead = True
                else:
                    a.dead = False
                # If agent is not recovered, infected, or a wall
                if not (a.recovered | a.infected | a.dead | (a.type == "wall")):
                    susceptible.append(True)
        return int(np.sum(susceptible))

    @property
    def infected_adults(self):
        agents = self.schedule.agents
        infected = [a.infected & (a.strata == "adult") for a in agents]
        return int(np.sum(infected))

    @property
    def infected_children(self):
        agents = self.schedule.agents
        infected = [a.infected & (a.strata == "child") for a in agents]
        return int(np.sum(infected))

    @property
    def infected_elderly(self):
        agents = self.schedule.agents
        infected = [a.infected & (a.strata == "elder") for a in agents]
        return int(np.sum(infected))

    @property
    def infected_pregnant(self):
        agents = self.schedule.agents
        infected = [a.infected & (a.strata == "pregnant") for a in agents]
        return int(np.sum(infected))

    @property
    def recovered_adults(self):
        agents = self.schedule.agents
        recovered = [a.recovered & (a.strata == "adult") for a in agents]
        return int(np.sum(recovered))

    @property
    def recovered_children(self):
        agents = self.schedule.agents
        recovered = [a.recovered & (a.strata == "child") for a in agents]
        return int(np.sum(recovered))

    @property
    def recovered_elderly(self):
        agents = self.schedule.agents
        recovered = [a.recovered & (a.strata == "elder") for a in agents]
        return int(np.sum(recovered))

    @property
    def recovered_pregnant(self):
        agents = self.schedule.agents
        recovered = [a.recovered & (a.strata == "pregnant") for a in agents]
        return int(np.sum(recovered))

    @property
    def dead_adults(self):
        agents = self.schedule.agents
        dead = [a.dead & (a.strata == "adult") for a in agents]
        return int(np.sum(dead))

    @property
    def dead_children(self):
        agents = self.schedule.agents
        dead = [a.dead & (a.strata == "child") for a in agents]
        return int(np.sum(dead))

    @property
    def dead_elderly(self):
        agents = self.schedule.agents
        dead = [a.dead & (a.strata == "elder") for a in agents]
        return int(np.sum(dead))

    @property
    def dead_pregnant(self):
        agents = self.schedule.agents
        dead = [a.dead & (a.strata == "pregnant") for a in agents]
        return int(np.sum(dead))

    @property
    def total_susceptible(self):
        return (
            self.susceptible_adults
            + self.susceptible_children
            + self.susceptible_elderly
            + self.susceptible_pregnant
        )

    @property
    def total_infected(self):
        return (
            self.infected_adults
            + self.infected_children
            + self.infected_elderly
            + self.infected_pregnant
        )

    @property
    def total_recovered(self):
        return (
            self.recovered_adults
            + self.recovered_children
            + self.recovered_elderly
            + self.recovered_pregnant
        )

    @property
    def total_dead(self):
        return (
            self.dead_adults
            + self.dead_children
            + self.dead_elderly
            + self.dead_pregnant
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
