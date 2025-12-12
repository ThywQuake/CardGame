from flask import Flask, render_template, request, jsonify
from app.core.engine.game import Game
import threading


app = Flask(__name__)
game = Game()


def run_game_loop():
    print("Game loop started.")
    game.run()


@app.route("/")
def index():
    return render_template("index.html", game=game)


@app.route("/api/play_card", methods=["POST"])
def api_play_card():
    data = request.get_json()

    if not data or "card_id" not in data or "seat_id" not in data:
        return jsonify({"error": "Invalid request"}), 400

    action_payload = {
        "action_type": "PLAY_CARD",
        "card_id": data["card_id"],
        "seat_id": data["seat_id"],
    }

    game.act_on(action_payload)
    return jsonify({"status": "Card played"}), 200


if __name__ == "__main__":
    game_thread = threading.Thread(target=run_game_loop)
    game_thread.daemon = True
    game_thread.start()

    app.run(debug=True, use_reloader=False)
