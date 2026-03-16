class_name WindowManager
extends Node

## Manages transparent overlay and mouse passthrough region.

func _ready() -> void:
	setup_transparent_overlay()

func setup_transparent_overlay() -> void:
	# Note: Most of these are already in project.godot, but we ensure them at runtime.
	get_viewport().transparent_bg = true
	# In Godot 4.x, we use DisplayServer for window management.
	DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_BORDERLESS, true)
	DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_ALWAYS_ON_TOP, true)
	# Enable mouse passthrough for the entire window initially.
	# We will punch a hole for the pet later.
	DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_MOUSE_PASSTHROUGH, true)

func update_passthrough_region(polygons: Array[PackedVector2Array]) -> void:
	# Update the interactive region of the window.
	# Input: An array of polygons (in screen coordinates) that should NOT be passthrough.
	# Note: Godot 4.x window_set_mouse_passthrough takes one PackedVector2Array.
	# To support multiple polygons, we can merge them or just use one for now.
	if polygons.is_empty():
		DisplayServer.window_set_mouse_passthrough(PackedVector2Array())
	else:
		# Use the first polygon for simplicity in Phase 02.
		DisplayServer.window_set_mouse_passthrough(polygons[0])

func get_screen_size() -> Vector2i:
	var screen_index = DisplayServer.window_get_current_screen()
	return DisplayServer.screen_get_size(screen_index)
