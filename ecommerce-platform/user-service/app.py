from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)

import os

db = pymysql.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "UP"
    })


@app.route("/users", methods=["POST"])
def create_user():

    data = request.get_json()

    name = data["name"]
    email = data["email"]
    city = data["city"]

    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO users(name,email,city)
        VALUES(%s,%s,%s)
        """,
        (name, email, city)
    )

    db.commit()

    return jsonify({
        "message": "User Created Successfully"
    })


@app.route("/users", methods=["GET"])
def get_users():

    cursor = db.cursor()

    cursor.execute(
        "SELECT * FROM users"
    )

    rows = cursor.fetchall()

    result = []

    for row in rows:
        result.append({
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "city": row[3]
        })

    return jsonify(result)


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):

    cursor = db.cursor()

    cursor.execute(
        """
        SELECT * FROM users
        WHERE id=%s
        """,
        (user_id,)
    )

    user = cursor.fetchone()

    if not user:
        return jsonify({
            "message": "User Not Found"
        }), 404

    return jsonify({
        "id": user[0],
        "name": user[1],
        "email": user[2],
        "city": user[3]
    })


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):

    cursor = db.cursor()

    cursor.execute(
        """
        DELETE FROM users
        WHERE id=%s
        """,
        (user_id,)
    )

    db.commit()

    return jsonify({
        "message": "User Deleted Successfully"
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
