# SDZM toolbox
Shear Damage Zones Measurement Toolbox for Rock Joint (SDZM toolbox) is an easy-to-use python-based software for measuring shear damage zones of post-shearing rock joint using images took by mobile phone.

# Usage
## Download
The first version has been released at [Release](https://github.com/Doradx/SDZMtoolbox/releases/latest).
## Install
Run ```Setup.exe``` to install, and a shortcut will be created on the desktop.

# Main Window
Double click the shortcut ```SDZM toolbox``` to start the program.
![](https://raw.githubusercontent.com/Doradx/SDZMtoolbox/master/static/MainWindow.png)

# Files

- `MainWindow.py` - The entry of the SDZM toolbox, including program design, grouping modules together
- `View.py` - the complex view inherit from QGraphicsView, including PolygonView and LabelImageView.
- `AnalysisThread.py` - All types of the analysis thread, including the manual method, the global OTSU method, the Riss method and the SDZM method.
- `ImageRegistration.py` - the plugin for the registrant the images before and after the test.
- `ImageTool.py` - the functions for image processing.
- `LabelImageDataTable.py` - the table that shows the data.
- `requirements.txt` - the third library used in this program.

# Author
Dorad
cug_xia@cug.edu.cn