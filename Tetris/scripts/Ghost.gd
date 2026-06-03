extends Node

## Ghost.gd - Ghost piece rendering helper.
## Manages ghost cell detection and delegates mesh creation
## to VisualOrchestrator (which handles the actual rendering).
##
## Called from VisualOrchestrator._draw_ghost() to determine
## ghost cell positions, which are then cached as meshes.

class_name Ghost

var piece_manager: PieceManager
var grid_manager: GridManager


func get_ghost_cells() -> Array:
	if piece_manager == null or piece_manager.ghost_cells.is_empty():
		return []
	return piece_manager.ghost_cells


func has_ghost() -> bool:
	return piece_manager != null and not piece_manager.ghost_cells.is_empty()


func get_ghost_color() -> Color:
	if piece_manager == null or piece_manager.active_type == "":
		return Color.WHITE
	var hex_str = str(
		TetrominoData.COLORS.get(piece_manager.active_type, "0xffffff")
	)
	return _parse_color(hex_str)


func _parse_color(hex_str: String) -> Color:
	var s = hex_str.lstrip("0x").lstrip("0X")
	if s.length() == 6:
		var c: int = _hex_to_int(s)
		var r: float = float((c >> 16) & 0xFF) / 255.0
		var g: float = float((c >> 8) & 0xFF) / 255.0
		var b: float = float(c & 0xFF) / 255.0
		return Color(r, g, b)
	return Color.WHITE


func _hex_to_int(hex: String) -> int:
	var hex_map := {"0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "a": 10, "b": 11, "c": 12, "d": 13, "e": 14, "f": 15, "A": 10, "B": 11, "C": 12, "D": 13, "E": 14, "F": 15}
	var result := 0
	for ch in hex:
		result = result * 16 + hex_map[ch]
	return result
