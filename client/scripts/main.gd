extends Node2D

@onready var ws_client: LuminaWSClient = $WSClient
@onready var window_manager: WindowManager = $WindowManager
@onready var pet: PetController = $Pet

func _ready() -> void:
	print("Lumina Client Main Scene Ready")
	ws_client.message_received.connect(_on_message_received)
	
	# Connect to pet signals for debugging
	pet.state_changed.connect(_on_pet_state_changed)
	pet.arrived_at_target.connect(_on_pet_arrived)
	pet.click_ready.connect(_on_pet_click_ready)
	
	# Initial window setup
	_update_window_passthrough()

func _process(_delta: float) -> void:
	# Update passthrough region every frame to follow the pet
	_update_window_passthrough()

func _on_message_received(msg: Dictionary) -> void:
	if msg["type"] == "pet_command":
		_handle_pet_command(msg["payload"])
	elif msg["type"] == "chat_response":
		print("Received CHAT_RESPONSE: ", msg["payload"].get("text", ""))

func _handle_pet_command(payload: Dictionary) -> void:
	var command = payload.get("command", "")
	# Note: Python sends payload={"command": "...", "position": {...}, "state": "..."}
	# But main.gd expects payload={"command": "...", "data": {...}}
	# I should align them. Let's make it flexible.
	
	match command:
		"move_to":
			var pos = payload.get("position", payload.get("data", {}))
			var target = Vector2(pos.get("x", 0), pos.get("y", 0))
			var speed = payload.get("speed", payload.get("data", {}).get("speed", 200.0))
			pet.move_to(target, speed)
		"set_state":
			var state = payload.get("state", payload.get("data", {}).get("state", "idle"))
			pet.set_pet_state(state)
		"perform_click":
			var pos = payload.get("position", payload.get("data", {}))
			var target = Vector2(pos.get("x", 0), pos.get("y", 0))
			pet.perform_click(target)
		"quit":
			print("Received quit command, quitting.")
			get_tree().quit()
		_:
			print("Unknown pet_command: ", command)

func _on_pet_click_ready(pos: Vector2) -> void:
	ws_client.send_message("pet_event", {
		"event": "click_ready",
		"position": {"x": pos.x, "y": pos.y}
	})

func _on_pet_state_changed(old_state: StringName, new_state: StringName) -> void:
	print("Pet state changed: ", old_state, " -> ", new_state)

func _on_pet_arrived() -> void:
	print("Pet arrived at target.")

func _update_window_passthrough() -> void:
	# Punch a hole for the pet in the passthrough window
	# We use the ClickArea collision shape (RectangleShape2D) to define the polygon
	var collision_shape = pet.click_area.get_child(0).shape as RectangleShape2D
	if collision_shape:
		var size = collision_shape.size
		var pos = pet.global_position - (size / 2.0)
		
		var rect_poly = PackedVector2Array([
			pos,
			pos + Vector2(size.x, 0),
			pos + size,
			pos + Vector2(0, size.y)
		])
		
		window_manager.update_passthrough_region([rect_poly])

func _input(event: InputEvent) -> void:
	if event is InputEventKey:
		if event.pressed and event.keycode == KEY_SPACE:
			print("Space pressed - Sending test user_message")
			ws_client.send_message("user_message", {"text": "Hello from Godot Spacebar!"})
