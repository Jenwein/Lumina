extends Node2D

@onready var ws_client: LuminaWSClient = $WSClient

func _ready() -> void:
	print("Lumina Client Main Scene Ready")
	ws_client.message_received.connect(_on_message_received)

func _on_message_received(msg: Dictionary) -> void:
	if msg["type"] == "pet_command":
		print("Received PET_COMMAND: ", msg["payload"])
	elif msg["type"] == "chat_response":
		print("Received CHAT_RESPONSE: ", msg["payload"].get("text", ""))

func _input(event: InputEvent) -> void:
	if event is InputEventKey:
		if event.pressed and event.keycode == KEY_SPACE:
			print("Space pressed - Sending test user_message")
			ws_client.send_message("user_message", {"text": "Hello from Godot Spacebar!"})
