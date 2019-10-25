from poligon.cells.elevator import Elevator
from poligon.cells.hatch import Hatch
from poligon.cells.hypnodisk import Hypnodisk
from poligon.cells.mine import Mine
from poligon.cells.tower import Tower
#from poligon.cells.fog import Fog

availableCells = {    # доступные испытания
    "Tower": Tower,
    "Elevator": Elevator,
    "Hatch": Hatch,
    "Hypnodisk": Hypnodisk,
    "Mine": Mine,
#    "Fog": Fog
}