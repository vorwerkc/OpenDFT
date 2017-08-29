from traits.api import HasTraits, Instance, on_trait_change, Range, Bool, Button
from traitsui.api import View, Item, Group
from mayavi.core.ui.api import MayaviScene, MlabSceneModel, \
    SceneEditor

import numpy as np

bohr = 0.52917721

cov_radii = np.loadtxt('./data/cov_radii.dat')/bohr

colors = {1: (0.8, 0.8, 0.8),3:(0,0.75,0.75),11:(0,0.75,0.75),19:(0,0.75,0.75),37:(0,0.75,0.75),5:(0.78,0.329,0.1176),7:(0,0,1),
          6:(0.25,.25,.25), 8: (1, 0, 0),9:(0,1,0),17:(0,1,0),35:(0,1,0),16:(1,1,0)}

for i in range(21,31):
    colors[i] = (0,1,1)

for i in range(39,49):
    colors[i] = (0,1,1)

for i in range(71,80):
    colors[i] = (0,1,1)

class StructureVisualization(HasTraits):
    n_x    = Range(1, 10, 1, mode='spinner')#)
    n_y  = Range(1, 10, 1,  mode='spinner')#mode='spinner')
    n_z  = Range(1, 10, 1,  mode='spinner')#mode='spinner')
    prop_but = Button(label='Properties')

    show_unitcell = Bool(True)
    show_bonds = Bool(True)

    view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                     height=450, width=500, show_label=False),Group('_', 'n_x', 'n_y', 'n_z','show_unitcell','show_bonds',orientation='horizontal'),
                resizable=True, # We need this to resize with the parent widget
                )
    scene = Instance(MlabSceneModel, ())

    def __init__(self, crystal_structure):
        super(StructureVisualization,self).__init__()

        self.crystal_structure = crystal_structure


    @on_trait_change('scene.activated,show_unitcell,show_bonds')
    def update_plot(self):
        if self.crystal_structure is None:
            return
        self.scene.anti_aliasing_frames = 5
        # We can do normal mlab calls on the embedded scene.
        self.scene.mlab.clf()
        repeat = [self.n_x,self.n_y,self.n_z]

        self.plot_atoms(repeat=repeat)

        if self.show_bonds:
            self.plot_bonds(repeat=repeat)

        if self.show_unitcell:
            self.plot_unit_cell(repeat=repeat)

    def check_if_line_exists(self,p1,p2,list_of_lines):
        for line in list_of_lines:
            x1 = line[0]
            x2 = line[1]
            norm1 = np.linalg.norm(p1-x1)+np.linalg.norm(p2-x2)
            norm2 = np.linalg.norm(p1-x2)+np.linalg.norm(p2-x1)
            if norm1 < 0.05 or norm2 < 0.05:
                return True
        return False

    def plot_unit_cell(self, repeat=[1, 1, 1]):
        cell = self.crystal_structure.lattice_vectors

        existing_lines = []

        for j1 in range(repeat[0]):
            for j2 in range(repeat[1]):
                for j3 in range(repeat[2]):
                    offset = j1 * cell[0, :] + j2 * cell[1, :] + j3 * cell[2, :]
                    for i1, a in enumerate(cell):
                        i2 = (i1 + 1) % 3
                        i3 = (i1 + 2) % 3
                        for b in [np.zeros(3), cell[i2]]:
                            for c in [np.zeros(3), cell[i3]]:
                                p1 = b + c + offset
                                p2 = p1 + a
                                if not self.check_if_line_exists(p1,p2,existing_lines):
                                    self.scene.mlab.plot3d([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], tube_radius=0.03)
                                    existing_lines.append([p1,p2])

    def plot_atoms(self, repeat=[1, 1, 1]):
        abs_coord_atoms = self.crystal_structure.calc_absolute_coordinates(repeat=repeat)
        species = set(abs_coord_atoms[:,3].astype(np.int))
        n_species = len(species)
        n_atoms = abs_coord_atoms.shape[0]



        for specie in species:
            species_mask = abs_coord_atoms[:,3].astype(np.int) == specie
            sub_coords = abs_coord_atoms[species_mask,:]

            cov_radius = cov_radii[specie]
            atom_size = 0.4*np.log(specie)+0.6
            try:
                atomic_color = colors[specie]
            except KeyError:
                atomic_color = (0.8,0.8,0.8)
            self.scene.mlab.points3d(sub_coords[:,0],sub_coords[:,1],sub_coords[:,2],
                                     scale_factor=atom_size,
                                     resolution=10,
                                     color=atomic_color)



    def plot_bonds(self,repeat=[1,1,1]):
        abs_coord_atoms = self.crystal_structure.calc_absolute_coordinates(repeat=repeat)
        bonds = self.crystal_structure.find_bonds(abs_coord_atoms)

        for bond in bonds:
            i1 = bond[0]
            i2 = bond[1]
            p1 = abs_coord_atoms[i1,:3]
            p2 = abs_coord_atoms[i2,:3]
            self.scene.mlab.plot3d([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], tube_radius=0.125)