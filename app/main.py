from flask import Flask, render_template
from app.core.game import Game
from app.core.models import Player, Faction

app = Flask(__name__)

zombie_player = Player(name="SuperBrainz", faction=Faction.ZOMBIE)
plant_player = Player(name="GreenShadow", faction=Faction.PLANT)
game = Game(zombie_player=zombie_player, plant_player=plant_player)


@app.route("/")
def index():
    return render_template("board.html", game=game)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
    game.run()
