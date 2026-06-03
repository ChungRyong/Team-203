extends Node

## PieceManager.gd
## Handles the spawning and lifecycle of active game pieces.

class_name PieceManager

# References to other managers
var grid_manager: GridManager
var data_provider: TetrominoData

# Bag randomizer for fair piece distribution
var _bag: BagRandomizer

# Number of future pieces to buffer for preview displays
var peek_ahead_count := 5

# Current active piece state
var active_type: String = ""
var active_position: Vector2 = Vector2.ZERO
var active_cells: Array = [] # Global coordinates of the 4 blocks
var ghost_cells: Array = []  # Global coordinates of the projected landing point

# Hold System State
var hold_type: String = ""
var can_hold: bool = true # Prevent multiple holds in a single spawn

func _ready():
	data_provider = TetrominoData.new()
	_bag = BagRandomizer.new()

## Injected dependency for grid access
func setup(gm: GridManager):
	grid_manager = gm

## Resets hold capability to allow holding the next piece
func reset_hold_capability():
	can_hold = true

## Gets the current hold type
func get_hold_type():
	return hold_type

## Swaps the active piece with the held piece.
## - If hold is empty: hold = active_type, then spawn new piece from bag.
## - If hold has a piece: swap active <-> hold, then spawn new piece from bag.
## Returns true if the hold operation succeeded, false if can_hold was already false.
func hold_piece() -> bool:
	if not can_hold:
		return false

	if hold_type == "":
		# First hold: save active piece to hold, spawn a new piece
		hold_type = active_type
		active_type = _bag.next_piece()
		active_position = Vector2(4, 0)
		update_global_cells()
	else:
		# Subsequent hold: swap active piece into hold, restore held piece as active
		var saved_hold = hold_type
		hold_type = active_type
		active_type = saved_hold
		active_position = Vector2(4, 0)
		update_global_cells()

	# Always spawn a fresh piece from the bag after any hold operation
	active_type = _bag.next_piece()
	active_position = Vector2(4, 0)
	update_global_cells()

	# Populate the lookahead buffer for preview displays
	_bag.peek(peek_ahead_count)

	can_hold = false
	return true

## Spawns a new piece from the bag at the top center of the board.
func spawn_piece() -> bool:
	active_type = _bag.next_piece()

	# Start position: Top-center (usually x=4, y=0)
	active_position = Vector2(4, 0)

	# Calculate global cells based on relative shape data
	update_global_cells()

	# Populate the lookahead buffer for preview displays
	_bag.peek(peek_ahead_count)

	# Reset hold capability for the next piece
	reset_hold_capability()

	# Verification: Check if the spawn area is clear
	if not can_place_piece():
		return false # Game over condition

	return true

## Returns the next piece type from the bag without consuming it.
func peek_next_piece() -> String:
	var peeked = _bag.peek(1)
	if peeked.size() > 0:
		return peeked[0]
	return ""

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
			return true

	return false

## Helper to check collision for a set of candidate cells
func can_place_rotated_cells(cells: Array) -> bool:
	if grid_manager == null: return true
	for cell in cells:
		if not grid_manager.is_cell_empty(int(cell.x), int(cell.y)):
			return false
	return true
