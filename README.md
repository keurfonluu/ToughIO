# ToughIO
![license](https://img.shields.io/badge/LICENSE-MIT-green)


## What is ToughIO?

ToughIO is an open-source Python package to facilitate pre- and post-processing for the numerical multiphase flow simulator [TOUGH](https://tough.lbl.gov/) developed at Berkeley Lab.

It offers the possibility to write TOUGH input file using the popular and more human-readable [JSON](http://json.org/) format.

It does **NOT** provide tools for meshing, but rather relies on the open-source library [meshio](https://github.com/nschloe/meshio) to import compatible mesh geometries generated by external softwares (e.g. [Gmsh](http://gmsh.info/)).