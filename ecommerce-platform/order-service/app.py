from flask import Flask, request, jsonify
import pymysql
import requests
import os

app = Flask(__name__)


def get_db_connection():

    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL")


@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "UP"
    })


@app.route("/orders", methods=["GET"])
def get_orders():

    db = get_db_connection()
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
            "quantity": row[3]
        })

    cursor.close()
    db.close()

    return jsonify(result)


@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT * FROM orders
        WHERE id=%s
        """,
        (order_id,)
    )

    order = cursor.fetchone()

    cursor.close()
    db.close()

    if not order:

        return jsonify({
            "message": "Order Not Found"
        }), 404

    return jsonify({
        "id": order[0],
        "user_id": order[1],
        "product_id": order[2],
        "quantity": order[3]
    })


@app.route("/orders", methods=["POST"])
def create_order():

    data = request.get_json()

    user_id = data["user_id"]
    product_id = data["product_id"]
    quantity = data["quantity"]

    user_response = requests.get(
        f"{USER_SERVICE_URL}/{user_id}"
    )

    if user_response.status_code != 200:

        return jsonify({
            "message": "User Not Found"
        }), 404

    product_response = requests.get(
        f"{PRODUCT_SERVICE_URL}/{product_id}"
    )

    if product_response.status_code != 200:

        return jsonify({
            "message": "Product Not Found"
        }), 404

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO orders(user_id,product_id,quantity)
        VALUES(%s,%s,%s)
        """,
        (user_id, product_id, quantity)
    )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({
        "message": "Order Created Successfully"
    })


@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        """
        DELETE FROM orders
        WHERE id=%s
        """,
        (order_id,)
    )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({
        "message": "Order Deleted Successfully"
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5002,
        debug=True
    )
