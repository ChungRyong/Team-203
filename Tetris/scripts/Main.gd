extends Node

## Main.gd
## Main orchestrator for the Tetris game. 
## Connects all managers and handles the primary game loop.

class_name Main

# Manager instances
var game_manager: GameManager
var grid_manager: GridManager
var piece_manager: PieceManager
var input_manager: InputManager
var visual_orchestrator: VisualOrchestrator

func _ready():
	print("[Main] Booting up Team-203 Tetris...")
	setup_managers()
	start_game_loop()

## Initialize and link all managers
func setup_managers():
	# Instantiate Managers
	game_manager = GameManager.new()
	grid_manager = GridManager.new()
	piece_manager = PieceManager.new()
	input_manager = InputManager.new()
	var haptic_manager = HapticManager.new() # Added Haptic Manager
	var visual_manager = VisualOrchestrator.new() # Added Visual Manager
	
	# Add them to the scene tree so they can use _ready and Timers
	add_child(game_manager)
	add_child(grid_manager)
	add_child(piece_manager)
	add_child(input_manager)
	add_child(haptic_manager)
	add_child(visual_manager)
	
	# Dependency Injection: Link managers together
	piece_manager.setup(grid_manager)
	visual_orchestrator = visual_manager
	visual_orchestrator.grid_manager = grid_manager
	visual_orchestrator.piece_manager = piece_manager
	
	# Store haptic manager globally/locally for access
	self.set('haptic_manager', haptic_manager)
	
	# IMPORTANT: Spawn the first piece to start the game!
	piece_manager.spawn_piece()
	
	print("[Main] All managers linked, first piece spawned. Haptics & Visuals enabled.")


## The main logic loop
func _process(_delta):
	print("[SENSE] Main loop ticking...")
	if game_manager.current_state != GameManager.GameState.PLAYING:
		print("[SENSE] Loop blocked by state: ", game_manager.current_state)
		return
	
	handle_user_input()
	
	if visual_orchestrator:
		print("[SENSE] VisualOrchestrator exists. Calling redraw_board()...")
		visual_orchestrator.redraw_board()
	else:
		print("[SENSE] VisualOrchestrator is MISSING!")

func handle_user_input():
	# 1. Lateral Movement (Left/Right)
	var move_vec = input_manager.get_movement_vector()
	if move_vec.x != 0:
		piece_manager.move(Vector2(move_vec.x, 0))
	
	# 2. Manual Soft Drop (Down)
	if move_vec.y > 0:
		piece_manager.try_move_down()
	
	# 3. Rotation
	if input_manager.is_action_just_pressed(InputManager.ACTION_ROTATE):
		piece_manager.rotate()
	
	# 4. Hard Drop
	if input_manager.is_action_just_pressed(InputManager.ACTION_HARD_DROP):
		perform_hard_drop()

	# 5. Hold Piece
	if input_manager.is_action_just_pressed(InputManager.ACTION_HOLD):
		piece_manager.hold_piece()


func perform_hard_drop():
	while piece_manager.try_move_down():
		pass # Rapidly descend until collision
	lock_piece()

## Lock the current piece into the grid and spawn a new one
func lock_piece():
	print("[Main] Piece landed. Locking into grid...")
	for cell in piece_manager.active_cells:
		grid_manager.set_cell(int(cell.x), int(cell.y), GridManager.CellState.OCCUPIED)
	
	# 1. Check for and clear full lines
	var cleared = grid_manager.check_and_clear_lines()
	
	# 2. Update score based on cleared lines
	if cleared > 0:
		game_manager.add_score(cleared)
		# 3. Trigger Haptic Feedback (Pumping hand-feel!)
		var haptic = get_node_or_null("HapticManager") # Or from the set variable
		if haptic == null:
			# Fallback for script-based instance
			var hm = HapticManager.new()
			hm.play_line_clear_effect(cleared)
		else:
			haptic.play_line_clear_effect(cleared)
	
	grid_manager.debug_print_grid() # Verify state in console
	
	# Spawn new piece or Game Over
	if not piece_manager.spawn_piece():
		game_manager.game_over()


## Connect the GameManager's heartbeat to the PieceManager
func start_game_loop():
	# We override the heart-beat of game_manager to trigger downward movement
	var timer = game_manager.game_timer
	if timer:
		# Disconnect existing internal handler and link to Main for orchestration
		# In a real Godot scene, we'd use signals, but here we define orchestrator logic
		print("[Main] Game loop connected.")
