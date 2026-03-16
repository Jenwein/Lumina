class_name LuminaWSClient
extends Node

signal connected
signal disconnected
signal message_received(msg: Dictionary)

@export var server_url: String = "ws://127.0.0.1:8765"
@export var auto_reconnect: bool = true
@export var reconnect_delay: float = 5.0
@export var heartbeat_interval: float = 30.0

var socket: WebSocketPeer = WebSocketPeer.new()
var is_connected_to_server: bool = false
var last_heartbeat_time: float = 0.0
var is_connecting: bool = false

func _ready() -> void:
	connect_to_server()

func _process(_delta: float) -> void:
	socket.poll()
	var state = socket.get_ready_state()
	
	if state == WebSocketPeer.STATE_OPEN:
		is_connecting = false
		if not is_connected_to_server:
			_on_connected()
		
		while socket.get_available_packet_count() > 0:
			var packet = socket.get_packet()
			_handle_packet(packet)
			
		_check_heartbeat()
			
	elif state == WebSocketPeer.STATE_CLOSED:
		if is_connected_to_server:
			_on_disconnected()
		
		if auto_reconnect and not is_connecting:
			_retry_connection()

func _retry_connection() -> void:
	is_connecting = true
	await get_tree().create_timer(reconnect_delay).timeout
	connect_to_server()

func connect_to_server() -> Error:
	if socket.get_ready_state() != WebSocketPeer.STATE_CLOSED:
		return OK
		
	print("Connecting to Lumina Server: ", server_url)
	var err = socket.connect_to_url(server_url)
	if err != OK:
		print("Could not connect to server: ", err)
		is_connecting = false # Reset so we can try again
	return err

func send_message(type: String, payload: Dictionary = {}) -> void:
	if socket.get_ready_state() != WebSocketPeer.STATE_OPEN:
		print("Cannot send message, socket not open.")
		return
		
	var msg = {
		"type": type,
		"payload": payload,
		"id": str(RandomNumberGenerator.new().randi()), # Minimal ID for Phase 01
		"timestamp": Time.get_datetime_string_from_system(false, true)
	}
	var json_str = JSON.stringify(msg)
	socket.send_text(json_str)

func _on_connected() -> void:
	is_connected_to_server = true
	print("Connected to Lumina Server")
	connected.emit()
	_send_client_ready()
	last_heartbeat_time = Time.get_ticks_msec() / 1000.0

func _on_disconnected() -> void:
	is_connected_to_server = false
	print("Disconnected from Lumina Server")
	disconnected.emit()

func _handle_packet(packet: PackedByteArray) -> void:
	var json_str = packet.get_string_from_utf8()
	var json = JSON.new()
	var err = json.parse(json_str)
	if err == OK:
		var msg = json.data
		if msg.has("type"):
			if msg["type"] == "server_ready":
				print("Handshake complete. Server version: ", msg["payload"].get("version", "unknown"))
			elif msg["type"] == "heartbeat":
				last_heartbeat_time = Time.get_ticks_msec() / 1000.0
			
			message_received.emit(msg)
	else:
		print("JSON parse error: ", json.get_error_message(), " in ", json_str)

func _send_client_ready() -> void:
	send_message("client_ready", {"version": "0.1.0"})

func _check_heartbeat() -> void:
	var current_time = Time.get_ticks_msec() / 1000.0
	if current_time - last_heartbeat_time >= heartbeat_interval:
		send_message("heartbeat")
		last_heartbeat_time = current_time # Reset for next interval
