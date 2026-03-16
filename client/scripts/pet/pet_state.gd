class_name PetState
extends Node

## Base class for all pet states.

var state_machine: PetStateMachine
var pet: PetController

func enter() -> void:
	pass

func exit() -> void:
	pass

func update(_delta: float) -> void:
	pass

func physics_update(_delta: float) -> void:
	pass
