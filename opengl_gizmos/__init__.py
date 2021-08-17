import bpy
import gpu
from gpu_extras.batch import batch_for_shader
import bgl
import blf
from . import gizmo_helpers

bl_info = { # pylint: disable=invalid-name
    "name" : "OpenGL Gizmos",
    "author" : "Frieder Erdmann",
    "description" : "Renders gizmos to display orientation in Blender",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "category" : "Generic"
}

def add_to_viewports():
    """Call the operator to add geometry to viewports"""
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            bpy.ops.opengl.helper_gizmos({'area': area}, 'INVOKE_DEFAULT')
            break

def draw_callback_px(self, context):
    """Callback Method for frame rendering"""
    bgl.glEnable(bgl.GL_DEPTH_TEST)
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glCullFace(bgl.GL_FRONT)
    bgl.glEnable(bgl.GL_CULL_FACE)
    shader = gizmo_helpers.helper_shader()
    shader.bind()

    batches = []

    planes = gizmo_helpers.get_plane_items()
    plane_color = (0.3, 0.9, 1.0, 0.5)
    plane_nrml_inf = 0.1
    for each in planes:
        coords, indices = gizmo_helpers.plane_shape(each)
        batches.append((
            batch_for_shader(shader, 'TRIS', {"pos": coords}, indices),
            plane_color,
            plane_nrml_inf
            ))

    snap = gizmo_helpers.get_snap_items()
    snap_color = (0.7, 0.9, 0.1, 1.0)
    snap_nrml_inf = 0.5
    for each in snap:
        coords, indices = gizmo_helpers.snap_shape(each)
        batches.append((
            batch_for_shader(shader, 'TRIS', {"pos": coords}, indices),
            snap_color,
            snap_nrml_inf
            ))

    for batch, color, normal_shading in batches:
        shader.uniform_float("color", color)
        shader.uniform_float("normal_shading", normal_shading)
        batch.draw(shader)

class GizmoInstance(object):
    """Instance class of the Gizmo from an operator"""
    inst = None

    def __bool__(self):
        return self.inst is not None

    def set_instance(self, inst):
        """Set a new instance for the calling operator"""
        self.term()
        self.inst = inst

    def term(self):
        """Terminate the instance"""
        self.inst = self.inst.terminate() if self.inst else None

GIZMO_INST = GizmoInstance()

class BL_OT_opengl_gizmos(bpy.types.Operator): # pylint: disable=invalid-name
    """Gizmo operator that creates a new Gizmo instance"""
    bl_idname = "opengl.helper_gizmos"
    bl_label = "OpenGL based Gizmos Renderer (Modal View3D Operator)"
    bl_category = "OpenGL"
    def __init__(self):
        self._handle = None

    def modal(self, context, event):
        """Keep the operator running"""
        return {'PASS_THROUGH'}

    def terminate(self):
        """Terminate the current operator's gizmos"""
        if GIZMO_INST:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, "WINDOW")

    def invoke(self, context, event):
        """Start the Operator"""
        if GIZMO_INST:
            return {'FINISHED'}
        if context.area.type == 'VIEW_3D':
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_VIEW')
            context.area.tag_redraw()
            context.window_manager.modal_handler_add(self)
            GIZMO_INST.set_instance(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}

class BL_PT_OpenGLGizmoPanel(bpy.types.Panel): # pylint: disable=invalid-name
    bl_idname = "BL_PT_OpenGLGizmoPanel"
    bl_label = "OpenGL Gizmos"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "OpenGL"

    class BL_OT_OpenGLGizmoToggle(bpy.types.Operator): # pylint: disable=invalid-name
        bl_label = "Toggle OpenGL Gizmos"
        bl_idname = "opengl.toggle_gizmos"
        bl_description = "Toggle the display of the Gizmos on/off"

        def execute(self, context):
            if not GIZMO_INST:
                add_to_viewports()
            else:
                GIZMO_INST.term()
                context.area.tag_redraw()
            return {'FINISHED'}

    bpy.types.Scene.opengl_gizmo_menu_expand = bpy.props.BoolProperty(
                name="opengl_gizmo_menu_expand",
                description="",
                default=True,
                )

    def draw(self, context):
        layout = self.layout
        btn_column = layout.column()
        btn_column.label(text="Node Helpers")
        btn_column.operator(
            "opengl.toggle_gizmos",
            icon="GHOST_DISABLED" if not GIZMO_INST else "GHOST_ENABLED",
            text="Show OpenGL Gizmos" if not GIZMO_INST else "Hide OpenGL Gizmos"
            )

CLASSES = (
    BL_OT_opengl_gizmos,
    BL_PT_OpenGLGizmoPanel,
    BL_PT_OpenGLGizmoPanel.BL_OT_OpenGLGizmoToggle,
)

def register():
    """Register"""
    from bpy.utils import register_class
    for cls in CLASSES:
        register_class(cls)

def unregister():
    """Unregister"""
    GIZMO_INST.term()
    from bpy.utils import unregister_class
    for cls in reversed(CLASSES):
        unregister_class(cls)

if __name__ == "__main__":
    register()
