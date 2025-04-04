sim_name = "FCS5_con_test"
mesh_file = "FCSMRF5.msh"


#add status updates as a text file for data and time of each process, find time taken for each process
#add seperate file for all HPC functions to declutter
#use for loops to declutter for report defs and report files + plots
#declutter all code after first fully sucessful run
#add proper error messages
#evaluate all lift+drag force over each components (named selection)
#add aero balance calcuator
#put all variables at the start of the script for ease of access

#---------------------------------------------------------------------------------------------
import os
import shutil
import cv2
import time
import re
from tqdm import tqdm
import ansys.fluent.core as pyfluent
import FCS_run_MRF_HPC_func as HPCfunc

start_time = time.time()

# velocity = 13.5
# front_mrf_origin = [0,-0.6448704,0.237]
# rear_mrf_origin = [-1.559238,-0.6448704,237]
# mrf_omega = 57.45
# mrf_axis_direction = [0,1,0]


def run_fluent():
    fluent = pyfluent.launch_fluent(
        dimension = pyfluent.Dimension.THREE ,
        processor_count = 14 , #TBC
        precision = pyfluent.Precision.DOUBLE,
        mode = "solver"
        )

    temp_mesh_path = os.path.abspath(mesh_file)

    fluent.file.read_case(file_name = temp_mesh_path)   

    surfaces = fluent.results.surfaces
    graphics = fluent.results.graphics

    interface = fluent.setup.boundary_conditions.interface.get_object_names()
    interface_edit = []

    for i in interface:
        test = bool(re.search("wheel", i))
        if test == True:
            test = i
            interface_edit.append(test)
        else:
            interface.pop(interface.index(i))

    for i in interface:
        fluent.setup.boundary_conditions.interface[i]
        name_new = HPCfunc.remove_digits(i)
        fluent.setup.boundary_conditions.interface[i](name = name_new)

    # internal_TEST = fluent.setup.boundary_conditions.interface.get_object_names()
    # f = open("{}-status.txt".format(sim_name), "w")
    # f.write("Time: Part 3 complete \n list: {l}".format(l = internal_TEST))
    # f.close

    inlet = fluent.setup.boundary_conditions.velocity_inlet["velocity_inlet"]
    inlet.momentum.velocity.value = 13.5

    wall = fluent.setup.boundary_conditions.wall["walls"]
    wall.momentum.shear_bc.set_state("Specified Shear") # shear_condition for 24R2

    ground = fluent.setup.boundary_conditions.wall["ground"]
    ground.momentum.motion_bc.set_state("Moving Wall") # wall_motion for 24R2
    ground.momentum.vmag.value = 13.5 # speed.value = 13.5  for 24R2
    ground.momentum(wall_translation = [0, 1, 0]) # (direction = [0, 1, 0]) for 24R2

    front_mrf = fluent.setup.cell_zone_conditions.fluid["front_mrf"]
    front_mrf.reference_frame.frame_motion = True
    front_mrf.reference_frame(reference_frame_axis_origin = [0,-0.6448704,0.237])
    front_mrf.reference_frame(mrf_omega = 57.45)
    front_mrf.reference_frame(reference_frame_axis_direction = [0,1,0])

    rear_mrf = fluent.setup.cell_zone_conditions.fluid["rear_mrf"]
    rear_mrf.reference_frame.frame_motion = True
    rear_mrf.reference_frame(reference_frame_axis_origin = [-1.559238,-0.6448704,237])
    rear_mrf.reference_frame(mrf_omega = 57.45)
    rear_mrf.reference_frame(reference_frame_axis_direction = [0,1,0])

    fluent.solution.report_definitions.lift["lift-force"] = {}
    lift = fluent.solution.report_definitions.lift["lift-force"]
    lift(report_output_type = "Lift Force")
    lift.zones = [
        "front_wing",
        "rear_wing",
        "side_wing",
        "chassis",
        "rear_wheel",
        "front_wheel"
    ]
    lift(force_vector = [0, 0, 1])
    lift(average_over = 30)
    lift(retain_instantaneous_values = True)

    fluent.solution.report_definitions.drag["drag-force"] = {}
    drag = fluent.solution.report_definitions.drag["drag-force"]
    drag(report_output_type = "Drag Force")
    drag.zones = [
        "front_wing",
        "rear_wing",
        "side_wing",
        "chassis",
        "rear_wheel",
        "front_wheel"
    ]
    drag(force_vector = [0, 1, 0])
    drag(average_over = 30)
    drag(retain_instantaneous_values = True)

    fluent.solution.report_definitions.force["side-force"] = {}
    side_force = fluent.solution.report_definitions.force["side-force"]
    side_force.zones = [
        "front_wing",
        "rear_wing",
        "side_wing",
        "chassis",
        "rear_wheel",
        "front_wheel"
    ]
    side_force(force_vector = [1, 0, 0])
    side_force(average_over = 30)
    side_force(retain_instantaneous_values = True)

    fluent.solution.report_definitions.flux["mfr"] = {}
    mfr = fluent.solution.report_definitions.flux["mfr"]
    mfr.boundaries = [
        "velocity_inlet",
        "pressure_outlet"
    ]

    fluent.solution.monitor.report_files.create("mfr")
    fluent.solution.monitor.report_files["mfr"](report_defs = "mfr")
    fluent.solution.monitor.report_files["mfr"](print = True)
    fluent.solution.monitor.report_plots.create("mfr")
    fluent.solution.monitor.report_plots["mfr"](report_defs = "mfr")
    fluent.solution.monitor.report_plots["mfr"](print = True)

    fluent.solution.monitor.report_files.create("lift-force")
    fluent.solution.monitor.report_files["lift-force"](report_defs = "lift-force")
    fluent.solution.monitor.report_files["lift-force"](print = True)
    fluent.solution.monitor.report_plots.create("lift-force")
    fluent.solution.monitor.report_plots["lift-force"](report_defs = "lift-force")
    fluent.solution.monitor.report_plots["lift-force"](print = True)

    fluent.solution.monitor.report_files.create("drag-force")
    fluent.solution.monitor.report_files["drag-force"](report_defs = "drag-force")
    fluent.solution.monitor.report_files["drag-force"](print = True)
    fluent.solution.monitor.report_plots.create("drag-force")
    fluent.solution.monitor.report_plots["drag-force"](report_defs = "drag-force")
    fluent.solution.monitor.report_plots["drag-force"](print = True)

    fluent.solution.monitor.report_files.create("side-force")
    fluent.solution.monitor.report_files["side-force"](report_defs = "side-force")
    fluent.solution.monitor.report_files["side-force"](print = True)
    fluent.solution.monitor.report_plots.create("side-force")
    fluent.solution.monitor.report_plots["side-force"](report_defs = "side-force")
    fluent.solution.monitor.report_plots["side-force"](print = True)

    fluent.solution.monitor.residual.equations["continuity"].check_convergence = False

    fluent.solution.monitor.convergence_conditions.convergence_reports.create("lift-force")
    fluent.solution.monitor.convergence_conditions.convergence_reports["lift-force"](report_defs = "lift-force")
    fluent.solution.monitor.convergence_conditions.convergence_reports["lift-force"](stop_criterion = 0.05) #5% uncertinaity
    fluent.solution.monitor.convergence_conditions.convergence_reports["lift-force"](initial_values_to_ignore = 300)
    fluent.solution.monitor.convergence_conditions.convergence_reports["lift-force"](previous_values_to_consider = 20)

    fluent.solution.monitor.convergence_conditions.convergence_reports.create("drag-force")
    fluent.solution.monitor.convergence_conditions.convergence_reports["drag-force"](report_defs = "drag-force")
    fluent.solution.monitor.convergence_conditions.convergence_reports["drag-force"](stop_criterion = 0.025) #2.5% uncertinaity
    fluent.solution.monitor.convergence_conditions.convergence_reports["drag-force"](initial_values_to_ignore = 300)
    fluent.solution.monitor.convergence_conditions.convergence_reports["drag-force"](previous_values_to_consider = 20)

    fluent.solution.monitor.convergence_conditions.convergence_reports.create("side-force")
    fluent.solution.monitor.convergence_conditions.convergence_reports["side-force"](report_defs = "side-force")
    fluent.solution.monitor.convergence_conditions.convergence_reports["side-force"](stop_criterion = 0.025) #2.5% uncertinaity
    fluent.solution.monitor.convergence_conditions.convergence_reports["side-force"](initial_values_to_ignore = 300)
    fluent.solution.monitor.convergence_conditions.convergence_reports["side-force"](previous_values_to_consider = 20)

    fluent.solution.monitor.convergence_conditions.convergence_reports.create("mfr")
    fluent.solution.monitor.convergence_conditions.convergence_reports["mfr"](report_defs = "mfr")
    fluent.solution.monitor.convergence_conditions.convergence_reports["mfr"](stop_criterion = 0.5)
    fluent.solution.monitor.convergence_conditions.convergence_reports["mfr"](initial_values_to_ignore = 300)
    fluent.solution.monitor.convergence_conditions.convergence_reports["mfr"](previous_values_to_consider = 1)

    fluent.solution.initialization.hybrid_initialize()
    fluent.solution.run_calculation.iterate(iter_count = 1000)

    fluent.file.write(file_type="case", file_name="{}.cas".format(sim_name))
    fluent.file.write(file_type="data", file_name="{}.dat".format(sim_name))

    fluent.solution.monitor.residual.plot()
    graphics.picture.save_picture(file_name = "{}-residuals-plot.png".format(sim_name))

    fluent.solution.monitor.report_plots["lift-force"].plot()
    graphics.picture.save_picture(file_name = "{}-lift-force-plot.png".format(sim_name))

    fluent.solution.monitor.report_plots["drag-force"].plot()
    graphics.picture.save_picture(file_name = "{}-drag-force-plot.png".format(sim_name))

    fluent.solution.monitor.report_plots["side-force"].plot()
    graphics.picture.save_picture(file_name = "{}-side-force-plot.png".format(sim_name))

    fluent.solution.monitor.report_plots["mfr"].plot()
    graphics.picture.save_picture(file_name = "{}-mfr-plot.png".format(sim_name))

    fluent.solution.report_definitions.compute(report_defs=["lift-force", "drag-force", "side-force", "mfr"])

    def folders():
        main_folder = './{}'.format(sim_name)
        contours_folders = './{}/contours'.format(sim_name)
        animations_folder = './{}/animations'.format(sim_name)
        results_folder = './{}/results'.format(sim_name)

        os.mkdir(main_folder)
        os.makedirs(contours_folders)
        os.makedirs(animations_folder)
        os.makedirs(results_folder)

        for v in var:
            os.makedirs('./{main}/contours/{var}'.format(main = sim_name, var = v))
            os.makedirs('./{main}/animations/revolve/{var}/top'.format(main = sim_name, var = v))
            os.makedirs('./{main}/animations/revolve/{var}/bottom'.format(main = sim_name, var = v))

        for d in dim:
            os.makedirs('./{main}/animations/sweep/cp/{dim}'.format(main = sim_name, dim = d))
            os.makedirs('./{main}/animations/sweep/ti/{dim}'.format(main = sim_name, dim = d))

    resolution_x    = 1920          #pixels
    resolution_y    = 1080          #pixels
    fps             = 15            #frames per second

    num_frames_x    = 73          #number for frames in the x-direction (i) for the sweep animation (730)(365)
    num_frames_y    = 15          #number for frames in the y-direction (j) for the sweep animation (150)(75)
    num_frames_z    = 25          #number for frames in the z-direction (k) for the sweep animation (248)(124)
    num_sweep_frames = 36         #number for frames for revolving (s) for the revolve animation (360))(180)

    ti = "turb-intensity"
    cp = "pressure-coefficient"
    cf = "skin-friction-coef"
    tau = "wall-shear"

    target_pos = [-0.6, 0, 0.6] #need to check for left view, with changed camera position methods

    # Detail the starting areas for the planes, e.g. start x=1, y=-1, z=0 -> start_dim = [1, -1, 0]
    # Detail the end areas for the planes, e.g. start x=-3, y=0, z=1.6 -> start_dim = [-3, 0, 1.6]
    start_dim = [1, -1, 0]
    end_dim = [-3, 0, 1.6]
    dist = []

    for i in start_dim:
        dist_i = start_dim[i] - end_dim[i]
        dist_i = abs(dist_i)
        dist.append(dist_i)
        dist.reverse()

    nums_x = range(1, (num_frames_x + 1))
    nums_y = range(1, (num_frames_y + 1))
    nums_z = range(1, (num_frames_z + 1))
    nums_s = range(0, num_sweep_frames)

    res = [ti, cp, cf, tau]
    var = ["ti", "cp", "cf", "tau"]
    dim = ["x", "y", "z"]

    def set_fluent():
        if graphics.picture.use_window_resolution.is_active():
            graphics.picture.use_window_resolution = False
        graphics.picture.x_resolution = resolution_x 
        graphics.picture.y_resolution = resolution_y
        fluent.tui.preferences.graphics.graphics_effects.grid_plane_enabled = "no"
        fluent.tui.preferences.graphics.graphics_effects.reflections_enabled = "no"
        fluent.tui.preferences.graphics.graphics_effects.shadow_map_enabled = "no"
        fluent.tui.preferences.graphics.graphics_effects.simple_shadows_enabled = "no"
        graphics.views.camera.projection(type = "orthographic")
        fluent.tui.display.set.mirror_zones("symmetry")
        fluent.setup.reference_values.velocity.set_state(13.5)
        print("Image settings set")

    def create_planes():
        plane_x = surfaces.plane_surface.create("x-sweep") #remember to enable sym for contour
        plane_x.method = "yz-plane"
        plane_x.x = start_dim[0]

        plane_y = surfaces.plane_surface.create("y-sweep")
        plane_y.method = "zx-plane"
        plane_y.y = start_dim[1]

        plane_z = surfaces.plane_surface.create("z-sweep")
        plane_z.method = "xy-plane"
        plane_z.z = start_dim[2]
    def reset_plane_xyz():
        fluent.results.surfaces.plane_surface["x-sweep"].x = start_dim[0]
        fluent.results.surfaces.plane_surface["y-sweep"].y = start_dim[1]
        fluent.results.surfaces.plane_surface["z-sweep"].z = start_dim[2]

    def move_plane_x(i):
        fluent.results.surfaces.plane_surface["x-sweep"].x = 1 - (i*(dist[0]/num_frames_x))
    def move_plane_y(j):
        fluent.results.surfaces.plane_surface["y-sweep"].y = -1 + (j*(dist[1]/num_frames_y))
    def move_plane_z(k):
        fluent.results.surfaces.plane_surface["z-sweep"].z = 0 + (k*(dist[2]/num_frames_z))

    def create_contours():
        graphics.contour.create("x-contour")
        x = graphics.contour["x-contour"]
        x.surfaces_list = "x-sweep"

        graphics.contour.create("y-contour")
        y = graphics.contour["y-contour"]
        y.surfaces_list = "y-sweep"

        graphics.contour.create("z-contour")
        z = graphics.contour["z-contour"]
        z.surfaces_list = "z-sweep"  

        graphics.contour.create("car")
        car = graphics.contour["car"]
        car.surfaces_list = [
            "chassis",
            "front_wheel",
            "front_wing",
            "rear_wheel",
            "rear_wing",
            "side_wing",
            "front_wheel-contact_region_-src",
            "rear_wheel-contact_region_-src"
        ]

    def x_sweep(i, r):
        graphics.contour["x-contour"].display()
        graphics.views.restore_view(view_name = "right")
        time.sleep(0.0025)
        graphics.views.auto_scale()
        time.sleep(0.0025)
        graphics.views.camera.target(xyz = [start_dim[0] - (i-1)*(dist[0]/num_frames_x), 0, 1])
        time.sleep(0.0025)
        graphics.views.camera.roll(counter_clockwise = -90)
        time.sleep(0.0025)
        graphics.views.camera.zoom(factor = 10)
        graphics.picture.save_picture(file_name="{result}-x_sweep-{iteration}.png".format(result = r, iteration = i))

        move_plane_x(i)
    def y_sweep(j, r):
        graphics.contour["y-contour"].display()
        graphics.views.restore_view(view_name = "top")
        time.sleep(0.0025)
        graphics.views.auto_scale()
        time.sleep(0.0025)
        graphics.views.camera.target(xyz = [-0.8, start_dim[1]  + (j-1)*(dist[1]/num_frames_y), 0.97])
        time.sleep(0.0025)
        graphics.views.camera.zoom(factor = 17.5)
        graphics.picture.save_picture(file_name="{result}-y_sweep-{iteration}.png".format(result = r, iteration = j))

        move_plane_y(j)
    def z_sweep(k, r):
        graphics.contour["z-contour"].display()
        graphics.views.restore_view(view_name = "front")
        time.sleep(0.0025)
        graphics.views.auto_scale()
        time.sleep(0.0025)
        graphics.views.camera.target(xyz = [-0.5, 0, start_dim[2]  + (k-1)*(dist[2]/num_frames_z)])
        time.sleep(0.0025)
        graphics.views.camera.roll(counter_clockwise = 180)
        time.sleep(0.0025)
        graphics.views.camera.zoom(factor = 20)
        graphics.picture.save_picture(file_name="{result}-z_sweep-{iteration}.png".format(result = r, iteration = k))

        move_plane_z(k)

    def revolve(s,r):
        graphics.contour["car"].field = r

        graphics.contour["car"].range_option.option = "auto-range-off"
        graphics.contour["car"].range_option.auto_range_off.clip_to_range = False

        if r == ti:
            graphics.contour["car"].range_option.auto_range_off(minimum = 0)
            graphics.contour["car"].range_option.auto_range_off(maximum = 0.2)
        elif r == cp:
            graphics.contour["car"].range_option.auto_range_off(minimum = -1.5)
            graphics.contour["car"].range_option.auto_range_off(maximum = 0.5)
        elif r == cf:
            graphics.contour["car"].range_option.auto_range_off(minimum = 1.867737e-07)
            graphics.contour["car"].range_option.auto_range_off(maximum = 0.0465)
        else:
            graphics.contour["car"].range_option.auto_range_off(minimum = 0)
            graphics.contour["car"].range_option.auto_range_off(maximum = 5)

        graphics.contour["car"].display()
        graphics.views.restore_view(view_name = "right")
        graphics.views.camera.target(xyz = target_pos)
        graphics.views.camera.roll(counter_clockwise = -90)
        graphics.views.camera.position(xyz = [125, 0, 7])
        graphics.views.camera.zoom(factor = 40)
        graphics.views.camera.orbit(right = s)
        graphics.views.camera.orbit(up = 30)
        graphics.views.camera.target(xyz = target_pos)
        graphics.views.camera.zoom(factor = -2)
        graphics.picture.save_picture(file_name="{result}-top_revolve-{iteration}.png".format(result = r, iteration = s))
        graphics.views.camera.orbit(up = -60)
        graphics.picture.save_picture(file_name="{result}-bottom_revolve-{iteration}.png".format(result = r, iteration = s))

    def set_animations(r):
        for d in dim:
            graphics.contour["{}-contour".format(d)].field = r

            graphics.contour["{}-contour".format(d)].range_option.option = "auto-range-off"
            graphics.contour["{}-contour".format(d)].range_option.auto_range_off.clip_to_range = False

            if r == ti:
                graphics.contour["{}-contour".format(d)].range_option.auto_range_off(minimum = 0)
                graphics.contour["{}-contour".format(d)].range_option.auto_range_off(maximum = 0.2)

            else:
                graphics.contour["{}-contour".format(d)].range_option.auto_range_off(minimum = -1.5)
                graphics.contour["{}-contour".format(d)].range_option.auto_range_off(maximum = 0.5)

        for i in tqdm(nums_x, desc = "x-contours"):
            x_sweep(i, r)
        print("X is Complete") 

        time.sleep(3)

        fluent.tui.display.set.mirror_zones("()")
        for j in tqdm(nums_y, desc = "y-contours"):
            y_sweep(j, r)
        print("Y is Complete")
        fluent.tui.display.set.mirror_zones("symmetry")

        time.sleep(3)

        for k in tqdm(nums_z, desc = "z-contours"):
            z_sweep(k, r)
        print("Z is Complete")

        time.sleep(3)
    def set_contours(r):
        graphics.contour["car"].field = r

        graphics.contour["car"].range_option.option = "auto-range-off"
        graphics.contour["car"].range_option.auto_range_off.clip_to_range = False

        if r == ti:
            graphics.contour["car"].range_option.auto_range_off(minimum = 0)
            graphics.contour["car"].range_option.auto_range_off(maximum = 0.2)
        elif r == cp:
            graphics.contour["car"].range_option.auto_range_off(minimum = -1.5)
            graphics.contour["car"].range_option.auto_range_off(maximum = 0.5)
        elif r == cf:
            graphics.contour["car"].range_option.auto_range_off(minimum = 1.867737e-07)
            graphics.contour["car"].range_option.auto_range_off(maximum = 0.0465)
        else:
            graphics.contour["car"].range_option.auto_range_off(minimum = 0)
            graphics.contour["car"].range_option.auto_range_off(maximum = 5)

        graphics.contour["car"].display()
        front(r)
        left(r)
        back(r)
        bottom(r)
        top(r)
        iso(r)

    def move_files():
        source_dir = os.getcwd()
        sim_folder = os.path.join(source_dir, sim_name)

        revolve_path = os.path.join(sim_folder, "animations", "revolve")
        sweep_path = os.path.join(sim_folder, "animations", "sweep")
        contours_path = os.path.join(sim_folder, "contours")

        for filename in os.listdir(source_dir):
            if "sweep" in filename:
                target_dir = sweep_path
            elif "revolve" in filename:
                target_dir = revolve_path
            elif "contour" in filename:
                target_dir = contours_path
            else:
                continue

            source_path = os.path.join(source_dir, filename)
            target_path = os.path.join(target_dir, filename)
            shutil.move(source_path, target_path)

        for filename in os.listdir(revolve_path):
                
            cf_path = os.path.join(revolve_path, "cf")
            cp_path = os.path.join(revolve_path, "cp")
            tau_path = os.path.join(revolve_path, "tau")
            ti_path = os.path.join(revolve_path, "ti")
            
            if cf in filename:
                target_dir = cf_path
            elif cp in filename:
                target_dir = cp_path
            elif tau in filename:
                target_dir = tau_path
            elif ti in filename:
                target_dir = ti_path
            else:
                continue

            source_path = os.path.join(revolve_path, filename)
            target_path = os.path.join(target_dir, filename)
            shutil.move(source_path, target_path)

            res_path = [cf_path, cp_path, tau_path, ti_path]

            for res in res_path:

                top = os.path.join(res, "top")
                bottom = os.path.join(res, "bottom")

                for filename in os.listdir(res):

                    if "-top" in filename:
                        target_dir = top
                    elif "-bottom" in filename:
                        target_dir = bottom
                    else:
                        continue

                    source_path = os.path.join(res, filename)
                    target_path = os.path.join(target_dir, filename)
                    shutil.move(source_path, target_path)


        for filename in os.listdir(sweep_path):

            ti_path = os.path.join(sweep_path, "ti")
            cp_path = os.path.join(sweep_path, "cp")

            if ti in filename:
                target_dir = ti_path
            elif cp in filename:
                target_dir = cp_path
            else:
                continue

            source_path = os.path.join(sweep_path, filename)
            target_path = os.path.join(target_dir, filename)
            shutil.move(source_path, target_path)

            res_path = [ti_path, cp_path]

            for res in res_path:

                x_path = os.path.join(res, "x")
                y_path = os.path.join(res, "y")
                z_path = os.path.join(res, "z")

                for filename in os.listdir(res):
                    if "-x" in filename:
                        target_dir = x_path
                    elif "-y" in filename:
                        target_dir = y_path
                    elif "-z" in filename:
                        target_dir = z_path
                    else:
                        continue

                    source_path = os.path.join(res, filename)
                    target_path = os.path.join(target_dir, filename)
                    shutil.move(source_path, target_path)



        for filename in os.listdir(contours_path):

            cf_path = os.path.join(contours_path, "cf")
            cp_path = os.path.join(contours_path, "cp")
            tau_path = os.path.join(contours_path, "tau")
            ti_path = os.path.join(contours_path, "ti")
            
            if cf in filename:
                target_dir = cf_path
            elif cp in filename:
                target_dir = cp_path
            elif tau in filename:
                target_dir = tau_path
            elif ti in filename:
                target_dir = ti_path
            else:
                continue

            source_path = os.path.join(contours_path, filename)
            target_path = os.path.join(target_dir, filename)
            shutil.move(source_path, target_path)

    def animate():

        source_dir = os.getcwd()
        sim_folder = os.path.join(source_dir, sim_name)

        revolve_path = os.path.join(sim_folder, "animations", "revolve")
        sweep_path = os.path.join(sim_folder, "animations", "sweep")

        for d in dim:
            res = ["ti", "cp"]
            for res in res:

                height = resolution_x
                width = resolution_y

                image_path = os.path.join(sweep_path, res, d)
                video_name = '{r} ({dim}-sweep)-{sim_name}.avi'.format(r = res, dim = d, sim_name = sim_name)

                images = [img for img in os.listdir(image_path) if img.endswith(".png")]
                images.sort(key=lambda x: int(re.search(r'-(\d+)\.png$', x).group(1)))

                frame = cv2.imread(os.path.join(image_path, images[0]))
                height, width, layer = frame.shape

                video = cv2.VideoWriter(video_name, 0, fps, (width, height))

                for image in images:
                    video.write(cv2.imread(os.path.join(image_path, image)))

                cv2.destroyAllWindows()
                video.release()


        orientation = ["top", "bottom"]
        for v in var:
            for o in orientation:
                height = resolution_x
                width = resolution_y

                image_path = os.path.join(revolve_path, v, o)
                video_name = '{r} ({orientation}-revolve)-{sim_name}.avi'.format(r = v, orientation = o, sim_name = sim_name)

                images = [img for img in os.listdir(image_path) if img.endswith(".png")]
                images.sort(key=lambda x: int(re.search(r'-(\d+)\.png$', x).group(1)))

                frame = cv2.imread(os.path.join(image_path, images[0]))
                height, width, layer = frame.shape

                video = cv2.VideoWriter(video_name, 0, fps, (width, height))

                for image in images:
                    video.write(cv2.imread(os.path.join(image_path, image)))

                cv2.destroyAllWindows()
                video.release()

    def front(r):
        graphics.views.restore_view(view_name = "right")
        graphics.views.camera.target(xyz = [-0.6, 0, 0.6])
        graphics.views.camera.roll(counter_clockwise = -90)
        graphics.views.camera.position(xyz = [125, 0, 7])
        graphics.views.camera.zoom(factor = 40)
        graphics.picture.save_picture(file_name="{result}-front-contour.png".format(result = r))
    def left(r):
        graphics.views.restore_view(view_name = "right")
        graphics.views.camera.roll(counter_clockwise = -90)
        graphics.views.camera.target(xyz = [-0.4, 0, 0.5])
        graphics.views.camera.position(xyz = [-0.4, 7.25, 0.5])
        graphics.views.camera.zoom(factor = 27.5)
        graphics.views.camera.roll(counter_clockwise = -2)
        graphics.picture.save_picture(file_name="{result}-left-contour.png".format(result = r))
    def back(r):
        graphics.views.restore_view(view_name = "left")
        graphics.views.camera.target(xyz = [-0.6, 0, 0.6])
        graphics.views.camera.roll(counter_clockwise = 90)
        graphics.views.camera.position(xyz = [-125, 0, 7])
        graphics.views.camera.zoom(factor = 40)
        graphics.picture.save_picture(file_name="{result}-back-contour.png".format(result = r))
    def bottom(r):
        graphics.views.restore_view(view_name = "back")
        graphics.views.camera.target(xyz = [-0.6, 0, 0.5])
        graphics.views.camera.roll(counter_clockwise = 180)
        graphics.views.camera.position(xyz = [-0.6, 0, -7])
        graphics.views.camera.zoom(factor = 22.5)
        graphics.picture.save_picture(file_name="{result}-bottom-contour.png".format(result = r))
    def top(r):
        graphics.views.restore_view(view_name = "front")
        graphics.views.camera.target(xyz = [-0.6, 0, 0.5])
        graphics.views.camera.roll(counter_clockwise = 180)
        graphics.views.camera.position(xyz = [-0.6, 0, 7])
        graphics.views.camera.zoom(factor = 22.5)
        graphics.picture.save_picture(file_name="{result}-top-contour.png".format(result = r))
    def iso(r):
        #iso 1,2
        graphics.views.restore_view(view_name = "right")
        graphics.views.camera.target(xyz = [-0.6, 0, 0.6])
        graphics.views.camera.roll(counter_clockwise = -90)
        graphics.views.camera.position(xyz = [125, 0, 7])
        graphics.views.camera.zoom(factor = 40)
        graphics.views.camera.orbit(right = 30)
        graphics.views.camera.orbit(up = 30)
        graphics.views.camera.target(xyz = [-0.6, 0, 0.5])
        graphics.views.camera.zoom(factor = -2)
        graphics.picture.save_picture(file_name="{result}-iso1-contour.png".format(result = r))

        graphics.views.camera.orbit(up = -60)
        graphics.picture.save_picture(file_name="{result}-iso2-contour.png".format(result = r))

        #iso 3,4
        graphics.views.restore_view(view_name = "right")
        graphics.views.camera.target(xyz = [-0.6, 0, 0.6])
        graphics.views.camera.roll(counter_clockwise = -90)
        graphics.views.camera.position(xyz = [125, 0, 7])
        graphics.views.camera.zoom(factor = 40)
        graphics.views.camera.orbit(right = 150)
        graphics.views.camera.orbit(up = 30)
        graphics.views.camera.target(xyz = [-0.6, 0, 0.5])
        graphics.views.camera.zoom(factor = -2)
        graphics.picture.save_picture(file_name="{result}-iso3-contour.png".format(result = r))

        graphics.views.camera.orbit(up = -60)
        graphics.picture.save_picture(file_name="{result}-iso4-contour.png".format(result = r))

    folders()

    set_fluent()

    create_planes()
    create_contours()
    print("Created Planes and Contours")

    for r in tqdm(res):
        set_contours(r)
    print("Surface Contours Complete")

    for r in tqdm(res):
            for s in tqdm(nums_s):
                revolve(s, r)
    print("Revolve Contours Complete")

    set_animations(ti)
    print("Turbulence Intensity Contours Complete")

    reset_plane_xyz()
    time.sleep(3)

    set_animations(cp)
    print("Pressure Coefficient Contours Complete")

    time.sleep(3)

    move_files()
    animate()

    source_dir = os.getcwd()
    destination_dir = os.path.join(source_dir, sim_name, "animations")

    for file in os.listdir(source_dir):
        if file.endswith(".avi"):
            
            source_path = os.path.join(source_dir, file)
            target_path = os.path.join(destination_dir, file)
            shutil.move(source_path, target_path)

    destination_dir = os.path.join(source_dir, sim_name, "results")

    for file in os.listdir(source_dir):
        if file.endswith(".out"):
            
            source_path = os.path.join(source_dir, file)
            target_path = os.path.join(destination_dir, file)
            shutil.move(source_path, target_path)

    time.sleep(5)
    run_time = (time.time() - start_time)
    print("Completed in {} seconds".format(run_time))

run_fluent()
