

class Player:
    def __init__(self, **kwargs):
        self.name: str = kwargs.get("name", "Player")
        self.hero: Hero = kwargs.get("hero", Hero())
        self.deck: Deck = kwargs.get("deck", Deck(cards=[FighterCard()] * 40))
        self.hand: Hand = kwargs.get("hand", Hand())
        self.graveyard: Graveyard = kwargs.get("graveyard", Graveyard())
        self.super_block: SuperBlock = kwargs.get("super_block", SuperBlock())
        self.energy: int = kwargs.get("energy", 0)

        self.game: "Game" = kwargs.get("game", None) 