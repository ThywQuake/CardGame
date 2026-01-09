from app.core.action.action import Action, Operation

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.engine.game import Game


class ActionManager:
    def __init__(self):
        self.pending_actions: list[Action] = []
        self.current_action: Action | None = None
        self.paused: bool = False

    def open_action(self, action: Action):
        self.pending_actions.append(action)
        self.current_action = action

    def close_action(self):
        if self.current_action in self.pending_actions:
            self.pending_actions.remove(self.current_action)
        self.current_action = self.pending_actions[-1] if self.pending_actions else None

    def receive(self, operation: dict, game: Game):
        try:
            op = Operation(
                operation_name=operation["operation_name"],
                faction=operation["faction"],
                data=operation["data"],
            )  # type: ignore
        except KeyError:
            return

        if op.operation_name == "end_phase":
            self.end_phase(op, game)
            return

        if self.current_action:
            self.current_action.receive(op)

    def update(self, dt: float, game: Game):
        if self.current_action:
            events = self.current_action.update(dt, game)
            if events:
                self.paused = True
                game.run_events(events)

    def end_phase(self, operation: Operation, game: Game):
        # Check endable
        faction = operation.faction
        if not game.item_manager.end_phase_button.activated[faction]:
            return  # Not endable

        self.pending_actions.clear()
        self.current_action = None
        self.paused = False
