extends Node

## TetrominoData.gd
## Definitive data for the 7 standard Tetromino shapes and SRS Wall Kicks.

class_name TetrominoData

# Color definitions
const COLORS = {
	"I": "0x00f0f0", # Cyan
	"O": "0xffff00", # Yellow
	"T": "0x800080", # Purple
	"S": "0x00ff00", # Green
	"Z": "0xff0000", # Red
	"J": "0x0000ff", # Blue
	"L": "ffa500",   # Orange
}

# Shape definitions (Relative coordinates from pivot center)
const SHAPE_I = [Vector2(0, -1), Vector2(0, 0), Vector2(0, 1), Vector2(0, 2)]
const SHAPE_O = [Vector2(0, 0), Vector2(1, 0), Vector2(0, 1), Vector2(1, 1)]
const SHAPE_T = [Vector2(-1, 0), Vector2(0, 0), Vector2(1, 0), Vector2(0, 1)]
const SHAPE_S = [Vector2(0, 0), Vector2(1, 0), Vector2(-1, 1), Vector2(0, 1)]
const SHAPE_Z = [Vector2(-1, 0), Vector2(0, 0), Vector2(0, 1), Vector2(1, 1)]
const SHAPE_J = [Vector2(-1, 0), Vector2(0, 0), Vector2(1, 0), Vector2(-1, 1)]
const SHAPE_L = [Vector2(-1, 0), Vector2(0, 0), Vector2(1, 0), Vector2(1, 1)]

## SRS Wall Kick Data (Simplified Standard)
# Order of attempts to resolve collision during rotation.
const WALL_KICKS = {
	"I": [Vector2(0, 0), Vector2(-1, 0), Vector2(1, 0), Vector2(0, -1)],
	"J": [Vector2(0, 0), Vector2(-1, 0), Vector2(1, 0), Vector2(0, -1)],
	"L": [Vector2(0, 0), Vector2(-1, 0), Vector2(1, 0), Vector2(0, -1)],
	"O": [Vector2(0, 0)], # O doesn't rotate/kick
	"S": [Vector2(0, 0), Vector2(-1, 0), Vector2(1, 0), Vector2(0, -1)],
	"T": [Vector2(0, 0), Vector2(-1, 0), Vector2(1, 0), Vector2(0, -1)],
	"Z": [Vector2(0, 0), Vector2(-1, 0), Vector2(1, 0), Vector2(0, -1)],
}

func get_shape(type: String) -> Array:
	match type:
		"I": return SHAPE_I
		"O": return SHAPE_O
		"T": return SHAPE_T
		"S": return SHAPE_S
		"Z": return SHAPE_Z
		"J": return SHAPE_J
		"L": return SHAPE_L
	return []

func get_wall_kicks(type: String) -> Array:
	if WALL_KICKS.has(type):
		return WALL_KICKS[type]
	return [Vector2(0, 0)]

func get_all_types() -> Array:
	return ["I", "O", "T", "S", "Z", "J", "L"]
