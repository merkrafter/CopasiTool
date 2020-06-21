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
    def __init__(self, id, name, substrates, products, k=0.1):
        self.id=id
        self.name=name
        self.substrates=substrates
        self.products=products
        self.k=k

def create_copasi_file_from_template(template_path, species, reactions):
    env = Environment(loader=FileSystemLoader(searchpath="./"), autoescape=True)
    template = env.get_template(template_path)
    return template.render(species_list=species, reactions=reactions)


if __name__ == "__main__":
    species = []
    X1 = CopasiSpecies("X1", 17); species.append(X1)
    X2 = CopasiSpecies("X2", 7); species.append(X2)
    Y = CopasiSpecies("Y"); species.append(Y)
    null = CopasiSpecies("null"); species.append(null)
    Z = CopasiSpecies("Z"); species.append(Z)
    
    reactions = []
    Ydecay = CopasiReaction(0, "Y decay", substrates=[(1, Y)], products=[(1,null)]); reactions.append(Ydecay)
    R1 = CopasiReaction(1, "R1", substrates=[(1,X1)], products=[(1,X1), (1,Y)]); reactions.append(R1)
    R2 = CopasiReaction(2, "R2", substrates=[(1,X2)], products=[(1,X2), (1,Z)]); reactions.append(R2)
    R3 = CopasiReaction(3, "R3", substrates=[(1,Y), (1,Z)], products=[(1,null)]); reactions.append(R3)
    
    with open("result.cps", "wb") as f:
        f.write(create_copasi_file_from_template("template.cps.jinja", species, reactions).encode("utf-8"))