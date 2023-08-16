# Codelink

Codelink is a node-based visual programming environment that can be easily and flexibly integrated into 
[PySide2](https://pypi.org/project/PySide2/) applications as a widget. With Codelink, functions (so-called nodes) can 
be logically linked to each other via wires, as in flowcharts, to create directed node graphs that can be used to 
perform complex calculations or control other programs. A main application area is node-based modeling of 3D geometries 
with the parametric CAD software [FreeCAD](https://www.freecad.org/).

![Startup image](https://github.com/j8sr0230/codelink/blob/main/img/start_up_image.png)


It provides:
* customizable nodes, sockets and data types
* framing and commenting nodes
* sub-graphs and group nodes
* socket options
* validation node connections (links)
* full undo/redo implementation
* framework for node developer
* easy integration in [PySide2](https://pypi.org/project/PySide2/) applications
* made for [FreeCAD](https://www.freecad.org/)

## Installation
Binary wheels for [codelink](https://pypi.org/project/codelink/) are available on 
[PyPI](https://pypi.org/).  
`pip install codelink`