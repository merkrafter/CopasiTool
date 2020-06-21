from jinja2 import Template, Environment, FileSystemLoader

N_a = 6.0221408570000002e+23

class CopasiSpecies:
    __counter = 0
    def __init__(self, name, initial_concentration=0):
        self.id=CopasiSpecies.__counter
        CopasiSpecies.__counter += 1
        self.name=name
        self.compartment=0
        self.noise="false"
        self.simulation_type="reactions"
        self.initial_concentration=initial_concentration/1000.0*N_a


class CopasiReaction:
    __counter = 0
    def __init__(self, name, substrates, products, k=0.1):
        self.id=CopasiReaction.__counter
        CopasiReaction.__counter += 1
        self.name=name
        self.substrates=substrates
        self.products=products
        self.k=k

class CopasiModel:

    def __init__(self, name):
        self.name = name
        self.species_list = []
        self.reactions = []
        # A functional reaction is a set of reactions that are tuned to represent a single higher order function as addition or division.
        self.num_functional_reactions = 0
        self.num_intermediate_species = 0
        # This null species is expected to exist by later functions.
        # It serves as a "bin", that is, other species that should decay in reality are converted to null in COPASI
        self.null = CopasiSpecies("null")
        self.add_species(self.null)
    
    def add_species(self, species):
        self.species_list.append(species)
    
    def add_reaction(self, reaction):
        self.reactions.append(reaction)

    def create_ADD_reactions(self, X1, X2, Y):
        """
        Creates reactions that represent the function: Y = X1 + X2
        Their naming scheme includes the type of function, an id, and descriptions of each reaction
        using the literals "X1", "X2", and "Y" instead of the species these variables stand for.
        This way it is easier to recognize their purpose in Copasi. For instance, if it just said
        "x25 -> x25 + intermediate2342" nobody would know what the purpose of that x25 is.
        """
        # TODO allow Y=None; return a tuple of created intermediate species as well
        name_prefix = "Add{}_".format(self.num_functional_reactions)
        self.num_functional_reactions += 1
        
        R1 = CopasiReaction(name_prefix+"X1toY", substrates=[(1,X1)], products=[(1,X1),(1,Y)])
        R2 = CopasiReaction(name_prefix+"X2toY", substrates=[(1,X2)], products=[(1,X2),(1,Y)])
        R3 = CopasiReaction(name_prefix+"Ydecay", substrates=[(1,Y)], products=[(1,self.null)])
        self.reactions += [R1, R2, R3]
        #self.species.append(Y)


def create_copasi_file_from_template(template_path, species, reactions):
    env = Environment(loader=FileSystemLoader(searchpath="./"), autoescape=True)
    template = env.get_template(template_path)
    return template.render(species_list=species, reactions=reactions)


if __name__ == "__main__":
    model = CopasiModel("New Model")
    
    X1 = CopasiSpecies("X1", 17); model.add_species(X1)
    X2 = CopasiSpecies("X2", 7); model.add_species(X2)
    Y = CopasiSpecies("Y"); model.add_species(Y)
    Z = CopasiSpecies("Z"); model.add_species(Z)
    
    model.create_ADD_reactions(X1, X2, Y)
    
    with open("result.cps", "wb") as f:
        f.write(create_copasi_file_from_template("template.cps.jinja", model.species_list, model.reactions).encode("utf-8"))