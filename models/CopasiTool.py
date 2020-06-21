from jinja2 import Template, Environment, FileSystemLoader
from yaml import safe_load


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
        # This null species is expected to exist by later functions.
        # It serves as a "bin", that is, other species that should decay in reality are converted to null in COPASI
        self.null = CopasiSpecies("null")
        self.ensure_species(self.null)
    
    def ensure_species(self, species=None, **kwargs):
        """
        Ensures a certain species is known to this model.
        This can either be done by passing a species directly or by passing arguments to create one.
        If a species with the same name already exists in this model, nothing will be added.
        The species that is part of this model after this method invocation is returned in the end.
        """
        if species is None:
            species = CopasiSpecies(**kwargs)
            
        try:
            idx = list(map(lambda s: s.name, self.species_list)).index(species.name)
            return self.species_list[idx]
        except ValueError:
            self.species_list.append(species)
            return species
        
        
    
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

    def create_SUB_reactions(self, X1, X2, Y):
        """
        Returns reactions that represent the function: Y = X1 - X2 if X1 >= X2
        Their naming scheme includes the type of function, an id, and descriptions of each reaction
        using the literals "X1", "X2", and "Y" instead of the species these variables stand for.
        This way it is easier to recognize their purpose in Copasi. For instance, if it just said
        "x25 -> x25 + intermediate2342" nobody would know what the purpose of that x25 is.
        """
        name_prefix = "Sub{}_".format(self.num_functional_reactions)
        self.num_functional_reactions += 1
        
        Z = CopasiSpecies(name_prefix+"Z")
        self.ensure_species(Z)
        
        R1 = CopasiReaction(name_prefix+"X1toY", substrates=[(1,X1)], products=[(1,X1), (1,Y)])
        R2 = CopasiReaction(name_prefix+"X2toZ", substrates=[(1,X2)], products=[(1,X2), (1,Z)])
        R3 = CopasiReaction("YandZdecay", substrates=[(1,Y), (1,Z)], products=[(1,self.null)])
        R4 = CopasiReaction("Ydecay", substrates=[(1, Y)], products=[(1,self.null)])
        self.reactions += [R1, R2, R3, R4]

    def create_MUL_reactions(self, X1, X2, Y):
        """
        Creates reactions that represent the function: Y = X1 * X2
        Their naming scheme includes the type of function, an id, and descriptions of each reaction
        using the literals "X1", "X2", and "Y" instead of the species these variables stand for.
        This way it is easier to recognize their purpose in Copasi. For instance, if it just said
        "x25 -> x25 + intermediate2342" nobody would know what the purpose of that x25 is.
        """
        name_prefix = "Mul{}_".format(self.num_functional_reactions)
        self.num_functional_reactions += 1
        
        R1 = CopasiReaction(name_prefix+"X1andX2toY", substrates=[(1,X1),(1,X2)], products=[(1,X1),(1,X2),(1,Y)])
        R2 = CopasiReaction(name_prefix+"Ydecay", substrates=[(1,Y)], products=[(1,self.null)])
        self.reactions += [R1, R2]
        
    def create_DIV_reactions(self, X2, X1, Y):
        """
        Creates reactions that represent the function: Y = X2 / X1 (note the order of arguments)
        Their naming scheme includes the type of function, an id, and descriptions of each reaction
        using the literals "X1", "X2", and "Y" instead of the species these variables stand for.
        This way it is easier to recognize their purpose in Copasi. For instance, if it just said
        "x25 -> x25 + intermediate2342" nobody would know what the purpose of that x25 is.
        """
        name_prefix = "Div{}_".format(self.num_functional_reactions)
        self.num_functional_reactions += 1
        
        R1 = CopasiReaction(name_prefix+"X1andYtoX1", substrates=[(1,X1),(1,Y)], products=[(1,X1)])
        R2 = CopasiReaction(name_prefix+"X2toX2andY", substrates=[(1,X2)], products=[(1,X2),(1,Y)])
        self.reactions += [R1, R2]

    def create_SQRT_reactions(self, X, Y):
        """
        Creates reactions that represent the function: Y = sqrt(X)
        Their naming scheme includes the type of function, an id, and descriptions of each reaction
        using the literals "X", and "Y" instead of the species these variables stand for.
        This way it is easier to recognize their purpose in Copasi. For instance, if it just said
        "x25 -> x25 + intermediate2342" nobody would know what the purpose of that x25 is.
        """
        name_prefix = "Sqrt{}_".format(self.num_functional_reactions)
        self.num_functional_reactions += 1
        
        R1 = CopasiReaction(name_prefix+"XtoXandY", substrates=[(1,X)], products=[(1,X),(1,Y)], k=0.2)
        R2 = CopasiReaction(name_prefix+"2Ydecay", substrates=[(2,Y)], products=[(1,self.null)])
        self.reactions += [R1, R2]

    def create_reactions_from(self, line):
        """
        Reads a string and creates functional reactions from it.
        """
        try:
            Yname, _, func, X1name, X2name = line.split(" ")
            Y = self.ensure_species(name=Yname)
            X1 = self.ensure_species(name=X1name)
            X2 = self.ensure_species(name=X2name)
            
            func = func.lower()
            if func=="add":
                self.create_ADD_reactions(X1, X2, Y)
            elif func=="sub":
                self.create_SUB_reactions(X1, X2, Y)
            elif func=="mul":
                self.create_MUL_reactions(X1, X2, Y)
            elif func=="div":
                self.create_DIV_reactions(X1, X2, Y)
        except ValueError: # too many values to unpack
            # this has to be a sqrt
            Yname, _, func, Xname = line.split(" ")
            if func.lower()=="sqrt":
                self.create_SQRT_reactions(X, Y)

    def dump(self, destination, template_path="template.cps.jinja"):
        """
        Creates an xml file from this model that can be read and executed with Copasi
        """
        with open(destination, "wb") as f:  # binary mode for utf-8 encoding
            env = Environment(loader=FileSystemLoader(searchpath="./"), autoescape=True)
            template = env.get_template(template_path)
            f.write(template.render(model=self, species_list=self.species_list, reactions=self.reactions).encode("utf-8"))


def yaml2model(yaml_str):
    """
    Reads the given YAML string and returns a CopasiModel from it.
    """
    data = safe_load(yaml_str)
    model = CopasiModel(data["name"])
    
    for species_description in data["input"]:
        species = model.ensure_species(**species_description)
    
    for function_description in data["functions"]:
        model.create_reactions_from(function_description)
        
    return model

if __name__ == "__main__":
    with open("avg.yaml") as f:
        data = f.read()
    model = yaml2model(data)
    
    model.dump("result.cps")