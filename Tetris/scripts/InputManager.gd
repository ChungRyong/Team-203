extends Node

## InputManager.gd
## Handles input abstraction for both Keyboard and DualSense Gamepads.

class_name InputManager

# Action constants to avoid typos in game logic
const ACTION_MOVE_LEFT = "move_left"
const ACTION_MOVE_RIGHT = "move_right"
const ACTION_MOVE_DOWN = "move_down"
const ACTION_ROTATE = "rotate"
const ACTION_HARD_DROP = "hard_drop"
const ACTION_HOLD = "hold"
const ACTION_PAUSE = "pause"

func _ready():
	print("[InputManager] Initialized. Mapping active for Keyboard and DualSense.")

## Returns true if the specific action is pressed (instant trigger)
func is_action_just_pressed(action: String) -> bool:
	return Input.is_action_just_pressed(action)

## Returns true if the action is being held down (continuous)
func is_action_pressed(action: String) -> bool:
	return Input.is_action_pressed(action)

## Specifically for holding moves to avoid "stuttering" in Tetris
func get_movement_vector() -> Vector2:
	var move_x = Input.get_axis(ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT)
	var move_y = 1 if Input.is_action_pressed(ACTION_MOVE_DOWN) else 0
	return Vector2(move_x, move_y)

## Log all inputs for debugging (TDD Verification)
func _input(event: InputEvent):
	if event is InputEventKey or event is InputEventJoypadButton or event is InputEventJoypadMotion:
		if event.is_action_pressed(ACTION_ROTATE):
			print("[Input] Action: ROTATE triggered")
		if event.is_action_pressed(ACTION_HARD_DROP):
			print("[Input] Action: HARD_DROP triggered")
		if event.is_action_pressed(ACTION_HOLD):
			print("[Input] Action: HOLD triggered")
