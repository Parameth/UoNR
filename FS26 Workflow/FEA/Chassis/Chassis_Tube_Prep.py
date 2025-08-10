# Python Script, API Version = V242

Tubes = List[IDesignBody]()
Beams = List[IBeam]()
distance = 14 #based on distances between points after extraction

for chassis_tube in GetRootPart().GetAllBodies():
    selection = Selection.Create(chassis_tube)
    Tubes.Add(chassis_tube)
    RenameObject.Execute(selection, "Tube")

for t in Tubes:
    Tube_Count = GetRootPart().GetAllBodies("Tube").Count
    if Tube_Count == 0:
        options = FixBeamConnectionsOptions()
        options.Distance = MM(distance)
        result = Beam.FixBeamConnections.FindAndFix(options)
        RenameObject.Execute(selection, "extracted")
        break
    selection = Selection.CreateByObjects(t)
    result = Beam.ExtractProfile(selection)
    
    options = FixBeamConnectionsOptions()
    options.Distance = MM(distance)
    result = Beam.FixBeamConnections.FindAndFix(options)
    RenameObject.Execute(selection, "extracted")
    
for chassis_tube in GetRootPart().GetAllBodies("Tube"):
        selection = Selection.CreateByObjects(chassis_tube)
        Delete.Execute(selection)

selection = Selection.Create(GetRootPart().GetAllBodies("extracted"))
Delete.Execute(selection )

options = ShareTopologyOptions()
options.Tolerance = MM(0.2)
result = ShareTopology.FindAndFix(options)
result = FixDuplicateCurves.FindAndFix()

DocumentSave.Execute(r"INSERT FILE PATH HERE") #<-----------
