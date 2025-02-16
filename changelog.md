# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

`*`: not done in master (or not known to be done)


## [git 7161e2477eda4751665567e93a5b0ccb3b8b8f34] - 2021-06-23
### Changed
- (from staging after fix) Add a variable to shorten lines & to reduce dict use in apply_vertex_offset.


## [git] - 2021-06-23
### Added
(from staging)
- (PyGlop) Warn if vector length (vertex depth) < 4 in `append_wobject`.

### Changed
(from staging except where noted with `*`)
- Invert some checks to reduce the level of nested statements in:
  - (KivyGlop) `calculate_hit_range`
  - (PyGlop) `append_wobject`
  - `*` (PyGlop) `apply_vertex_offset`
  - `*` (PyGlop) `has_item`
  - (PyGlops) `set_as_actor_at`
  - (PyGlops) `set_as_item_at`
    - `*` (PyGlops) Finish incomplete code changes for inverting checks for when: item_dict is missing, no `'name'`, not `is_ready`, not `cooldown` reached in `set_as_item_at`.
  - (PyGlops) `throw_glop`
- Change `env_rectangle.texture.wrap`'s value to "mirrored_repeat"
- Add/change variables to shorten lines:
  - `ad = self.actor_dict` in `pop_glop_item`, `has_item`
  - `sv = self.vertices` and `vo = v_offset+self._POSITION_OFFSET` in `apply_vertex_offset`
  - `ov = od[this_key]` in `deepcopy_with_my_type`
  - `hb = self.properties.get('hitbox')`, `phr = self.properties.get('hit_radius')`, `hr = phr` in `apply_vertex_offset`
  - `rmte = ref_my_type_enable` in `deepcopy_with_my_type` & change uses.
  - Use `vf` `pi` in `append_wobject`
    - `*` Use `vf` where longhand was used in `append_wobject`.
  - Change `axisIndex` to `axI` in `angles_to_angle_and_matrix`
  - `ddu = debug_dict[user_glop.name]`, `ugad = user_glop.actor_dict` in `use_item_at`
  - `fgid` and `fgpd` in `throw_glop`
    - rename `fgid` and `fgpd` to `item` and `projectile`
  - `hb`, `hr`, `PO` in `calculate_hit_range`
- Utilize `get_is_glop` instead of `isinstance` in `deepcopy_with_my_type`.
- `*` Add a True return if the item was used in `use_item_at` and `throw_glop`, otherwise False.
- Change some local variable names.
- `*` change `not...in` to `not in` in `preprocess_item`.

### Fixed
(from staging)
- Handle missing vertex format metadata in:
  - `generate_plane`
  - `generate_axes`
- `*` change "calling method" to "calling_method" where wrong (wrong in fewer but one or more places in staging).
- (not wrong in stable) Fix PEP8 issues in staging.
- Fix PEP8 issues in both staging and stable.
- Change `ancestors=ancestors` to `ancestors=ancestors[:oa_len]`  in `deepcopy_with_my_type`.
  - `*` Change `orig_ancestors_len` in beginning of `deepcopy_with_my_type` and change uses.
  - `*` Move `rmve` (added to stable) to beginning of `deepcopy_with_my_type`.
- Implement new `hitbox` key (no longer a member) in `calculate_hit_range`

## [git] - 2021-06-23
### Added
(from staging: KivyGlops-audit-3a66898)
- Add methods to standardize position get/set for PyGlops and subclasses.
- Add `unflip_enable` variable and corresponding `set_background_cylmap` param and set `self.env_flip_enable` from that.
- Initialize `self.env_orig_rect`.
- various docstrings (and move comments to doctstrings in several cases)
- warn if glop is not item in `get_owner_name` and `get_owner_index`
- `env_orig_rect` & `env_flip_enable`
- `*` comment: `#  stays false if inventory was full` after `sied['fit_enable'] = False` in pyglops.py.

### Changed
(from staging: KivyGlops-audit-3a66898)
- `*` (done in staging) Improve the `is_in_triangle_coords` docstring.
- Change double to single quotes in several places to match the new style choice of staging and master branches.
- Move `*Glop` variables to `__init__`.
- Move `PyGlops` variables to `__init__`.
- Change method order to match staging branch:
  - Move the `append_wobject` to before `save`
  - (PyGlops) Move `set_fly` and `set_gravity` to after `__init__`
- Change `exit` to `raise RuntimeError` in one case.
- `*` Rename `get_owner_index` to `get_owner_key`.
- Rename (from staging):
  - `show_next_no_mesh_warning_enable` to `no_mesh_warning_enable`
  - `pivot_to_geometry_enable` to `pivot_to_g_enable`
  - `owner_index` to `owner_key`
  - `copy_my_type_by_reference_enable` to `ref_my_type_enable`
  - `copy_verts_by_ref_enable` to `ref_my_verts_enable`
  - Rename several local variables to make lines shorter.
  - `*` `get_owner_index` to `get_owner_key`
  - `new_glop` to `new_glop_method`
  - `killed_glop` to `on_killed_glop`
  - `attacked_glop` to `on_attacked_glop`
  - `_last_frame_tick` to `_fps_last_frame_tick`
  - `select_next_inventory_slot` to `sel_next_inv_slot`
  - `display_explosion` to `on_explode_glop`
  - `process_ai` to `on_process_ai`

### Fixed
- (from staging) Make ishadereditor compatible with the new `dict` material.
- `*` (already correct in stable) Improve PEP8 in:
  - example-stadium.py
  - ishadereditor.py
  - pyrealtime.py
  - testing.py
- `*` (already correct in stable) Improve pathing in example-stadium.py.
- (from staging) Add a missing `on_vertex_format_change` call in `copy_as_mesh_instance`.
- `*` (already correct in stable) Change `global look_at_none_warning_enable` to `look_at_pos_none_warning_enable` in one instance.
  - Both are real globals but one was used wrongly.
- `*` Initialize material in `KivyGlop` `__init__`.
- `*` Add missing `self.showNextHashWarning = True` in `KivyGlops`' `__init__`.
- `*` (only in staging) change `siedsied` to `sied` (There was one instance in pyglops.py).
- (from staging) Change `if line_strip[:1] != "# ":` to `if line_strip[:1] != "#":`
- Improve use of PEP8 (Also make fixes in staging from stable and fixes listed below that weren't in either).
  - `*` (for ones only wrong in staging, see today's commit in staging).
    - See [d928809](https://github.com/poikilos/KivyGlops/commit/d9288091c9b32fb1a02a71e94910996a871877c9)
  - `*` at `print("y:"+str(this_glop._t_ins.y))`
  - `*` at `print("not out of range yet")`
  - `*` at `print("did not bump`
  - `*` at `print("update_glsl...")` and line after that
  - `*` at `glwCv["_world_light_dir"]` and line after that
  - `*` at `self.scene.env_rectangle.size =` and after that `self.scene.env_rectangle.pos =` (comments)
  - `*` at `for i in range(len(self.scene.glops)):` and lines after that (comments)
  - `*` at `print("[ KivyGlopsWindow ] scene.camera_glop._r_ins_y.angle:` and line after that (comments)
  - `*` at `if "bumpable_name" in result:` and 3 lines after that and one before (comments).
  - `*` at `Process the item event so selected inventory slot`
  - `*` at `bump loop is done in update` (comment)
  - `*` at `if thisTextureFileName is not None:`
  - `*` at `target.projectile_dict =` in `copy_as_subclass`
  - `*` at `RenderContext(compute_normal_mat=True)`, `rotated in update_glsl`, `to hide` in testingkivy3d.py
  (comments)
  - `*` at `ok since adding it below` in wobjfile.py (comment)
  - `*` Move comments to docstring for `give_item_by_keyword_to_player_number`.
  - `*` Move comments to docstring for `give_item_index_to_player_number`.
  - `*` Move comments to docstring for `def CAMERA_*`.
  - `*` Move comments to docstring for `set_gravity`.
  - `*` wrap `give_item_by_keyword_to_player_number`, `give_item_index_to_player_number` to reduce line length.
  - `*` "aka" to "a.k.a." in ishadereditor.py
- `*` (already correct in stable) `....to_string()` where `str(...)` should be used because hitbox became a dict at `bumpable is not in bumper's hitbox`
- `*` (already correct in stable) `axes_index` to `axis_index`
- `*` (done in staging) `hide seem` to `hide seam`
- (from staging) change "# " to '#' in wobjfile.py


## [git] - 2021-06-19
### Fixed
- `*` (ishadereditor.py) change `is ... not this_glop` to `... is not this_glop` and remove an extra parenthesis.


## [git] - 2021-06-19
### Added
- globals and common functions from staging (KivyGlops-audit-3a66898)

### Changed
- Reorganize globals.
- Rename `get_index_by_name` to `find_by_name`.
- Make PEP8 changes.
- Rename `set_true_like_strings` to `set_truthies`.
- Rename `true_like_strings` to `truthies`.
- Rename `getAngleBetweenPoints` to `get_angle_between_points`

### Fixed
- (common.py) Use `val` instead of `val_lower` for `is True`.

## [git] - 2021-06-19
### Changed
- Change `KivyGlopsMaterial` and `PyGlopsMaterial` to dict (instances: `material`; methods: constructor, `copy`, `new_material`; change related methods: `set_textures_from_wmaterial`, `copy_as_subclass`--deprecate `new_material_method` argument)
  - deprecate methods: `create_material`, `new_material_method`

### Fixed
- `*` `specular_coefficent` to `specular_coefficient`
- `*` (pyglops) Remove deprecated calls to `emit_yaml` method of material (now a dict).
  - Change emit_yaml
- `*`  Add the missing return in `copy_material`
- `*`  Improve the error handling in `get_texture_diffuse_path`.


## [git] - 2021-06-19
### Changed
- Change `PyGlopHitBox` to dict (instances: `hitbox`, `target`; methods: `constructor` [to `new_hitbox`], `.copy` [to `copy_hitbox`], `contains_vec3` [to `hitbox_contains_vec3`], `to_string`; properties: `minimums`, `maximums`; deprecate methods: `*is_glop_hitbox`)

### Fixed
- `*` `global look_at_none_warning_enable` becomes `global look_at_pos_none_warning_enable`.
- `*` (in comment) `rediculously` to `ridiculously`
- `*` (in comment) `hitbot` to `hitbox`
- `*` use pythonic array multiplication to initialize the hitbox lists (`[sys.maxsize] * 3`, `[-sys.maxsize] * 3`)
  - `*` change from `sys.maxsize` and `-sys.maxsize` to `sys.float_info.max` and `sys.float_info.min`


## [git] - 2018-01-12
- (was sending self.new_glop_method instead of self.new_material_method) fix KivyGlopMaterial not using copy_as_subclass correctly
- changed default projectile_speed (see also throw_speed) to 15 (was 1.0) for realism (works now, with since now physics is correct--second-based)--still no wind resistance, so things will go rather far
- added infinite recursion checking to copy_as_subclass & deepcopy_with_my_type (and fixed deepcopy_with_my_type)
- kivyglops.py: moved code using walkmesh from update to new method: constrain_glop_to_walkmesh
- changed boolean is_out_of_range to list in_range_indices which makes way more sense (bumpable gets one bump per bumper, and thrower can be added to list so bumper doesn't hit itself with the bumpable)
- pyglops.py: limited eye height to 86.5% of hitbox['maximums'][1] in calculate_hit_range (so throwing looks better; see "Phi in the human body")
- pyglops.py: eliminated `fired_glop.name = str(fires_glop.name) + "." + str(projectile_dict["subscript"])` (was redundant since `fired_glop.name = "fired[" + str(self.fired_count) + "]"` was already used)
- pyglops.py: (PyGlops) combined throw types into single throw_glop method
- pyglops.py: changed usage of whether item drops on use from `['droppable'] = "no"` to `['drop_enable'] = False`
- pyglops.py: (PyGlop) added `has_item_with_any_use(uses)` method
- kivyglops.py: (KivyGlops update) fixed ai_enable case (weapon choosing, attacking only if target is glop, etc)
- pyglops.py: now required to use `item_dict['projectile_keys']` to specify any keys (such as hit_damage) from item_dict which should be copied to projectile_dict while traveling
- pyglops.py: removes owner as should


## [git] - 2018-01-11
- pyglops.py: (move `is_out_of_range` from `_internal_bump_glop` to `_update` in kivyglops.py and set immediately after checked) fixed issue where is_out_of_range was only being set for items
- kivyglops.py, pyglops.py: (only bumper [not even bumpable] has or needs hitbox; hitbox is set to None by super calculate_hit_range so stays that way if no override, so check for bumpable_enable before calling calculate_hit_range from _on_change_s_ins; check for hitbox before using in apply_vertex_offset; check whether glop_index is usable during calculate_hit_range to make sure it is not used improperly) prevent using glop_index before assigned (since _on_change_s_ins happens during append_wobject via _on_change_pivot, before glop is bumpable)
- change copy.deepcopy to get_dict_deepcopy where possible for safety with wierd types and python2
- fix PyGlop deepcopy_with_my_type (pre-allocate list, use copy or '=', etc)
- reduced verbosity by checking get_verbose_enable() in more situations
- show glop_name of selected item on debug screen
- removed extra declaration of _run_command in PyGlops
- pyglops.py: removed redundant call to self._run_semicolon_separated_commands from _internal_bump_glop
- pyglops.py: (PyGlops) added missing spawn_pex_particles (calls self.ui.spawn_pex_particles)
- pyglops.py: (if as_projectile in item_dict used, set bump_enable to True--is set to false when obtained) make thrown items bumping work while traveling (airborne after thrown, etc)
- pyglops.py: put projectile_dict case before item_dict case in _internal_bump_glop so projectiles that are items work (such as thrown glop items with weapon_dict stored at as_projectile key in item_dict)
- common.py: now you can do `from common import *` then `set_verbose_enable(True)` for manipulating debug output manually (now False can stay as default during debugging)
- pyglops.py: now you can set `item_dict['droppable']` to false for any item to be emitted (produces items which can't be picked up, so that inventory is not duplicated forever)
- pyglops.py: (now multiplies velocities [meters per second] by got_frame_delay [seconds] as should) make speed of objects more realistic


## [git] - 2018-01-10
- move `properties['inventory_items']` to `actor_dict['inventory_items']` (same for `'inventory_index'`)
- move `is_linked_as`, `get_link_as`, `get_link_and_type`, `push_glop_item`, `pop_glop_item` from KivyGlop to PyGlop
- made `projectile_dict` a deepcopy of `item_glop.item_dict['as_projectile']` instead of a reference since `projectile_dict` contains flight-specific information
- changed `item['use'] = "*"` to `item['uses'] = ["*"]`  where `*` is a use for the item such as `throw_arc` or `melee`
- replaced `bump_sound_paths` with `properties['bump_sound_paths']`
- created `add_damaged_sound_at` method for PyGlops scene (in properties so available to non-actors)
- (no longer inherits from Widget) workaround disturbing `'dict' is not callable` error in Kivy 1.9.0
- pyglops.py: (copy_as_subclass call in copy) fix potentially very bad bug -- `self.copy_as_subclass(self.new_glop_method, new_material_method)` had 3 params (not correct) 2nd one being another self.new_glop_method
- remove redundant call to _init_glop in KivyGlop __init__ (still calls it if super fails)
- improved monkey: added eyelids, UV mapped eyelids, improved texture for eyes and around eyes
- now uses `_deferred_load_glops` to load glops; to be more clear and functional, made separate load, loading, loaded booleans for `*_glops_enable`
- pyglops.py: `_internal_bump_glop` now plays random sound from bumper's `properties['damaged_sound_paths']`


## [git] - 2018-01-09
- fresnel.glsl utilize per-object booleans
- renamed shade-kivyglops-minimal.glsl to kivyglops-testing.glsl
- added `use_parent_frag_modelview=True` to RenderContext constructor for KivyGlop
- made `_multicontext_enable` global (if false, glop gets InstructionGroup as canvas instead of RenderContext)
- renamed `print_location` to `log_camera_info`
- consolidated get_verbose_enable() to be in one file only (common.py)
- pyglops.py: removed uses of `Logger` to `print` to be framework-independent
- eliminate scene.log_camera_info()
  - create kivyglop.debug_to(dict);
  - move ui's camera_walk_units_per_second and
    `camera_turn_radians_per_second` to
    `*_glop.actor_dict['land_speed']` and `land_degrees_per_second`
    (player_glop in this case); changed their per_frame equivalents to
    local variables in kivyglops.update
- move `self.camera_walk_units_per_second = 12.0` to actor_dict
- move `self.camera_turn_radians_per_second = math.radians(90.0)` to actor_dict
- fixed issue where projectile sprites not visible (probably a refactoring bug)


## [git] - 2018-01-03
- fixed selection crash (issue caused by refactoring)
- added use_walkmesh_at method for using walkmesh when you know glop index
- renamed set_as_item_by_index to set_as_item_at; set_as_actor_by_index to set_as_actor_at; explode_glop_by_index to explode_glop_at; kill_glop_by_index to kill_glop_at; give_item_by_index_to_player_number to give_item_index_to_player_number; obtain_glop_by_index to obtain_glop_at; add_bump_sound_by_index to add_bump_sound_at; select_mesh_by_index to select_mesh_at
- changed `set_player_fly(self, fly_enable)` to `set_player_fly(self, player_number, fly_enable)`


## [git] - 2018-01-02
- changed `new_glop_method` to `new_material_method` in KivyGlopMaterial


## [git] - 2018-01-01
- changed KivyGlop canvas to default type instead of InstructionGroup
  - commented `self.canvas = InstructionGroup` in KivyGlop `__init__`
  - changed uses of texture0_enable to use canvas as dict
  - changed init to set it to RenderContext
  - kivyglops.py (KivyGlop) changed init to manually call `_init_glop`
    after `__init__` since with multiple inheritance, super only calls
    first inherited object (first type in parenthesis on `class` line);
    - Rename PyGlop `__init__` to `_init_glop`
    - Change order of inheritance to `Widget, PyGlop`


## [git] - 2017-12-28
- added optional set_visible_enable param to add_glop (and made default not set visible to True)
- moved glop canvas editing from KivyGlops.add_glop to KivyGlop.prepare_canvas
- renamed `_meshes` to `_contexts` for clarity (but `_meshes` is used other places as an actual list of Mesh objects)


## [git] - 2017-12-27
- transitioned from material classes to material dict--see "wmaterial dict spec" subheading under "Developer Notes" (since dict can just be interpreted later; and so 100% of data can be loaded even if mtl file doesn't follow spec)
- In mtl loader, renamed `args_string`, `args` & `param` to `options_string`, `options` & `option` for clarity, since mtl spec calls the chunks following the command values: option if starts with hyphen, args if follow option, and values if is part of statement (or command) [1]
- eliminated numerical indices for objects in WObjFile object (changed self.wobjects from list to dict), and name property of WObject
- renamed set_textures_from_mtl_dict to set_textures_from_wmaterial
- fully implemented face grouping from complete OBJ spec including multiple groups (`g` with no param means "default" group, and no `g` at all means "default" group)
- ishadereditor.py: made it use KivyGlops; renamed viewer to gl_widget


## [git] - 2017-12-26
- fixed issue where cooldown last used time wasn't set before item was first used (now is ready upon first time ever added to an inventory)
- started implementing "carry" and dict-ify KivyGlops savable members ("tmp" dict member should not be saved)


## [git] - 2017-12-22
- get_indices_by_source_path now checks against original_path (as passed to load_obj; non-normalized) in addition to processed path
- renamed is_possible to fit_enable
- refactored global get_glop_from_wobject into `*Glop append_wobject` to assist with overriding, and with expandability (in case multi submesh glops are needed later)


## [git] - 2017-12-21
- renamed get_dict_deepcopy_except_my_type to deepcopy_with_my_type and made it work for either list or dict (and should work for any subclass since checks for type(self), so was eliminated from subclass)
- renamed bump_sounds to bump_sound_paths for clarity
- added copy constructors to PyGlops, PyGlopMaterial, and where appropriate, subclasses
- Change `Color(Color(1.0, 1.0, 1.0, 1.0))` to
  `Color(1.0, 1.0, 1.0, 1.0)`.
- Rename `*append_dump` to `*emit_yaml`.
- changed emit_yaml methods since an object shouldn't need to know its
  own context to save (for example, should be allowable to have data
  members directly indented under line equal to "-")
- (fixed issue introduced by refactoring) translate instruction should
  be copied by value not reference for glop
- separated `player_glop` from `camera_glop` (see PyGlops `__init__`)
  and keys now move player instead of camera (if most recent param sent
  to self.set_camera_person was self.CAMERA_FIRST_PERSON(), which is
  done by default)
- fix issue where add_actor_weapon uses player_glop instead of the glop
  referenced by the glop_index param (bug was exposed by camera_glop and
  player_glop being separated)
- split `rotate_view_relative` into `rotate_camera_relative` and
  `rotate_player_relative`; moved them to KivyGlops since they use Kivy
  OpenGL instructions; renamed rotate_view_relative_around_point to
  rotate_relative_around_point and forces you to specify a glop as first
  parameter (still needs to be edited in major way to rotate around the
  point instead of assuming things about the object)


## [git] - 2017-12-20
### Changed
- Rename kivyglopsminimal.py to etc/kivyglops-mini-deprecated.py
- Update kivyglopstesting.py to account for refactoring
- Change to more permissive license (See
  [license.txt](license.txt))


## [git] - 2017-12-19
- added ability to load non-standard obj file using commands without
  params
  - Leave WObject name as None if not specified
  - Add ability to load non-standard object signaling (AND naming) in
    obj file AFTER useless g command, (such as, name WObject
    `some_name` if has `# object some_name then useless comments` on
    any line before data but after line with just `g` or `o` command
    but only if no name follows those commands).
- Store vertex_group_type in WObject (for future implementation).
- Standardize `emit_yaml` methods (and use `standard_emit_yaml` when
  necessary) for consistent yaml and consistent coding: (list, tab, name
  [, data | self]).
- wobjfile.py: always use face groups, to accomodate face groups feature
  of OBJ spec [1]; added more fault-tolerance to by creating vertex list
  whenever first vertex of a list is declared, and creating face groups
  whenever first face of a list is declared
- wobjfile.py: elimintated smoothing_group in favor of
  this_face_group_type and this_face_group_name (this_face_group_type
  's' is a smoothing group)


## [git] - 2017-12-17
- `frames_per_second` moved from KivyGlops to KivyGlops window since it
  is implementation-specific (and so KivyGlops instance doesn't need to
  exist during KivyGlopsWindow constructor).


## [git] - 2017-12-16
- Changed recipe for game so that you subclass KivyGlops instead of
  KivyGlopsWindow (removes arbitrary border between ui and scene, and
  changes self.scene. to self. in projects which utilize KivyGlops)
- renamed create_mesh to new_glop_method for clarity, and use
  new_glop_method to create camera so conversion is not needed
  (eliminate get_kivyglop_from_pyglop)
  - rename get_pyglops_list_from_obj to get_glop_list_from_obj
  - rename get_pyglop_from_wobject to get_glop_from_wobject
- complete shift of most methods from KivyGlopsWindow to PyGlops, or at
  least KivyGlops if kivy-specific; same for lines from init; same for
  lines from update_glsl (moved to new PyGlops `update` method)


## [git] - 2017-12-11
- allow handling the obtain glop event by a new on_obtain_glop instead
  of `_deprecated_on_obtain_glop_by_name` in order to have access to the
  glop indices (you can still handle both if you desire for some
  reason, but be aware both will fire)
- moved projectile handling to `_internal_bump_glop` (formerly was
  directly after the `_internal_bump_glop` call)
- give_item_by_keyword_to_player_number and
  give_item_index_to_player_number methods for manual item transfers
  without bumping or manually calling _internal_bump_glop
- `_internal_bump_glop` now calls the new
  `_run_semicolon_separated_commands` which calls the new `_run_command`
  method, so that these new methods are available to other methods
- Began developing a platform-independent spec for the ui object so that
  PyGlops can specify more platform-independent methods (such as
  `_internal_bump_glop`) that push ui directly (ui being the
  platform-DEPENDENT object such as KivyGlopsWindow, which must inherit
  from some kind of OS Window or framework Window).
  - so far, ui must include:
    - potentially anything else in KivyGlopsWindow (KivyGlopsWindow is
      the only tested spec at this time, however see Developer Notes
      section of this file, which should be maintained well)


## [git] - 2017-11-06
- Your KivyGlopsWindow implementation can now select mesh by name:
  self.select_mesh_by_name("some_named_mesh") (or filename but shows
  warning in stdout: self.select_mesh_by_name("somefilename") or
  self.select_mesh_by_name("somefilename.obj"))


## [git] - 2016-04-29
- Switch to using only graphics that are public domain
  (change license of modified resources to CC-BY-SA 4.0)
  - Remove graphics based on cinder block wall from
    photoshoptextures.com due to a quirky custom license.


## [git] - 2016-02-12
- Change the PyGlops ObjFile and objfile.py to WObjFile and wobjfile.py
  (to avoid naming conflict with ObjFile and objfile.py in Kivy
  examples).


## [git] - 2016-02-04
- Rename `*MesherMesh` types to `*Glop` to avoid confusion with
  (Kivy's) Mesh type which is stored in `*o3d._mesh`.
- Finish separating (native) PyGlop from (Wavefront(R)) WObject for many
  reasons including: avoid storing redundant data; keep track of what
  format of data is stored in list members; allow storage of strict obj
  format; allow conversion back&forth or to other formats being sure of
  what o3d contains.


## [git] - 2016-01-10
- Created new classes to hold the data from newobj and newmtl files, in
  order to keep strict obj+mtl data, separately from native
  OpenGL-style class.


## [git] - 2015-05-12
- Include a modified testnurbs file (with added textures and improved
  geometry)
  - Remove orion.


## [git] - 2015-04-15
### Changed
- Change `Material_orion.png` to `Material_orion` in orion.obj and
  orion.mtl to avoid confusion (It is a material object name, not a
  filename).
- For clarity and less dependence on OBJ format, refactor
  `object.vertices` to `object._vertex_strings`, and refactor
  `object.mesh.vertices` to `object.vertices`.

### Fixed
- Add a line to orion.obj: `mtllib orion.mtl`


## [git] - 2015-04-13
### Fixed
- No longer crash on missing textures.
- Make the pyramid in testnurbs-textured.obj into a true solid (It had
  0-sized triangles on bottom edges that had one face)
  - Simplify it manually.
  - Make sides equilateral from side view.


## [git] - 2015-04-10
### Added
- Implement the mtl loader from "kivy-rotation3d".


## [git] - 2015-04-08
### Added
- Redo the project starting from "kivy-trackball-python3".

### Removed
- all code from before this commit


## [git] - 2015-04-06

### Changed
- Run 2to3 (originally based on nskrypnik's kivy-rotation3d), which only
  had to change objloader (changes raise to function notation, and
  `map(a,b)` to `map(list(a,b))`).

### Fixed
- Change `vertex_format` tuples from `string,int,string` to
  `bytestring,int,string` (Since strings are not bytestrings by default
  in Python 3).
