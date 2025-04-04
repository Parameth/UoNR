# add residuals to the post pro
# add force outputs to the files
# update the code to 24R2 or 25R1 for back support form 24R2
# remove the rem_sys.log file with the new commands from 24R2 (in documentation)
# create a solidworks and catia creation of this code to allow people to visualise the configuration
# auto adjust camera position
# revolve the contours of the surface plots on top and bottom, keep iso
# use cwd for folders and files


import os
import shutil
import cv2
import time
import re
from tqdm import tqdm
import ansys.fluent.core as pyfluent

start_time = time.time()
sim_name = "INSERT SIM NAME" #Insert Sim Name e.g. FCS4-MRF or FCS4
case_file_path = r"C:\\Users\\egypy1\\Documents\\Full Car Sim\\FCS4MOVINGWHEELS.cas.h5"

resolution_x    = 1920          #pixels
resolution_y    = 1080          #pixels
fps             = 15            #frames per second

num_frames_x    = 365           #number for frames in the x-direction (i) for the sweep animation (730)(365)
num_frames_y    = 75            #number for frames in the y-direction (j) for the sweep animation (150)(75)
num_frames_z    = 124           #number for frames in the z-direction (k) for the sweep animation (248)(124)

num_sweep_frames = 360
frame_spacing = 5e-3 #change frame spacing or number of frames, what resolution would be best?

#range values
ti_range = [0, 0.2]
cp_range = [-1.5, 0.5]
cf_range = [1.867737e-07, 0.0465] # possible to add custom selection of the range
tau_range = [0, 5]

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

ti = "turb-intensity"
cp = "pressure-coefficient"
cf = "skin-friction-coef"
tau = "wall-shear"

nums_x = range(1, (num_frames_x + 1))
nums_y = range(1, (num_frames_y + 1))
nums_z = range(1, (num_frames_z + 1))
nums_s = range(0, num_sweep_frames)

res = [ti, cp, cf, tau] #outlines results
dim = ["x", "y", "z"]

fluent = pyfluent.launch_fluent(
    mode = "solver",
    processor_count = 10,
    start_transcript = False
)
print("FLUENT opened")

fluent.file.read_case_data(file_name = case_file_path)
print("Case and data file read")

surfaces = fluent.results.surfaces
graphics = fluent.results.graphics

def set_fluent():
    if graphics.picture.use_window_resolution.is_active():
        graphics.picture.use_window_resolution = False
    graphics.picture.x_resolution = resolution_x 
    graphics.picture.y_resolution = resolution_y
    fluent.tui.preferences.graphics.graphics_effects.grid_plane_enabled("no")
    fluent.tui.preferences.graphics.graphics_effects.reflections_enabled("no")
    fluent.tui.preferences.graphics.graphics_effects.shadow_map_enabled("no")
    fluent.tui.preferences.graphics.graphics_effects.simple_shadows_enabled("no")
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
    fluent.results.surfaces.plane_surface["x-sweep"].x = start_dim[0] - (i*(dist[0]/num_frames_x))
def move_plane_y(j):
    fluent.results.surfaces.plane_surface["y-sweep"].y = start_dim[1] + (j*(dist[1]/num_frames_y))
def move_plane_z(k):
    fluent.results.surfaces.plane_surface["z-sweep"].z = start_dim[2] + (k*(dist[2]/num_frames_z))

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
        "front_wheel-contact_region-src",
        "rear_wheel-contact_region_2-src"
    ]

# add camera position as well as target 
def x_sweep(i, r):
    graphics.contour["x-contour"].display()
    graphics.views.restore_view(view_name = "right")
    graphics.views.auto_scale()
    graphics.views.camera.target(xyz = [start_dim[0] - (i-1)*(dist[0]/num_frames_x), 0, 1])
    graphics.views.camera.roll(counter_clockwise = -90)
    graphics.views.camera.zoom(factor = 10)
    graphics.picture.save_picture(file_name="{result}-x_contour-{iteration}.png".format(result = r, iteration = i))

    move_plane_x(i)
def y_sweep(j, r):
    graphics.contour["y-contour"].display()
    graphics.views.restore_view(view_name = "top")
    graphics.views.auto_scale()
    graphics.views.camera.target(xyz = [-0.8, start_dim[1]  + (j-1)*(dist[1]/num_frames_y), 0.97])
    graphics.views.camera.zoom(factor = 25)
    graphics.picture.save_picture(file_name="{result}-y_contour-{iteration}.png".format(result = r, iteration = j))

    move_plane_y(j)
def z_sweep(k, r):
    graphics.contour["z-contour"].display()
    graphics.views.restore_view(view_name = "front")
    graphics.views.auto_scale()
    graphics.views.camera.target(xyz = [-0.5, 0, start_dim[2]  + (k-1)*(dist[2]/num_frames_z)])
    graphics.views.camera.roll(counter_clockwise = 180)
    graphics.views.camera.zoom(factor = 20)
    graphics.picture.save_picture(file_name="{result}-z_contour-{iteration}.png".format(result = r, iteration = k))

    move_plane_z(k)

def set_animations(r):
    for d in dim:
        graphics.contour["{}-contour".format(d)].field = r

        graphics.contour["{}-contour".format(d)].range_option.option = "auto-range-off"
        graphics.contour["{}-contour".format(d)].range_option.auto_range_off.clip_to_range = False

        if r == ti:
            graphics.contour["{}-contour".format(d)].range_option.auto_range_off(minimum = min(ti_range))
            graphics.contour["{}-contour".format(d)].range_option.auto_range_off(maximum = max(ti_range))

        else:
            graphics.contour["{}-contour".format(d)].range_option.auto_range_off(minimum = min(cp_range))
            graphics.contour["{}-contour".format(d)].range_option.auto_range_off(maximum = max)

    for i in tqdm(nums_x, desc = "x-contours"):
        x_sweep(i, r)
    print("X is Complete") 

    time.sleep(3)

    fluent.file.read_journal(file_name_list = ["C:/Users/egypy1/Documents/Full Car Sim/rem_sys.log"])
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
        graphics.contour["car"].range_option.auto_range_off(minimum = min(ti_range))
        graphics.contour["car"].range_option.auto_range_off(maximum = max(ti_range))
    elif r == cp:
        graphics.contour["car"].range_option.auto_range_off(minimum = min(cp_range))
        graphics.contour["car"].range_option.auto_range_off(maximum = max(cp_range))
    elif r == cf:
        graphics.contour["car"].range_option.auto_range_off(minimum = min(cf_range))
        graphics.contour["car"].range_option.auto_range_off(maximum = max(cf_range))
    else:
        graphics.contour["car"].range_option.auto_range_off(minimum = min(tau_range))
        graphics.contour["car"].range_option.auto_range_off(maximum = max(tau_range))

    front(r)
    left(r)
    back(r)
    bottom(r)
    top(r)
    iso(r)

def move_files_ti():
    source_dir = "C:\\Users\\egypy1\\Documents\\Full Car Sim"

    x_dir = os.path.join(source_dir, "ti_x")
    y_dir = os.path.join(source_dir, "ti_y")
    z_dir = os.path.join(source_dir, "ti_z")

    for filename in tqdm(os.listdir(source_dir), desc = "Moving Ti Files"):
        if ti in filename:
            if "-x" in filename:
                target_dir = x_dir
            elif "-y" in filename:
                target_dir = y_dir
            elif "-z" in filename:
                target_dir = z_dir
            else:
                continue

            source_path = os.path.join(source_dir, filename)
            target_path = os.path.join(target_dir, filename)
            shutil.move(source_path, target_path)
    print("Ti Files Moved")
def move_files_cp():
    source_dir = "C:\\Users\\egypy1\\Documents\\Full Car Sim"

    x_dir = os.path.join(source_dir, "cp_x")
    y_dir = os.path.join(source_dir, "cp_y")
    z_dir = os.path.join(source_dir, "cp_z")

    for filename in tqdm(os.listdir(source_dir), desc = "Moving Cp Files"):
        if cp in filename:
            if "-x" in filename:
                target_dir = x_dir
            elif "-y" in filename:
                target_dir = y_dir
            elif "-z" in filename:
                target_dir = z_dir
            else:
                continue

            source_path = os.path.join(source_dir, filename)
            target_path = os.path.join(target_dir, filename)
            shutil.move(source_path, target_path)
    print("Cp Files Moved")

def make_animation_ti():
    for d in dim:
        height = resolution_x
        width = resolution_y

        image_folder = "C:\\Users\\egypy1\\Documents\\Full Car Sim\\ti_{}".format(d)
        video_name = 'Turbulence Intensity ({dim}-sweep) -{sim_name}.avi'.format(dim = d, sim_name = sim_name )

        images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
        images.sort(key=lambda x: int(re.search(r'-(\d+)\.png$', x).group(1)))

        frame = cv2.imread(os.path.join(image_folder, images[0]))
        height, width, layer = frame.shape

        video = cv2.VideoWriter(video_name, 0, fps, (width, height))

        for image in images:
            video.write(cv2.imread(os.path.join(image_folder, image)))

        cv2.destroyAllWindows()
        video.release()
def make_animation_cp():
    for d in dim:
        height = resolution_x
        width = resolution_y

        image_folder = "C:\\Users\\egypy1\\Documents\\Full Car Sim\\cp_{}".format(d)
        video_name = 'Pressure Coefficient ({dim}-sweep) -{sim_name}.avi'.format(dim = d, sim_name = sim_name )

        images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
        images.sort(key=lambda x: int(re.search(r'-(\d+)\.png$', x).group(1)))

        frame = cv2.imread(os.path.join(image_folder, images[0]))
        height, width, layer = frame.shape

        video = cv2.VideoWriter(video_name, 0, fps, (width,height))

        for image in images:
            video.write(cv2.imread(os.path.join(image_folder, image)))

        cv2.destroyAllWindows()
        video.release()

def front(r):
    graphics.contour["car"].display()
    graphics.views.restore_view(view_name = "right")
    graphics.views.camera.target(xyz = target_pos)
    graphics.views.camera.roll(counter_clockwise = -90)
    graphics.views.camera.position(xyz = [125, 0, 7])
    graphics.views.camera.zoom(factor = 40)
    graphics.picture.save_picture(file_name="{result}-front.png".format(result = r))
def left(r):
    graphics.contour["car"].display()
    graphics.views.restore_view(view_name = "right")
    graphics.views.camera.roll(counter_clockwise = -90)
    graphics.views.camera.target(xyz = [-0.4, 0, 0.5])
    graphics.views.camera.position(xyz = [-0.4, 7.25, 0.5])
    graphics.views.camera.zoom(factor = 27.5)
    graphics.views.camera.roll(counter_clockwise = -2)
    graphics.picture.save_picture(file_name="{result}-left.png".format(result = r))
def back(r):
    graphics.contour["car"].display()
    graphics.views.restore_view(view_name = "left")
    graphics.views.camera.target(xyz = target_pos)
    graphics.views.camera.roll(counter_clockwise = 90)
    graphics.views.camera.position(xyz = [-125, 0, 7])
    graphics.views.camera.zoom(factor = 40)
    graphics.picture.save_picture(file_name="{result}-back.png".format(result = r))
def bottom(r):
    graphics.contour["car"].display()
    graphics.views.restore_view(view_name = "back")
    graphics.views.camera.target(xyz = target_pos)
    graphics.views.camera.roll(counter_clockwise = 180)
    graphics.views.camera.position(xyz = [-0.6, 0, -7])
    graphics.views.camera.zoom(factor = 22.5)
    graphics.picture.save_picture(file_name="{result}-bottom.png".format(result = r))
def top(r):
    graphics.contour["car"].display()
    graphics.views.restore_view(view_name = "front")
    graphics.views.camera.target(xyz = target_pos)
    graphics.views.camera.roll(counter_clockwise = 180)
    graphics.views.camera.position(xyz = [-0.6, 0, 7])
    graphics.views.camera.zoom(factor = 22.5)
    graphics.picture.save_picture(file_name="{result}-top.png".format(result = r))
def iso(r):
    #iso 1,2
    graphics.contour["car"].display()
    graphics.views.restore_view(view_name = "right")
    graphics.views.camera.target(xyz = target_pos)
    graphics.views.camera.roll(counter_clockwise = -90)
    graphics.views.camera.position(xyz = [125, 0, 7])
    graphics.views.camera.zoom(factor = 40)
    graphics.views.camera.orbit(right = 30)
    graphics.views.camera.orbit(up = 30)
    graphics.views.camera.target(xyz = target_pos)
    graphics.views.camera.zoom(factor = -2)
    graphics.picture.save_picture(file_name="{result}-iso1.png".format(result = r))

    graphics.views.camera.orbit(up = -60)
    graphics.picture.save_picture(file_name="{result}-iso2.png".format(result = r))

    #iso 3,4
    graphics.contour["car"].display()
    graphics.views.restore_view(view_name = "right")
    graphics.views.camera.target(xyz = target_pos)
    graphics.views.camera.roll(counter_clockwise = -90)
    graphics.views.camera.position(xyz = [125, 0, 7])
    graphics.views.camera.zoom(factor = 40)
    graphics.views.camera.orbit(right = 150)
    graphics.views.camera.orbit(up = 30)
    graphics.views.camera.target(xyz = target_pos)
    graphics.views.camera.zoom(factor = -2)
    graphics.picture.save_picture(file_name="{result}-iso3.png".format(result = r))

    graphics.views.camera.orbit(up = -60)
    graphics.picture.save_picture(file_name="{result}-iso4.png".format(result = r))

set_fluent()

create_planes()
create_contours()
print("Created Planes and Contours")

# for r in tqdm(res):
#     set_contours(r)
# print("Surface Contours Complete")

# set_animations(ti)
# move_files_ti()
# print("Turbulence Intensity Contours Complete")

# reset_plane_xyz()
# time.sleep(3)

# set_animations(cp)
# move_files_cp()
# print("Pressure Coefficient Contours Complete")

# time.sleep(3)

# make_animation_ti()
# make_animation_cp()

# time.sleep(5)
# run_time = (time.time() - start_time)
# print("Animations Completed in {} seconds".format(run_time))

def revolve_top(s,r):
    graphics.contour["car"].display()
    graphics.views.restore_view(view_name = "right")
    graphics.views.camera.target(xyz = target_pos)
    graphics.views.camera.roll(counter_clockwise = -90)
    graphics.views.camera.position(xyz = [125, 0, 7])
    graphics.views.camera.zoom(factor = 40)
    graphics.views.camera.orbit(right = s/nums_s)
    graphics.views.camera.orbit(up = 30)
    graphics.views.camera.target(xyz = target_pos)
    graphics.views.camera.zoom(factor = -2)
    graphics.picture.save_picture(file_name="{result}-top_sweep_{iteration}.png".format(result = r, iteration = s))

for s in nums_s:
    revolve_top(s, ti)
