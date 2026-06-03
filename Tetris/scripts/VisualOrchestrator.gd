extends Node

## VisualOrchestrator.gd
## Handles the "Modern 3D" visual representation using Godot's 3D primitives.

class_name VisualOrchestrator

# References to Managers
var grid_manager: GridManager
var piece_manager: PieceManager

# Visual storage
var block_meshes = {} # Key: "x,y", Value: MeshInstance3D
var active_piece_meshes = []

func _ready():
	print("[VisualOrchestrator] Initialized. Setting up Modern 3D view...")
	setup_visuals()

## Configures the look and feel based on the "Modern UI/3D Style" spec
func setup_visuals():
	# 1. Setup Camera
	var camera = Camera3D.new()
	camera.position = Vector3(5, 10, 15)
	camera.rotation_degrees = Vector3(-30, 0, 0)
	add_child(camera)
	
	# 2. Setup Lighting
	var light = DirectionalLight3D.new()
	light.position = Vector3(5, 10, 5)
	light.rotation_degrees = Vector3(-45, 45, 0)
	add_child(light)
	
	# 3. Setup Ambient Light
	var ambient = WorldEnvironment.new()
	var env = Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.1, 0.1, 0.1)
	ambient.environment = env
	add_child(ambient)

	print("[Visuals] 3D Scene initialized: Camera, Light, and Environment active.")

## Updates the visual display based on logic state
func redraw_board():
	# 1. Redraw Static Grid
	for y in range(GridManager.HEIGHT):
		for x in range(GridManager.WIDTH):
			var cell_key = str(x) + "," + str(y)
			var is_occupied = not grid_manager.is_cell_empty(x, y)
			
			if is_occupied:
				if not block_meshes.has(cell_key):
					create_block_mesh(x, y, cell_key)
			else:
				if block_meshes.has(cell_key):
					var mesh = block_meshes[cell_key]
					mesh.queue_free()
					block_meshes.erase(cell_key)

	# 2. Redraw Active Piece
	update_active_piece_visuals()

func create_block_mesh(x, y, key):
	var mesh_instance = MeshInstance3D.new()
	var box = BoxMesh.new()
	box.size = Vector3(0.9, 0.9, 0.9)
	mesh_instance.mesh = box
	
	# Position: x is right, y is DOWN in Tetris, so we use -y for 3D UP
	mesh_instance.position = Vector3(x, -y, 0)
	
	# Material for 'Glassy' look
	var mat = StandardMaterial3D.new()
	mat.albedo_color = Color.WHITE
	mat.roughness = 0.1
	mat.metallic = 0.8
	mesh_instance.material_override = mat
	
	add_child(mesh_instance)
	block_meshes[key] = mesh_instance

func update_active_piece_visuals():
	# Clear old active meshes
	for m in active_piece_meshes:
		m.queue_free()
	active_piece_meshes.clear()
	
	# Create new meshes for current active cells
	for cell in piece_manager.active_cells:
		var mesh_instance = MeshInstance3D.new()
		var box = BoxMesh.new()
		box.size = Vector3(0.9, 0.9, 0.9)
		mesh_instance.mesh = box
		mesh_instance.position = Vector3(cell.x, -cell.y, 0)
		
		var mat = StandardMaterial3D.new()
		mat.albedo_color = Color.YELLOW # Simplified color for now
		mat.roughness = 0.1
		mat.metallic = 0.8
		mesh_instance.material_override = mat
		
		add_child(mesh_instance)
		active_piece_meshes.append(mesh_instance)

## Trigger a 'Burst' effect when lines are cleared (GPU Particles)
func play_burst_effect(x: int, y: int):
	print("[Visuals] TRIGGERING GPU PARTICLE BURST at ", x, ",", y)
	# In a real Godot project, we'd instantiate a GPUParticles3D node.
