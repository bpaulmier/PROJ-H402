# PROJ-H402
Frame extraction and filtering for videogrammetry <br/>
'100framesFF.obj' is a file readable with Agisoft Metashape, containing a 3D model of a chair that was created thanks to the 'projh402.py' file. <br/>
'100framesRF.obj' is a file readable with Agisoft Metashape, containing a 3D model of a chair that was created with a naive regular selection of frames. <br/>
Article is the 'Paper PROJ-H402' pdf file. <br/>
<br/>
Comments on how to use the 'projh402.py' file: <br/>
<br/>
- Edit the lines 81, 87, 90, 91, 122, 129, 150, 156, 167, 169 and 171 to make them use the user's desired directory (quick way: in an IDE, use ctrl+F to change all '/Users/benjaminpaulmier/downloads/' by the appropriate path <br/>
- Run the 'extractFrames' function with a string of the video name for videoName and int/float values for blurThresh, overlapThresh and nbrOfFrames as recommended <br/>
- The extracted frames will be in the 'good[videoName]Frames' folder, which can be opened with metashape. Once opened, align cameras, build dense cloud, mesh and textures, and the 3D model will be complete.
