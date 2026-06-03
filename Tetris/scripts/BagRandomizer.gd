class_name BagRandomizer

enum { PIECE_I, PIECE_O, PIECE_T, PIECE_S, PIECE_Z, PIECE_J, PIECE_L }

const PIECE_TYPES := ["I", "O", "T", "S", "Z", "J", "L"]
const BAG_SIZE := 7

var _bag: PackedStringArray = PackedStringArray()
var _bag_index: int = 0
var _peek_buffer: PackedStringArray = PackedStringArray()
var _peek_index: int = 0

func _init() -> void:
	refresh_bag()


func shuffle(arr: PackedStringArray) -> PackedStringArray:
	var result := PackedStringArray(arr)
	for i in range(result.size() - 1, 0, -1):
		var j := randi() % (i + 1)
		var temp := result[i]
		result[i] = result[j]
		result[j] = temp
	return result


func refresh_bag() -> void:
	var full_bag := PackedStringArray(PIECE_TYPES)
	_bag = shuffle(full_bag)
	_bag_index = 0


func next_piece() -> String:
	if _peek_buffer.size() > 0:
		var val := _peek_buffer[_peek_index]
		_peek_index += 1
		return val

	if _bag_index >= _bag.size():
		refresh_bag()

	var piece: String = _bag[_bag_index]
	_bag_index += 1
	return piece


func peek(count: int) -> PackedStringArray:
	var result := PackedStringArray()
	var effective_count := count
	if effective_count < 0:
		effective_count = 0

	# Build peek buffer lazily so repeated peeks see the same data.
	var buffer_end := _peek_index + effective_count
	while buffer_end > _peek_buffer.size():
		if _peek_index >= _bag.size():
			_refresh_peek_buffer()
		_peek_buffer.append(_bag[_bag_index])
		_bag_index += 1

	for i in range(effective_count):
		result.append(_peek_buffer[_peek_index + i])

	return result


func _refresh_peek_buffer() -> void:
	# Drain remaining peek buffer items into the main bag for consistency.
	while _peek_index < _peek_buffer.size():
		_bag.append(_peek_buffer[_peek_index])
		_peek_index += 1

	_refresh_bag()
	_peek_buffer = PackedStringArray()
	_peek_index = 0
