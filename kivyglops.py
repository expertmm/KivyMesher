"""
This module is the Kivy implementation of PyGlops.
It provides features that are specific to display method
(Kivy's OpenGL-like API in this case).
"""
__author__ = 'Jake Gustafson'
import os
import sys
import time
import random
import uuid
import ast
import hashlib
import math
from pyglops import *

from kivy.resources import resource_find
from kivy.graphics import *
from kivy.uix.widget import Widget
from kivy.core.image import Image
from pyrealtime import *
from kivy.clock import Clock

# stuff required for KivyGlopsWindow
from kivy.app import App
from kivy.core.window import Window
from kivy.core.window import Keyboard
from kivy.graphics.transformation import Matrix
from kivy.graphics.opengl import *
from kivy.graphics import *
# from kivy.input.providers.mouse import MouseMotionEvent
from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle

from kivy.logger import Logger
from kivy.vector import Vector

from kivy.core.audio import SoundLoader

from common import *

nearest_not_found_warning_enable = True
_multicontext_enable = False  # only should be set while not running
print("[ kivyglops.py ] default _multicontext_enable: "
      + str(_multicontext_enable))
# region changed automatically after showing error only once
tltf = " (this is the last time this message will be shown for "
tlt = "this is the last time this message will be shown"
bounds_warning_enable = True
look_at_none_warning_enable = True
look_at_pos_none_warning_enable = True
missing_bumpable_warning_enable = True
missing_bumper_warning_enable = True
missing_radius_warning_enable = True
out_of_hitbox_note_enable = True
no_bounds_warning_enable = True
show_zero_degrees_pf_warning_enable = True  # pf is per frame
show_zero_walk_upf_warning_enable = True  # upf is units per frame
# endregion changed automatically after showing error only once


def get_distance_kivyglops(a_glop, b_glop):
    return math.sqrt((b_glop._t_ins.x - a_glop._t_ins.x)**2
                     + (b_glop._t_ins.y - a_glop._t_ins.y)**2
                     + (b_glop._t_ins.z - a_glop._t_ins.z)**2)

# def get_distance_vec3(a_vec3, b_vec3):
#    return math.sqrt((b_vec3[0] - a_vec3[0])**2 +
#                     (b_vec3[1] - a_vec3[1])**2 +
#                     (b_vec3[2] - a_vec3[2])**2)

# NOTE: use str(_t_ins.xyz) instead
# def translate_to_string(_t_ins):
#     result = "None"
#     if _t_ins is not None:
#         result = str([_t_ins.x, _t_ins.y, _t_ins.z])
#     return result


# If inherits from Widget, has the following error only on
# Kivy 1.9.0 (on Windows 10; does not occur on 1.10.0 on linux):
# [ KivyGlop ] ERROR--__init__ could not finish super!
# <class 'TypeError'> 'dict' object is not callable:
#   File "T:\pcerruti2020\Programming\Open GL\kivyglops.py", \
# line 111, in __init__
#     super(KivyGlop, self).__init__()  # only does class inherited \
# FIRST (see class line above) therefore _init_glop is called below
#   File "C:\kivy\kivy34\kivy\uix\widget.py", line 261, in __init__
#     super(Widget, self).__init__(**kwargs)
#   File "kivy\_event.pyx", line 252, in kivy._event.EventDispatcher.\
# __init__ (kivy\_event.c:4571)
#   File "kivy\_event.pyx", line 777, in kivy._event.EventDispatcher.\
# properties (kivy\_event.c:8189)
class KivyGlop(PyGlop):  # formerly KivyGlop(Widget, PyGlop)

    # freeAngle = None
    # degreesPerSecond = None
    # freePos = None
    _mesh = None  # the (Kivy) Mesh object
    _calculated_size = None
    _t_ins = None
    _r_ins_x = None
    _r_ins_y = None
    _r_ins_z = None
    _s_ins = None
    _color_instruction = None
    _context_instruction = None

    _axes_mesh = None  # InstructionGroup for axes

    _pivot_scaled_point = None
    _pushmatrix = None
    _updatenormalmatrix = None
    _popmatrix = None
    _own_shader_enable = None
    no_mesh_warning_enable = None

    def __init__(self, default_templates=None):
        try:
            super(KivyGlop, self).__init__(
                default_templates=default_templates
            )
            # super only runs the class inherited FIRST
            # (see class line above)
            # therefore call _init_glop below.
        except:
            print("[ KivyGlop ] ERROR--__init__ could not finish"
                  " super!")
            view_traceback()
            try:
                self._init_glop(default_templates=default_templates)
            except:
                print("[ KivyGlop ] ERROR--uh oh, "
                      "self._init_glop didn't work either:")
                view_traceback()
        self.material = new_material()
        self.material['diffuse_color'] = (1.0, 1.0, 1.0, 1.0)
        # ^ overlay vertex color onto this using vertex alpha
        self.material['ambient_color'] = (0.0, 0.0, 0.0, 1.0)
        self.material['specular_color'] = (1.0, 1.0, 1.0, 1.0)
        self.material['specular_coefficient'] = 16.0

        self._own_shader_enable = False
        # ^ if False during add_glop, gets shader of parent if
        #   _multicontext_enable, else does nothing either way
        self.no_mesh_warning_enable = True
        # self.freeAngle = 0.0
        # self.degreesPerSecond = 0.0
        # self.freePos = (10.0,100.0)

        # TODO: use a RenderContext instead?
        # self.canvas = RenderContext()
        if _multicontext_enable:
            self.canvas = RenderContext(
                use_parent_projection=True,
                use_parent_modelview=True,
                use_parent_frag_modelview=True,
                # compute_normal_mat=False,
            )
        else:
            self.canvas = InstructionGroup()
        self.canvas.clear()
        self._context_instruction = ContextInstruction()

        self._calculated_size = (1.0, 1.0)

        # finish this--or skip since only needed for getting
        # pivot point

        # Rotate(
        #     angle=self.freeAngle,
        #     origin=(self._calculated_size[0]/2.0,
        #             self._calculated_size[1]/2.0)
        # )
        self._pivot_point = 0.0, 0.0, 0.0
        # self.get_center_average_of_vertices()
        self._pivot_scaled_point = 0.0, 0.0, 0.0
        self._r_ins_x = Rotate(0, 1, 0, 0)  # angle, x, y z
        self._r_ins_x.origin = self._pivot_scaled_point
        self._r_ins_y = Rotate(0, 0, 1, 0)  # angle, x, y z
        self._r_ins_y.origin = self._pivot_scaled_point
        self._r_ins_z = Rotate(0, 0, 0, 1)  # angle, x, y z
        self._r_ins_z.origin = self._pivot_scaled_point
        self._s_ins = Scale(1.0, 1.0, 1.0)
        # self._s_ins.origin = self._pivot_point
        self._t_ins = Translate(0, 0, 0)
        self._color_instruction = Color(1.0, 0.0, 1.0, 1.0)
        # TODO: eliminate this in favor of
        # self.set_uniform("mat_diffuse_color",
        #                  (1.0, 0.0, 1.0, 1.0))

        self.generate_axes()

    def __str__(self):
        result = str(type(self))
        if self._t_ins is not None:
            result = ("{} named {} at {}"
                      "".format(type(self), self.name, self._t_ins.xyz))
        return result

    def debug_to(self, dest):
        dest['pos'] = fixed_width(self._t_ins.xyz, 4, " ")

    def get_angles(self):
        return (self._r_ins_x.angle,
                self._r_ins_y.angle,
                self._r_ins_z.angle)

    def set_angles(self, angles):
        self._r_ins_x.angle = angles[0]
        self._r_ins_y.angle = angles[1]
        self._r_ins_z.angle = angles[2]

    def get_pos(self):
        return (self._t_ins.xyz)

    def set_pos(self, pos):
        self._t_ins.x = pos[0]
        self._t_ins.y = pos[1]
        self._t_ins.z = pos[2]

    def get_angle(self, axis_index):
        if axis_index == 0:
            return self._r_ins_x.angle
        elif axis_index == 1:
            return self._r_ins_y.angle
        elif axis_index == 2:
            return self._r_ins_z.angle
        return None

    def set_angle(self, axis_index, angle):
        if axis_index == 0:
            self._r_ins_x.angle = angle
        elif axis_index == 1:
            self._r_ins_y.angle = angle
        elif axis_index == 2:
            self._r_ins_z.angle = angle
        else:
            print("[ KivyGlop ] ERROR in set_angle: "
                  "{} is out of range (dimension"
                  " should be 0, 1, or 2)".format(axis_index))

    def append_wobject(self, this_wobject,
                       pivot_to_g_enable=True):
        super(KivyGlop, self).append_wobject(
            this_wobject,
            pivot_to_g_enable=pivot_to_g_enable)
        if self.material is not None:
            self._color_instruction = Color(
                self.material['diffuse_color'][0],
                self.material['diffuse_color'][1],
                self.material['diffuse_color'][2],
                self.material['diffuse_color'][3])
        else:
            print("[ KivyGlop ] WARNING in append_wobject:"
                  " self.material is None for {}".format(self.name))

    def save(self, path):
        lines = []
        self.emit_yaml(lines, "")
        try:
            outs = open(path, 'w')
            for line in lines:
                outs.write(line + "\n")
            outs.close()
        except:
            print('[ KivyGlop ] ERROR--could not finish save to "{}":'
                  ''.format(path))
            view_traceback()

    def load(self, source_path, original_path=None):
        '''
        load yaml-formatted glop file
        '''
        specified_path = source_path
        if self.vertices is not None:
            print("[ KivyGlop ] WARNING: vertices are already "
                  "present during load, overwriting")
        if specified_path is not None:
            if original_path is None:
                original_path = source_path
            if not os.path.isfile(source_path):
                source_path = resource_find(source_path)
            if os.path.isfile(source_path):
                ins = open(source_path)
                line = True
                line_number = 1
                scopes = [ScopeInfo()]
                scopes[0].indent = ""
                scopes[0].name = ""
                scopes[0].line_number = -1
                nyi_names = {}
                while line:
                    line = ins.readline()
                    if line:
                        line_strip = line.strip()
                        indent = find_any_not(line, " \t")
                        depth = int(len(indent)/2)
                        # ^ assumes "  " yaml indent
                        while len(scopes) <= depth:
                            scopes.append(ScopeInfo())
                        if line_strip[:1] != "#":
                            op_i = line_strip.find(":")
                            if line_strip[-1:] == ":":
                                scopes[depth].name = \
                                    line_strip[:-1].strip()
                                scopes[depth].indent = indent
                                scopes[depth].line_number = line_number
                            array_i = line_strip.find("-")
                            if line_strip[0:1] == "-":
                                if depth > 0:
                                    val = \
                                        get_literal_value_from_yaml(
                                            line_strip[2:].strip()
                                        )
                                    if scopes[depth-1].name == \
                                            "vertices":
                                        self.vertices.append(float(val))
                                    elif scopes[depth-1].name == \
                                            "indices":
                                        self.indices.append(int(val))
                                    else:
                                        if scopes[depth-1].name not in \
                                                nyi_names:
                                            print(
                                                specified_path + "("
                                                + str(line_number)
                                                + ",0): (INPUT ERROR)"
                                                " item for unknown "
                                                "array "
                                                + scopes[depth-1].name
                                                + " not implemented"
                                                + ttl
                                                + scopes[depth-1].name
                                                + ")"
                                            )
                                            prevScp = scopes[depth-1]
                                            nyi_names[prevScp.name] = \
                                                False
                                else:
                                    print(
                                        specified_path + "("
                                        + str(line_number) + ",0): "
                                        "(INPUT ERROR) array in "
                                        "deepest scope (should be"
                                        " indented under an object"
                                        " name)"
                                    )
                            else:
                                if op_i > -1:
                                    name = line_strip[:op_i]
                                    val = get_literal_value_from_yaml(
                                        line_strip[op_i+1:])
                                    if name == \
                                            "get_texture_diffuse_path()":
                                        self.set_texture_diffuse(val)
                                else:
                                    print(
                                        specified_path + "("
                                        + str(line_number) + ",0): "
                                        "(INPUT ERROR) input with "
                                        "neither colon nor starting"
                                        " with hyphen is not "
                                        "implemented"
                                    )
                        prev_indent = indent
                    line_number += 1
                ins.close()
            else:
                print("[ KivyGlop ] ERROR in load: missing '"
                      + specified_path + "")
            # TODO: if cached, change source_path for each object to
            # that in stats.yml in cache folder
        else:
            print("[ KivyGlop ] ERROR in load: source_path was None")

    def emit_yaml(self, lines, min_tab_string):
        super(KivyGlop, self).emit_yaml(lines, min_tab_string)
        lines.append(min_tab_string
                     + "translate_x: "
                     + get_yaml_from_literal_value(self._t_ins.x))
        lines.append(min_tab_string
                     + "translate_y: "
                     + get_yaml_from_literal_value(self._t_ins.y))
        lines.append(min_tab_string
                     + "translate_z: "
                     + get_yaml_from_literal_value(self._t_ins.z))

    def set_coord(self, index, value):
        if index == 0:
            self._t_ins.x = value
        elif index == 1:
            self._t_ins.y = value
        elif index == 2:
            self._t_ins.z = value
        else:
            print("[ KivyGlop ] ERROR in set_coord: bad index "
                  + str(index))

    def get_coord(self, index):
        if index == 0:
            return self._t_ins.x
        elif index == 1:
            return self._t_ins.y
        elif index == 2:
            return self._t_ins.z
        else:
            print("[ KivyGlop ] ERROR in get_coord: bad index "
                  "{}".format(index))
        return None

    def new_vertex(self, set_coords, set_color):
        # NOTE: assumes vertex format is ok (should be checked by
        # generate_axes)
        # assumes normal should be point relative to 0,0,0
        vertex_components = [0.0]*self.vertex_depth
        for i in range(0, 3):
            vertex_components[self._POSITION_OFFSET+i] = set_coords[i]

        # Without the 4th index, matrix math cannot work and geometry
        # cannot be translated (!):
        V_LEN_I = VFORMAT_VECTOR_LEN_INDEX
        if self.vertex_format[self.POSITION_INDEX][V_LEN_I] > 3:
            vertex_components[self._POSITION_OFFSET+3] = 1.0
        if set_color is not None:
            for i in range(0, len(set_color)):
                vertex_components[self.COLOR_OFFSET+i] = set_color[i]
            if (len(set_color)) < 4 and (self.vertex_depth > 3):
                vertex_components[self.COLOR_OFFSET+3] = 1.0
        normals = [0.0] * 3
        for i in range(0, 3):
            normals[i] = set_coords[i]
        normalize_3d_by_ref(normals)
        for i in range(0, 3):
            vertex_components[self._NORMAL_OFFSET+i] = normals[i]
        # print("  #* made new vertex " + str(vertex_components) +
        #       " (color at " + str(self.COLOR_OFFSET) + ")")
        return vertex_components

    def append_vertex(self, target_vertices, set_coords, set_color):
        offset = len(target_vertices)
        index = int(offset/self.vertex_depth)
        target_vertices.extend(self.new_vertex(set_coords, set_color))
        return index

    def generate_plane(self):
        f_name = "generate_plane"
        _axes_vertices = []
        _axes_indices = []

        IS_SELF_VFORMAT_OK = True
        try:
            fail_prefix = ("[ KivyGlop ] ERROR in " + f_name + ":" +
                           " could not find name containing ")
            fail_suffix = (" in any vertex format element" +
                           " (see PyGlop __init__)")
            if self._POSITION_OFFSET < 0:
                IS_SELF_VFORMAT_OK = False
                print(fail_prefix + "'pos' or 'position'" + fail_suffix)
            if self._NORMAL_OFFSET < 0:
                IS_SELF_VFORMAT_OK = False
                print(fail_prefix + "'normal'" + fail_suffix)
            if self._TEXCOORD0_OFFSET < 0:
                IS_SELF_VFORMAT_OK = False
                print(fail_prefix + "'texcoord'" + fail_suffix)
            if self.COLOR_OFFSET < 0:
                IS_SELF_VFORMAT_OK = False
                print(fail_prefix + "'color'" + fail_suffix)
        except TypeError as ex:
            if "NoneType" in str(ex):
                IS_SELF_VFORMAT_OK = False
                print("[ KivyGlop ] ERROR in " + f_name + ":"
                      " self._POSITION_OFFSET is {}; "
                      " self._NORMAL_OFFSET is {}; "
                      " self._TEXCOORD0_OFFSET is {}; "
                      " self.COLOR_OFFSET is {}; "
                      "".format(
                          self._POSITION_OFFSET,
                          self._NORMAL_OFFSET,
                          self._TEXCOORD0_OFFSET,
                          self.COLOR_OFFSET,
                      ))
            else:
                raise(ex)

        offset = 0
        white = (1.0, 1.0, 1.0, 1.0)
        nv = -.5  # near vector
        fv = .5  # far vector
        self.append_vertex(_axes_vertices, (nv, 0.0, nv), white)
        self.append_vertex(_axes_vertices, (nv, 0.0, fv), white)
        self.append_vertex(_axes_vertices, (fv, 0.0, fv), white)
        self.append_vertex(_axes_vertices, (fv, 0.0, nv), white)
        _axes_indices.extend([0, 3, 2,
                              #
                              2, 1, 0])
        # ^ counterclockwise winding
        # clockwise winding (not usual unless want to flip normal):
        # _axes_indices.extend([0,1,2, 2,3,0])

        self._mesh = Mesh(
                               vertices=_axes_vertices,
                               indices=_axes_indices,
                               fmt=self.vertex_format,
                               mode='triangles',
                               texture=None,
                              )

    def generate_axes(self):
        '''
        result is a full solid (3 boxes) where all axes can always
        be seen except when another is in the way (some vertices are
        doubled so that vertex color can be used).
        See etc/axes-widget-diagram.png
        '''
        f_name = "generate_axes"

        _axes_vertices = []
        _axes_indices = []
        if self.vertex_depth is None:
            print("[ KivyGlop ] WARNING in generate_axes: "
                  "vertex_depth was None--trying "
                  "on_vertex_format_change...")
            self.on_vertex_format_change()
        IS_SELF_VFORMAT_OK = True
        try:
            fail_prefix = ("[ KivyGlop ] ERROR in " + f_name + ":" +
                           " could not find name containing ")
            fail_suffix = (" in any vertex format element" +
                           " (see PyGlop __init__)")
            if self._POSITION_OFFSET < 0:
                IS_SELF_VFORMAT_OK = False
                print(fail_prefix + "'pos' or 'position'" + fail_suffix)
            if self._NORMAL_OFFSET < 0:
                IS_SELF_VFORMAT_OK = False
                print(fail_prefix + "'normal'" + fail_suffix)
            if self._TEXCOORD0_OFFSET < 0:
                IS_SELF_VFORMAT_OK = False
                print(fail_prefix + "'texcoord'" + fail_suffix)
            if self.COLOR_OFFSET < 0:
                IS_SELF_VFORMAT_OK = False
                print(fail_prefix + "'color'" + fail_suffix)
        except TypeError as ex:
            if "NoneType" in str(ex):
                # TODO: ^ see what happened then choose what to handle
                IS_SELF_VFORMAT_OK = False
                print("[ KivyGlop ] ERROR in " + f_name + ":" +
                      " couldn't find offsets")
                return None
                # Stop here, otherwise there will be a
                # `ZeroDivisionError: division by zero` in
                # append_vertex.
            else:
                raise ex

        offset = 0
        red = (1.0, 0.0, 0.0)
        green = (0.0, 1.0, 0.0)
        blue = (0.0, 0.0, 1.0)
        # NOTE: default opengl winding order is counter-clockwise
        # (where makes normal face you)
        cv = 0.0  # center vector
        nv = 0.1  # near vector
        fv = 1.0  # far vector
        self.append_vertex(_axes_vertices, (cv, cv, cv), green)  # 0
        self.append_vertex(_axes_vertices, (nv, cv, cv), green)  # 1
        self.append_vertex(_axes_vertices, (cv, cv, nv), green)  # 2
        self.append_vertex(_axes_vertices, (nv, cv, nv), green)  # 3
        self.append_vertex(_axes_vertices, (cv, fv, cv), green)  # 4
        self.append_vertex(_axes_vertices, (nv, fv, cv), green)  # 5
        self.append_vertex(_axes_vertices, (cv, fv, nv), green)  # 6
        self.append_vertex(_axes_vertices, (nv, fv, nv), green)  # 7

        # bottom & right
        # back & top
        # left & front
        _axes_indices.extend([0, 1, 3,
                              0, 3, 2,
                              0, 2, 6,
                              0, 6, 4,
                              #
                              0, 4, 5,
                              0, 5, 1,
                              4, 5, 7,
                              4, 7, 6,
                              #
                              1, 5, 7,
                              1, 7, 3,
                              2, 3, 7,
                              2, 7, 6
                              ])

        self.append_vertex(_axes_vertices, (nv, cv, cv), red)  # 8
        self.append_vertex(_axes_vertices, (nv, cv, nv), red)  # 9
        self.append_vertex(_axes_vertices, (nv, nv, cv), red)  # 10
        self.append_vertex(_axes_vertices, (fv, nv, nv), red)  # 11
        self.append_vertex(_axes_vertices, (fv, cv, cv), red)  # 12
        self.append_vertex(_axes_vertices, (fv, nv, cv), red)  # 13
        self.append_vertex(_axes_vertices, (fv, cv, nv), red)  # 14
        self.append_vertex(_axes_vertices, (fv, nv, nv), red)  # 15

        # back & outside
        # bottom & inside
        # top & front
        _axes_indices.extend([8,  9, 11,
                              8, 11, 10,
                              8, 10, 13,
                              8, 13, 12,
                              #
                              8, 12, 14,
                              8, 14, 9,
                              9, 14, 15,
                              9, 15, 11,
                              #
                              10, 11, 15,
                              11, 15, 13,
                              12, 13, 15,
                              12, 15, 14
                              ])

        self.append_vertex(_axes_vertices, (cv, cv, nv), blue)  # 16
        self.append_vertex(_axes_vertices, (nv, cv, nv), blue)  # 17
        self.append_vertex(_axes_vertices, (cv, nv, nv), blue)  # 18
        self.append_vertex(_axes_vertices, (nv, nv, nv), blue)  # 19
        self.append_vertex(_axes_vertices, (cv, cv, fv), blue)  # 20
        self.append_vertex(_axes_vertices, (nv, cv, fv), blue)  # 21
        self.append_vertex(_axes_vertices, (cv, nv, fv), blue)  # 22
        self.append_vertex(_axes_vertices, (nv, nv, fv), blue)  # 23

        # back & outside
        # bottom & inside
        # top & front
        _axes_indices.extend([16, 18, 19,
                              16, 19, 17,
                              16, 22, 18,
                              16, 20, 22,
                              #
                              16, 17, 21,
                              16, 21, 20,
                              17, 19, 20,
                              17, 20, 21,
                              #
                              19, 18, 22,
                              19, 22, 23,
                              20, 21, 23,
                              20, 23, 22
                              ])

        # new_texcoord = new_tuple(
        #     self.vertex_format[
        #         self.TEXCOORD0_INDEX][VFORMAT_VECTOR_LEN_INDEX])
        if IS_SELF_VFORMAT_OK:
            self._axes_mesh = Mesh(
                vertices=_axes_vertices,
                indices=_axes_indices,
                fmt=self.vertex_format,
                mode='triangles',
                texture=None,
            )
        else:
            # error already shown
            # print("[ KivyGlop ] ERROR in generate_axes:"
            #       " bad vertex_format")
            pass
        # return _axes_vertices, _axes_indices

    # "Called by the repr() built-in function to compute the "official"
    # string representation of an object. If at all possible, this
    # should look like a valid Python expression that could be used to
    # recreate an object..."
    # <https://docs.python.org/3/reference/datamodel.html#customization>
    def __repr__(self):
        return ("KivyGlop(name=" + str(self.name) + ", location="
                + str(self._t_ins.xyz) + ")")

    def copy(self, depth=0):
        target = None
        try:
            if get_verbose_enable():
                print("[ KivyGlop ] " + "  " * depth + "copy is"
                      " calling copy_as_subclass")
            target = self.copy_as_subclass(self.new_glop_method,
                                           depth=depth+1)
            target.canvas = InstructionGroup()
            target._pivot_point = self._pivot_point
            target._pivot_scaled_point = self._pivot_scaled_point
            target._r_ins_x = Rotate(self._r_ins_x.angle, 1, 0, 0)
            # ^ angle, x, y z
            target._r_ins_x.origin = self._pivot_scaled_point
            target._r_ins_y = Rotate(self._r_ins_y.angle, 0, 1, 0)
            # ^ angle, x, y z
            target._r_ins_y.origin = self._pivot_scaled_point
            target._r_ins_z = Rotate(self._r_ins_z.angle, 0, 0, 1)
            # ^ angle, x, y z
            target._r_ins_z.origin = self._pivot_scaled_point
            target._t_ins = Translate(self._t_ins.x,
                                      self._t_ins.y, self._t_ins.z)
            target._color_instruction = Color(self._color_instruction.r,
                                              self._color_instruction.g,
                                              self._color_instruction.b,
                                              self._color_instruction.a)
        except:
            print("[ KivyGlop ] ERROR--could not finish copy:")
            view_traceback()
        return target

    def rotate_camera_relative(self, angle, axis_index):
        # TODO: delete this method and see solutions from
        # <http://stackoverflow.com/questions/10048018/
        #  opengl-camera-rotation>
        # such as set_view method of
        # <https://github.com/sgolodetz/hesperus2/blob/master/Shipwreck/
        #  MapEditor/GUI/Camera.java>
        self.rotate_relative_around_point(self.camera_glop, angle,
                                          axis_index,
                                          self.camera_glop._t_ins.x,
                                          self.camera_glop._t_ins.y,
                                          self.camera_glop._t_ins.z)

    def rotate_player_relative(self, angle, axis_index):
        # TODO: delete this method and see solutions from
        # <http://stackoverflow.com/questions/10048018/
        # opengl-camera-rotation>
        # such as set_view method of
        # <https://github.com/sgolodetz/hesperus2/blob/master/Shipwreck/
        # MapEditor/GUI/Camera.java>
        self.rotate_relative_around_point(self.player_glop, angle,
                                          axis_index,
                                          self.player_glop._t_ins.x,
                                          self.player_glop._t_ins.y,
                                          self.player_glop._t_ins.z)

    def rotate_relative_around_point(self, this_glop, angle, axis_index,
                                     around_x, around_y, around_z):
        if axis_index == 0:  # x
            # += around_y * math.tan(angle)
            this_glop._r_ins_x.angle += angle
            # origin_distance = math.sqrt(around_z*around_z
            #                             + around_y*around_y)
            # this_glop._t_ins.z += origin_distance * math.cos(-1*angle)
            # this_glop._t_ins.y += origin_distance * math.sin(-1*angle)
        elif axis_index == 1:  # y
            this_glop._r_ins_y.angle += angle
            # origin_distance = math.sqrt(around_x*around_x
            #                             + around_z*around_z)
            # this_glop._t_ins.x += origin_distance * math.cos(-1*angle)
            # this_glop._t_ins.z += origin_distance * math.sin(-1*angle)
        else:  # z
            # this_glop._t_ins.z += around_y * math.tan(angle)
            this_glop._r_ins_z.angle += angle
            # origin_distance = math.sqrt(around_x*around_x
            #                             + around_y*around_y)
            # this_glop._t_ins.x += origin_distance * math.cos(-1*angle)
            # this_glop._t_ins.y += origin_distance * math.sin(-1*angle)

    def new_glop_method(self, default_templates=None):
        # return PyGlops.new_glop_method(self)
        return KivyGlop(default_templates=default_templates)

    def get_class_name(self):
        return "KivyGlop"

    def look_at(self, target_glop):
        if target_glop is not None:
            self.look_at_pos(target_glop._t_ins.xyz)
            # pitch = 0.0
            # pitch = get_angle_between_points(self._t_ins.y,
            #                                  self._t_ins.z,
            #                                  target_glop._t_ins.y,
            #                                  target_glop._t_ins.z)
            # self._r_ins_x.angle = pitch
            # yaw = get_angle_between_points(self._t_ins.x,
            #                                self._t_ins.z,
            #                                target_glop._t_ins.x,
            #                                target_glop._t_ins.z)
            # self._r_ins_y.angle = yaw
            # print("look at pitch,yaw: "
            #     + str(int(math.degrees(pitch))) + ","
            #     + str(int(math.degrees(yaw))))
        else:
            global look_at_none_warning_enable
            if look_at_none_warning_enable:
                print("[ KivyGlop ] look_at got None for target_glop")
                look_at_none_warning_enable = False

    def look_at_pos(self, pos):
        if pos is not None:
            pitch = self._r_ins_x.angle
            yaw = self._r_ins_y.angle
            if len(pos) > 2:
                pitch = get_angle_between_points(self._t_ins.y,
                                                 self._t_ins.z,
                                                 pos[1], pos[2])
                yaw = get_angle_between_points(self._t_ins.x,
                                               self._t_ins.z,
                                               pos[0], pos[2])
            else:
                yaw = get_angle_between_points(self._t_ins.x,
                                               self._t_ins.z,
                                               pos[0], pos[1])
                if get_verbose_enable():
                    print("[ KivyGlop ]"
                          " WARNING: look_at_pos got 2D coords")
            self._r_ins_x.angle = pitch
            self._r_ins_y.angle = yaw
            # print("look at pitch,yaw: "
            #     + str(int(math.degrees(pitch))) + ","
            #     + str(int(math.degrees(yaw))))
        else:
            global look_at_pos_none_warning_enable
            if look_at_pos_none_warning_enable:
                print(
                    "[ KivyGlop ] ERROR: look_at_pos got None for pos"
                )
                look_at_pos_none_warning_enable = False

    def copy_as_mesh_instance(self, depth=0, ref_vertices_enable=True):
        result = KivyGlop()
        result.name = self.name
        if ref_vertices_enable:
            result.vertex_format = self.vertex_format
            result.on_vertex_format_change()
            result.vertices = self.vertices
            result.indices = self.indices
        else:
            result.vertex_format = copy.deepcopy(self.vertex_format)
            result.on_vertex_format_change()
        result.properties['hit_radius'] = self.properties['hit_radius']
        result.properties['hitbox'] = self.properties['hitbox']
        context = result.get_context()
        result._t_ins.x = self._t_ins.x
        result._t_ins.y = self._t_ins.y
        result._t_ins.z = self._t_ins.z
        result._r_ins_x.angle = self._r_ins_x.angle
        result._r_ins_y.angle = self._r_ins_y.angle
        result._r_ins_z.angle = self._r_ins_z.angle
        # result._s_ins.x = self._s_ins.x
        # result._s_ins.y = self._s_ins.y
        # result._s_ins.z = self._s_ins.z
        # result._color_instruction.r = self._color_instruction.r
        # result._color_instruction.g = self._color_instruction.g
        # result._color_instruction.b = self._color_instruction.b
        result._pushmatrix = PushMatrix()
        result._updatenormalmatrix = UpdateNormalMatrix()
        result._popmatrix = PopMatrix()

        context.add(result._pushmatrix)
        context.add(result._t_ins)
        context.add(result._r_ins_x)
        context.add(result._r_ins_y)
        context.add(result._r_ins_z)
        context.add(result._s_ins)
        context.add(result._updatenormalmatrix)
        # context.add(this_glop._color_instruction)
        # TODO: asdf uniform instead?
        if self._mesh is not None:
            context.add(self._mesh)
        else:
            print("[ KivyGlop ] " + "  " * depth + "WARNING in "
                  "copy_as_mesh_instance: meshless glop '"
                  + str(self.name) + "'")
        context.add(result._popmatrix)

        return result

    def calculate_hit_range(self):
        # TODO: re-implement super method, changing hitbox taking
        # rotation & scale into account
        # NOTE: index is set by add_glop so None if done earlier:
        glop_msg = "new glop"
        if self.glop_index is not None:
            glop_msg = str(self.glop_index)
        if self.name is not None:
            glop_msg += " '" + self.name + "'"
        if get_verbose_enable():
            print("[ KivyGlop ] calculate_hit_range (hitbox) for "
                  + glop_msg + "...")
        if self.vertices is None:
            self.properties['hitbox'] = None
            # ^ avoid 0-size hitbox which would prevent bumps
            if self.properties['hit_radius'] is None:
                self.properties['hit_radius'] = .4444  # flag value
            print("[ KivyGlop ] hitbox skipped since vertices None"
                  " (name={}).".format(self.name))
            return None
        vertex_count = int(len(self.vertices)/self.vertex_depth)
        if vertex_count <= 0:
            self.properties['hitbox'] = None
            # ^ avoid 0-size hitbox which would prevent bumps
            if self.properties.get('hit_radius') is None:
                self.properties['hit_radius'] = .4444  # flag value
            print("    skipped (0 vertices).")
            return None
        self.properties['hitbox'] = {}
        v_offset = 0
        self.properties['hit_radius'] = 0.0
        hb = self.properties.get('hitbox')
        hr = self.properties.get('hit_radius')
        PO = self._POSITION_OFFSET
        if hb is None:
            hb = new_hitbox()
            self.properties['hitbox'] = hb
            print("WARNING: created 'hitbox' key for {}"
                  "".format(self.name))
        # intentionally set to ridiculously far in opposite direction:
        self.properties['hitbox']['minimums'] = [sys.float_info.max] * 3
        self.properties['hitbox']['maximums'] = [sys.float_info.min] * 3
        for v_number in range(0, vertex_count):
            for i in range(0,3):
                if self.vertices[v_offset+self._POSITION_OFFSET+i] < self.properties['hitbox']['minimums'][i]:
                    self.properties['hitbox']['minimums'][i] = self.vertices[v_offset+self._POSITION_OFFSET+i]
                if self.vertices[v_offset+self._POSITION_OFFSET+i] > self.properties['hitbox']['maximums'][i]:
                    self.properties['hitbox']['maximums'][i] = self.vertices[v_offset+self._POSITION_OFFSET+i]
            this_vertex_relative_distance = get_distance_vec3(self.vertices[v_offset+self._POSITION_OFFSET:v_offset+self._POSITION_OFFSET+3], self._pivot_point)
            if this_vertex_relative_distance > self.properties['hit_radius']:
                self.properties['hit_radius'] = this_vertex_relative_distance
            v_offset += self.vertex_depth
        phi_eye_height = 86.5 * self.properties['hitbox']['maximums'][1]
        if self.eye_height > phi_eye_height:
            print("[ KivyGlop ] WARNING in calculate_hit_range:" + \
                  " eye_height " + str(self.eye_height) + \
                  " is beyond phi_eye_height" + \
                  str(phi_eye_height) + \
                  " so is being set to that value")
            self.eye_height = self.properties['hitbox']['maximums'][1]
        print("    done calculate_hit_range")

    def rotate_x_relative(self, angle):
        self._r_ins_x.angle += angle

    def rotate_y_relative(self, angle):
        self._r_ins_y.angle += angle

    def rotate_z_relative(self, angle):
        self._r_ins_z.angle += angle

    def move_x_relative(self, distance):
        self._t_ins.x += distance

    def move_y_relative(self, distance):
        self._t_ins.y += distance

    def move_z_relative(self, distance):
        self._t_ins.z += distance

    def transform_pivot_to_geometry(self):
        previous_point = self._pivot_point
        super(KivyGlop, self).transform_pivot_to_geometry()
        # self._change_instructions()
        # self._on_change_pivot(previous_point)
        # ^ commenting this assumes this subclass' version
        #   of _on_change_pivot is already run by super

    def _on_change_pivot(self, previous_point=(0.0, 0.0, 0.0)):
        super(KivyGlop, self)._on_change_pivot(
            previous_point=previous_point, class_name="KivyGlop")
        print("[ KivyGlop ] (verbose message in _on_change_pivot)"
              " from " + str(previous_point))
        self._on_change_s_ins()  # does calculate_hit_range

    def get_scale(self):
        return (self._s_ins.x + self._s_ins.y + self._s_ins.z) / 3.0

    def set_scale(self, overall_scale):
        self._s_ins.x = overall_scale
        self._s_ins.y = overall_scale
        self._s_ins.z = overall_scale
        self._on_change_s_ins()  # does calculate_hit_range

    def _on_change_s_ins(self):
        if self._pivot_point is not None:
            self._pivot_scaled_point = (
                self._pivot_point[0] * self._s_ins.x + self._t_ins.x,
                self._pivot_point[1] * self._s_ins.y + self._t_ins.y,
                self._pivot_point[2] * self._s_ins.z + self._t_ins.z
            )
        # else:
        #     self._pivot_point = 0,0,0
        #     self._pivot_scaled_point = 0,0,0
        # super(KivyGlop, self)._on_change_scale()
        # if self._pivot_point is not None:
        self._r_ins_x.origin = self._pivot_scaled_point
        self._r_ins_y.origin = self._pivot_scaled_point
        self._r_ins_z.origin = self._pivot_scaled_point
        # self._t_ins.x = self.freePos[0] - \
        #     self._rectangle_instruction.size[0]*self._s_ins.x/2
        # self._t_ins.y = self.freePos[1] - \
        #     self._rectangle_instruction.size[1]*self._s_ins.y/2
        # self._rotate_instruction.origin = \
        #     (self._rectangle_instruction.size[0]*self._s_ins.x/2.0,
        #      self._rectangle_instruction.size[1]*self._s_ins.x/2.0)
        # self._rotate_instruction.angle = self.freeAngle
        this_name = ""
        if self.name is not None:
            this_name = self.name
        # print("")
        # print("_on_change_s_ins for object named '"+this_name+"'")
        # print ("_pivot_point:"+str(self._pivot_point))
        # print ("_pivot_scaled_point:"+str(self._pivot_scaled_point))
        # if self.properties['hitbox'] is not None:
        #     # ^ only should be recalculated if already
        #     #   (already bumper or bumpable list)
        self.calculate_hit_range()

    def apply_translate(self):
        vertex_count = int(len(self.vertices)/self.vertex_depth)
        v_offset = 0
        for v_number in range(0, vertex_count):
            self.vertices[v_offset+self._POSITION_OFFSET+0] -= \
                self._t_ins.x
            self.vertices[v_offset+self._POSITION_OFFSET+1] -= \
                self._t_ins.y
            self.vertices[v_offset+self._POSITION_OFFSET+2] -= \
                self._t_ins.z
            self._pivot_point = (self._pivot_point[0] - self._t_ins.x,
                                 self._pivot_point[1] - self._t_ins.y,
                                 self._pivot_point[2] - self._t_ins.z)
            self._t_ins.x = 0.0
            self._t_ins.y = 0.0
            self._t_ins.z = 0.0
            v_offset += self.vertex_depth
        self.apply_pivot()

    def set_texture_diffuse(self, path):
        self.last_loaded_path = path
        this_texture_image = None
        if self.last_loaded_path is not None:
            participle = "getting image filename"
            try:
                participle = "loading "+self.last_loaded_path
                if os.path.isfile(self.last_loaded_path):
                    this_texture_image = Image(self.last_loaded_path)
                else:
                    this_texture_image = Image(
                        resource_find(self.last_loaded_path))
                print("[ KivyGlop ] Loaded texture '"
                      + str(self.last_loaded_path) + "'")
            except:
                print(
                    "[ KivyGlop ] ERROR--"
                    "could not finish loading texture: "
                    + str(self.last_loaded_path)
                )
                view_traceback()
        else:
            if get_verbose_enable():
                Logger.debug("[ KivyGlop ] Warning: no texture"
                             " specified for glop named '"
                             + str(self.name) + "'")
                this_material_name = ""
                if self.material is not None:
                    try_name = self.material.get('name')
                    if try_name is not None:
                        this_material_name = try_name
                        Logger.debug("[ KivyGlop ] (material named '"
                                     + this_material_name + "')")
                    else:
                        Logger.debug(
                            "[ KivyGlop ] (material with no name)"
                        )
                else:
                    Logger.debug("[ KivyGlop ] (no material)")
        if self._mesh is not None and this_texture_image is not None:
            self._mesh.texture = this_texture_image.texture
            context = self.get_context()
            self.set_uniform("texture0_enable", True)
        return this_texture_image

    def _generate_kivy_mesh(self):
        participle = "checking for texture"
        if self._mesh is not None:
            print("[ KivyGlop ] WARNING in generate_kivy_mesh:"
                  " self._mesh is not None, overriding")
        self._mesh = None
        this_texture_image = self.set_texture_diffuse(
            self.get_texture_diffuse_path()
        )
        participle = "assembling kivy Mesh"
        this_texture = None
        if self.vertices is not None:
            if len(self.vertices) > 0:
                if (this_texture_image is not None):
                    this_texture = this_texture_image.texture
                    this_texture.wrap = 'repeat'
                    # does same as GL_REPEAT -- see
                    # <https://gist.github.com/tshirtman/
                    # 3868962#file-main-py-L15>

                self._mesh = Mesh(
                        vertices=self.vertices,
                        indices=self.indices,
                        fmt=self.vertex_format,
                        mode='triangles',
                        texture=this_texture,
                    )
                if get_verbose_enable():
                    print("[ KivyGlop ] " + str(len(self.vertices))
                          + " vert(s)")
            else:
                print("[ KivyGlop ] WARNING: 0 vertices in glop")
                if self.name is not None:
                    print("[ KivyGlop ]   named " + self.name)
        else:
            print("[ KivyGlop ] WARNING: vertices is None in glop "
                  + str(self.name))

    def set_uniform(self, name, val):
        '''
        This is the LOCAL object canvas, which may be
        either a RenderContext (not full Canvas) if
        _multicontext_enable (global) is True,
        otherwise it is an InstructionGroup.
        '''
        if _multicontext_enable:
            self.canvas[name] = val
        else:
            # can't do it to InstructionGroup so don't try
            pass

    def get_uniform(self, name):
        if _multicontext_enable:
            return self.canvas[name]
        else:
            # can't do it so don't try
            return None

    def prepare_canvas(self, use_meshes=None, xyz_widget_index=-1):
        '''
        Keyword arguments:
        use_meshes -- Set the list of meshes to override `[self._mesh]`.
        xyz_widget_index -- The index in use_meshes that is the XYZ
                            widget that shows this model's orientation.
        '''
        # props = self.properties
        # hitbox = props['hitbox']
        if self._mesh is None:
            # verts, indices = self.generate_kivy_mesh()
            self._generate_kivy_mesh()
            # _contexts = [ self._axes_mesh ]
            # print("[ KivyGlop ] WARNING: glop had no mesh, so was"
            #       " generated when added to render context. Please"
            #       "ensure it is a KivyGlop and not a PyGlop "
            #       "(however, vertex indices misread could also "
            #       "lead to missing Mesh object).")
        if use_meshes is None:
            use_meshes = [self._mesh]

        m_i = 0
        context = self.get_context()
        context.clear()

        # self.generate_axes()
        # self.generate_plane()
        self.set_uniform("texture0_enable", False)
        for i in range(len(use_meshes)):
            use_mesh = use_meshes[i]
            # self._axes_mesh.
            # self._s_ins = Scale(0.6)
            self._pushmatrix = PushMatrix()
            self._updatenormalmatrix = UpdateNormalMatrix()
            self._popmatrix = PopMatrix()

            context.add(self._pushmatrix)
            context.add(self._t_ins)
            context.add(self._r_ins_x)
            context.add(self._r_ins_y)
            context.add(self._r_ins_z)
            context.add(self._s_ins)
            context.add(self._updatenormalmatrix)
            context.add(self._context_instruction)
            # context.add(self._color_instruction)
            # TODO: asdf add as uniform instead
            # print("_color_instruction.r,.g,.b,.a: " + str( [self._color_instruction.r, self._color_instruction.g, self._color_instruction.b, self._color_instruction.a] ))
            # print("u_color: " + str(self.material['diffuse_color']))
            # if self._axes_mesh is not None:
            #     context.add(self._axes_mesh)  # debug only
            #     self._mesh = self._axes_mesh  # debug only
            #     pass
            # else:
            #     print("[ KivyGlop ] no _axes_mesh.")  # debug only
            #     pass

            if use_mesh is not None:
                context.add(use_mesh)
                if get_verbose_enable():
                    print("[ KivyGlop ] (verbose message) Added"
                          " mesh to render context.")
                if use_mesh.texture is not None:
                    self.set_uniform("texture0_enable", True)
                else:
                    self.set_uniform("texture0_enable", False)
                if get_verbose_enable():
                    print("[ KivyGlop ] (verbose message)"
                          " texture0_enable: "
                          + str(self.get_uniform("texture0_enable")))
            else:
                if get_verbose_enable():
                    print("[ KivyGlop ] (verbose message)"
                          " NOT adding mesh None at " + str(m_i) + ".")
            context.add(self._popmatrix)

            # context.add(PushMatrix())
            # context.add(self._t_ins)
            # context.add(self._r_ins_x)
            # context.add(self._r_ins_y)
            # context.add(self._r_ins_z)
            # context.add(self._s_ins)
            # context.add(self._updatenormalmatrix)
            # context.add(self._axes_mesh)
            # context.add(PopMatrix())
            m_i += 1

    def get_context(self):
        return self.canvas


class KivyGlops(PyGlops):

    def __init__(self, new_ui):
        self.showNextHashWarning = True
        # region moved from ui
        self.projection_near = None
        self.look_point = None
        self.focal_distance = None
        # ^ exists so look_point has more freedom
        self.selected_glop = None
        self.selected_glop_index = None
        self.mode = None
        self.controllers = None
        self.player1_controller = None
        self._previous_world_light_dir = None
        self._previous_camera_rotate_y_angle = None
        self._world_cube = None
        self.world_boundary_min = None
        self.world_boundary_max = None
        self._sounds = None
        # endregion moved from ui
        # camera_glop = None
        # ^ inherited from PyGlops (so are many other member variables)

        self._load_glops_enable = False
        self._loading_glops_enable = False
        self._loaded_glops_enable = False
        self.env_orig_rect = None
        self.env_rectangle = None
        self.env_flip_enable = False
        self.ui = new_ui
        if self.ui is None:
            raise RuntimeError("[ KivyGlops ] FATAL ERROR in __init__:"
                               "KivyGlops cannot init without a ui")

        # TODO? or remove if is ok without it: Clock.schedule_once(
        #    self._update,
        #    self.update_interval)
        self.ui.scene = self
        try:
            super(KivyGlops, self).__init__(self.new_glop_method)
        except:
            print("[ KivyGlops ] ERROR--could not finish super:")
            view_traceback()
        try:
            self.controllers = list()
            # region moved from ui
            self.world_boundary_min = [None,None,None]
            self.world_boundary_max = [None,None,None]
            self.mode = MODE_EDIT
            self.player1_controller = PyRealTimeController()
            self.controllers.append(self.player1_controller)
            self.focal_distance = 2.0
            self.projection_near = 0.1
            self._sounds = {}

            self.player_glop = KivyGlop()
            self.player_glop.eye_height = 1.7  # 1.7 since 5'10" person is ~1.77m, and eye down a bit
            self.player_glop.properties['hit_radius'] = .2  # default is 0.1524  # .5' equals .1524m
            self.player_glop.reach_radius = 2.5  # default is 0.381 # 2.5' .381m

            # x,y,z where y is up:
            self.player_glop._t_ins.x = 0
            self.player_glop._t_ins.y = 0
            self.player_glop._t_ins.z = 25  # + toward view

            self.player_glop._r_ins_x.angle = 0.0
            self.player_glop._r_ins_y.angle = math.radians(-90.0)  # [math.radians(-90.0), 0.0, 1.0, 0.0]
            self.player_glop._r_ins_z.angle = 0.0
            # region moved from ui

            self.set_camera_mode(self.CAMERA_FIRST_PERSON())
            # self.player_glop = self.camera_glop  # TODO: separate into two objects and make camera follow player
            self.player_glop.bump_enable = True
            self.camera_glop.glop_index = len(self.glops)
            self.glops.append(self.camera_glop)
            self.player_glop.name = "Player 1"
            self._fly_enables[self.player_glop.name] = True
            self.player_glop.glop_index = len(self.glops)
            self.glops.append(self.player_glop)
            self._player_glop_index = len(self.glops)-1
            self.set_as_actor_at(self._player_glop_index, None)
            if self.glops[self._player_glop_index] is not self.player_glop:
                # then address multithreading paranoia
                self._player_glop_index = None
                for try_i in range(len(self.glops)):
                    if self.glops[try_i] is self.player_glop:
                        self._player_glop_index = try_i
                        break
                if self._player_glop_index is not None:
                    print("WARNING: glop array changed during init, so redetected self._player_glop_index.")
                else:
                    print("WARNING: glop array changed during init, and self._player_glop_index could not be detected.")
            # self._bumper_indices.append(self._player_glop_index)

            # TODO: why was this code here? it's not good. these are set during update instead now
            # this_actor_dict = dict()
            # this_actor_dict['land_units_per_second'] = 12.0
            # this_actor_dict['land_degrees_per_second'] = 90.0
            # self.set_as_actor_at(self._player_glop_index, this_actor_dict)

            # NOTE: set_as_actor_at sets hitbox to None if has no vertices
        except:
            print("[ KivyGlops ] ERROR--__init__ could not finish:")
            view_traceback()

    def new_glop_method(self):
        # return PyGlops.new_glop_method(self)
        return KivyGlop()

    def on_load_glops(self):
        print("WARNING: app's subclass of KivyGlops should "
              "implement on_load_glops (and usually "
              "on_update_glops, which will be called before"
              " each frame is drawn)")

    def hide_glop(self, this_glop):
        self.ui._contexts.remove(this_glop.get_context())
        this_glop.visible_enable = False

    def show_glop(self, this_glop_index):
        self.ui._contexts.add(self.glops[this_glop_index].get_context())
        self.glops[this_glop_index].visible_enable = True

    def use_walkmesh_at(self, index, hide=True):
        if self.glops[index] not in self._walkmeshes:
            self._walkmeshes.append(self.glops[index])
            print("[ KivyGlops ] Applying walkmesh translate "
                  + str(self.glops[index]._t_ins.xyz))
            self.glops[index].apply_translate()
            print("[ KivyGlops ]   pivot:"
                  + str(self.glops[index]._pivot_point))
            if hide:
                self.hide_glop(self.glops[index])

    def use_walkmesh(self, name, hide=True):
        result = False
        # for this_glop in self.glops:
        for index in range(0, len(self.glops)):
            if self.glops[index].name == name:
                result = True
                self.use_walkmesh_at(index, hide=hide)
                break
        return result

    def set_hud_background(self, path):
        self.ui.set_hud_background(path)

    def set_background_cylmap(self, path, unflip_enable=True):
        # self.load_obj("env_sphere.obj")
        # self.load_obj("maps/gi/etc/sky_sphere.obj")
        # env_indices = \
        #     self.get_indices_by_source_path("env_sphere.obj")
        # for i in range(0,len(env_indices)):
        #     index = env_indices[i]
        #     print("Preparing sky object "+str(index))
        #     self.ui.glops[index].set_texture_diffuse(path)
        if self.env_rectangle is not None:
            self.ui.canvas.before.remove(self.env_rectangle)
            self.env_rectangle = None
        original_path = path
        if path is not None:
            if not os.path.isfile(path):
                path = resource_find(path)
            if path is not None:
                # texture = CoreImage(path).texture
                # texture.wrap = repeat
                # self.env_rectangle = Rectangle(texture=texture)
                self.env_rectangle = Rectangle(source=path)
                self.env_orig_rect = Rectangle(source=path)
                # default is clamp_to_edge
                # self.env_rectangle.texture.wrap = "repeat"
                self.env_rectangle.texture.wrap = "mirrored_repeat"
                self.ui.canvas.before.add(self.env_rectangle)
                self.env_flip_enable = unflip_enable
            else:
                print("ERROR in set_background_cylmap: "
                      "\"{}\" not found in search path"
                      "".format(original_path))
        else:
            print("ERROR in set_background_cylmap: path is None")

    def preload_sound(self, path):
        if path is not None:
            if path not in self._sounds:
                self._sounds[path] = {}
                print("loading " + path)
                self._sounds[path]["loader"] = SoundLoader.load(path)

    def explode_glop_at(self, index, weapon_dict=None):
        self.on_explode_glop(
            get_vec3_from_point(self.glops[index]._t_ins),
            self.glops[index].properties['hit_radius'],
            index,
            weapon_dict
        )
        self.kill_glop_at(index, weapon_dict)

    def on_explode_glop(self, pos, radius, attacked_index, weapon_dict):
        print("[ KivyGlops ] NOTICE: there is no default on_explode_glop in this version, so nothing will be shown")

    def play_sound(self, path, loop=False):
        if path is not None:
            self.preload_sound(path)
            if self._sounds[path]:
                if get_verbose_enable():
                    print("playing " + path)
                self._sounds[path]["loader"].play()
            else:
                print("[ KivyGlops ] ERROR: Failed to play " + path)
        else:
            print("[ KivyGlops ] ERROR in play_sound: path is None")

    def play_music(self, path, loop=True):
        self.play_sound(path, loop=loop)

    def load_obj(self, source_path, swapyz_enable=False, centered=False,
                 pivot_to_g_enable=True):
        self.ui.suspend_debug_label_update(True)
        load_obj_start_s = best_timer()
        results = None
        cache_path = None
        cached_count = 0
        cache_path = None
        original_path = source_path
        if swapyz_enable:
            print("[ KivyGlops ] (load_obj)"
                  " swapyz_enable is NOT YET IMPLEMENTED")
        if source_path is not None:
            source_path = resource_find(source_path)
            if source_path is not None:
                if os.path.isfile(source_path):
                    # cache_name = \
                    #     hashlib.sha224(source_path).hexdigest()
                    # path_hash = hashlib.new('ripemd160')
                    # cache_name = path_hash.hexdigest()
                    # cache_name = \
                    #    hashlib.ripemd160(source_path).hexdigest()
                    # 20 like SHA-1, but blake2b is more secure:
                    try:
                        cache_name = \
                            hashlib.blake2b(digest_size=20).hexdigest()
                    except AttributeError:
                        if self.showNextHashWarning:
                            print("[ KivyGlops ] WARNING:"
                                  " blake2b is not present. KivyGlops"
                                  " is reverting to sha1.")
                        self.showNextHashWarning = False
                        cache_name = hashlib.sha1().hexdigest()
                    # NOTE: at this point, len(cache_name) should be 40
                    # (since is a hexdigest of a 20-value hash)
                    caches_path = "cache"
                    if not os.path.isdir(caches_path):
                        os.mkdir(caches_path)
                    glop_caches_path = os.path.join(caches_path, 'glop')
                    if not os.path.isdir(glop_caches_path):
                        os.mkdir(glop_caches_path)
                    cache_path = os.path.join(glop_caches_path,
                                              cache_name)
                    cache_path_enable = False
                    if not os.path.isdir(cache_path):
                        os.mkdir(cache_path)
                        cache_path_enable = True
                    new_glops = self.get_glop_list_from_obj(
                        source_path,
                        self.new_glop_method
                    )
                    if new_glops is None:
                        print("[ KivyGlops ] (load_obj) "
                              "FAILED TO LOAD '" + str(source_path)
                              + "'")
                    elif len(new_glops) < 1:
                        print("[ KivyGlops ] (load_obj) "
                              "NO VALID OBJECTS FOUND in '"
                              + str(source_path) + "'")
                    else:
                        if self.glops is None:
                            self.glops = list()

                        # for index in range(0, len(self.glops)):
                        favorite_pivot_point = None
                        for index in range(0, len(new_glops)):
                            new_glops[index].original_path = \
                                original_path
                            # this_glop = new_glops[index]
                            # this_glop = \
                            #     KivyGlop(pyglop=self.glops[index])
                            # if len(self.glops<=index):
                            #     self.glops.append(this_glop)
                            # else:
                            #     self.glops[index]=this_glop
                            # print("")
                            if favorite_pivot_point is None:
                                favorite_pivot_point = \
                                    new_glops[index]._pivot_point
                        if favorite_pivot_point is None:
                            favorite_pivot_point = (0.0, 0.0, 0.0)
                        folder_path = cache_path
                        for sub_name in os.listdir(folder_path):
                            sub_path = os.path.join(folder_path,
                                                    sub_name)
                            if sub_name[:1] != ".":
                                if len(sub_name) == 40 and \
                                   sub_name[:-5] == ".glop":
                                    # Remove uuid hex digest-named files
                                    os.remove(sub_path)
                        for index in range(0, len(new_glops)):
                            if pivot_to_g_enable:
                                # apply pivot point (so that glop's
                                # _t_ins is actually the center)
                                some_name = ""
                                if new_glops[index].name is not None:
                                    some_name = new_glops[index].name
                                self.ui.set_debug_label("processing pivot for mesh '" + some_name + "'...")
                                print("[ KivyGlops ] (load_obj) applying pivot point for " + some_name + "...")
                                prev_pivot = new_glops[index]._pivot_point[0], new_glops[index]._pivot_point[1], new_glops[index]._pivot_point[2]
                                new_glops[index].apply_pivot()
                                # print("    moving from "+str( (new_glops[index]._t_ins.x, new_glops[index]._t_ins.y, new_glops[index]._t_ins.z) ))
                                new_glops[index]._t_ins.x = prev_pivot[0]
                                new_glops[index]._t_ins.y = prev_pivot[1]
                                new_glops[index]._t_ins.z = prev_pivot[2]
                            new_glops[index].prepare_canvas()  # does generate_kivy_mesh() if needed
                            self.ui.add_glop(new_glops[index])
                            if results is None:
                                results = list()
                            results.append(len(self.glops)-1)
                            if (new_glops[index].name is None) and \
                               (cache_path_enable):
                                # ok since deleted uuid-named files already:
                                new_glops[index].name = str(uuid.uuid4())
                            if new_glops[index].name is not None:
                                new_glops[index].save(os.path.join(cache_path, good_path_name(new_glops[index].name) + ".glop"))
                        if centered:
                            # TODO: apply pivot point instead (change vertices as if pivot point were 0,0,0) to ensure translate 0 is world 0; instead of:
                            # center it (use only one pivot point, so all objects in obj file remain aligned with each other):

                            for index in range(0,len(new_glops)):
                                if index==0:
                                    print("  centering from "+str(favorite_pivot_point))
                                    print("  (this is the last centering message that will be shown)")
                                    print("")
                                new_glops[index].move_x_relative(-1.0*favorite_pivot_point[0])
                                new_glops[index].move_y_relative(-1.0*favorite_pivot_point[1])
                                new_glops[index].move_z_relative(-1.0*favorite_pivot_point[2])
                                # TODO: new_glops[index].apply_translate()
                                # TODO: new_glops[index].reset_translate()

                        # print("")
                else:
                    print("[ KivyGlops ] (load_obj) missing '" + \
                          source_path + "'")
            else:
                print("[ KivyGlops ] (load_obj) missing '" + \
                      original_path + "'")
        else:
            print("[ KivyGlops ] (load_obj) ERROR: source_path is None" + \
                  " for load_obj")
        load_obj_s = best_timer() - load_obj_start_s
        if results is not None:
            print("[ KivyGlops ] (load_obj) Loaded '" + original_path + \
                  "' in " + str(load_obj_s) + " seconds.")
            if cache_path is not None:
                stats_name = "stats.yml"
                stats_path = os.path.join(cache_path, stats_name)
                try:
                    outs = open(stats_path, 'w')
                    outs.write("original_path: " + original_path + "\n")
                    outs.write("path: " + source_path + "\n")
                    outs.close()
                    if cached_count > 0:
                        stats_name = "stats-cached.yml"
                        stats_path = os.path.join(cache_path, stats_name)
                        if not os.path.isfile(stats_path):
                            outs = open(stats_path, 'w')
                            outs.write("cached_load_time_s: " + \
                                       str(load_obj_s) + "\n")
                            outs.close()
                    else:
                        stats_name = "stats-notcached.yml"
                        stats_path = os.path.join(cache_path, stats_name)
                        if not os.path.isfile(stats_path):
                            outs = open(stats_path, 'w')
                            outs.write("not_cached_load_time_s: " + \
                                       str(load_obj_s) + "\n")
                            outs.close()
                except:
                    print("[ KivyGlops ] ERROR in load_obj--could not" + \
                          " finish saving stats to '" + stats_path + "'")
        else:
            print("[ KivyGlops ] (load_obj) WARNING: Loaded 0 objects.")
        self.ui.suspend_debug_label_update(False)
        return results

    def get_pressed(self, key_name):
        print("WARNING: (KivyGlops scene).get_pressed(key_name)"
              " is for backward compatibility only.")
        return self.player1_controller.get_pressed(self.ui.get_keycode(key_name))

    def constrain_glop_to_walkmesh(self, this_glop, height_only_enable=False):
        if len(self._walkmeshes)>0:
            walkmesh_result = self.get_container_walkmesh_and_poly_index_xz(this_glop._t_ins.xyz)
            if walkmesh_result is None:
                # print("Out of bounds")
                corrected_pos = None
                # if self.prev_inbounds_camera_translate is not None:
                #     this_glop._t_ins.x = self.prev_inbounds_camera_translate[0]
                #     this_glop._t_ins.y = self.prev_inbounds_camera_translate[1]
                #     this_glop._t_ins.z = self.prev_inbounds_camera_translate[2]
                # else:
                corrected_pos = self.get_nearest_walkmesh_vec3_using_xz(this_glop._t_ins.xyz)
                if corrected_pos is not None:
                    pushed_angle = get_angle_between_two_vec3_xz(this_glop._t_ins.xyz, corrected_pos)
                    corrected_pos = get_pushed_vec3_xz_rad(corrected_pos, this_glop.properties['hit_radius'], pushed_angle)
                    if not height_only_enable:
                        this_glop._t_ins.x = corrected_pos[0]
                        this_glop._t_ins.y = corrected_pos[1]   # TODO: check y (vertical) axis against eye height and jump height etc
                    # + this_glop.eye_height # no longer needed since swizzled to xz (get_nearest_walkmesh_vec3_using_xz returns original's y in return's y)
                    this_glop._t_ins.z = corrected_pos[2]
                # else:
                #     print("ERROR: could not find point to bring player in bounds.")
            else:
                # print("In bounds")
                result_glop = self._walkmeshes[walkmesh_result["walkmesh_index"]]
                X_i = result_glop._POSITION_OFFSET + 0
                Y_i = result_glop._POSITION_OFFSET + 1
                Z_i = result_glop._POSITION_OFFSET + 2
                ground_tri = list()
                ground_tri.append( (result_glop.vertices[result_glop.indices[walkmesh_result["polygon_offset"]]*result_glop.vertex_depth+X_i], result_glop.vertices[result_glop.indices[walkmesh_result["polygon_offset"]]*result_glop.vertex_depth+Y_i], result_glop.vertices[result_glop.indices[walkmesh_result["polygon_offset"]]*result_glop.vertex_depth+Z_i]) )
                ground_tri.append( (result_glop.vertices[result_glop.indices[walkmesh_result["polygon_offset"]+1]*result_glop.vertex_depth+X_i], result_glop.vertices[result_glop.indices[walkmesh_result["polygon_offset"]+1]*result_glop.vertex_depth+Y_i], result_glop.vertices[result_glop.indices[walkmesh_result["polygon_offset"]+1]*result_glop.vertex_depth+Z_i]) )
                ground_tri.append( (result_glop.vertices[result_glop.indices[walkmesh_result["polygon_offset"]+2]*result_glop.vertex_depth+X_i], result_glop.vertices[result_glop.indices[walkmesh_result["polygon_offset"]+2]*result_glop.vertex_depth+Y_i], result_glop.vertices[result_glop.indices[walkmesh_result["polygon_offset"]+2]*result_glop.vertex_depth+Z_i]) )
                # this_glop._t_ins.y = ground_tri[0][1] + this_glop.eye_height
                ground_y = get_y_from_xz(ground_tri[0], ground_tri[1], ground_tri[2], this_glop._t_ins.x, this_glop._t_ins.z)
                this_glop._t_ins.y = ground_y  # no longer add eye height, since that is done later to camera_glop relative to player, and only for CAMERA_FIRST_PERSON()
                if self._world_min_y is None or ground_y < self._world_min_y:
                    self._world_min_y = ground_y
                # if self.prev_inbounds_camera_translate is None or this_glop._t_ins.y != self.prev_inbounds_camera_translate[1]:
                #     print("y:"+str(this_glop._t_ins.y))
            global bounds_warning_enable
            if bounds_warning_enable:
                print("[ KivyGlops ] (verbose message) bounds used")
                bounds_warning_enable = False
        else:
            global no_bounds_warning_enable
            if no_bounds_warning_enable:
                print("[ KivyGlops ] (verbose message) no bounds")
                no_bounds_warning_enable = False
            pass

    def update(self):
        # KivyGlops.update is called by KivyGlopsWindow.*update*
        # such as update_glsl
        # super(KivyGlops, self).update()
        # region pre-bump ops
        # NOT: tried to move regions "pre-bump ops" and
        # "bump loop" to pyglops but didn't work well
        # print("coords:"+str(Window.mouse_pos))
        # see also asp and clip_top in init
        # screen_w_arc_theta = 32.0
        #     # actual number is fromprojectionMatrix matrix
        # screen_h_arc_theta = 18.0
        #     # actual number is from projectionMatrix matrix
        got_frame_delay = 0.0
        if self.last_update_s is not None:
            got_frame_delay = best_timer() - self.last_update_s
        self.last_update_s = best_timer()

        for i in range(0,len(self.glops)):
            if self.glops[i].look_target_glop is not None:
                self.glops[i].look_at(self.glops[i].look_target_glop)
                # print(str(self.glops[i].name)+" looks at "+str(self.glops[i].look_target_glop.name))
                # print("  at "+str((self.camera_glop._t_ins.x, self.camera_glop._t_ins.y, self.camera_glop._t_ins.z)))

        self.on_update_glops()

        rotation_multiplier_y = 0.0  # 1.0 is maximum speed
        moving_x = 0.0  # 1.0 is maximum speed
        moving_y = 0.0  # 1.0 is maximum speed
        moving_z = 0.0  # 1.0 is maximum speed; NOTE: increased z should move object closer to viewer in right-handed coordinate system
        moving_theta = 0.0
        position_change = [0.0, 0.0, 0.0]

        # for keycode strings, see  http://kivy.org/docs/_modules/kivy/core/window.html
        p1c = self.player1_controller
        chars = p1c.get_keymap_dict()
        if p1c.get_pressed(self.ui.get_keycode(chars['left'])):
            # if p1c.get_pressed(self.ui.get_keycode("shift")):
            moving_x = 1.0
            # else:
            #     rotation_multiplier_y = -1.0
        if p1c.get_pressed(self.ui.get_keycode(chars['right'])):
            # if p1c.get_pressed(self.ui.get_keycode("shift")):
            moving_x = -1.0
            # else:
            #     rotation_multiplier_y = 1.0
        if p1c.get_pressed(self.ui.get_keycode(chars['up'])):
            if self._fly_enables[self.player_glop.name]:
                # intentionally use z,y:
                moving_z, moving_y = get_rect_from_polar_rad(1.0, self.player_glop._r_ins_x.angle)
            else:
                moving_z = 1.0

        if p1c.get_pressed(self.ui.get_keycode(chars['down'])):
            # ^ r for Colemak
            if self._fly_enables[self.player_glop.name]:
                # intentionally use z,y:
                moving_z, moving_y = get_rect_from_polar_rad(1.0, self.player_glop._r_ins_x.angle)
                moving_z *= -1.0
                moving_y *= -1.0
            else:
                moving_z = -1.0

        if p1c.get_pressed(self.ui.get_keycode("enter")):
            self.use_selected(self.player_glop)


        land_units_this_frame = 12. / self.ui.frames_per_second
        # ^ TODO: compute this
        turn_radians_per_frame = math.radians(90.) / self.ui.frames_per_second
        # above are changed to glop settings if present:
        if (self.player_glop.actor_dict is not None):
            if ('land_units_per_second' in self.player_glop.actor_dict):
                land_units_this_frame = float(self.player_glop.actor_dict['land_units_per_second']) / self.ui.frames_per_second
            if 'land_degrees_per_second' in self.player_glop.actor_dict:
                turn_radians_per_frame = math.radians(float(self.player_glop.actor_dict['land_degrees_per_second'])) / self.ui.frames_per_second

        if rotation_multiplier_y != 0.0:
            delta_y = turn_radians_per_frame * rotation_multiplier_y
            self.player_glop._r_ins_y.angle += delta_y
            # origin_distance = math.sqrt(self.player_glop._t_ins.x*self.player_glop._t_ins.x + self.player_glop._t_ins.z*self.player_glop._t_ins.z)
            # self.player_glop._t_ins.x -= origin_distance * math.cos(delta_y)
            # self.player_glop._t_ins.z -= origin_distance * math.sin(delta_y)

        # xz coords of edges of 16x16 square are:
        # move in the direction you are facing
        moving_theta = 0.0
        if moving_x != 0.0 or moving_y != 0.0 or moving_z != 0.0:
            # makes movement relative to rotation (which alaso limits speed when moving diagonally):
            moving_theta = theta_radians_from_rectangular(moving_x, moving_z)
            moving_r_multiplier = math.sqrt((moving_x*moving_x)+(moving_z*moving_z))
            if moving_r_multiplier > 1.0:
                moving_r_multiplier = 1.0  # Limited so that you can't move faster when moving diagonally

            # TODO: reprogram so adding math.radians(-90) is not needed (?)
            position_change[0] = land_units_this_frame*moving_r_multiplier * math.cos(self.player_glop._r_ins_y.angle+moving_theta+math.radians(-90))
            position_change[1] = land_units_this_frame*moving_y
            position_change[2] = land_units_this_frame*moving_r_multiplier * math.sin(self.player_glop._r_ins_y.angle+moving_theta+math.radians(-90))

            # if (self.player_glop._t_ins.x + move_by_x > self._world_cube.get_max_x()):
            #     move_by_x = self._world_cube.get_max_x() - self.player_glop._t_ins.x
            #     print(str(self.player_glop._t_ins.x)+" of max_x:"+str(self._world_cube.get_max_x()))
            # if (self.player_glop._t_ins.z + move_by_z > self._world_cube.get_max_z()):
            #     move_by_z = self._world_cube.get_max_z() - self.player_glop._t_ins.z
            #     print(str(self.player_glop._t_ins.z)+" of max_z:"+str(self._world_cube.get_max_z()))
            # if (self.player_glop._t_ins.x + move_by_x < self._world_cube.get_min_x()):
            #     move_by_x = self._world_cube.get_min_x() - self.player_glop._t_ins.x
            #     print(str(self.player_glop._t_ins.x)+" of max_x:"+str(self._world_cube.get_max_x()))
            # if (self.player_glop._t_ins.z + move_by_z < self._world_cube.get_min_z()):
            #     move_by_z = self._world_cube.get_min_z() - self.player_glop._t_ins.z
            #     print(str(self.player_glop._t_ins.z)+" of max_z:"+str(self._world_cube.get_max_z()))

            # print(str(self.player_glop._t_ins.x)+","+str(self.player_glop._t_ins.z)+" each coordinate should be between matching one in "+str(self._world_cube.get_min_x())+","+str(self._world_cube.get_min_z())+" and "+str(self._world_cube.get_max_x())+","+str(self._world_cube.get_max_z()))
            # print(str( (self.player_glop._t_ins.x, self.player_glop._t_ins.y, self.player_glop._t_ins.z) )+" each coordinate should be between matching one in "+str(self.world_boundary_min)+" and "+str(self.world_boundary_max))

        # for axis_index in range(0,3):
        if position_change[0] is not None:
            self.player_glop._t_ins.x += position_change[0]
        if position_change[1] is not None:
            self.player_glop._t_ins.y += position_change[1]
        if position_change[2] is not None:
            self.player_glop._t_ins.z += position_change[2]

        self.constrain_glop_to_walkmesh(self.player_glop)

        # self.prev_inbounds_camera_translate = self.camera_glop._t_ins.x, self.camera_glop._t_ins.y, self.camera_glop._t_ins.z

        # else:
        #     self.camera_glop._t_ins.x += self.land_units_this_frame * moving_x
        #     self.camera_glop._t_ins.z += self.land_units_this_frame * moving_z

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #   DONE FINALIZING PLAYER LOCATION  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


        if self._camera_person_number == 1:
            self.camera_glop._t_ins.x = self.player_glop._t_ins.x
            self.camera_glop._t_ins.y = self.player_glop._t_ins.y + self.player_glop.eye_height
            self.camera_glop._t_ins.z = self.player_glop._t_ins.z
            self.camera_glop._r_ins_x.angle = self.player_glop._r_ins_x.angle
            self.camera_glop._r_ins_y.angle = self.player_glop._r_ins_y.angle
            self.camera_glop._r_ins_z.angle = self.player_glop._r_ins_z.angle
        elif self._camera_person_number == 0:
            pass
        else:
            print("ERROR: _camera_person_number " + str(_camera_person_number) + " is not yet implemented.")

        global missing_bumper_warning_enable
        global missing_bumpable_warning_enable
        global missing_radius_warning_enable
        for bumper_index_index in range(0,len(self._bumper_indices)):
            bumper_index = self._bumper_indices[bumper_index_index]
            if self.glops[bumper_index].actor_dict is None:
                print("[ KivyGlops ] error in update: actor_dict is None for bumper named '" + str(self.glops[bumper_index].name) + "'")
            if self.glops[bumper_index].actor_dict is not None and \
               "ai_enable" in self.glops[bumper_index].actor_dict and \
               self.glops[bumper_index].actor_dict["ai_enable"]:
                self.on_process_ai(bumper_index)
                # NOTE: moveto_index and target_index are guaranteed to exist by set_as_actor_at
                if self.glops[bumper_index].actor_dict["target_index"] is not None:
                    self.glops[bumper_index].actor_dict["target_pos"] = get_vec3_from_point(self.glops[self.glops[bumper_index].actor_dict["target_index"]]._t_ins)
                elif self.glops[bumper_index].actor_dict["moveto_index"] is not None:
                    if not self.glops[self.glops[bumper_index].actor_dict["moveto_index"]].visible_enable:
                        self.glops[bumper_index].actor_dict["moveto_index"] = None
                    else:
                        self.glops[bumper_index].actor_dict["target_pos"] = get_vec3_from_point(self.glops[self.glops[bumper_index].actor_dict["moveto_index"]]._t_ins)
                if self.glops[bumper_index].actor_dict["target_pos"] is not None:
                    self.glops[bumper_index].look_at_pos(self.glops[bumper_index].actor_dict["target_pos"])
                    src_pos = get_vec3_from_point(self.glops[bumper_index]._t_ins)
                    dest_pos = self.glops[bumper_index].actor_dict["target_pos"]
                    r = self.glops[bumper_index].actor_dict['land_units_per_second'] / self.ui.frames_per_second
                    distance = get_distance_vec3_xz(src_pos, dest_pos)
                    attack_radius = None
                    attack_s = None
                    acquire_radius = self.glops[bumper_index].reach_radius
                    if "target_index" in self.glops[bumper_index].actor_dict and self.glops[bumper_index].actor_dict["target_index"] is not None:
                        weapon_index = None
                        # NOTE: uses is determined by item, ranges is by actor
                        if self.glops[bumper_index].actor_dict['inventory_index'] > -1:
                            try_item = self.glops[bumper_index].actor_dict["inventory_items"][self.glops[bumper_index].actor_dict['inventory_index']]
                            if "uses" in try_item:
                                for this_use in try_item["uses"]:
                                    if this_use in self.attack_uses:
                                        attack_s = this_use
                                        # attack guarantees attack_types exists
                                        # (via set_as_item)
                                        acquire_radius = self.glops[bumper_index].actor_dict["ranges"]["throw_arc"]  # guaranteed to exist by set_as_actor_at
                                        weapon_index = self.glops[bumper_index].actor_dict['inventory_index']  # guaranteed to exist by set_as_actor_at
                                # TODO: loop again and look for melee
                            # else item has no use
                        if weapon_index is None:
                            # If weapon is not selected, choose random weapon even if selected a slot.
                            weapon_index, attack_s = self.glops[bumper_index].find_item_with_any_use(self.attack_uses)
                            if weapon_index > -1:
                                acquire_radius = self.glops[bumper_index].actor_dict["ranges"]["throw_arc"]
                            else:
                                weapon_index = None
                    if distance > acquire_radius:
                        theta = get_angle_between_two_vec3_xz(src_pos, dest_pos)
                        self.glops[bumper_index]._r_ins_y.angle = theta
                        delta_x, delta_z = get_rect_from_polar_rad(r, theta)
                        self.glops[bumper_index]._t_ins.x += delta_x
                        self.glops[bumper_index]._t_ins.z += delta_z
                        self.constrain_glop_to_walkmesh(self.glops[bumper_index], height_only_enable=True)
                    else:
                        # if has weapon and attack target, attack
                        if self.glops[bumper_index].actor_dict["target_index"] is not None:
                            if weapon_index is not None:
                                try:
                                    self.use_item_at(self.glops[bumper_index], weapon_index, this_use=attack_s)
                                except:
                                    print("[ KivyGlops ] ERROR--update could not finish using item " + str(weapon_index))
                                    view_traceback()
                        # else in range but can't attack

            bumper_name = self.glops[bumper_index].name
        # endregion pre-bump ops
        # region bump loop
        for bumpable_index_index in range(0, len(self._bumpable_indices)):
            bumpable_index = self._bumpable_indices[bumpable_index_index]
            if bumpable_index is not None:
                bumpable_name = self.glops[bumpable_index].name
                # self.glops[bumpable_index]._temp_bump_enable = True
                if (self.glops[bumpable_index].item_dict is None) or \
                   (not ('owner_key' in self.glops[bumpable_index].item_dict)) or \
                   (self.glops[bumpable_index].item_dict['owner_key'] is None):

                    if self.glops[bumpable_index].bump_enable is True:
                        for bumper_index_index in range(0,len(self._bumper_indices)):
                            bumper_index = self._bumper_indices[bumper_index_index]
                            if bumper_index is not None:
                                bumper_name = self.glops[bumper_index].name
                                distance = get_distance_kivyglops(self.glops[bumpable_index], self.glops[bumper_index])
                                if self.glops[bumpable_index].properties['hit_radius'] is not None and self.glops[bumpable_index].properties['hit_radius'] is not None:
                                    total_hit_radius = 0.0
                                    if self.glops[bumpable_index].projectile_dict is not None:
                                        total_hit_radius = self.glops[bumpable_index].properties['hit_radius'] + self.glops[bumper_index].properties['hit_radius']
                                    else:
                                        total_hit_radius = self.glops[bumpable_index].properties['hit_radius'] + self.glops[bumper_index].reach_radius
                                    if distance <= total_hit_radius:
                                        # print("total_hit_radius:" + str(total_hit_radius))
                                        if not (bumper_index in self.glops[bumpable_index].in_range_indices):
                                            # (only run if ever moved away from it)
                                            if get_verbose_enable():
                                                print("[ KivyGlops ] (verbose message) '" + str(self.glops[bumper_index].name) + "' in range of '" + str(self.glops[bumpable_index].name) + "'")
                                            if self.glops[bumper_index].bump_enable:
                                                if (self.glops[bumpable_index].projectile_dict is None) or \
                                                   (self.glops[bumper_index].properties['hitbox'] is None) or \
                                                   hitbox_contains_vec3(self.glops[bumper_index].properties['hitbox'], self.glops[bumpable_index]._t_ins.xyz):
                                                    # NOTE: already checked
                                                    # bumpable_index bump_enable above
                                                    # print("distance:" + str(total_hit_radius) + " <= total_hit_radius:" + str(total_hit_radius))
                                                    if self.glops[bumpable_index].projectile_dict is None or \
                                                       ("owner" not in self.glops[bumpable_index].projectile_dict) or \
                                                       (self.glops[bumpable_index].projectile_dict["owner"] != self.glops[bumper_index].name):
                                                        self._internal_bump_glop(bumpable_index, bumper_index)
                                                        if get_verbose_enable():
                                                            print("[ KivyGlops ] " + str(self.glops[bumper_index].name) + " bumped " + str(self.glops[bumpable_index].name))
                                                    else:
                                                        if get_verbose_enable():
                                                            print("[ KivyGlops ] (verbose message) cannot bump own projectile")
                                                else:
                                                    global out_of_hitbox_note_enable
                                                    if out_of_hitbox_note_enable:
                                                        print("[ KivyGlops ] (debug only--this is normal) within total_hit_radius, but bumpable is not in bumper's hitbox: "+str(self.glops[bumper_index].properties['hitbox']))
                                                        out_of_hitbox_note_enable = False
                                            else:
                                                if get_verbose_enable():
                                                    print("[ KivyGlops ] (verbose message) '" + str(self.glops[bumper_index].name) + "' is not a bumper.")
                                            if not bumper_index in self.glops[bumpable_index].in_range_indices:
                                                self.glops[bumpable_index].in_range_indices.append(bumper_index)
                                        # else:
                                        #    print("not out of range yet")
                                    else:
                                        if bumper_index in self.glops[bumpable_index].in_range_indices:
                                            self.glops[bumpable_index].in_range_indices.remove(bumper_index)
                                        if distance < 2:
                                            # debug only:
                                            # print("did not bump "+str(bumpable_name)+" (distance:"+str(distance)+"; bumper is at "+str( (self.glops[bumper_index]._t_ins.x,self.glops[bumper_index]._t_ins.y,self.glops[bumper_index]._t_ins.z) )+")")
                                            pass
                                        pass
                                else:
                                    if missing_radius_warning_enable:
                                        print("WARNING: Missing radius while checking bumped named "+str(bumpable_name))
                                        missing_radius_warning_enable = False
                            else:
                                pass  # None will be cleaned up after bump loop
                    if self.glops[bumpable_index]._cached_floor_y is None:
                        self.glops[bumpable_index]._cached_floor_y = self._world_min_y
                        # TODO: get from walkmesh instead
                    if self.glops[bumpable_index].physics_enable:
                        if self.glops[bumpable_index]._cached_floor_y is not None:
                            if self.glops[bumpable_index]._t_ins.y - self.glops[bumpable_index].properties['hit_radius'] - kEpsilon > self.glops[bumpable_index]._cached_floor_y:
                                # TODO: why does this make things float? self.glops[bumpable_index]._r_ins_x.angle += 15.
                                self.glops[bumpable_index]._t_ins.x += self.glops[bumpable_index].x_velocity * got_frame_delay
                                self.glops[bumpable_index]._t_ins.y += self.glops[bumpable_index].y_velocity * got_frame_delay
                                self.glops[bumpable_index]._t_ins.z += self.glops[bumpable_index].z_velocity * got_frame_delay
                                if got_frame_delay > 0.0:
                                    # print("[ KivyGlops ] (verbose message) GRAVITY AFFECTED:"+str(self.glops[bumpable_index]._t_ins.y)+" += "+str(self.glops[bumpable_index].y_velocity))
                                    self.glops[bumpable_index].y_velocity -= self._world_grav_acceleration * got_frame_delay
                                    # print("[ KivyGlops ] (verbose message) THEN VELOCITY CHANGED TO:"+str(self.glops[bumpable_index].y_velocity))
                                    # print("[ KivyGlops ] (verbose message) FRAME INTERVAL:"+str(got_frame_delay))
                                else:
                                    print("[ KivyGlops ] WARNING: no frame delay is detectable (update normally runs automatically once per frame but seems to be running more often)")
                            else:
                                # TODO: optionally, such as for bottom-heavy items: self.glops[bumpable_index]._r_ins_x.angle = 0.
                                # if self.glops[bumpable_index].z_velocity > kEpsilon:
                                if (self.glops[bumpable_index].y_velocity < 0.0 - (kEpsilon + self.glops[bumpable_index].properties['hit_radius'])):
                                    # print("  HIT GROUND Y:"+str(self.glops[bumpable_index]._cached_floor_y))
                                    # bump_sound_paths is guaranteed by PyGlop _init_glop to exist
                                    if len(self.glops[bumpable_index].properties["bump_sound_paths"]) > 0:
                                        rand_i = random.randrange(0,len(self.glops[bumpable_index].properties["bump_sound_paths"]))
                                        self.play_sound(self.glops[bumpable_index].properties["bump_sound_paths"][rand_i])
                                if self.glops[bumpable_index].projectile_dict is not None:
                                    if self.glops[bumpable_index].projectile_dict is not None:
                                        self.glops[bumpable_index].projectile_dict = None

                                self.glops[bumpable_index]._t_ins.y = self.glops[bumpable_index]._cached_floor_y + self.glops[bumpable_index].properties['hit_radius']
                                if self.glops[bumpable_index].x_velocity != 0.0 or \
                                   self.glops[bumpable_index].y_velocity != 0.0 or \
                                   self.glops[bumpable_index].z_velocity != 0.0:
                                    if get_verbose_enable():
                                        print("[ KivyGlops ] stopped glop {" + \
                                              "hit_radius:" + \
                                              str(self.glops[bumpable_index].properties['hit_radius']) + \
                                              "; glop._cached_floor_y:" + \
                                              str(self.glops[bumpable_index]._cached_floor_y) + \
                                              "}")
                                self.glops[bumpable_index].x_velocity = 0.0
                                self.glops[bumpable_index].y_velocity = 0.0
                                self.glops[bumpable_index].z_velocity = 0.0
                        else:
                            # no gravity
                            self.glops[bumpable_index]._t_ins.x += self.glops[bumpable_index].x_velocity
                            self.glops[bumpable_index]._t_ins.y += self.glops[bumpable_index].y_velocity
                            self.glops[bumpable_index]._t_ins.z += self.glops[bumpable_index].z_velocity
                else:  # is in inventory of some actor
                    self.glops[bumpable_index]._t_ins.x = self.glops[self.glops[bumpable_index].item_dict['owner_key']]._t_ins.x
                    self.glops[bumpable_index]._t_ins.y = self.glops[self.glops[bumpable_index].item_dict['owner_key']]._t_ins.y
                    self.glops[bumpable_index]._t_ins.z = self.glops[self.glops[bumpable_index].item_dict['owner_key']]._t_ins.z
            else:
                pass  # None will be cleaned up later
        # endregion bump loop
        for j in reversed(range(len(self._bumpable_indices))):
            if self._bumpable_indices[j] == None:
                del(self._bumpable_indices[j])
        for j in reversed(range(len(self._bumper_indices))):
            if self._bumper_indices[j] == None:
                del(self._bumper_indices[j])

        # if get_verbose_enable():
        #     print("update_glsl...")
        #     print("[ KivyGlops ] (verbose message) update matrices...")
        asp = float(self.ui.width) / float(self.ui.height)

        clip_top = 0.06  # NOTE: 0.03 is ~1.72 degrees, if that matters
        # formerly field_of_view_factor
        # was changed to .03 when projection_near was changed from
        # 1 to .1
        # was .3 when projection_near was 1

        clip_right = asp*clip_top  # formerly overwrote asp
        self.projectionMatrix = Matrix()
        self.modelViewMatrix = Matrix()

        # self.modelViewMatrix.rotate(
        #     self.camera_glop._r_ins_x.angle,1.0,0.0,0.0)
        # self.modelViewMatrix.rotate(
        #     self.camera_glop._r_ins_y.angle,0.0,1.0,0.0)
        # look_at(eyeX, eyeY, eyeZ, centerX, centerY, centerZ, upX, upY,
        #         upZ)  # http://kivy.org/docs/
        #               # api-kivy.graphics.transformation.html
        # self.modelViewMatrix.rotate(self.camera_glop._r_ins_z.angle,
        #                             0.0, 0.0, 1.0)
        previous_look_point = None
        if self.look_point is not None:
            previous_look_point = (
                self.look_point[0],
                self.look_point[1],
                self.look_point[2]
            )

        self.look_point = [0.0, 0.0, 0.0]

        # 0 is the angle (1, 2, and 3 are the matrix)
        self.look_point[0] = \
            (self.focal_distance
             * math.cos(self.camera_glop._r_ins_y.angle))
        self.look_point[2] = \
            (self.focal_distance
             * math.sin(self.camera_glop._r_ins_y.angle))
        # print("self.camera_glop._r_ins_y.angle: "
        #       + str(self.camera_glop._r_ins_y.angle))

        # self.look_point[1] = 0.0
        # ^ (changed in "for" loop below) since y is up, and 1 is y,
        #   ignore index 1 when we are rotating on that axis
        self.look_point[1] = \
            (self.focal_distance
             * math.sin(self.camera_glop._r_ins_x.angle))

        # self.modelViewMatrix = self.modelViewMatrix.look_at(
        #     0, self.camera_glop._t_ins.y,0, self.look_point[0],
        #     self.look_point[1], self.look_point[2], 0, 1, 0)

        # Since camera's target should be relative to camera,
        # add camera's position:

        self.look_point[0] += self.camera_glop._t_ins.x
        self.look_point[1] += self.camera_glop._t_ins.y
        self.look_point[2] += self.camera_glop._t_ins.z

        # must translate first, otherwise look_at will override
        # position on rotation axis ('y' in this case)
        self.modelViewMatrix.translate(self.camera_glop._t_ins.x,
                                       self.camera_glop._t_ins.y,
                                       self.camera_glop._t_ins.z)
        self.modelViewMatrix = self.modelViewMatrix.look_at(
            self.camera_glop._t_ins.x,
            self.camera_glop._t_ins.y,
            self.camera_glop._t_ins.z,
            self.look_point[0],
            self.look_point[1],
            self.look_point[2],
            0,
            1,
            0
        )

        # projectionMatrix.
        # view_clip(left, right, bottom, top, near, far, perspective)
        # "In OpenGL, a 3D point in eye space is projected onto the
        # near plane (projection plane)"
        # -http://www.songho.ca/opengl/gl_projectionmatrix.html
        # The near plane and far plane distances are in the -z direction
        # but are expressed as positive values since they are distances
        # from the camera then they are compressed to -1 to 1
        # -https://www.youtube.com/watch?v=frtzb2WWECg
        self.projectionMatrix = self.projectionMatrix.view_clip(
            -clip_right, clip_right, -1*clip_top, clip_top,
            self.projection_near,
            100,  # far
            1,  # perspective
        )
        top_theta = theta_radians_from_rectangular(
            self.projection_near, clip_top)
        right_theta = theta_radians_from_rectangular(
            self.projection_near, clip_right)
        self.ui.screen_w_arc_theta = right_theta*2.0
        self.ui.screen_h_arc_theta = top_theta*2.0

        glwCv = self.ui.gl_widget.canvas
        glwCv['projection_mat'] = self.projectionMatrix
        glwCv['modelview_mat'] = self.modelViewMatrix
        glwCv['camera_world_pos'] = self.camera_glop._t_ins.xyz

        # if get_verbose_enable():
        #     Logger.debug("ok (update_glsl)")

        # is_look_point_changed = False
        # if previous_look_point is not None:
        #     for axis_index in range(3):
        #         if self.look_point[axis_index] != \
        #                 previous_look_point[axis_index]:
        #             is_look_point_changed = True
        #             # print(str(self.look_point) + " was " +
        #             #       str(previous_look_point))
        #             break
        # else:
        #     is_look_point_changed = True
        # if is_look_point_changed:
        #     pass
        #     # print("Now looking at " + str(self.look_point))
        #     # print(
        #         # "position: " +
        #         # str(get_vec3_from_point(self.camera_glop._t_ins)" +
        #         # "; self.camera_glop._r_ins_y.angle:" +
        #         # str(self.camera_glop._r_ins_y.angle) +
        #         # "(" +
        #         # str(math.degrees(self.camera_glop._r_ins_y.angle)) +
        #         # "degrees); moving_theta:" +
        #         # str(math.degrees(moving_theta)) +
        #         # " degrees")

        if ((self._previous_world_light_dir is None)
                or (self._previous_world_light_dir[0]
                    != glwCv['_world_light_dir'][0])
                or (self._previous_world_light_dir[1]
                    != glwCv['_world_light_dir'][1])
                or (self._previous_world_light_dir[2]
                    != glwCv['_world_light_dir'][2])
                or (self._previous_camera_rotate_y_angle is None)
                or (self._previous_camera_rotate_y_angle
                    != self.camera_glop._r_ins_y.angle)):
            # glwCv['_world_light_dir'] = (0.0,.5,1.0)
            # glwCv['_world_light_dir_eye_space'] = (0.0,.5,1.0)
            world_light_theta = theta_radians_from_rectangular(glwCv['_world_light_dir'][0], glwCv['_world_light_dir'][2])
            light_theta = world_light_theta + self.camera_glop._r_ins_y.angle
            light_r = math.sqrt((glwCv['_world_light_dir'][0] * glwCv['_world_light_dir'][0]) + (glwCv['_world_light_dir'][2] * glwCv['_world_light_dir'][2]))
            glwCv['_world_light_dir_eye_space'] = light_r * math.cos(light_theta), glwCv['_world_light_dir_eye_space'][1], light_r * math.sin(light_theta)
            self._previous_camera_rotate_y_angle = self.camera_glop._r_ins_y.angle
            self._previous_world_light_dir = glwCv['_world_light_dir'][0], glwCv['_world_light_dir'][1], glwCv['_world_light_dir'][2]


class GLWidget(Widget):
    pass


class HudForm(BoxLayout):
    pass


class ContainerForm(BoxLayout):
    pass


class KivyGlopsWindow(ContainerForm):  # formerly a subclass of Widget

    scene = None  # only use for drawing frames and sending input
    frames_per_second = None
    _fps_last_frame_tick = None
    _fps_accumulated_time = None
    _fps_accumulated_count = None
    _average_fps = None
    _contexts = None
    # ^ InstructionGroup so gl operations can be added in
    # realtime (after resetCallback is added, but so
    # resetCallback is on the stack after them)

    # region Window TODO: rename to _*
    use_button = None
    hud_bg_rect = None
    screen_w_arc_theta = None
    screen_h_arc_theta = None
    # endregion Window TODO: rename to _*
    # region Window
    hud_form = None
    hud_buttons_form = None
    gl_widget = None
    # endregion Window

    def __init__(self, **kwargs):
        # self.scene = KivyGlops()
        # self.scene.ui = self
        self.debug_label_suspended_level = 0
        self.dummy_glop = KivyGlop()
        self._fps_accumulated_time = 0.0
        self._fps_accumulated_count = 0
        self.frames_per_second = 60.0
        self.gl_widget = GLWidget()
        self.hud_form = HudForm(orientation="vertical",
                                size_hint=(1.0, 1.0))
        self.hud_buttons_form = BoxLayout(orientation="horizontal",
                                          size_hint=(1.0, 0.1))

        # fix incorrect keycodes if present (such as in kivy <= 1.8.0):
        if (Keyboard.keycodes['-'] == 41):
            Keyboard.keycodes['-'] = 45
        if (Keyboard.keycodes['='] == 43):
            Keyboard.keycodes['='] = 61

        try:
            self._keyboard = Window.request_keyboard(
                self._keyboard_closed,
                self
            )
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
            self._keyboard.bind(on_key_up=self._on_keyboard_up)
        except:
            print("[ KivyGlopsWindow ] Could not finish loading "
                  "keyboard (keyboard may not be present).")

        # self.bind(on_touch_down=self.canvasTouchDown)

        self.gl_widget.canvas = RenderContext(compute_normal_mat=True)
        self.gl_widget.canvas['_world_light_dir'] = (0.0, 0.5, 1.0)
        self.gl_widget.canvas['_world_light_dir_eye_space'] = \
            (0.0, 0.5, 1.0)  # rotated in update*
        self.gl_widget.canvas['camera_light_multiplier'] = \
            (1.0, 1.0, 1.0, 1.0)
        # self.gl_widget.canvas.shader.source = \
        #     resource_find('simple1b.glsl')
        # self.gl_widget.canvas.shader.source = \
        #     resource_find('shade-kivyglops-standard.glsl')  # BROKEN
        # self.gl_widget.canvas.shader.source = \
        #     resource_find('shade-normal-only.glsl') #partially working
        # self.gl_widget.canvas.shader.source = \
        #     resource_find('shade-texture-only.glsl')
        # self.gl_widget.canvas.shader.source = \
        #     resource_find(os.path.join('shaders','fresnel.glsl'))
        shader_path = None
        if _multicontext_enable:
            # self.gl_widget.canvas.shader.source = \
            #     resource_find('kivyglops-testing.glsl')  # BROKEN
            shader_path = os.path.join('shaders', 'kivyglops.glsl')
        else:
            shader_path = os.path.join('shaders',
                                       'kivyglops-singlecontext.glsl')
        print("[ KivyGlopsWindow ] default shader has been set to '"
              + shader_path + "'")
        self.gl_widget.canvas.shader.source = resource_find(shader_path)

        # formerly, .obj was loaded here using load_obj
        # (now calling program does that)

        # print(self.gl_widget.canvas.shader)
        # ^ just prints type and memory address
        if dump_enable:
            glopsYAMLLines = []
            # self.scene.emit_yaml(glopsYAMLLines)
            try:
                thisFile = open('glops-dump.yml', 'w')
                for i in range(0, len(glopsYAMLLines)):
                    thisFile.write(glopsYAMLLines[i] + "\n")
                thisFile.close()
            except:
                print("[ KivyGlopsWindow ] ERROR: Update"
                      " could not finish writing a dump.")
        super(KivyGlopsWindow, self).__init__(**kwargs)
        self.cb = Callback(self.setup_gl_context)
        self.gl_widget.canvas.add(self.cb)

        self.gl_widget.canvas.add(PushMatrix())

        # self.gl_widget.canvas.add(PushMatrix())
        # self.gl_widget.canvas.add(this_texture)
        # self.gl_widget.canvas.add(Color(1, 1, 1, 1))
        # for this_glop_index in range(0,len(self.scene.glops)):
        #    this_mesh_name = ""
        #    # thisMesh = KivyGlop()
        #    this_glop = self.scene.glops[this_glop_index]
        #    add_glop(this_glop)
        # self.gl_widget.canvas.add(PopMatrix())
        self._contexts = InstructionGroup()
        # RenderContext(compute_normal_mat=True)
        self.gl_widget.canvas.add(self._contexts)

        self.finalize_canvas()
        self.add_widget(self.gl_widget)
        # self.hud_form.rows = 1
        self.add_widget(self.hud_form)

        self.debug_label = Factory.Label(text="...",
                                         color=(.5, .5, .5, 1.0))
        self.hud_form.add_widget(self.debug_label)
        self.hud_form.add_widget(self.hud_buttons_form)
        self.inventory_prev_button = Factory.Button(
            text="<",
            # id="inventory_prev_button",
            size_hint=(.2, 1.0),
            on_press=self.inventory_prev_button_press
        )
        self.use_button = Factory.Button(
            text="0: Empty",
            # id="use_button",
            size_hint=(.2, 1.0),
            on_press=self.inventory_use_button_press
        )
        self.inventory_next_button = Factory.Button(
            text=">",
            # id="inventory_next_button",
            size_hint=(.2, 1.0),
            on_press=self.inventory_next_button_press
        )
        self.hud_buttons_form.add_widget(self.inventory_prev_button)
        self.hud_buttons_form.add_widget(self.use_button)
        self.hud_buttons_form.add_widget(self.inventory_next_button)

        # Window.bind(on_motion=self.on_motion)
        # # TODO ?: formerly didn't work, but maybe failed since
        # # used Window instead of self--see
        # # <https://kivy.org/docs/api-kivy.input.motionevent.html>

        Clock.schedule_interval(self.update_glsl,
                                1.0 / self.frames_per_second)
        #                        1.0 / 5.)  # debug only

        self._touches = []

    def get_class_name(self):
        return "KivyGlopsWindow"

    def set_hud_background(self, path):
        if path is not None:
            original_path = path
            if not os.path.isfile(path):
                path = resource_find(path)
            if path is not None:
                self.hud_form.canvas.before.clear()
                # self.hud_form.canvas.before.add(
                #     Color(1.0,1.0,1.0,1.0))
                self.hud_bg_rect = Rectangle(size=self.hud_form.size,
                                             pos=self.hud_form.pos,
                                             source=path)
                self.hud_form.canvas.before.add(self.hud_bg_rect)
                self.hud_form.source = path
            else:
                print("[ KivyGlopsWindow ] ERROR in set_hud_image:"
                      " could not find \"{}\"".format(original_path))
        else:
            print("[ KivyGlopsWindow ] ERROR in set_hud_image:"
                  " path is None")

    def set_primary_item_caption(self, name):
        self.use_button.text = name

    def get_keycode(self, key_name):
        return Keyboard.keycodes[key_name]

    def spawn_pex_particles(self, path, pos, radius=1.0,
                            duration_seconds=None):
        if path is not None:
            if os.path.isfile(path):
                print("[ KivyGlopsWindow ] found '{}'"
                      "  (not yet implemented)".format(path))
                # Range is 0 to 250px for size, so therefore translate
                # to meters:
                # divide by 125 to get meters, then multiply by radius,
                # so that pex file can determine "extra" (>125)
                # or "reduced" (<125) size while retaining pixel-based
                # sizing.
            else:
                print("[ KivyGlopsWindow ] missing '{}'"
                      "".format(path))
        else:
            print("[ KivyGlopsWindow ] ERROR in "
                  "spawn_pex_particles: path is None")

    def inventory_prev_button_press(self, instance):
        event_dict = self.scene.player_glop.sel_next_inv_slot(False)
        self.scene.after_selected_item(event_dict)

    def inventory_use_button_press(self, instance):
        event_dict = self.scene.use_selected(self.scene.player_glop)
        # self.scene.after_selected_item(event_dict)

    def inventory_next_button_press(self, instance):
        event_dict = self.scene.player_glop.sel_next_inv_slot(True)
        self.scene.after_selected_item(event_dict)

    def get_view_angles_by_pos_rad(self, pos):
        global debug_dict  # from common.py
        x_angle = -math.pi + (float(pos[0])/float(self.width-1))*(2.0*math.pi)
        y_angle = -(math.pi/2.0) + (float(pos[1])/float(self.height-1))*(math.pi)
        if 'View' not in debug_dict:
            debug_dict['View'] = {}
        # debug_dict['View']['NOTE'] = "should match camera_glop"
        debug_dict['View']['mouse_pos'] = str(pos)
        debug_dict['View']['size'] = str((self.width, self.height))
        debug_dict['View']['pitch,yaw'] = str((
            int(math.degrees(x_angle)),
            int(math.degrees(y_angle))
        ))
        if ((self.screen_w_arc_theta is not None)
                and (self.screen_h_arc_theta is not None)):
            debug_dict['View']['field of view'] = \
                str((int(math.degrees(self.screen_w_arc_theta)),
                     int(math.degrees(self.screen_h_arc_theta))))
        else:
            if 'field of view' in debug_dict['View']:
                debug_dict['View']['field of view'] = None
        self.update_debug_label()
        return x_angle, y_angle

    # def hide_glop(self, this_glop):
    #     self.scene.hide_glop(this_glop)

    # def show_glop(self, this_glop_index):
    #     self.scene.show_glop(this_glop_index)

    def add_glop(self, this_glop, set_visible_enable=None):
        participle = "initializing"
        try:
            if set_visible_enable is not None:
                this_glop.visible_enable = set_visible_enable
            # context = self._contexts
            # context = self.gl_widget.canvas
            # if self.scene.selected_glop_index is None:
            #     self.scene.selected_glop_index = this_glop_index
            #     self.scene.selected_glop = this_glop
            if self.scene.glops is None:
                self.scene.glops = []
            self.scene.selected_glop_index = len(self.scene.glops)
            self.scene.selected_glop = this_glop
            this_glop.glop_index = len(self.scene.glops)
            self.scene.glops.append(this_glop)
            if self.scene.glops[this_glop.glop_index] is not this_glop:
                # then deal with multithreading paranoia:
                print("[ KivyGlopsWindow ] ERROR in add_glop"
                      ": index was wrong, correcting...")
                this_glop.glop_index = None
                for i in range(len(self.scene.glops)):
                    if self.scene.glops[i] is this_glop:
                        self.scene.glops[i].glop_index = i
                        break
                if this_glop.glop_index is None:
                    print("                      ERROR: unable to correct index")
            # self.scene.glops[len(self.scene.glops)-1].glop_index = len(self.scene.glops) - 1
            # this_glop.glop_index = len(self.scene.glops) - 1

            self._contexts.add(this_glop.get_context())  # _contexts is a visible instruction group
            if get_verbose_enable():
                print("[ KivyGlopsWindow ] Appended Glop (count:" + str(len(self.scene.glops)) + ").")
            if _multicontext_enable:
                if not this_glop._own_shader_enable:
                    this_glop.canvas.shader.source = self.gl_widget.canvas.shader.source
                # NOTE: projectionMatrix and modelViewMatrix don't exist yet if add_glop was called before first frame!
                # this_glop.set_uniform('projection_mat', self.scene.projectionMatrix)
                # this_glop.set_uniform('modelview_mat', self.scene.modelViewMatrix)
                this_glop.set_uniform('camera_world_pos', self.scene.camera_glop._t_ins.xyz)

        except:
            print("[ KivyGlopsWindow ] ERROR: Could not finish "
                  + participle + " in KivyGlops load_obj")
            view_traceback()

    def setup_gl_context(self, *args):
        glEnable(GL_DEPTH_TEST)

    def reset_gl_context(self, *args):
        glDisable(GL_DEPTH_TEST)

    def finalize_canvas(self):
        self.gl_widget.canvas.add(PopMatrix())
        self.resetCallback = Callback(self.reset_gl_context)
        self.gl_widget.canvas.add(self.resetCallback)

    def update_glsl(self, *largs):
        actual_fps = None
        actual_frame_interval = None
        update_enable = False
        try:
            if self.scene._loaded_glops_enable:
                update_enable = True
        except:
            print("[ KivyGlopsWindow ] ERROR in update_glsl:"
                  " Could not finish accessing scene. You must:")
            print("# Create your main program class like:")
            print("class MainScene(KivyGlops):")
            print("# Then create your scene like:")
            print("scene = MainScene(KivyGlopsWindow())")
            print("# You do not save the mainform class,"
                  " scene does that, so")
            print("# hand over your scene to Kivy in"
                  " your App's build method:")
            print("return scene.ui  # (not mainform)")
            sys.exit(1)
        if update_enable:
            if self.scene._loaded_glops_enable:
                if self._fps_last_frame_tick is not None:
                    # NOTE: best_timer() is a second
                    actual_frame_interval = best_timer() - self._fps_last_frame_tick
                    self._fps_accumulated_time += actual_frame_interval
                    self._fps_accumulated_count += 1
                    if self._fps_accumulated_time > .5:
                        self._average_fps = 1.0 / (self._fps_accumulated_time/float(self._fps_accumulated_count))
                        self._fps_accumulated_time = 0.0
                        self._fps_accumulated_count = 0
                    if actual_frame_interval > 0.0:
                        actual_fps = 1.0 / actual_frame_interval
                self._fps_last_frame_tick = best_timer()
                if not self.scene._visual_debug_enable:
                    self.debug_label.opacity = 0.0
                else:
                    self.debug_label.opacity = 1.0

                if self.scene.env_rectangle is not None:
                    if self.screen_w_arc_theta is not None and self.screen_h_arc_theta is not None:
                        # then calculate environment mapping variables
                        # region old way (does not repeat)
                        # env_h_ratio = (2 * math.pi) / self.screen_h_arc_theta
                        # env_w_ratio = env_h_ratio * math.pi
                        # self.scene.env_rectangle.size = (
                        #     Window.size[0]*env_w_ratio,
                        #     Window.size[1]*env_h_ratio
                        # )
                        # self.scene.env_rectangle.pos = (
                        #     -(self.camera_glop._r_ins_y.angle/(2*math.pi)*self.scene.env_rectangle.size[0]),
                        #     -(self.camera_glop._r_ins_x.angle/(2*math.pi)*self.scene.env_rectangle.size[1])
                        # )
                        # engregion old way (does not repeat)
                        self.scene.env_rectangle.size = Window.size
                        self.scene.env_rectangle.pos = 0.0, 0.0
                        view_right = self.screen_w_arc_theta / 2.0 + self.scene.camera_glop._r_ins_y.angle
                        view_left = view_right - self.screen_w_arc_theta
                        view_top = self.screen_h_arc_theta / 2.0 + self.scene.camera_glop._r_ins_x.angle + 90.0
                        view_bottom = view_top - self.screen_h_arc_theta
                        circle_theta = 2*math.pi
                        view_right_ratio = view_right / circle_theta
                        view_left_ratio = view_left / circle_theta
                        view_top_ratio = view_top / circle_theta
                        view_bottom_ratio = view_bottom / circle_theta
                        # tex_coords order: u,      v,      u + w,  v,
                        #                   u + w,  v + h,  u,      v + h
                        # as per https://kivy.org/planet/2014/02/using-tex_coords-in-kivy-for-fun-and-profit/
                        self.scene.env_rectangle.tex_coords = view_left_ratio, view_bottom_ratio, view_right_ratio, view_bottom_ratio, \
                                                        view_right_ratio, view_top_ratio, view_left_ratio, view_top_ratio

                x_rad, y_rad = self.get_view_angles_by_pos_rad(Window.mouse_pos)
                self.scene.player_glop._r_ins_y.angle = x_rad
                self.scene.player_glop._r_ins_x.angle = y_rad
                if 'View' not in debug_dict:
                    debug_dict['View'] = dict()
                debug_dict['View']["camera x,y: "] = str(self.scene.camera_glop._t_ins.xyz)
                if self._average_fps is not None:
                    debug_dict['View']['fps'] = str(self._average_fps)
                # global debug_dict
                # if "Player" not in debug_dict:
                #     debug_dict["Player"] = {}
                # debug_dict["Player"]["_r_ins_x.angle"] = str(_r_ins_x.angle)
                # debug_dict["Player"]["_r_ins_y.angle"] = str(_r_ins_y.angle)
                # debug_dict["Player"]["_r_ins_z.angle"] = str(_r_ins_z.angle)
                # self.ui.update_debug_label()

                self.hud_form.pos = 0.0, 0.0
                self.hud_form.size = Window.size
                if self.hud_bg_rect is not None:
                    self.hud_bg_rect.size = self.hud_form.size
                    self.hud_bg_rect.pos=self.hud_form.pos

                self.scene.update()

                # forcibly use parent info (should not be needed if use_parent_projection use_parent_modelview use_parent_frag_modelview options of RenderContext constructor for canvas of children)
                # for i in range(len(self.scene.glops)):
                #    this_glop = self.scene.glops[i]
                #    this_glop.set_uniform('modelview_mat', self.scene.modelViewMatrix)
                #    this_glop.set_uniform('camera_world_pos', self.scene.camera_glop._t_ins.xyz)
            # else not loaded yet so don't try to use gl_widget or glops
        if not self.scene._loaded_glops_enable:
            self.debug_label.opacity = 1.0
            self.scene._load_glops_enable = False
            self.debug_label.text = ("Welcome to KivyGlops\n"
                                     "Controls:\n"
                                     "* F3: debug screen\n\n"
                                     "\n"
                                     "busy loading glops...\n")
            if not self.scene._loading_glops_enable:
                self.scene._loading_glops_enable = True
                Clock.schedule_once(self._deferred_load_glops, 0.)

    def _deferred_load_glops(self, dt):
        if get_verbose_enable():
            print("_deferred_load_glops: {} dt = {}"
                  "".format(type(dt), dt))
        self.scene.on_load_glops()  # also moved from ui
        self.scene._loaded_glops_enable = True
        self.debug_label.text = ""

    '''
    def get_view_angles_by_touch_deg(self, touch):
        # formerly define_rotate_angle(self, touch):
        x_angle = (touch.dx/self.width)*360
        y_angle = -1*(touch.dy/self.height)*360
        return x_angle, y_angle

    def get_view_angles_by_pos_deg(self, pos):
        x_angle = (pos[0]/self.width)*360
        y_angle = -1*(pos[1]/self.height)*360
        return x_angle, y_angle
    '''

    def toggle_visual_debug(self):
        if not self.scene._visual_debug_enable:
            self.scene._visual_debug_enable = True
            self.debug_label.opacity = 1.0
            # self._contexts.clear()
            for this_glop in self.scene.glops:
                if this_glop._axes_mesh is not None:
                    this_glop.prepare_canvas([this_glop._axes_mesh],
                                             xyz_widget_index=0)
                    context = this_glop.get_context()
                    this_glop.set_uniform("texture0_enable", False)
                else:
                    print("[ KivyGlopsWindow ] ERROR in "
                          "toggle_visual_debug: no _axes_mesh"
                          " for glop '{}'".format(this_glop.name))
            print("[ KivyGlopsWindow ] set _visual_debug_enable: True")
        else:
            self.scene._visual_debug_enable = False
            self.debug_label.opacity = 0.0
            # self._contexts.clear()
            for this_glop in self.scene.glops:
                this_glop.prepare_canvas([this_glop._mesh])
                if this_glop._mesh is not None:
                    if this_glop._mesh.texture is not None:
                        this_glop.set_uniform("texture0_enable", True)
                else:
                    # doesn't actually matter
                    if get_verbose_enable():
                        if this_glop.no_mesh_warning_enable:
                            this_glop.no_mesh_warning_enable = False
                            print("[ KivyGlopsWindow ] WARNING in"
                                  " toggle_visual_debug: _mesh is"
                                  " None for {}".format(this_glop.name))
            print("[ KivyGlopsWindow ] set _visual_debug_enable: False")

    def set_debug_label(self, text):
        self.debug_label.text = text

    def suspend_debug_label_update(self, enable):
        if enable:
            if self.debug_label_suspended_level < 0:
                print("[ KivyGlopsWindow ] WARNING: "
                      "self.debug_label_suspended_level was {}"
                      "so forcing to 0"
                      "".format(self.debug_label_suspended_level))
                self.debug_label_suspended_level = 0
            self.debug_label_suspended_level += 1
        else:
            self.debug_label_suspended_level -= 1

    def update_debug_label(self):
        if self.debug_label_suspended_level <= 0:
            yaml = ""
            indent = ""
            for key in debug_dict.keys():
                yaml += indent + key + ":\n"
                yaml = \
                    push_yaml_text(yaml, key, debug_dict[key], indent)
                # if debug_dict[key] is None:
                #     self.debug_label.text = key + ": None"
                # elif type(debug_dict[key]) is dict:
            self.debug_label.text = yaml

    # def canvasTouchDown(self, touch, *largs):
    #     touchX, touchY = largs[0].pos
    #     # self.player_glop.targetX = touchX
    #     # self.player_glop.targetY = touchY
    #     print("\n")
    #     print(str(largs).replace("\" ", "\"\n"))

    def on_touch_down(self, touch):
        super(KivyGlopsWindow, self).on_touch_down(touch)
        # touch.grab(self)
        # self._touches.append(touch)

        # thisTouch = MouseMotionEvent(touch)
        # thisTouch.
        if touch.is_mouse_scrolling:
            event_dict = None
            if touch.button == "scrolldown":
                event_dict = \
                    self.scene.player_glop.sel_next_inv_slot(True)
            else:
                event_dict = \
                    self.scene.player_glop.sel_next_inv_slot(False)
            self.scene.after_selected_item(event_dict)
        else:
            if get_verbose_enable():
                print("[ KivyGlopsWindow ] (verbose message in"
                      " on_touch_down) touch down")
            event_dict = \
                self.scene.use_selected(self.scene.player_glop)

    def on_touch_up(self, touch):
        super(KivyGlopsWindow, self).on_touch_up(touch)
        # touch.ungrab(self)
        # self._touches.remove(touch)
        # self.scene.player1_controller.dump()

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        # print('The key' + str(keycode) + ' pressed')
        # print(' - text is ' + text)
        # print(' - modifiers are ' + str(modifiers))

        # print("pressed keycode " + str(keycode[0]) +
        #       " (should match keycode constant: " +
        #       str(Keyboard.keycodes[keycode[1]]) + ")")

        # if len(keycode[1])>0:
        self.scene.player1_controller.set_pressed(keycode[0],
                                                  keycode[1], True)

        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard
        if keycode[1] == 'escape':
            pass  # keyboard.release()
        # elif keycode[1] == 'w':
        #     self.scene.player_glop._t_ins.z += \
        #         land_units_this_frame
        # elif keycode[1] == 's':
        #     self.scene.player_glop._t_ins.z -= \
        #         land_units_this_frame
        # elif text == 'a':
        #     self.scene.player1_controller['left'] = True
        #     self.moving_x = -1.0
        # elif text == 'd':
        #     self.moving_x = 1.0
        #     self.scene.player1_controller['right'] = True
        # elif keycode[1] == '.':
        #     self.look_at_center()
        # elif keycode[1] == 'numpadadd':
        #     pass
        # elif keycode[1] == 'numpadsubtract' or \
        #         keycode[1] == 'numpadsubstract':
        #                 # since is mispelled as
        #                 # numpadsubstract in kivy ~ 1.8
        #     pass
        elif keycode[1] == "tab":
            self.scene.select_mesh_at(self.scene.selected_glop_index+1)
            # if get_verbose_enable():
            this_name = None
            if self.scene.selected_glop_index is not None:
                this_name = ("[{}]"
                             "".format(self.scene.selected_glop_index))
            if self.scene.selected_glop is not None and \
                    self.scene.selected_glop.name is not None:
                this_name = self.scene.selected_glop.name
            if this_name is not None:
                print("[ KivyGlopsWindow ] Selected glop: " + this_name)
            else:
                print("[ KivyGlopsWindow ] Select glop failed"
                      " (maybe there are no glops loaded.")
        elif keycode[1] == "x":
            event_dict = self.scene.player_glop.sel_next_inv_slot(True)
            self.scene.after_selected_item(event_dict)
        elif keycode[1] == "z":
            event_dict = self.scene.player_glop.sel_next_inv_slot(False)
            self.scene.after_selected_item(event_dict)
        elif keycode[1] == "f3":
            self.toggle_visual_debug()
        # else:
        #     print('Pressed unused key: '
        #           + str(keycode) + "; text:"+text)

        global debug_dict
        if 'View' not in debug_dict:
            debug_dict['View'] = {}
        debug_dict['View']['modelview_mat'] = str(self.gl_widget.canvas['modelview_mat'])
        if 'camera_glop' not in debug_dict:
            debug_dict['camera_glop'] = {}
        debug_dict['camera_glop']['rot_y'] = str(self.scene.camera_glop._r_ins_y.angle)
        if 'player_glop' not in debug_dict:
            debug_dict['player_glop'] = {}
        if 'land_units_per_second' in self.scene.player_glop.actor_dict:
            debug_dict['player_glop']['land_units_per_second'] = self.scene.player_glop.actor_dict['land_units_per_second']
        if 'hp' in self.scene.player_glop.actor_dict:
            debug_dict['player_glop']['hp'] = self.scene.player_glop.actor_dict['hp']
        self.scene.camera_glop.debug_to(debug_dict['camera_glop'])


        # if get_verbose_enable():
        #     print("[ KivyGlopsWindow ] "
        #           "scene.camera_glop._r_ins_y.angle: "
        #           + str(self.scene.camera_glop._r_ins_y.angle))
        #     print("[ KivyGlopsWindow ] modelview_mat: "
        #           + str(self.gl_widget.canvas['modelview_mat']))
        # self.update_glsl()
        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True

    def _on_keyboard_up(self, keyboard, keycode):
        self.scene.player1_controller.set_pressed(keycode[0],
                                                  keycode[1], False)
        # print('[ KivyGlopsWindow ] Released key ' + str(keycode))

    def _keyboard_closed(self):
        print('[ KivyGlopsWindow ] Keyboard disconnected!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    '''
    def on_motion(self, etype, motionevent):
        print("[ KivyGlopsWindow ] coords:"
              + str(motionevent.dx) + "," + str(motionevent.dx))
        # will receive all motion events.
        pass
    '''

    def on_touch_move(self, touch):
        # print("[ KivyGlopsWindow ] touch.dx:" + str(touch.dx)
        #       + " touch.dy:" + str(touch.dx))
        pass
        '''
        print ("[ KivyGlopsWindow ] on_touch_move")
        print (str(touch))
        # Logger.debug("dx: %s, dy: %s. Widget: (%s, %s)"
        #              % (touch.dx, touch.dy,
        #                 self.width, self.height))
        # self.update_glsl()
        if touch in self._touches and touch.grab_current == self:
            if len(self._touches) == 1:
                # here do just rotation
                ax, ay = self.define_rotate_angle(touch)
                self.rotx.angle += ax
                self.roty.angle += ay
                # ax, ay = math.radians(ax), math.radians(ay)
            elif len(self._touches) == 2: # scaling here
                # use two touches to determine do we need scale
                touch1, touch2 = self._touches
                old_pos1 = \
                    (touch1.x - touch1.dx, touch1.y - touch1.dy)
                old_pos2 = \
                    (touch2.x - touch2.dx, touch2.y - touch2.dy)
                old_dx = old_pos1[0] - old_pos2[0]
                old_dy = old_pos1[1] - old_pos2[1]
                old_distance = (old_dx*old_dx + old_dy*old_dy)
                Logger.debug('Old distance: %s' % old_distance)
                new_dx = touch1.x - touch2.x
                new_dy = touch1.y - touch2.y
                new_distance = (new_dx*new_dx + new_dy*new_dy)
                Logger.debug('New distance: %s' % new_distance)
                self.camera_walk_units_per_frame = \
                    self.camera_walk_units_per_second /
                    self.frames_per_second
                # self.camera_walk_units_per_frame = 0.01
                if new_distance > old_distance:
                    scale = -1*self.camera_walk_units_per_frame
                    Logger.debug('Scale up')
                elif new_distance == old_distance:
                    scale = 0
                else:
                    scale = self.camera_walk_units_per_frame
                    Logger.debug('Scale down')
                if scale:
                    self.scene.camera_glop._t_ins.z += scale
                    print(str(scale) + " " +
                          (self.scene.camera_glop._t_ins.x,
                           self.scene.camera_glop._t_ins.y,
                           self.scene.camera_glop._t_ins.z
                           ))
            self.update_glsl()
        '''
