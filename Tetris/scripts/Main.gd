extends Control

## Main.gd - Main orchestrator for Team-203 Tetris (Godot 4.6)
## Handles manager lifecycle, input processing, and game state flow.

class_name Main

# Manager instances
# Note: PieceManager creates its own BagRandomizer internally — fully self-contained.
# Main only uses PieceManager's public API.
var game_manager: GameManager
var grid_manager: GridManager
var piece_manager: PieceManager
var input_manager: InputManager
var visual_orchestrator: VisualOrchestrator
var haptic_manager: HapticManager

# Game timer reference
var game_timer: Timer

# Soft drop timing
var soft_drop_timer: Timer = null
var soft_drop_accumulator: float = 0.0
var soft_drop_delayed: bool = false
const SOFT_DROP_ACCEL_DELAY: float = 0.3
const SOFT_DROP_INITIAL_INTERVAL: float = 0.4
const SOFT_DROP_MAX_INTERVAL: float = 0.05

# UI references
var score_label: Label
var level_label: Label
var lines_label: Label
var next_piece_grid: NextPiecePreview
var hold_piece_grid: HoldPiecePreview
var game_over_overlay: CanvasLayer
var start_overlay: CanvasLayer

# Total lines cleared across game session
var total_lines_cleared: int = 0

# Current game state for input handling
var game_started: bool = false


func _ready():
	_build_ui()
	_setup_managers()
	_setup_timer()

	# Connect game_started flag to start_overlay visibility.
	# Show the start overlay before the game begins.
	start_overlay.visible = true


func _setup_managers():
	game_manager = GameManager.new()
	grid_manager = GridManager.new()
	piece_manager = PieceManager.new()
	input_manager = InputManager.new()
	haptic_manager = HapticManager.new()
	visual_orchestrator = VisualOrchestrator.new()

	add_child(game_manager)
	add_child(grid_manager)
	add_child(piece_manager)
	add_child(input_manager)
	add_child(haptic_manager)
	add_child(visual_orchestrator)

	piece_manager.setup(grid_manager)
	visual_orchestrator.grid_manager = grid_manager
	visual_orchestrator.piece_manager = piece_manager


func _setup_timer():
	game_timer = game_manager.game_timer
	game_timer.timeout.disconnect(game_manager._on_game_tick)
	game_timer.timeout.connect(_on_game_tick)


func _process(delta: float):
	if not game_started:
		_check_start_input()
		return

	_handle_input()
	_handle_soft_drop(delta)

	if game_manager.current_state == GameManager.GameState.PLAYING:
		visual_orchestrator.redraw_board()
		_update_ui_labels()


func _check_start_input():
	if Input.is_action_just_pressed("ui_accept") or Input.is_action_just_pressed("hard_drop"):
		_start_game()


func _handle_input():
	var vec = input_manager.get_movement_vector()
	if vec.x != 0:
		piece_manager.move(Vector2(vec.x, 0))

	if input_manager.is_action_just_pressed(InputManager.ACTION_ROTATE):
		piece_manager.rotate()

	if input_manager.is_action_just_pressed(InputManager.ACTION_HARD_DROP):
		while piece_manager.try_move_down():
			pass
		lock_piece()

	if input_manager.is_action_just_pressed(InputManager.ACTION_HOLD):
		piece_manager.hold_piece()

	if input_manager.is_action_just_pressed(InputManager.ACTION_PAUSE):
		_toggle_pause()


func _handle_soft_drop(delta: float):
	if not input_manager.is_action_pressed(InputManager.ACTION_MOVE_DOWN):
		soft_drop_accumulator = 0.0
		soft_drop_delayed = false
		return

	soft_drop_accumulator += delta
	var interval = SOFT_DROP_INITIAL_INTERVAL
	if soft_drop_accumulator >= SOFT_DROP_ACCEL_DELAY:
		soft_drop_delayed = true
		interval = maxf(
			SOFT_DROP_MAX_INTERVAL,
			game_manager.current_drop_interval * 0.5
		)

	if not soft_drop_delayed:
		return

	if soft_drop_timer == null:
		soft_drop_timer = Timer.new()
		soft_drop_timer.one_shot = true
		add_child(soft_drop_timer)

	if soft_drop_timer.wait_time != interval:
		soft_drop_timer.wait_time = interval
		soft_drop_timer.timeout.disconnect(_on_soft_drop_tick)
		soft_drop_timer.timeout.connect(_on_soft_drop_tick)
		soft_drop_timer.start()


func _on_soft_drop_tick():
	if game_manager.current_state != GameManager.GameState.PLAYING:
		return
	piece_manager.try_move_down()


func _toggle_pause():
	if game_manager.current_state == GameManager.GameState.PLAYING:
		game_manager.toggle_pause()
	elif game_manager.current_state == GameManager.GameState.PAUSED:
		game_manager.toggle_pause()


func lock_piece():
	for cell in piece_manager.active_cells:
		grid_manager.set_cell(
			int(cell.x), int(cell.y),
			GridManager.CellState.OCCUPIED
		)

	piece_manager.active_cells.clear()
	piece_manager.ghost_cells.clear()

	var cleared = grid_manager.check_and_clear_lines()
	total_lines_cleared += cleared

	if cleared > 0:
		game_manager.add_score(cleared, total_lines_cleared)
		haptic_manager.play_line_clear_effect(cleared)

	if not piece_manager.spawn_piece():
		_handle_game_over()


func _on_game_tick():
	if game_manager.current_state != GameManager.GameState.PLAYING:
		return
	if not piece_manager.try_move_down():
		lock_piece()


func _handle_game_over():
	game_manager.game_over()
	game_timer.stop()
	game_over_overlay.visible = true


func _start_game():
	game_started = true
	grid_manager.clear_grid()
	game_manager.score = 0
	game_manager.current_level = 1
	total_lines_cleared = 0

	piece_manager.spawn_piece()

	# Standard Tetris: hold is disabled on the first piece of a game.
	# Only after the first piece is placed can the player use hold.
	if piece_manager.hold_type == "":
		piece_manager.can_hold = false

	game_manager.current_state = GameManager.GameState.PLAYING
	game_manager.current_drop_interval = game_manager.base_drop_interval
	game_manager.game_timer.wait_time = game_manager.current_drop_interval
	game_manager.game_timer.start()

	_hide_all_overlays()
	_update_ui_labels()


func restart_game():
	_start_game()


func _hide_all_overlays():
	game_over_overlay.visible = false
	start_overlay.visible = false


func _build_ui():
	score_label = get_node("UI/ScoreLabel")
	level_label = get_node("UI/LevelLabel")
	lines_label = get_node("UI/LinesLabel")
	next_piece_grid = get_node("UI/NextPieceGrid") as NextPiecePreview
	hold_piece_grid = get_node("UI/HoldPieceGrid") as HoldPiecePreview
	game_over_overlay = get_node("UI/GameOverOverlay")
	start_overlay = get_node("UI/StartOverlay")

	score_label.text = "점수: 0"
	level_label.text = "레벨: 1"
	lines_label.text = "라인: 0"
	next_piece_grid.text = ""
	hold_piece_grid.text = ""

	if next_piece_grid != null:
		next_piece_grid.piece_manager = piece_manager
	if hold_piece_grid != null:
		hold_piece_grid.piece_manager = piece_manager

	var retry_btn = get_node("UI/GameOverOverlay/Panel/VBox/RetryButton")
	retry_btn.pressed.connect(restart_game)

	game_manager.game_over_signal.connect(_handle_game_over)


func _update_ui_labels():
	score_label.text = "점수: " + str(game_manager.score)
	level_label.text = "레벨: " + str(game_manager.current_level)
	lines_label.text = "라인: " + str(total_lines_cleared)

	if next_piece_grid != null:
		next_piece_grid.update_preview()
	if hold_piece_grid != null:
		hold_piece_grid.update_preview()
