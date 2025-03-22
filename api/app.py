from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/annonces", methods=["GET"])
def get_annonces():
    return jsonify([{"titre": "Appartement", "prix": "200 000 TND"}])

if __name__ == "__main__":
    app.run(debug=True)