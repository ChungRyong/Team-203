extends RichTextLabel
## NextPiecePreview.gd - Shows the next upcoming piece in an ASCII grid.
## Uses peek_next_piece() from PieceManager to preview the upcoming shape.
## Color-codes each block using TetrominoData.COLORS.

class_name NextPiecePreview

var piece_manager: PieceManager


func update_preview() -> void:
	if piece_manager == null:
		text = ""
		return

	var next_type: String = piece_manager.peek_next_piece()

	if next_type == "":
		text = "[color=#aaaaaa]다음: ?[/color]"
		return

	var grid: String = _format_piece_grid(next_type)
	text = "[color=#aaaaaa]다음:[/color]\n" + grid


func _format_piece_grid(piece_type: String) -> String:
	var shape: Array = piece_manager.data_provider.get_shape(piece_type)
	if shape.is_empty():
		return ""

	var color_hex: String = TetrominoData.COLORS.get(piece_type, "")
	var block_color: String = "[color=#%s]##[/color]" % color_hex
	var space_color: String = "[color=#1a1a2e]  [/color]"

	var min_x: int = 10
	var max_x: int = -10
	var min_y: int = 10
	var max_y: int = -10

	for cell in shape:
		min_x = mini(min_x, cell.x)
		max_x = maxi(max_x, cell.x)
		min_y = mini(min_y, cell.y)
		max_y = maxi(max_y, cell.y)

	var w: int = max_x - min_x + 1
	var h: int = max_y - min_y + 1
	var occupied: Dictionary = {}

	for cell in shape:
		occupied[(cell.x - min_x) * 10 + (cell.y - min_y)] = true

	var result: String = ""
	for row in range(max_y - min_y, -1, -1):
		for col in range(w):
			if occupied.get(col * 10 + row, false):
				result += block_color
			else:
				result += space_color
		result += "\n"

	return result
