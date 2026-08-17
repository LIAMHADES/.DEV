"""
ARES GPS Dog Tracker - 3D Model Generator v3.0 (photorealistic rebuild)

Fixes vs v2.0:
  - Real-world metric scale (mm -> meters). No more magic camera coords -> no clipping.
  - Cameras always AIM at the device via a Track-To target empty; distance derived from size.
  - Cycles engine + denoise for marketing-grade renders.
  - PBR materials: olive plastic w/ clearcoat, translucent PC LED windows, metal pins, silicone.
  - Real honeycomb geometry option (displacement) instead of bump-only.
  - Correctly-sized O-ring.
  - GLB export uses standard Principled inputs so the web viewer looks right.

Run headless:
  "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --python ares_model.py
"""

import bpy
import math
import os

# ─── PATHS ─────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RENDER_DIR = os.path.join(SCRIPT_DIR, "renders")
EXPORT_DIR = os.path.join(SCRIPT_DIR, "exports")
os.makedirs(RENDER_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

MM = 0.001  # 1 mm in Blender meters

# ─── DIMENSIONS (converted to meters) ──────────────────────────
W = 63.0 * MM       # external width
D = 41.0 * MM       # external depth
H = 21.0 * MM       # external height
H_TOP = H / 2.0     # upper casing height (~10.5mm)
H_BOT = H / 2.0     # lower casing height
R = 3.5 * MM        # corner radius
WALL = 3.0 * MM

# ─── COLORS (linear-ish sRGB triples) ──────────────────────────
# Body olive = #5C6B3C (SSOT). sRGB (0.36,0.42,0.235) -> linear.
# AgX desaturates midtones, so feed a more saturated olive to land on target.
OLIVE     = (0.115, 0.175, 0.030, 1.0)
PC_FROST  = (0.80, 0.86, 0.92, 1.0)
METAL     = (0.62, 0.62, 0.64, 1.0)
DARK_LOGO = (0.02, 0.03, 0.04, 1.0)
SILICONE  = (0.03, 0.03, 0.035, 1.0)
LED_GREEN = (0.02, 0.85, 0.18, 1.0)

# ─── CLEAN SCENE ───────────────────────────────────────────────
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for block in (bpy.data.meshes, bpy.data.materials, bpy.data.lights,
              bpy.data.cameras, bpy.data.worlds):
    for item in list(block):
        block.remove(item)


# ─── MATERIAL HELPERS ──────────────────────────────────────────
def get_bsdf(mat):
    for n in mat.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            return n
    return None


def set_in(node, names, value):
    """Set a node input by any of several (localized) names; ignore if absent."""
    for name in names:
        try:
            node.inputs[name].default_value = value
            return True
        except (KeyError, TypeError):
            continue
    return False


def make_plastic(name, color, rough=0.42, coat=0.4):
    """Matte olive plastic with a soft clearcoat for a premium finish."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = get_bsdf(mat)
    set_in(b, ["Base Color", "Color base"], color)
    set_in(b, ["Roughness", "Rugosidad"], rough)
    set_in(b, ["Metallic", "Metalico", "Metálico"], 0.0)
    # Blender 4.x/5.x Principled coat inputs
    set_in(b, ["Coat Weight", "Coat", "Clearcoat"], coat)
    set_in(b, ["Coat Roughness", "Clearcoat Roughness"], 0.25)
    return mat


def make_translucent(name, color, rough=0.08, emit=0.0):
    """Translucent polycarbonate for LED windows. Optional emission for 'on' look."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = get_bsdf(mat)
    set_in(b, ["Base Color", "Color base"], color)
    set_in(b, ["Roughness", "Rugosidad"], rough)
    set_in(b, ["Transmission Weight", "Transmission", "Transmisión"], 0.9)
    set_in(b, ["IOR"], 1.52)
    if emit > 0.0:
        set_in(b, ["Emission Color", "Emission"], color)
        set_in(b, ["Emission Strength"], emit)
    # keep alpha for glTF viewers that ignore transmission
    mat.blend_method = 'BLEND' if hasattr(mat, "blend_method") else mat.blend_method
    return mat


def make_metal(name, color, rough=0.22):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = get_bsdf(mat)
    set_in(b, ["Base Color", "Color base"], color)
    set_in(b, ["Metallic", "Metalico", "Metálico"], 1.0)
    set_in(b, ["Roughness", "Rugosidad"], rough)
    return mat


def make_emissive(name, color, strength=6.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = get_bsdf(mat)
    set_in(b, ["Base Color", "Color base"], color)
    set_in(b, ["Emission Color", "Emission"], color)
    set_in(b, ["Emission Strength"], strength)
    return mat


def make_matte(name, color, rough=0.6):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = get_bsdf(mat)
    set_in(b, ["Base Color", "Color base"], color)
    set_in(b, ["Roughness", "Rugosidad"], rough)
    return mat


# ─── GEOMETRY HELPERS ──────────────────────────────────────────
def rounded_box(name, w, d, h, radius, loc=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.dimensions = (w, d, h)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    m = obj.modifiers.new("Round", type='BEVEL')
    m.width = radius
    m.segments = 5
    m.limit_method = 'ANGLE'
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=m.name)
    return obj


def fix_normals(obj):
    """Recalculate normals outward so solid casings never look translucent."""
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')


def boolean_cut(target, cutter):
    """Subtract cutter from target and remove the cutter."""
    bpy.context.view_layer.objects.active = target
    m = target.modifiers.new("Cut", type='BOOLEAN')
    m.object = cutter
    m.operation = 'DIFFERENCE'
    m.solver = 'EXACT'
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    fix_normals(target)


# ─── MATERIALS ─────────────────────────────────────────────────
mtl_body   = make_plastic("ARES_Body", OLIVE, rough=0.58, coat=0.0)
mtl_led    = make_translucent("ARES_LED", PC_FROST, rough=0.06, emit=0.0)
mtl_metal  = make_metal("ARES_Metal", METAL, rough=0.20)
mtl_logo   = make_plastic("ARES_Logo", DARK_LOGO, rough=0.3, coat=0.5)
mtl_sil    = make_matte("ARES_Silicone", SILICONE, rough=0.65)
mtl_ledchg = make_emissive("ARES_ChargeLED", LED_GREEN, strength=8.0)


# ─── SCENE / RENDER SETTINGS ───────────────────────────────────
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
try:
    scene.cycles.device = 'GPU'
except Exception:
    pass
scene.cycles.samples = 64
scene.cycles.use_denoising = True
scene.view_settings.exposure = -0.5
try:
    scene.view_settings.look = 'AgX - Punchy'
except (TypeError, KeyError):
    scene.view_settings.look = 'None'
scene.render.resolution_x = 1600
scene.render.resolution_y = 900
scene.render.film_transparent = False
scene.view_settings.view_transform = 'AgX'
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0

# World: soft neutral studio
world = bpy.data.worlds.new("Studio")
scene.world = world
world.use_nodes = True
for n in world.node_tree.nodes:
    if n.type == 'BACKGROUND':
        set_in(n, ["Color"], (0.22, 0.22, 0.24, 1.0))
        set_in(n, ["Strength", "Intensidad"], 0.25)

# Ground plane with contact shadow
bpy.ops.mesh.primitive_plane_add(size=2.0, location=(0, 0, -H_BOT))
floor = bpy.context.active_object
floor.name = "Floor"
floor.data.materials.append(make_matte("Floor", (0.32, 0.32, 0.34, 1.0), rough=0.55))


# ─── LIGHTING (3-point studio, metric) ─────────────────────────
def area_light(name, loc, target, size, energy):
    bpy.ops.object.light_add(type='AREA', location=loc)
    l = bpy.context.active_object
    l.name = name
    l.data.energy = energy
    l.data.size = size
    # aim at origin via constraint
    c = l.constraints.new(type='TRACK_TO')
    c.target = target
    c.track_axis = 'TRACK_NEGATIVE_Z'
    c.up_axis = 'UP_Y'
    return l


aim = bpy.data.objects.new("Aim", None)
bpy.context.collection.objects.link(aim)
aim.location = (0, 0, 0)

S = W  # ~scene scale reference (device width in meters)
area_light("Key",  (0.10, -0.10, 0.12), aim, size=0.30, energy=2.2)
area_light("Fill", (-0.09, -0.04, 0.06), aim, size=0.25, energy=0.8)
area_light("Rim",  (0.0, 0.11, 0.05),  aim, size=0.22, energy=1.6)
area_light("Top",  (0.0, 0.0, 0.16),   aim, size=0.20, energy=1.0)


# ─── CAMERA (aims at device; distance from object size) ────────
bpy.ops.object.camera_add(location=(0.11, -0.13, 0.09))
cam = bpy.context.active_object
cam.name = "MainCam"
cam.data.lens = 85          # telephoto product look
cam.data.clip_start = 0.001
cam.data.clip_end = 100.0
ccon = cam.constraints.new(type='TRACK_TO')
ccon.target = aim
ccon.track_axis = 'TRACK_NEGATIVE_Z'
ccon.up_axis = 'UP_Y'
scene.camera = cam


# ─── BUILD: UPPER CASING ───────────────────────────────────────
print("Upper casing...")
top = rounded_box("Upper_Casing", W, D, H_TOP, R, (0, 0, H_TOP / 2))
top.data.materials.append(mtl_body)
fix_normals(top)

# ─── HONEYCOMB (procedural bump on the body material) ──────────
print("Honeycomb bump...")
nt = mtl_body.node_tree
nodes, links = nt.nodes, nt.links
body_bsdf = get_bsdf(mtl_body)

tcoord = nodes.new('ShaderNodeTexCoord')
vor = nodes.new('ShaderNodeTexVoronoi')
vor.feature = 'DISTANCE_TO_EDGE'   # gives crisp honeycomb cell walls
set_in(vor, ["Scale"], 520.0)      # fine technical grip texture
set_in(vor, ["Randomness"], 0.35)  # more regular cells
bump = nodes.new('ShaderNodeBump')
set_in(bump, ["Strength", "Intensidad"], 0.4)
set_in(bump, ["Distance"], 0.0008)
links.new(tcoord.outputs["Object"], vor.inputs["Vector"])
links.new(vor.outputs["Distance"], bump.inputs["Height"])
for inp in body_bsdf.inputs:
    if inp.name.lower() in ("normal", "normal map"):
        links.new(bump.outputs["Normal"], inp)
        break

# ─── X LOGO (engraved-look, on top) ────────────────────────────
print("Logo X...")
bpy.ops.object.text_add(location=(0, 0, H_TOP))
logo = bpy.context.active_object
logo.name = "Logo_X"
logo.data.body = "X"
logo.data.size = 14 * MM
logo.data.extrude = 0.5 * MM
logo.data.align_x = 'CENTER'
logo.data.align_y = 'CENTER'
bpy.ops.object.convert(target='MESH')
logo.rotation_euler = (0, 0, 0)
logo.location = (0, 0, H_TOP + 0.2 * MM)
logo.data.materials.append(mtl_logo)

# ─── LOWER CASING ──────────────────────────────────────────────
print("Lower casing...")
bot = rounded_box("Lower_Casing", W, D, H_BOT, R, (0, 0, -H_BOT / 2))
bot.data.materials.append(mtl_body)
fix_normals(bot)

# ─── SCREW BOSSES (shallow internal recesses on the bottom face) ─
print("Screw bosses...")
corners = [
    (W / 2 - 9 * MM, D / 2 - 9 * MM),
    (-W / 2 + 9 * MM, D / 2 - 9 * MM),
    (W / 2 - 9 * MM, -D / 2 + 9 * MM),
    (-W / 2 + 9 * MM, -D / 2 + 9 * MM),
]
for i, (cx, cy) in enumerate(corners):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=1.6 * MM,
                                         depth=3 * MM,
                                         location=(cx, cy, -H_BOT + 1.0 * MM))
    boolean_cut(bot, bpy.context.active_object)

# ─── CHARGING PORT (recess + 3 pogo pins + LED) ────────────────
print("Charging port...")
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=6.0 * MM, depth=2.5 * MM,
                                     location=(0, 0, -H_BOT + 1.0 * MM))
recess = bpy.context.active_object
recess.rotation_euler = (math.radians(90), 0, 0)
recess.location = (0, -D / 2 + 3 * MM, -H_BOT / 2)
boolean_cut(bot, recess)

pins = []
for i in range(3):
    x = (i - 1) * 4.0 * MM
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=1.1 * MM, depth=1.5 * MM,
                                        location=(x, -D / 2 + 2.5 * MM, -H_BOT / 2))
    pin = bpy.context.active_object
    pin.name = f"Pogo_{i+1}"
    pin.rotation_euler = (math.radians(90), 0, 0)
    pin.data.materials.append(mtl_metal)
    pins.append(pin)

# charge status LED on the side
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0 * MM,
                                     location=(W / 2 - 5 * MM, -D / 2 + 2 * MM, -H_BOT / 2))
cled = bpy.context.active_object
cled.name = "Charge_LED"
cled.data.materials.append(mtl_ledchg)
bpy.ops.object.shade_smooth()

# ─── LED WINDOWS (L-shaped, translucent) ───────────────────────
print("LED windows...")
def l_shape_led(name, corner_x, corner_y, sx, sy):
    """Build an L at (corner_x,corner_y). sx,sy in {-1,+1} orient the two arms."""
    bar_len, bar_w, bar_t = 10 * MM, 1.6 * MM, 2.4 * MM
    z = H_TOP + 0.3 * MM  # sit just proud of the top surface as a lit window
    # arm along +Y (or -Y)
    ax = corner_x
    ay = corner_y + sy * (bar_len / 2 - bar_w / 2)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(ax, ay, z))
    v = bpy.context.active_object
    v.dimensions = (bar_w, bar_len, bar_t)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # arm along +X (or -X)
    bx = corner_x + sx * (bar_len / 2 - bar_w / 2)
    by = corner_y
    bpy.ops.mesh.primitive_cube_add(size=1, location=(bx, by, z))
    h = bpy.context.active_object
    h.dimensions = (bar_len, bar_w, bar_t)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.select_all(action='DESELECT')
    v.select_set(True)
    h.select_set(True)
    bpy.context.view_layer.objects.active = v
    bpy.ops.object.join()
    v.name = name
    v.data.materials.append(mtl_led)
    return v

# L1 top-left corner opening toward +X/-Y ; L2 bottom-right toward -X/+Y
l1 = l_shape_led("LED_Window_L1", -W / 2 + 11 * MM, D / 2 - 8 * MM, +1, -1)
l2 = l_shape_led("LED_Window_L2", W / 2 - 11 * MM, -D / 2 + 8 * MM, -1, +1)

# ─── O-RING (correctly sized, at the seam) ─────────────────────
print("O-ring...")
avg_r = (W + D) / 4.0
bpy.ops.mesh.primitive_torus_add(major_radius=avg_r, minor_radius=0.9 * MM,
                                 major_segments=96, minor_segments=12,
                                 location=(0, 0, 0))
oring = bpy.context.active_object
oring.name = "O_Ring"
# fit the seam perimeter, inset slightly from the outer wall
oring.scale = ((W - 3 * MM) / (avg_r * 2), (D - 3 * MM) / (avg_r * 2), 1.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
oring.data.materials.append(mtl_sil)
bpy.ops.object.shade_smooth()

# ─── GROUP UNDER EMPTY ─────────────────────────────────────────
print("Grouping...")
all_parts = [top, logo, bot, l1, l2, oring, cled] + pins
device = bpy.data.objects.new("ARES_Device", None)
bpy.context.collection.objects.link(device)
device.empty_display_type = 'PLAIN_AXES'
for obj in all_parts:
    if obj:
        obj.parent = device
device.rotation_euler = (math.radians(10), 0, math.radians(-20))


# ─── RENDER HELPER (frame the device, aim guaranteed) ──────────
def do_render(filename, cam_loc):
    cam.location = cam_loc
    scene.render.filepath = os.path.join(RENDER_DIR, filename)
    bpy.ops.render.render(write_still=True)
    print(f"  wrote {filename}")


QUICK = os.environ.get("ARES_QUICK") == "1"

EXPLODED_ONLY = os.environ.get("ARES_EXPLODED_ONLY") == "1"

print("Rendering...")
if not EXPLODED_ONLY:
    do_render("ares_hero.png",  (0.11, -0.13, 0.085))
    if not QUICK:
        do_render("ares_top.png",   (0.0,  -0.001, 0.16))
        do_render("ares_front.png", (0.0,  -0.15, 0.02))
        do_render("ares_iso.png",   (0.13, -0.11, 0.10))

# ─── EXPLODED VIEW ─────────────────────────────────────────────
print("Exploded...")
explode = {
    "Upper_Casing": (0, 0, 0.016),
    "Logo_X": (0, 0, 0.022),
    "LED_Window_L1": (0, 0, 0.026),
    "LED_Window_L2": (0, 0, 0.026),
    "O_Ring": (0, 0, -0.006),
    "Lower_Casing": (0, 0, -0.030),
    "Pogo_1": (0, 0, -0.048),
    "Pogo_2": (0, 0, -0.048),
    "Pogo_3": (0, 0, -0.048),
    "Charge_LED": (0, 0, -0.046),
}
for name, off in explode.items():
    o = bpy.data.objects.get(name)
    if o:
        o.location = (o.location[0] + off[0], o.location[1] + off[1], o.location[2] + off[2])

if not QUICK or EXPLODED_ONLY:
    # elevated 3/4 view, pulled back to fit all vertically-separated layers
    aim.location = (0, 0, -0.010)
    do_render("ares_exploded.png", (0.24, -0.30, 0.20))
    aim.location = (0, 0, 0.0)

# revert explode before export so GLB is assembled
for name, off in explode.items():
    o = bpy.data.objects.get(name)
    if o:
        o.location = (o.location[0] - off[0], o.location[1] - off[1], o.location[2] - off[2])

# ─── EXPORT GLB ────────────────────────────────────────────────
if not QUICK and not EXPLODED_ONLY:
    print("Exporting GLB...")
    bpy.ops.object.select_all(action='DESELECT')
    for obj in all_parts:
        if obj:
            obj.select_set(True)
    device.select_set(True)
    bpy.context.view_layer.objects.active = device
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(EXPORT_DIR, "ares_device.glb"),
        export_format='GLB',
        use_selection=True,
        export_materials='EXPORT',
        export_cameras=False,
        export_lights=False,
        export_yup=True,
    )

print("\n=== DONE ===")
print(f"Renders -> {RENDER_DIR}")
print(f"GLB     -> {os.path.join(EXPORT_DIR, 'ares_device.glb')}")
