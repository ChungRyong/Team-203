extends Node

## PieceManager.gd
## Handles the spawning and lifecycle of active game pieces.

class_name PieceManager

# References to other managers
var grid_manager: GridManager
var data_provider: TetrominoData

# Current active piece state
var active_type: String = ""
var active_position: Vector2 = Vector2.ZERO
var active_cells: Array = [] # Global coordinates of the 4 blocks
var ghost_cells: Array = []  # Global coordinates of the projected landing point

# Hold System State
var hold_type: String = ""
var can_hold: bool = true # Prevent multiple holds in a single spawn

func _ready():
	print("[PieceManager] Initialized.")
	data_provider = TetrominoData.new()



## Injected dependency for grid access
func setup(gm: GridManager):
	grid_manager = gm

## Resets hold capability to allow holding the next piece
func reset_hold_capability():
	can_hold = true

## Gets the current hold type
func get_hold_type():
	return hold_type

## Spawns a new random piece at the top center of the board
func spawn_piece() -> bool:
	var types = data_provider.get_all_types()
	active_type = types[randi() % types.size()]
	
	# Start position: Top-center (usually x=3,4 / y=0)
	active_position = Vector2(4, 0)
	
	# Calculate global cells based on relative shape data
	var shape = data_provider.get_shape(active_type)
	update_global_cells()
	
	print("[PieceManager] Spawned new piece: ", active_type, " at ", active_position)
	
	# Reset hold capability for the next piece
	reset_hold_capability()
	
	# Verification: Check if the spawn area is clear
	if not can_place_piece():
		print("[PieceManager] Collision detected on spawn! GAME OVER condition.")
		return false # This will trigger game over
		
	return true

## Recalculates global coordinates based on current pivot position
func update_global_cells():
	active_cells = []
	var shape = data_provider.get_shape(active_type)
	for offset in shape:
		active_cells.append(active_position + offset)
	
	# Whenever the active piece moves, we must update the ghost position
	update_ghost_position()

## Calculates where the piece would land if it dropped immediately
func update_ghost_position():
	var ghost_pos = active_position
	
	# Simulate falling down until collision
	while true:
		var next_pos = ghost_pos + Vector2(0, 1)
		if can_place_at_position(next_pos):
			ghost_pos = next_pos
		else:
			break
	
	# Now generate the actual cells for the ghost piece based on final ghost_pos
	ghost_cells = []
	var shape = data_provider.get_shape(active_type)
	for offset in shape:
		ghost_cells.append(ghost_pos + offset)

## Helper to check collision at a specific pivot position (used by Ghost & Movement)
func can_place_at_position(pos: Vector2) -> bool:
	if grid_manager == null: return true
	var shape = data_provider.get_shape(active_type)
	for offset in shape:
		var cell = pos + offset
		if not grid_manager.is_cell_empty(int(cell.x), int(cell.y)):
			return false
	return true

## Check if the piece can exist at its current position without collisions
func can_place_piece() -> bool:
	return can_place_at_position(active_position)


## Move the piece logically (relative movement)
func move(delta: Vector2) -> bool:
	var old_pos = active_position
	active_position += delta
	update_global_cells()
	
	if can_place_piece():
		return true # Movement successful
	else:
		active_position = old_pos # Revert on collision
		update_global_cells()
		return false

## Special handling for vertical drop to detect landing
func try_move_down() -> bool:
	if move(Vector2(0, 1)):
		return true # Successfully moved down
	else:
		# If we can't move down, the piece has 'landed'
		return false # Signal for locking the piece into grid


## Rotate the piece using SRS (Super Rotation System)
func rotate() -> bool:
	if active_type == "O": return true # O-piece doesn't need rotation logic
	
	# 1. Calculate new cells by rotating coordinates around pivot (0,0)
	# Formula for 90deg clockwise: (x, y) -> (-y, x)
	var current_shape = data_provider.get_shape(active_type)
	var rotated_cells = []
	for cell in active_cells:
		# Localize relative to pivot first
		var local_pos = cell - active_position
		var rotated_local = Vector2(-local_pos.y, local_pos.x) 
		rotated_cells.append(active_position + rotated_local)

	# 2. Try Wall Kicks to resolve collisions
	var kicks = data_provider.get_wall_kicks(active_type)
	for kick in kicks:
		var test_cells = []
		for rc in rotated_cells:
			test_cells.append(rc + kick)
		
		if can_place_rotated_cells(test_cells):
			# SUCCESS! Apply rotation and the kick offset
			active_cells = test_cells
			active_position += kick # Shift pivot too
			print("[PieceManager] Rotation successful with kick: ", kick)
			return true
	
	print("[PieceManager] Rotation failed - blocked by wall/piece.")
	return false

## Helper to check collision for a set of candidate cells
func can_place_rotated_cells(cells: Array) -> bool:
	if grid_manager == null: return true
	for cell in cells:
		if not grid_manager.is_cell_empty(int(cell.x), int(cell.y)):
			return false
	return true

