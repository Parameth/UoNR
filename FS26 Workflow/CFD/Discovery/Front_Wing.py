# Ansys Discovery Python Script, API Version = V251
# For UoNR Front Wing

################################################################

# Insert Geometry
File.InsertGeometry(r"INSERT FILE PATH HERE") #<----------------

################################################################

# Parameters
inlet = [1000, 750, 750, "inlet"]   
outlet = [-3000, 750, 750, "outlet"]
ground = [-1000, 750, 0, "ground"]
symmetry = [-1000, 0, 750, "symmetry"]
velocity = 13.5 #m/s

################################################################

# Create Sketch Cylinder
result = CylinderBody.Create(Point.Create(MM(-490), MM(516.9), MM(265)), Point.Create(MM(-490), MM(736.9), MM(265)), Point.Create(MM(-230), MM(736.9), MM(265)), ExtrudeType.None)
# EndBlock

# Create Sketch Cylinder
result = CylinderBody.Create(Point.Create(MM(-490), MM(516.9), MM(265)), Point.Create(MM(-490), MM(676.9), MM(265)), Point.Create(MM(-340), MM(676.9), MM(265)), ExtrudeType.ForceIndependent)
# EndBlock

# Solidify Sketch
mode = InteractionMode.Solid
result = ViewHelper.SetViewMode(mode, None)
# EndBlock

# Intersecting bodies
targets = BodySelection.Create(GetRootPart().Bodies[0])
tools = BodySelection.Create(GetRootPart().Bodies[1])
options = MakeSolidsOptions()
result = Combine.Intersect(targets, tools, options)
# EndBlock

# Delete Objects
selection = BodySelection.Create(GetRootPart().Bodies[2])
result = Combine.RemoveRegions(selection)
# EndBlock

# Delete Selection
selection = BodySelection.Create(GetRootPart().Bodies[1])
result = Delete.Execute(selection)
# EndBlock

# Rename 'Solid' to 'Wheel'
selection = BodySelection.Create(GetRootPart().Bodies[0])
result = RenameObject.Execute(selection,"Wheel")
# EndBlock

# Set Sketch Plane
sectionPlane = Plane.PlaneZX
result = ViewHelper.SetSketchPlane(sectionPlane, None)

# Sketch Rectangle
point1 = Point2D.Create(MM(1500),MM(1000))
point2 = Point2D.Create(MM(1500),MM(-3000))
point3 = Point2D.Create(MM(0),MM(-3000))
result = SketchRectangle.Create(point1, point2, point3)

# Solidify Sketch
mode = InteractionMode.Solid
result = ViewHelper.SetViewMode(mode, None)

# Extrude 1 Face
selection = FaceSelection.Create(GetRootPart().Bodies[1].Faces[0])
options = ExtrudeFaceOptions()
options.ExtrudeType = ExtrudeType.ForceIndependent
result = ExtrudeFaces.Execute(selection, MM(1500), options)

# Intersecting bodies
targets = BodySelection.Create(GetRootPart().Bodies[1])
tools = BodySelection.Create(GetRootPart().Bodies[0])
options = MakeSolidsOptions()
options.KeepCutter = False
result = Combine.Intersect(targets, tools, options)
# EndBlock

# Intersecting bodies
targets = BodySelection.Create(GetRootPart().Bodies[0])
tools = Selection.Create(GetRootPart().GetComponents())
options = MakeSolidsOptions()
options.KeepCutter = False
result = Combine.Intersect(targets, tools, options)
# EndBlock

def findface_X(location_tuple):
    xx, yy, zz, name = location_tuple

    searchPoint = Point.Create(MM(xx), MM(yy), MM(zz))
    direction = Direction.DirX
    rayOrigin = searchPoint + (direction.UnitVector * -0.001)
    hits = RayFire.Fire(rayOrigin, direction, 1E-10, 1E-5)

    for item in hits:
        if isinstance(item, IDesignFace):
            Selection.Create(item).CreateAGroup(name)
            break
def findface_Y(location_tuple):
    xx, yy, zz, name = location_tuple

    searchPoint = Point.Create(MM(xx), MM(yy), MM(zz))
    direction = Direction.DirY
    rayOrigin = searchPoint + (direction.UnitVector * -0.001)
    hits = RayFire.Fire(rayOrigin, direction, 1E-10, 1E-5)

    for item in hits:
        if isinstance(item, IDesignFace):
            Selection.Create(item).CreateAGroup(name)
            break      
def findface_Z(location_tuple):
    xx, yy, zz, name = location_tuple

    searchPoint = Point.Create(MM(xx), MM(yy), MM(zz))
    direction = Direction.DirZ
    rayOrigin = searchPoint + (direction.UnitVector * -0.001)
    hits = RayFire.Fire(rayOrigin, direction, 1E-10, 1E-5)

    for item in hits:
        if isinstance(item, IDesignFace):
            Selection.Create(item).CreateAGroup(name)
            break

def definefaces():
    findface_X(inlet)
    findface_X(outlet)
    findface_Y(symmetry)
    findface_Z(ground)
    
definefaces()

# Create Simulation
simulation=Solution.Simulation.Create()
Solution.Simulation.SetCurrentSimulation(simulation)

# Apply Flow
selection = Selection.Create(NamedSelection.GetGroup("inlet"))
speed = SpeedQuantity.Create(velocity, SpeedUnit.MeterPerSecond)
result = Conditions.Flow.Create(selection, speed, FlowDirection.In)

# Apply Flow
selection = Selection.Create(NamedSelection.GetGroup("outlet"))
pressure = PressureQuantity.Create(0, PressureUnit.Pascal)
result = Conditions.Flow.Create(selection, pressure, FlowDirection.Out)

# Apply Symmetry 1
selection = Selection.Create(NamedSelection.GetGroup("symmetry"))
result = Conditions.Symmetry.Create(selection)

# Apply Translating Wall 3
selection = Selection.Create(NamedSelection.GetGroup("ground"))
result = Conditions.Wall.Create(selection)
result.WallSurfaceFriction = WallSurfaceFriction.NoSlip
result.MotionSpecification = WallMotion.Translating
result.TranslationalVelocity = VectorQuantityTranslationalSpeed.Create(0, velocity, 0, SpeedUnit.MeterPerSecond)

# Find Fluid Domain
Test = List[IDesignBody]()
part = GetRootPart()

for body in part.GetAllBodies():
    if body.Shape.Volume > 1 : #m^3
        Test.Add(body)       

Selection.Create(Test).SetActive()

# Create Named Selection Group
primarySelection = Selection.GetActive()
secondarySelection = Selection.Empty()
result = NamedSelection.Create(primarySelection, secondarySelection)

# Rename Named Selection
result = NamedSelection.Rename("Selection1", "Fluid")

# Create Named Selection Group
selection = Selection.CreateByGroups("Fluid").ConvertToFaces().FilterFaces().FilterByArea(0.35, 0.36)
selection.SetActive()
# Create Named Selection Group
primarySelection = PowerSelection.Faces.Coaxial(Selection.GetActive())
secondarySelection = Selection.Empty()
result = NamedSelection.Create(primarySelection, secondarySelection, "Wheel")
# EndBlock

# Create Named Selection Group
primarySelection = Selection.CreateByGroups("Fluid").ConvertToFaces().FilterFaces().FilterByArea(0, 0.3)
secondarySelection = Selection.Empty()
result = NamedSelection.Create(primarySelection, secondarySelection, "Wings")

# Repair Overlapping Named Selections
result = NamedSelection.RemoveOverlaps()
# EndBlock

# Change Stage
Solution.Stages.SetStage("RefineStage")

# Change flow simulation meshing method
simulation = Solution.Simulation.GetCurrentSimulation()
simulation.SimulationOptions.FlowMeshingOption = FlowMeshingOption.PolyhedraMesh

# Add monitor
resultVariable = Results.ResultVariable.FluidForce
resultFunction = Results.ResultFunction.Integral
selection1 = Selection.Create(NamedSelection.GetGroup("Wings"))
selection2 = Selection.Empty()
result = Results.Monitor.Create(selection1, selection2, resultVariable, resultFunction)
result.ResultVectorComponent = Results.ResultVectorComponent.X

# Add monitor
result2 = Results.Monitor.Create(selection1, selection2, resultVariable, resultFunction)
result2.ResultVectorComponent = Results.ResultVectorComponent.Y

# Add monitor
result3 = Results.Monitor.Create(selection1, selection2, resultVariable, resultFunction)
result3.ResultVectorComponent = Results.ResultVectorComponent.Z

# Apply Rotating Wall 2
selection = Selection.Create(NamedSelection.GetGroup("Wheel"))
result = Conditions.Wall.Create(selection)
result.WallThermalSpecification = WallThermalSpecification.Insulated
result.WallSurfaceFriction = WallSurfaceFriction.NoSlip
result.MotionSpecification = WallMotion.Rotating
result.RotationalVelocity = VectorQuantityRotationalSpeed.Create(0, 57.45, 0, RotationalSpeedUnit.RevolutionPerMinute)
# EndBlock

# Set Surface Friction
condition = Conditions.Wall.GetByLabel("Non-Slip Wall (default)")
condition.WallSurfaceFriction = WallSurfaceFriction.FreeSlip

# Replaces the assigned material
materialAssignment = Materials.MaterialAssignment.GetByLabel("Water (Liquid)")
material = Materials.Material.GetLibraryMaterial("Air")
materialAssignment.Material = material

# Set Fidelity Value
Solution.Stages.SetFidelity(0.04)

# Start Solver in Refine Mode 
Solution.Solver.StartRefine()

# Start Solver in Refine Mode 
Solution.Solver.StartRefine()
