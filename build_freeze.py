import sys
import os
from cx_Freeze import setup, Executable
import cx_Freeze.hooks
def hack(finder, module):
    return
cx_Freeze.hooks.load_matplotlib = hack
import scipy
import matplotlib
from encodings import ascii
from encodings import idna
from encodings import unicode_escape

scipy_path = os.path.dirname(scipy.__file__) #use this if you are also using scipy in your application

build_exe_options = {"packages": ["pyface.ui.qt4", "tvtk.vtk_module", "tvtk.pyface.ui.wx", "matplotlib.backends.backend_qt4",'pkg_resources._vendor','pkg_resources.extern','pygments.lexers',
                                  'tvtk.pyface.ui.qt4'],
                     "include_files": [(str(scipy_path), "scipy"), #for scipy
                    (matplotlib.get_data_path(), "mpl-data"),'/home/jannick/python_programs/OpenDFT/data'],
                     "includes":['numpy.core._methods', 'numpy.lib.format','PyQt4.QtCore','PyQt4.QtGui'],
                     'excludes':'Tkinter'
                    }

executables = [
    Executable('main.py', targetName="OpenDFT")
]

setup(name='OpenDFT',
      version='1.0',
      description='OpenDFT',
      options = {"build_exe": build_exe_options},
      executables=executables
      )