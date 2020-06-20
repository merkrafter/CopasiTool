from jinja2 import Template, Environment, FileSystemLoader

N_a = 6.0221408570000002e+23

class CopasiSpecies:
    def __init__(self, id, name, initial_concentration=0):
        self.id=id
        self.name=name
        self.compartment=0
        self.noise="false"
        self.simulation_type="reactions"
        self.initial_concentration=initial_concentration/100.0*N_a

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
    species.append(CopasiSpecies(3, "null"))
    species.append(CopasiSpecies(0, "X1", 17))
    species.append(CopasiSpecies(1, "X2", 7))
    species.append(CopasiSpecies(2, "Y"))
    species.append(CopasiSpecies(4, "Z"))
    
    with open("result.cps", "wb") as f:
        f.write(create_copasi_file_from_template("template.cps.jinja", species, []).encode("utf-8"))