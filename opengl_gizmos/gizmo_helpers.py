import bpy
import mathutils
import gpu

def helper_shader():
    """Returns a GPU shader for viewport helper geometry"""
    vertex_shader = '''
        uniform mat4 ModelViewProjectionMatrix;

        in vec3 pos;
        out vec3 position;
        out vec3 ec_pos;

        void main()
        {
            position = pos;
            gl_Position = ModelViewProjectionMatrix * vec4(pos, 1.0f);
            ec_pos = gl_Position.xyz;
        }
    '''

    fragment_shader = '''
        uniform vec4 color;
        uniform float normal_shading;

        in vec3 position;
        in vec3 ec_pos;

        void main()
        {
            vec3 ec_normal = normalize(cross(dFdx(ec_pos),dFdy(ec_pos)));//dFdx(world_pos), dFdy(world_pos));
            float shade = (ec_normal.x + ec_normal.y + ec_normal.z) / 3 + 1 - normal_shading;
            float cshade = clamp(shade, 0.0, 1.0);
            gl_FragColor = vec4(cshade * color.xyz, color.w);
        }
    '''
    return gpu.types.GPUShader(vertex_shader, fragment_shader)

def multiply_vectors(vec_one, vec_two):
    """Helper function to multiply two mathutils vectors"""
    return mathutils.Vector((vec_one.x * vec_two.x, vec_one.y * vec_two.y, vec_one.z * vec_two.z))

def add_vectors(vec_one, vec_two):
    """Helper function to add two mathutils vectors"""
    return mathutils.Vector((vec_one.x + vec_two.x, vec_one.y + vec_two.y, vec_one.z + vec_two.z))

def helper_shape(obj, vertices, triangles):
    """Transforms vertices and triangles to match an object's transformations"""
    o_matrix = obj.matrix_world
    translate = o_matrix.to_translation()
    scale = o_matrix.to_scale()
    o_matrix = o_matrix.to_3x3()
    shape = []
    for vtx_s in vertices:
        vtx_r = multiply_vectors(vtx_s, scale)
        vtx_r.rotate(o_matrix)
        vtx_t = add_vectors(vtx_r, translate)
        shape.append(vtx_t)
    return shape, triangles

def plane_shape(obj):
    """Basic geometry of a plane"""
    base_shape = [mathutils.Vector((-.50, 0, 0)),
                  mathutils.Vector((-.50, 1.00, 0)),
                  mathutils.Vector((.50, 1.00, 0)),
                  mathutils.Vector((.50, 0, 0))]
    triangles = ((0, 1, 2), (0, 2, 3))
    return helper_shape(obj, base_shape, triangles)

def snap_shape(obj):
    """Basic geometry of a snap node"""
    base_shape = [mathutils.Vector((-.062771, -0.062771, 0.1000)),
                  mathutils.Vector((-.062771, 0.062771, 0.1000)),
                  mathutils.Vector((-0.1000, -0.1000, -0.1000)),
                  mathutils.Vector((-0.1000, 0.1000, -0.1000)),
                  mathutils.Vector((0.062771, -0.062771, 0.1000)),
                  mathutils.Vector((0.062771, 0.062771, 0.1000)),
                  mathutils.Vector((0.1000, -0.1000, -0.1000)),
                  mathutils.Vector((0.1000, 0.1000, -0.1000)),
                  mathutils.Vector((0.1000, 0.099407, -0.1000)),
                  mathutils.Vector((0.1000, 0.1000, -0.099101)),
                  mathutils.Vector((0.0225, .177369, 0.0225)),
                  mathutils.Vector((-0.1000, -0.1000, 0.1000)),
                  mathutils.Vector((-0.1000, 0.1000, 0.1000)),
                  mathutils.Vector((0.1000, 0.1000, 0.1000)),
                  mathutils.Vector((0.1000, -0.1000, 0.1000)),
                  mathutils.Vector((-0.062771, -0.062771, 0.306351)),
                  mathutils.Vector((-0.062771, 0.062771, 0.306351)),
                  mathutils.Vector((0.062771, 0.062771, 0.306351)),
                  mathutils.Vector((0.062771, -0.062771, 0.306351))]
    triangles = ((11, 2, 12), (8, 7, 3), (14, 13, 9),
                 (5, 17, 1), (2, 11, 6), (9, 10, 7),
                 (13, 10, 9), (7, 8, 9), (12, 3, 10),
                 (12, 10, 13), (0, 11, 1), (5, 13, 4),
                 (4, 14, 0), (1, 12, 5), (18, 15, 17),
                 (4, 18, 5), (0, 15, 4), (1, 16, 0),
                 (2, 3, 12), (8, 2, 6), (8, 3, 2),
                 (9, 6, 14), (9, 8, 6), (17, 16, 1),
                 (11, 14, 6), (10, 3, 7), (11, 12, 1),
                 (13, 14, 4), (14, 11, 0), (12, 13, 5),
                 (15, 16, 17), (18, 17, 5), (15, 18, 4),
                 (16, 15, 0))
    return helper_shape(obj, base_shape, triangles)

def get_items_by_type_suffix(o_type="EMPTY", o_suffix=""):
    """Returns a list of objects from the current scene by type and suffix"""
    scene_objs = bpy.context.scene.objects
    objects = []
    for obj in scene_objs:
        if obj.type == o_type and obj.name.lower().endswith(o_suffix.lower()):
            objects.append(obj)
    return objects

def get_plane_items():
    """Returns a list of all cover items (marked with _plane suffix)"""
    return get_items_by_type_suffix(o_suffix="_plane")

def get_snap_items():
    """Returns a list of all snap items (marked with _snap suffix)"""
    return get_items_by_type_suffix(o_suffix="_snap")
