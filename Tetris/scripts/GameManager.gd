extends Node

## GameManager.gd - Game state, timing, and scoring for Team-203 Tetris.

class_name GameManager

signal game_over_signal(final_score: int)

enum GameState { START, PLAYING, PAUSED, GAME_OVER }

var current_state = GameState.START
var current_level = 1
var score = 0

var base_drop_interval = 1.0
var drop_interval_multiplier = 0.8
var current_drop_interval = 1.0

var game_timer: Timer

func _ready():
	setup_timer()


func setup_timer():
	game_timer = Timer.new()
	game_timer.wait_time = current_drop_interval
	game_timer.one_shot = false
	add_child(game_timer)


func _on_game_tick():
	if current_state != GameState.PLAYING:
		return


func update_level(new_level: int):
	current_level = new_level
	current_drop_interval = base_drop_interval * pow(
		drop_interval_multiplier, current_level - 1
	)
	game_timer.wait_time = current_drop_interval


func add_score(lines: int, total_lines: int):
	var points = 0
	match lines:
		1: points = 100
		2: points = 300
		3: points = 600
		4: points = 1200
		_: points = 0

	score += points * current_level

	var new_level = (total_lines // 10) + 1
	if new_level > current_level:
		update_level(new_level)


func toggle_pause():
	if current_state == GameState.PLAYING:
		current_state = GameState.PAUSED
		game_timer.stop()
	elif current_state == GameState.PAUSED:
		current_state = GameState.PLAYING
		game_timer.start()


func game_over():
	current_state = GameState.GAME_OVER
	game_timer.stop()
