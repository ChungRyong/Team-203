extends Node

## GridManager.gd
## Manages the logical 10x20 game board for Tetris.

class_name GridManager

# Board Dimensions (Standard Tetris)
const WIDTH = 10
const HEIGHT = 20

# Cell States
enum CellState { EMPTY, OCCUPIED }

# The actual grid data: A 2D Array [HEIGHT][WIDTH]
var grid = []

func _ready():
	setup_grid()

## Initialize the grid with EMPTY cells
func setup_grid():
	grid = []
	for y in range(HEIGHT):
		var row = []
		for x in range(WIDTH):
			row.append(CellState.EMPTY)
		grid.append(row)

## Check if a cell is within boundaries and empty
func is_cell_empty(x: int, y: int) -> bool:
	# Boundary check first (Prevent index out of bounds)
	if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
		return false # Out of bounds is considered 'not empty' (blocking)

	return grid[y][x] == CellState.EMPTY

## Set a cell to OCCUPIED or EMPTY
func set_cell(x: int, y: int, state: CellState):
	if x >= 0 and x < WIDTH and y >= 0 and y < HEIGHT:
		grid[y][x] = state
	else:
		push_error("[GridManager] Attempted to set cell out of bounds: ", x, ",", y)

## Clear the entire board
func clear_grid():
	setup_grid()

## Check for full lines and remove them
## Returns the number of lines cleared
func check_and_clear_lines() -> int:
	var lines_cleared = 0
	var rows_to_remove = []

	# 1. Identify all full lines (from bottom up)
	for y in range(HEIGHT - 1, -1, -1):
		var is_full = true
		for x in range(WIDTH):
			if grid[y][x] == CellState.EMPTY:
				is_full = false
				break
		if is_full:
			rows_to_remove.append(y)

	lines_cleared = rows_to_remove.size()

	# 2. Remove lines and shift everything above down
	for row_index in rows_to_remove:
		# Shift all rows above this one down by 1
		for y in range(row_index, 0, -1):
			grid[y] = grid[y-1].duplicate()
		# Top row becomes empty
		grid[0] = []
		for x in range(WIDTH):
			grid[0].append(CellState.EMPTY)

	return lines_cleared
