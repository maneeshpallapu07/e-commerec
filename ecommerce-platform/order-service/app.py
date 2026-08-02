from flask import Flask, request, jsonify
import pymysql
import requests

app = Flask(__name__)

db = pymysql.connect(
    host="database-1.c9o8eugeq7eq.ap-southeast-2.rds.amazonaws.com",
    user="admin",
    password="db2develop123",
    database="order_db"
)

USER_SERVICE = "http://54.79.93.183:5000"
PRODUCT_SERVICE = "http://54.79.93.183:5001"


@app.route("/health")
def health():
    return jsonify({
        "status": "UP"
    })


@app.route("/orders", methods=["POST"])
def create_order():

    data = request.get_json()

    user_id = data["user_id"]
    product_id = data["product_id"]
    quantity = data["quantity"]

    # Validate User
    user_response = requests.get(
        f"{USER_SERVICE}/users/{user_id}"
    )

    if user_response.status_code != 200:
        return jsonify({
            "message": "User Not Found"
        }), 404

    # Validate Product
    product_response = requests.get(
        f"{PRODUCT_SERVICE}/products/{product_id}"
    )

    if product_response.status_code != 200:
        return jsonify({
            "message": "Product Not Found"
        }), 404

    product = product_response.json()

    if quantity > product["quantity"]:
        return jsonify({
            "message": "Insufficient Product Quantity"
        }), 400

    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO orders(
            user_id,
            product_id,
            quantity,
            order_status
        )
        VALUES(%s,%s,%s,%s)
        """,
        (
            user_id,
            product_id,
            quantity,
            "CREATED"
        )
    )

    db.commit()

    return jsonify({
        "message": "Order Created Successfully"
    })


@app.route("/orders", methods=["GET"])
def get_orders():

    cursor = db.cursor()

    cursor.execute(
        "SELECT * FROM orders"
    )

    rows = cursor.fetchall()

    result = []

    for row in rows:
        result.append({
            "id": row[0],
            "user_id": row[1],
            "product_id": row[2],
            "quantity": row[3],
            "order_status": row[4]
        })

    return jsonify(result)


@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):

    cursor = db.cursor()

    cursor.execute(
        """
        SELECT * FROM orders
        WHERE id=%s
        """,
        (order_id,)
    )

    order = cursor.fetchone()

    if not order:
        return jsonify({
            "message": "Order Not Found"
        }), 404

    return jsonify({
        "id": order[0],
        "user_id": order[1],
        "product_id": order[2],
        "quantity": order[3],
        "order_status": order[4]
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5002,
        debug=True
    )
