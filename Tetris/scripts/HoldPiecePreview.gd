extends RichTextLabel

## HoldPiecePreview.gd - Shows held piece preview.
## Displays the currently held piece type as a color-coded ASCII grid.
## Shows "보류: -" when no piece has been held yet.

class_name HoldPiecePreview

var piece_manager: PieceManager


func update_preview():
	if piece_manager == null:
		text = ""
		return
	if piece_manager.data_provider == null:
		text = ""
		return
	if piece_manager.hold_type == "":
		text = "[i]보류: -[/i]"
		return
	text = _format_piece_grid(piece_manager.hold_type)


func _format_piece_grid(piece_type: String) -> String:
	var color = TetrominoData.COLORS.get(piece_type, "0xffffff")
	# Strip "0x" prefix for bbcode (bbcode uses #RRGGBB format)
	var bbcode_color = color.trim_prefix("0x")
	var shape = piece_manager.data_provider.get_shape(piece_type)
	var min_x = 10
	var max_x = -10
	var min_y = 10
	var max_y = -10

	for cell in shape:
		min_x = mini(min_x, cell.x)
		max_x = maxi(max_x, cell.x)
		min_y = mini(min_y, cell.y)
		max_y = maxi(max_y, cell.y)

	var w = max_x - min_x + 1
	var h = max_y - min_y + 1
	var occupied = {}

	for cell in shape:
		occupied[(cell.x - min_x) * 10 + (cell.y - min_y)] = true

	var result = ""
	for row in range(max_y - min_y, -1, -1):
		for col in range(w):
			if occupied.get(col * 10 + row, false):
				result += "[color=%s]##[/color]" % bbcode_color
			else:
				result += "  "
		result += "\n"

	return result
