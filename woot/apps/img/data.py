# apps.img.data

'''
Specific experiment and series information in the form of lists of prototype objects
'''
import os

### Classes
class Region():
  def __init__(self, name, index, description):
    self.index = index
    self.name = name
    self.description = description

class Experiment():
  def __init__(self, name, rmop, cmop, zmop, tpf):
    self.name = name
    self.rmop = rmop
    self.cmop = cmop
    self.zmop = zmop
    self.tpf = tpf

class Series():
  def __init__(self, experiment_name, index):
    self.experiment_name = experiment_name
    self.index = index

### Data
regions = [
  Region(index=1, name='medium', description='Cells in the medium not connected to any endothelial cells or PDMS boundaries.'),
  Region(index=2, name='barrier_boundary', description='Cells immediately adjacent to the front edge of the barrier without any full contact with endothelial cells.'),
  Region(index=3, name='barrier_embedded', description='Cells fully embedded in the barrier. In contact with endothelial cells on all sides.'),
  Region(index=4, name='gel', description='Cells in the gel not connected to any endothelial cells or PDMS boundaries.'),
]

experiments = [
  Experiment(name='050714', rmop=0.5369, cmop=0.5369, zmop=1.482, tpf=10.7003),
  Experiment(name='190714', rmop=0.501, cmop=0.5015, zmop=1.482, tpf=9.7408),
  Experiment(name='260714', rmop=0.5696074, cmop=0.5701647, zmop=1.482, tpf=7.6807),
]

series = [
  # 050714
  Series(experiment_name='050714', index=14),

  # 190714
  Series(experiment_name='190714', index=13),

  # 260714
  Series(experiment_name='260714', index=13),
  Series(experiment_name='260714', index=14),
  Series(experiment_name='260714', index=15),
  Series(experiment_name='260714', index=16),
]
