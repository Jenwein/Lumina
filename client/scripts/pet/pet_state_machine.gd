class_name PetStateMachine
extends Node

## Finite State Machine for the pet.

signal state_changed(old_state: StringName, new_state: StringName)

@export var initial_state: NodePath

var current_state: PetState
var states: Dictionary = {}

func _ready() -> void:
	# Wait for the pet (parent) to be ready
	var parent = get_parent()
	if not parent.is_node_ready():
		await parent.ready
	
	# Populate states from children
	for child in get_children():
		if child is PetState:
			states[child.name.to_lower()] = child
			child.state_machine = self
			child.pet = parent as PetController
			
	if initial_state:
		transition_to(get_node(initial_state).name.to_lower())

func _process(delta: float) -> void:
	if current_state:
		current_state.update(delta)

func _physics_process(delta: float) -> void:
	if current_state:
		current_state.physics_update(delta)

func transition_to(state_name: StringName, msg: Dictionary = {}) -> void:
	var state_key = state_name.to_lower()
	if not states.has(state_key):
		push_warning("Attempted to transition to non-existent state: ", state_name)
		return
		
	var old_state_name = current_state.name if current_state else ""
	
	if current_state:
		current_state.exit()
		
	current_state = states[state_key]
	current_state.enter() # Optional: pass msg if needed
	
	state_changed.emit(old_state_name, current_state.name)
