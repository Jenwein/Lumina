class_name PetController
extends CharacterBody2D

## Main controller for the desktop pet.

signal arrived_at_target
signal state_changed(old_state: StringName, new_state: StringName)
signal click_ready(position: Vector2)

@onready var sprite: AnimatedSprite2D = $Sprite
@onready var state_machine: PetStateMachine = $StateMachine
@onready var click_area: Area2D = $ClickArea

func _ready() -> void:
	# Connect to state machine signals
	state_machine.state_changed.connect(func(o, n): state_changed.emit(o, n))
	
	# Connect to ClickingState if it exists
	var clicking = state_machine.states.get("clicking")
	if clicking:
		clicking.click_impact.connect(_on_click_impact)
	
	# Initial position: Center of viewport
	global_position = get_viewport().get_visible_rect().size / 2.0

func _on_click_impact() -> void:
	click_ready.emit(global_position)

func perform_click(target: Vector2) -> void:
	# 1. Move to target
	move_to(target)
	
	# 2. Once arrived, transition to clicking
	# We need a way to wait for arrival. WalkingState usually emits arrived?
	# Let's check walking_state.gd
	var walk = state_machine.states["walking"]
	if not walk.is_connected("arrived_at_target", _on_walking_arrived):
		walk.arrived_at_target.connect(_on_walking_arrived, CONNECT_ONE_SHOT)

func _on_walking_arrived() -> void:
	# Arrived at target! Now click.
	state_machine.transition_to("clicking")

func move_to(target: Vector2, speed: float = 200.0) -> void:
	# Transition to walking state and set target
	var walking_state = state_machine.states["walking"]
	walking_state.target_position = target
	walking_state.move_speed = speed
	state_machine.transition_to("walking")

func set_pet_state(state_name: StringName) -> void:
	state_machine.transition_to(state_name)

func get_pet_state() -> StringName:
	return state_machine.current_state.name if state_machine.current_state else "idle"

func _input_event(_viewport: Viewport, event: InputEvent, _shape_idx: int) -> void:
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_RIGHT and event.pressed:
			print("Right click on pet! Current state: ", get_pet_state())
			# Future: Open context menu here.
		elif event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
			print("Left click on pet! Moving to a random spot.")
			# Test: random move
			var screen_size = get_viewport().get_visible_rect().size
			move_to(Vector2(randf_range(50, screen_size.x-50), randf_range(50, screen_size.y-50)))
