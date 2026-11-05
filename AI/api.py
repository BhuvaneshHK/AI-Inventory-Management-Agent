from flask import Flask, jsonify, request
from inventory_analysis import generate_reorder_suggestions

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/reorder-suggestions")
def reorder_suggestions():
    results = generate_reorder_suggestions()

    store_id = request.args.get("store_id")
    if store_id:
        results = results[results["Store_id"] == store_id]

    if request.args.get("only_flagged", "false").lower() == "true":
        results = results[results["Reorder_Suggested"]]

    return jsonify(results.to_dict(orient="records"))


@app.get("/forecast")
def forecast():
    store_id = request.args.get("store_id")
    product_id = request.args.get("product_id")
    if not store_id or not product_id:
        return jsonify(error="store_id and product_id are required"), 400

    results = generate_reorder_suggestions()
    match = results[(results["Store_id"] == store_id) & (results["Product_id"] == product_id)]
    if match.empty:
        return jsonify(error="No data for that store/product"), 404

    return jsonify(match.iloc[0].to_dict())


if __name__ == "__main__":
    # Port 5001 because macOS uses 5000 for AirPlay Receiver.
    app.run(host="127.0.0.1", port=5001, debug=True)