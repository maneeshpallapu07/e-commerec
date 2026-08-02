from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)

db = pymysql.connect(
    host="database-1.c9o8eugeq7eq.ap-southeast-2.rds.amazonaws.com",
    user="admin",
    password="db2develop123",
    database="product_db"
)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "UP"
    })


@app.route("/products", methods=["GET"])
def get_products():

    cursor = db.cursor()

    cursor.execute(
        "SELECT * FROM products"
    )

    rows = cursor.fetchall()

    result = []

    for row in rows:
        result.append({
            "id": row[0],
            "product_name": row[1],
            "price": float(row[2]),
            "quantity": row[3]
        })

    return jsonify(result)


@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):

    cursor = db.cursor()

    cursor.execute(
        """
        SELECT * FROM products
        WHERE id=%s
        """,
        (product_id,)
    )

    product = cursor.fetchone()

    if not product:
        return jsonify({
            "message": "Product Not Found"
        }), 404

    return jsonify({
        "id": product[0],
        "product_name": product[1],
        "price": float(product[2]),
        "quantity": product[3]
    })


@app.route("/products", methods=["POST"])
def create_product():

    data = request.get_json()

    product_name = data["product_name"]
    price = data["price"]
    quantity = data["quantity"]

    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO products(product_name,price,quantity)
        VALUES(%s,%s,%s)
        """,
        (product_name, price, quantity)
    )

    db.commit()

    return jsonify({
        "message": "Product Created Successfully"
    })


@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):

    cursor = db.cursor()

    cursor.execute(
        """
        DELETE FROM products
        WHERE id=%s
        """,
        (product_id,)
    )

    db.commit()

    return jsonify({
        "message": "Product Deleted Successfully"
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )
