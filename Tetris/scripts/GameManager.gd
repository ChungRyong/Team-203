extends Node

## GameManager.gd
## Central orchestrator for game state and timing (The Heartbeat of Tetris).

class_name GameManager

# Game State Constants
enum GameState { START, PLAYING, PAUSED, GAME_OVER }

# Configuration
var current_state = GameState.START
var current_level = 1
var score = 0

# Gravity Settings (Speed increases as level goes up)
var base_drop_interval = 1.0  # Seconds between drops at Level 1
var drop_interval_multiplier = 0.8 # Speed increase rate per level
var current_drop_interval = 1.0

# Timer reference
var game_timer: Timer

func _ready():
	print("[GameManager] Initialized. Setting up game heartbeat...")
	setup_timer()
	start_game()

## Initialize the gravity timer
func setup_timer():
	game_timer = Timer.new()
	game_timer.wait_time = current_drop_interval
	game_timer.one_shot = false
	game_timer.timeout.connect(_on_game_tick)
	add_child(game_timer)

## Transition to playing state
func start_game():
	current_state = GameState.PLAYING
	game_timer.start()
	print("[GameManager] Game Started. Tick rate: ", current_drop_interval, "s")

## The 'Heartbeat' - triggered every tick
func _on_game_tick():
	if current_state != GameState.PLAYING:
		return
	
	print("[Tick] Gravity drop trigger!")
	# This is where the ActivePiece will be told to move down one cell
	# Example: if active_piece: active_piece.move_down()

## Update gravity based on level
func update_level(new_level: int):
	current_level = new_level
	current_drop_interval = base_drop_interval * pow(drop_interval_multiplier, current_level - 1)
	game_timer.wait_time = current_drop_interval
	print("[GameManager] Level Up! New Speed: ", current_drop_interval, "s")

## Add score based on lines cleared
func add_score(lines: int):
	var points = 0
	match lines:
		1: points = 100 # Single
		2: points = 300 # Double
		3: points = 600 # Triple
		4: points = 1200 # Tetris!
		_: points = 0
	
	score += points
	print("[GameManager] Scored: +", points, " | Total Score: ", score)
	
	# Level up every 10 lines (simplified logic)
	# In a real game, we'd track total lines cleared across the whole session


## State management
func toggle_pause():
	if current_state == GameState.PLAYING:
		current_state = GameState.PAUSED
		game_timer.stop()
		print("[GameManager] Game Paused.")
	elif current_state == GameState.PAUSED:
		current_state = GameState.PLAYING
		game_timer.start()
		print("[GameManager] Game Resumed.")

func game_over():
	current_state = GameState.GAME_OVER
	game_timer.stop()
	print("[GameManager] GAME OVER! Final Score: ", score)
