Analysis_FrontFix = Model.AddStaticStructuralAnalysis()
Analysis_RearFix = Model.AddStaticStructuralAnalysis()

import_path = r"P:\\Formula Student\\FS26\\FEA  Example\\Chassis_Tubes_Beams.scdoc"
geomImport = Model.GeometryImportGroup.AddGeometryImport()
geomImport.Import(import_path)

#Only consider the right hand side of the car as if you are the drive
Front_WheelHub = [490.48, 623.6, 235.03]  # (X,Y,Z) with respect to the global coordinate system (RIGHT SIDE Y = POSITIVE, LEFT SIDE Y = NEGATIVE)
Rear_WheelHub = [2035.26, 639.58, 252.83] # (X,Y,Z) with respect to the global coordinate system (RIGHT SIDE Y = POSITIVE, LEFT SIDE Y = NEGATIVE)
Wheel_Force = 3100

#Named Selections

#Chassis Beam Body
ns = Model.AddNamedSelection()
ns.ScopingMethod = GeometryDefineByType.Worksheet
Tree.Refresh()
ns.Name = "Chassis"
Chassis = ns.GenerationCriteria
Chassis.Add(None)
Chassis[0].EntityType = SelectionType.GeoBody
Chassis[0].Criterion = SelectionCriterionType.Type
Chassis[0].Operator = SelectionOperatorType.Equal
Chassis[0].Value = BodyType.Line
Tree.Refresh()
ns.Generate()
Tree.Refresh()

#LHS_Rear Nodes
ns = Model.AddNamedSelection()
ns.ScopingMethod = GeometryDefineByType.Worksheet
Tree.Refresh()
ns.Name = "LHS_Rear"
LHS_Rear = ns.GenerationCriteria
LHS_Rear.Add(None)
LHS_Rear[0].EntityType = SelectionType.GeoVertex
LHS_Rear[0].Criterion = SelectionCriterionType.LocationX
LHS_Rear[0].Operator = SelectionOperatorType.GreaterThan
LHS_Rear[0].Value = Quantity(1700, "mm")
Tree.Refresh()
LHS_Rear.Add(None)
LHS_Rear[1].Action = SelectionActionType.Filter
LHS_Rear[1].EntityType = SelectionType.GeoVertex
LHS_Rear[1].Criterion = SelectionCriterionType.LocationZ
LHS_Rear[1].Operator = SelectionOperatorType.LessThan
LHS_Rear[1].Value = Quantity(360, "mm")
Tree.Refresh()
LHS_Rear.Add(None)
LHS_Rear[2].Action = SelectionActionType.Filter
LHS_Rear[2].EntityType = SelectionType.GeoVertex
LHS_Rear[2].Criterion = SelectionCriterionType.LocationY
LHS_Rear[2].Operator = SelectionOperatorType.LessThan
LHS_Rear[2].Value = Quantity(0, "mm")
Tree.Refresh()
ns.Generate()
Tree.Refresh()

#RHS_Rear Nodes
ns = Model.AddNamedSelection()
ns.ScopingMethod = GeometryDefineByType.Worksheet
Tree.Refresh()
ns.Name = "RHS_Rear"
RHS_Rear = ns.GenerationCriteria
RHS_Rear.Add(None)
RHS_Rear[0].EntityType = SelectionType.GeoVertex
RHS_Rear[0].Criterion = SelectionCriterionType.LocationX
RHS_Rear[0].Operator = SelectionOperatorType.GreaterThan
RHS_Rear[0].Value = Quantity(1700, "mm")
Tree.Refresh()
RHS_Rear.Add(None)
RHS_Rear[1].Action = SelectionActionType.Filter
RHS_Rear[1].EntityType = SelectionType.GeoVertex
RHS_Rear[1].Criterion = SelectionCriterionType.LocationZ
RHS_Rear[1].Operator = SelectionOperatorType.LessThan
RHS_Rear[1].Value = Quantity(360, "mm")
Tree.Refresh()
RHS_Rear.Add(None)
RHS_Rear[2].Action = SelectionActionType.Filter
RHS_Rear[2].EntityType = SelectionType.GeoVertex
RHS_Rear[2].Criterion = SelectionCriterionType.LocationY
RHS_Rear[2].Operator = SelectionOperatorType.GreaterThan
RHS_Rear[2].Value = Quantity(0, "mm")
Tree.Refresh()
ns.Generate()
Tree.Refresh()

#LHS_Front Nodes
ns = Model.AddNamedSelection()
ns.ScopingMethod = GeometryDefineByType.Worksheet
Tree.Refresh()
ns.Name = "LHS_Front"
LHS_Front = ns.GenerationCriteria
LHS_Front.Add(None)
LHS_Front[0].EntityType = SelectionType.GeoVertex
LHS_Front[0].Criterion = SelectionCriterionType.LocationX
LHS_Front[0].Operator = SelectionOperatorType.RangeInclude
LHS_Front[0].LowerBound = Quantity(500, "mm")
LHS_Front[0].UpperBound = Quantity(900, "mm")
Tree.Refresh()
LHS_Front.Add(None)
LHS_Front[1].Action = SelectionActionType.Filter
LHS_Front[1].EntityType = SelectionType.GeoVertex
LHS_Front[1].Criterion = SelectionCriterionType.LocationZ
LHS_Front[1].Operator = SelectionOperatorType.LessThan
LHS_Front[1].Value = Quantity(500, "mm")
Tree.Refresh()
LHS_Front.Add(None)
LHS_Front[2].Action = SelectionActionType.Filter
LHS_Front[2].EntityType = SelectionType.GeoVertex
LHS_Front[2].Criterion = SelectionCriterionType.LocationY
LHS_Front[2].Operator = SelectionOperatorType.LessThan
LHS_Front[2].Value = Quantity(0, "mm")
Tree.Refresh()
LHS_Front.Add(None)
LHS_Front[3].Action = SelectionActionType.Remove
LHS_Front[3].EntityType = SelectionType.GeoVertex
LHS_Front[3].Criterion = SelectionCriterionType.LocationZ
LHS_Front[3].Operator = SelectionOperatorType.Equal
LHS_Front[3].Value = Quantity(339, "mm")
Tree.Refresh()
ns.Generate()
Tree.Refresh()

#RHS_Front Nodes
ns = Model.AddNamedSelection()
ns.ScopingMethod = GeometryDefineByType.Worksheet
Tree.Refresh()
ns.Name = "RHS_Front"
RHS_Front = ns.GenerationCriteria
RHS_Front.Add(None)
RHS_Front[0].EntityType = SelectionType.GeoVertex
RHS_Front[0].Criterion = SelectionCriterionType.LocationX
RHS_Front[0].Operator = SelectionOperatorType.RangeInclude
RHS_Front[0].LowerBound = Quantity(500, "mm")
RHS_Front[0].UpperBound = Quantity(900, "mm")
Tree.Refresh()
RHS_Front.Add(None)
RHS_Front[1].Action = SelectionActionType.Filter
RHS_Front[1].EntityType = SelectionType.GeoVertex
RHS_Front[1].Criterion = SelectionCriterionType.LocationZ
RHS_Front[1].Operator = SelectionOperatorType.LessThan
RHS_Front[1].Value = Quantity(500, "mm")
Tree.Refresh()
RHS_Front.Add(None)
RHS_Front[2].Action = SelectionActionType.Filter
RHS_Front[2].EntityType = SelectionType.GeoVertex
RHS_Front[2].Criterion = SelectionCriterionType.LocationY
RHS_Front[2].Operator = SelectionOperatorType.GreaterThan
RHS_Front[2].Value = Quantity(0, "mm")
Tree.Refresh()
RHS_Front.Add(None)
RHS_Front[3].Action = SelectionActionType.Remove
RHS_Front[3].EntityType = SelectionType.GeoVertex
RHS_Front[3].Criterion = SelectionCriterionType.LocationZ
RHS_Front[3].Operator = SelectionOperatorType.Equal
RHS_Front[3].Value = Quantity(339, "mm")
Tree.Refresh()
ns.Generate()
Tree.Refresh()

#Set Boundary Conditions (ANALYSIS 1 - FRONT FIXED / REAR MOVES)

#Fixed Supports
LHS_Fixed = DataModel.GetObjectsByName("LHS_Front")
FS_1 = Analysis_FrontFix.AddFixedSupport()
FS_1.Location = LHS_Fixed[0]

RHS_Fixed = DataModel.GetObjectsByName("RHS_Front")
FS_2 = Analysis_FrontFix.AddFixedSupport()
FS_2.Location = RHS_Fixed[0]

#Remote Forces
LHS_Remote = DataModel.GetObjectsByName("LHS_Rear")
RF_1 = Analysis_FrontFix.AddRemoteForce()
RF_1.Location = LHS_Remote[0]
RF_1.XCoordinate = Quantity(Rear_WheelHub[0], "mm")
RF_1.YCoordinate = Quantity(Rear_WheelHub[1], "mm")
RF_1.ZCoordinate = Quantity(Rear_WheelHub[2], "mm")
RF_1.DefineBy = LoadDefineBy.Components
RF_1.ZComponent.Output.SetDiscreteValue(0, Quantity(Wheel_Force, "N"))

RHS_Remote = DataModel.GetObjectsByName("RHS_Rear")
RF_2 = Analysis_FrontFix.AddRemoteForce()
RF_2.Location = RHS_Remote[0]
RF_2.XCoordinate = Quantity(Rear_WheelHub[0], "mm")
RF_2.YCoordinate = Quantity(-Rear_WheelHub[1], "mm")
RF_2.ZCoordinate = Quantity(Rear_WheelHub[2], "mm")
RF_2.DefineBy = LoadDefineBy.Components
RF_2.ZComponent.Output.SetDiscreteValue(0, Quantity(-Wheel_Force, "N"))

#Set Boundary Conditions (ANALYSIS 2 - REAR FIXED / FRONT MOVES)

#Fixed Supports
LHS_Fixed = DataModel.GetObjectsByName("LHS_Rear")
FS_1 = Analysis_RearFix.AddFixedSupport()
FS_1.Location = LHS_Fixed[0]

RHS_Fixed = DataModel.GetObjectsByName("RHS_Rear")
FS_2 = Analysis_RearFix.AddFixedSupport()
FS_2.Location = RHS_Fixed[0]

#Remote Forces
LHS_Remote = DataModel.GetObjectsByName("LHS_Front")
RF_1 = Analysis_RearFix.AddRemoteForce()
RF_1.Location = LHS_Remote[0]
RF_1.XCoordinate = Quantity(Front_WheelHub[0], "mm")
RF_1.YCoordinate = Quantity(Front_WheelHub[1], "mm")
RF_1.ZCoordinate = Quantity(Front_WheelHub[2], "mm")
RF_1.DefineBy = LoadDefineBy.Components
RF_1.ZComponent.Output.SetDiscreteValue(0, Quantity(Wheel_Force, "N"))

RHS_Remote = DataModel.GetObjectsByName("RHS_Front")
RF_2 = Analysis_RearFix.AddRemoteForce()
RF_2.Location = RHS_Remote[0]
RF_2.XCoordinate = Quantity(Front_WheelHub[0], "mm")
RF_2.YCoordinate = Quantity(-Front_WheelHub[1], "mm")
RF_2.ZCoordinate = Quantity(Front_WheelHub[2], "mm")
RF_2.DefineBy = LoadDefineBy.Components
RF_2.ZComponent.Output.SetDiscreteValue(0, Quantity(-Wheel_Force, "N"))

#Solve
mesh = Model.Mesh
Tree.Refresh()
mesh.GenerateMesh()
Analysis_FrontFix.Solution.Solve(True)
Analysis_RearFix.Solution.Solve(True)

#Add Displacement Results X Y Z for BOTH ANALYSIS'

#ANALYSIS 1 - FRONT FIXED / REAR MOVES
Deformation_Selection = DataModel.GetObjectsByName("Chassis")
Analysis_FrontFix.Solution.AddTotalDeformation()
DDef_X = Analysis_FrontFix.Solution.AddDirectionalDeformation()
DDef_X.NormalOrientation = NormalOrientationType.XAxis
DDef_Y = Analysis_FrontFix.Solution.AddDirectionalDeformation()
DDef_Y.NormalOrientation = NormalOrientationType.YAxis
DDef_Z = Analysis_FrontFix.Solution.AddDirectionalDeformation()
DDef_Z.NormalOrientation = NormalOrientationType.ZAxis
Analysis_FrontFix.Solution.EvaluateAllResults()

#ANALYSIS 2 - REAR FIXED / FRONT MOVES
Deformation_Selection = DataModel.GetObjectsByName("Chassis")
Analysis_RearFix.Solution.AddTotalDeformation()
DDef_X = Analysis_RearFix.Solution.AddDirectionalDeformation()
DDef_X.NormalOrientation = NormalOrientationType.XAxis
DDef_Y = Analysis_RearFix.Solution.AddDirectionalDeformation()
DDef_Y.NormalOrientation = NormalOrientationType.YAxis
DDef_Z = Analysis_RearFix.Solution.AddDirectionalDeformation()
DDef_Z.NormalOrientation = NormalOrientationType.ZAxis
Analysis_RearFix.Solution.EvaluateAllResults()
