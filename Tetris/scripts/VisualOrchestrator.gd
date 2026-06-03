extends Node3D

## VisualOrchestrator.gd - 3D rendering for Team-203 Tetris.
## Renders grid blocks, active piece, and ghost piece.
## Uses visibility toggle for ghost meshes (not create/destroy every frame).

class_name VisualOrchestrator

var grid_manager: GridManager
var piece_manager: PieceManager

var static_meshes = {}
var active_piece_meshes = []
var ghost_node: Ghost = null

# Pre-allocated ghost mesh cache: key = "x,y", value = MeshInstance3D
var ghost_meshes = {}


func _ready():
	_setup_3d_scene()
	ghost_node = get_node("Ghost")


func _setup_3d_scene():
	var camera = Camera3D.new()
	camera.position = Vector3(5, 10, 16)
	camera.rotation_degrees = Vector3(-35, 0, 0)
	add_child(camera)

	var light = DirectionalLight3D.new()
	light.position = Vector3(5, 15, 10)
	light.rotation_degrees = Vector3(-45, 45, 0)
	add_child(light)

	var ambient = WorldEnvironment.new()
	var env = Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.08, 0.08, 0.1)
	ambient.environment = env
	add_child(ambient)


func redraw_board():
	_redraw_static_grid()
	_redraw_active_piece()
	_draw_ghost()


func _redraw_static_grid():
	for y in range(GridManager.HEIGHT):
		for x in range(GridManager.WIDTH):
			var key = str(x) + "," + str(y)
			var occupied = not grid_manager.is_cell_empty(x, y)

			if occupied:
				if not static_meshes.has(key):
					_create_static_block(x, y, key)
			else:
				if static_meshes.has(key):
					static_meshes[key].queue_free()
					static_meshes.erase(key)


func _create_static_block(x, y, key):
	var mi = MeshInstance3D.new()
	mi.mesh = BoxMesh.new()
	mi.mesh.size = Vector3(0.9, 0.9, 0.9)
	mi.position = Vector3(float(x), float(-y), 0.0)

	var mat = StandardMaterial3D.new()
	mat.albedo_color = Color(0.45, 0.45, 0.5)
	mat.metallic = 0.3
	mat.roughness = 0.6
	mi.material_override = mat

	add_child(mi)
	static_meshes[key] = mi


func _redraw_active_piece():
	for m in active_piece_meshes:
		m.queue_free()
	active_piece_meshes.clear()

	var color = _get_piece_color()

	for cell in piece_manager.active_cells:
		var mi = _make_block_mesh(cell.x, cell.y, color)
		add_child(mi)
		active_piece_meshes.append(mi)


func _draw_ghost():
	if ghost_node == null:
		return
	if piece_manager == null or piece_manager.ghost_cells.is_empty():
		for mi in ghost_meshes.values():
			mi.visible = false
		return

	ghost_node.piece_manager = piece_manager
	ghost_node.grid_manager = grid_manager

	var color = _get_piece_color()

	for cell in piece_manager.ghost_cells:
		var key = str(int(cell.x)) + "," + str(int(cell.y))
		if not ghost_meshes.has(key):
			var mi = _make_ghost_mesh(int(cell.x), int(cell.y), color)
			add_child(mi)
			ghost_meshes[key] = mi
		ghost_meshes[key].visible = true

	# Hide any ghost meshes not in current ghost cells
	for key in ghost_meshes:
		var in_current = false
		for cell in piece_manager.ghost_cells:
			if str(int(cell.x)) + "," + str(int(cell.y)) == key:
				in_current = true
				break
		if not in_current:
			ghost_meshes[key].visible = false


func _make_ghost_mesh(x, y, color: Color) -> MeshInstance3D:
	var mi = MeshInstance3D.new()
	mi.mesh = BoxMesh.new()
	mi.mesh.size = Vector3(0.85, 0.85, 0.85)
	mi.position = Vector3(float(x), float(-y), 0.0)

	var mat = StandardMaterial3D.new()
	mat.albedo_color = color
	mat.albedo_color.a = 0.25
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.metallic = 0.0
	mat.roughness = 1.0
	mi.material_override = mat

	return mi


func _get_piece_color() -> Color:
	var hex_str = str(
		TetrominoData.COLORS.get(piece_manager.active_type, "0xffffff")
	)
	return _parse_color(hex_str)


func _parse_color(hex_str: String) -> Color:
	var s = hex_str.lstrip("0x").lstrip("0X")
	if s.length() == 6:
		var c: int = _hex_to_int(s)
		var r: float = float((c >> 16) & 0xFF) / 255.0
		var g: float = float((c >> 8) & 0xFF) / 255.0
		var b: float = float(c & 0xFF) / 255.0
		return Color(r, g, b)
	return Color.WHITE


func _hex_to_int(hex: String) -> int:
	var hex_map := {"0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "a": 10, "b": 11, "c": 12, "d": 13, "e": 14, "f": 15, "A": 10, "B": 11, "C": 12, "D": 13, "E": 14, "F": 15}
	var result := 0
	for ch in hex:
		result = result * 16 + hex_map[ch]
	return result


func _make_block_mesh(x, y, color: Color) -> MeshInstance3D:
	var mi = MeshInstance3D.new()
	mi.mesh = BoxMesh.new()
	mi.mesh.size = Vector3(0.9, 0.9, 0.9)
	mi.position = Vector3(float(x), float(-y), 0.0)

	var mat = StandardMaterial3D.new()
	mat.albedo_color = color
	mat.metallic = 0.2
	mat.roughness = 0.4
	mi.material_override = mat

	return mi


func draw_next_piece(label: Label):
	if piece_manager == null or piece_manager.data_provider == null:
		return
	var next_type = _get_next_piece_type()
	label.text = _format_piece_grid(next_type)


func draw_hold_piece(label: Label):
	if piece_manager == null or piece_manager.data_provider == null:
		return
	if piece_manager.hold_type == "":
		label.text = ""
		return
	label.text = _format_piece_grid(piece_manager.hold_type)


func _get_next_piece_type() -> String:
	var data = piece_manager.data_provider
	var types = data.get_all_types()
	return types[randi() % types.size()]


func _format_piece_grid(piece_type: String) -> String:
	var shape = piece_manager.data_provider.get_shape(piece_type)
	var min_x = 10
	var max_x = -10
	var min_y = 10
	var max_y = -10

	for cell in shape:
		min_x = mini(min_x, cell.x)
		max_x = maxi(max_x, cell.x)
		min_y = mini(min_y, cell.y)
		max_y = maxi(max_y, cell.y)

	var w = max_x - min_x + 1
	var h = max_y - min_y + 1
	var occupied = {}

	for cell in shape:
		occupied[(cell.x - min_x) * 10 + (cell.y - min_y)] = true

	var result = ""
	for row in range(max_y - min_y, -1, -1):
		for col in range(w):
			if occupied.get(col * 10 + row, false):
				result += "# "
			else:
				result += "  "
		result += "\n"

	return result
