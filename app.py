from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify
)

import sqlite3
import joblib
import pandas as pd

from werkzeug.security import generate_password_hash, check_password_hash


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)

app.secret_key = "smart_agriculture_secret_key_2026"


# ============================================================
# MACHINE LEARNING MODEL
# ============================================================

MODEL_PATH = "models/crop_prediction_model.pkl"

model = joblib.load(MODEL_PATH)


# Exact feature names used while training the Random Forest model
MODEL_FEATURES = [
    "N",
    "P",
    "K",
    "temperature",
    "humidity",
    "ph",
    "rainfall"
]


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db_connection():

    connection = sqlite3.connect("users.db")

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# GLOBAL USER INFORMATION FOR ALL TEMPLATES
# ============================================================
#
# This is the important fix.
#
# Now user_name and user_email are automatically available
# inside:
#
# index.html
# history.html
# profile.html
# change_password.html
# and other templates.
#
# Therefore we don't have to manually pass user_name from
# every individual Flask route.
# ============================================================

@app.context_processor
def inject_user_data():

    user_name = None
    user_email = None
    user_created_at = None

    if "user_id" in session:

        connection = get_db_connection()

        user = connection.execute(
            """
            SELECT
                name,
                email,
                created_at
            FROM users
            WHERE id = ?
            """,
            (session["user_id"],)
        ).fetchone()

        connection.close()

        if user:

            user_name = user["name"]
            user_email = user["email"]
            user_created_at = user["created_at"]

    return {
        "user_name": user_name,
        "user_email": user_email,
        "user_created_at": user_created_at
    }


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_database():

    connection = get_db_connection()

    # --------------------------------------------------------
    # USERS TABLE
    # --------------------------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    connection.commit()

    # --------------------------------------------------------
    # CHECK USERS TABLE COLUMNS
    # --------------------------------------------------------

    columns = connection.execute(
        "PRAGMA table_info(users)"
    ).fetchall()

    column_names = [
        column["name"]
        for column in columns
    ]

    # --------------------------------------------------------
    # ADD created_at IF IT DOES NOT EXIST
    # --------------------------------------------------------

    if "created_at" not in column_names:

        connection.execute("""
            ALTER TABLE users
            ADD COLUMN created_at TIMESTAMP
        """)

        connection.execute("""
            UPDATE users
            SET created_at = CURRENT_TIMESTAMP
            WHERE created_at IS NULL
        """)

        connection.commit()

    # --------------------------------------------------------
    # PREDICTIONS TABLE
    # --------------------------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS predictions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            nitrogen REAL NOT NULL,

            phosphorus REAL NOT NULL,

            potassium REAL NOT NULL,

            temperature REAL NOT NULL,

            humidity REAL NOT NULL,

            ph REAL NOT NULL,

            rainfall REAL NOT NULL,

            predicted_crop TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
            REFERENCES users(id)
        )
    """)

    connection.commit()

    connection.close()


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    if "user_id" in session:

        return redirect(
            url_for("dashboard")
        )

    return redirect(
        url_for("login")
    )


# ============================================================
# REGISTER
# ============================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        # ----------------------------------------------------
        # REQUIRED FIELDS
        # ----------------------------------------------------

        if not name or not email or not password:

            return render_template(
                "register.html",
                error="Please fill in all required fields."
            )

        # ----------------------------------------------------
        # PASSWORD MATCH
        # ----------------------------------------------------

        if password != confirm_password:

            return render_template(
                "register.html",
                error="Passwords do not match."
            )

        # ----------------------------------------------------
        # PASSWORD LENGTH
        # ----------------------------------------------------

        if len(password) < 6:

            return render_template(
                "register.html",
                error="Password must contain at least 6 characters."
            )

        connection = get_db_connection()

        # ----------------------------------------------------
        # CHECK EXISTING EMAIL
        # ----------------------------------------------------

        existing_user = connection.execute(
            """
            SELECT id
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        if existing_user:

            connection.close()

            return render_template(
                "register.html",
                error="An account with this email already exists."
            )

        # ----------------------------------------------------
        # HASH PASSWORD
        # ----------------------------------------------------

        hashed_password = generate_password_hash(
            password
        )

        # ----------------------------------------------------
        # CREATE USER
        # ----------------------------------------------------

        connection.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password,
                created_at
            )
            VALUES
            (
                ?,
                ?,
                ?,
                CURRENT_TIMESTAMP
            )
            """,
            (
                name,
                email,
                hashed_password
            )
        )

        connection.commit()

        connection.close()

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        connection = get_db_connection()

        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        connection.close()

        # ----------------------------------------------------
        # VALIDATE LOGIN
        # ----------------------------------------------------

        if user and check_password_hash(
            user["password"],
            password
        ):

            session.clear()

            session["user_id"] = user["id"]

            session["user_name"] = user["name"]

            session["user_email"] = user["email"]

            return redirect(
                url_for("dashboard")
            )

        return render_template(
            "login.html",
            error="Invalid email or password."
        )

    return render_template(
        "login.html"
    )


# ============================================================
# FORGOT PASSWORD
# ============================================================

@app.route(
    "/forgot-password",
    methods=["GET", "POST"]
)
def forgot_password():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        connection = get_db_connection()

        user = connection.execute(
            """
            SELECT id, email
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        connection.close()

        if not user:

            return render_template(
                "forgot_password.html",
                error="No account found with this email address."
            )

        session["reset_user_id"] = user["id"]

        return redirect(
            url_for("reset_password")
        )

    return render_template(
        "forgot_password.html"
    )


# ============================================================
# RESET PASSWORD
# ============================================================

@app.route(
    "/reset-password",
    methods=["GET", "POST"]
)
def reset_password():

    if "reset_user_id" not in session:

        return redirect(
            url_for("forgot_password")
        )

    if request.method == "POST":

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        # ----------------------------------------------------
        # VALIDATE PASSWORD
        # ----------------------------------------------------

        if not password:

            return render_template(
                "reset_password.html",
                error="Please enter a new password."
            )

        if password != confirm_password:

            return render_template(
                "reset_password.html",
                error="Passwords do not match."
            )

        if len(password) < 6:

            return render_template(
                "reset_password.html",
                error="Password must contain at least 6 characters."
            )

        # ----------------------------------------------------
        # HASH PASSWORD
        # ----------------------------------------------------

        hashed_password = generate_password_hash(
            password
        )

        connection = get_db_connection()

        # ----------------------------------------------------
        # UPDATE PASSWORD
        # ----------------------------------------------------

        connection.execute(
            """
            UPDATE users
            SET password = ?
            WHERE id = ?
            """,
            (
                hashed_password,
                session["reset_user_id"]
            )
        )

        connection.commit()

        connection.close()

        session.pop(
            "reset_user_id",
            None
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "reset_password.html"
    )


# ============================================================
# CHANGE PASSWORD
# ============================================================

@app.route(
    "/change-password",
    methods=["GET", "POST"]
)
def change_password():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        current_password = request.form.get(
            "current_password",
            ""
        )

        new_password = request.form.get(
            "new_password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        connection = get_db_connection()

        # ----------------------------------------------------
        # GET CURRENT USER
        # ----------------------------------------------------

        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE id = ?
            """,
            (session["user_id"],)
        ).fetchone()

        # ----------------------------------------------------
        # CHECK CURRENT PASSWORD
        # ----------------------------------------------------

        if not user or not check_password_hash(
            user["password"],
            current_password
        ):

            connection.close()

            return render_template(
                "change_password.html",
                error="Current password is incorrect."
            )

        # ----------------------------------------------------
        # NEW PASSWORD LENGTH
        # ----------------------------------------------------

        if len(new_password) < 6:

            connection.close()

            return render_template(
                "change_password.html",
                error="New password must contain at least 6 characters."
            )

        # ----------------------------------------------------
        # NEW PASSWORD MATCH
        # ----------------------------------------------------

        if new_password != confirm_password:

            connection.close()

            return render_template(
                "change_password.html",
                error="New passwords do not match."
            )

        # ----------------------------------------------------
        # HASH NEW PASSWORD
        # ----------------------------------------------------

        hashed_password = generate_password_hash(
            new_password
        )

        # ----------------------------------------------------
        # UPDATE PASSWORD
        # ----------------------------------------------------

        connection.execute(
            """
            UPDATE users
            SET password = ?
            WHERE id = ?
            """,
            (
                hashed_password,
                session["user_id"]
            )
        )

        connection.commit()

        connection.close()

        return render_template(
            "change_password.html",
            success="Password changed successfully."
        )

    return render_template(
        "change_password.html"
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    user_id = session["user_id"]

    connection = get_db_connection()

    # --------------------------------------------------------
    # GET CURRENT USER
    # --------------------------------------------------------

    user = connection.execute(
        """
        SELECT
            id,
            name,
            email,
            created_at
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()

    # --------------------------------------------------------
    # USER NOT FOUND
    # --------------------------------------------------------

    if user is None:

        connection.close()

        session.clear()

        return redirect(
            url_for("login")
        )

    # --------------------------------------------------------
    # TOTAL PREDICTIONS
    # --------------------------------------------------------

    prediction_count = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM predictions
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()["count"]

    # --------------------------------------------------------
    # RECENT PREDICTIONS
    # --------------------------------------------------------

    recent_predictions = connection.execute(
        """
        SELECT *
        FROM predictions
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 5
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    return render_template(
        "index.html",
        user_name=user["name"],
        user_email=user["email"],
        user_created_at=user["created_at"],
        prediction_count=prediction_count,
        recent_predictions=recent_predictions
    )


# ============================================================
# CROP PREDICTION
# ============================================================

@app.route(
    "/predict",
    methods=["POST"]
)
def predict():

    if "user_id" not in session:

        if request.headers.get(
            "X-Requested-With"
        ) == "XMLHttpRequest":

            return jsonify({
                "success": False,
                "message": "Please login to continue."
            }), 401

        return redirect(
            url_for("login")
        )

    try:

        # ----------------------------------------------------
        # GET INPUT VALUES
        # ----------------------------------------------------

        nitrogen = float(
            request.form.get(
                "nitrogen"
            )
        )

        phosphorus = float(
            request.form.get(
                "phosphorus"
            )
        )

        potassium = float(
            request.form.get(
                "potassium"
            )
        )

        temperature = float(
            request.form.get(
                "temperature"
            )
        )

        humidity = float(
            request.form.get(
                "humidity"
            )
        )

        ph = float(
            request.form.get(
                "ph"
            )
        )

        rainfall = float(
            request.form.get(
                "rainfall"
            )
        )

        # ----------------------------------------------------
        # CREATE DATAFRAME
        # ----------------------------------------------------
        # Using the same feature names as model training
        # prevents the sklearn feature-name warning.

        input_data = pd.DataFrame(
            [[
                nitrogen,
                phosphorus,
                potassium,
                temperature,
                humidity,
                ph,
                rainfall
            ]],
            columns=MODEL_FEATURES
        )

        # ----------------------------------------------------
        # PREDICT
        # ----------------------------------------------------

        prediction = model.predict(
            input_data
        )

        predicted_crop = str(
            prediction[0]
        )

        # ----------------------------------------------------
        # FORMAT CROP NAME
        # ----------------------------------------------------

        crop_name = predicted_crop.replace(
            "_",
            " "
        ).title()

        # ----------------------------------------------------
        # SAVE PREDICTION
        # ----------------------------------------------------

        connection = get_db_connection()

        connection.execute(
            """
            INSERT INTO predictions
            (
                user_id,
                nitrogen,
                phosphorus,
                potassium,
                temperature,
                humidity,
                ph,
                rainfall,
                predicted_crop
            )
            VALUES
            (
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )
            """,
            (
                session["user_id"],
                nitrogen,
                phosphorus,
                potassium,
                temperature,
                humidity,
                ph,
                rainfall,
                crop_name
            )
        )

        connection.commit()

        connection.close()

        # ----------------------------------------------------
        # AJAX RESPONSE
        # ----------------------------------------------------

        if request.headers.get(
            "X-Requested-With"
        ) == "XMLHttpRequest":

            return jsonify({
                "success": True,
                "crop": crop_name,
                "message": "Prediction completed successfully."
            })

        return redirect(
            url_for("dashboard")
        )

    except (ValueError, TypeError):

        if request.headers.get(
            "X-Requested-With"
        ) == "XMLHttpRequest":

            return jsonify({
                "success": False,
                "message": "Please enter valid numeric values."
            }), 400

        return redirect(
            url_for("dashboard")
        )

    except Exception as error:

        print(
            "Prediction Error:",
            error
        )

        if request.headers.get(
            "X-Requested-With"
        ) == "XMLHttpRequest":

            return jsonify({
                "success": False,
                "message": "An error occurred while making the prediction."
            }), 500

        return redirect(
            url_for("dashboard")
        )


# ============================================================
# PREDICTION HISTORY
# ============================================================

@app.route("/history")
def history():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    user_id = session["user_id"]

    search = request.args.get(
        "search",
        ""
    ).strip()

    connection = get_db_connection()

    # --------------------------------------------------------
    # SEARCH HISTORY
    # --------------------------------------------------------

    if search:

        predictions = connection.execute(
            """
            SELECT *
            FROM predictions
            WHERE user_id = ?
            AND predicted_crop LIKE ?
            ORDER BY created_at DESC
            """,
            (
                user_id,
                f"%{search}%"
            )
        ).fetchall()

    else:

        predictions = connection.execute(
            """
            SELECT *
            FROM predictions
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,)
        ).fetchall()

    # --------------------------------------------------------
    # TOTAL HISTORY COUNT
    # --------------------------------------------------------

    total_count = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM predictions
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()["count"]

    connection.close()

    # --------------------------------------------------------
    # IMPORTANT:
    # user_name does NOT need to be manually passed here.
    #
    # @app.context_processor automatically provides it.
    # --------------------------------------------------------

    return render_template(
        "history.html",
        predictions=predictions,
        total_count=total_count,
        search=search
    )


# ============================================================
# DELETE SINGLE PREDICTION
# ============================================================

@app.route(
    "/delete-prediction/<int:prediction_id>",
    methods=["POST"]
)
def delete_prediction(prediction_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    connection = get_db_connection()

    connection.execute(
        """
        DELETE FROM predictions
        WHERE id = ?
        AND user_id = ?
        """,
        (
            prediction_id,
            session["user_id"]
        )
    )

    connection.commit()

    connection.close()

    return redirect(
        url_for("history")
    )


# ============================================================
# CLEAR ALL HISTORY
# ============================================================

@app.route(
    "/clear-history",
    methods=["POST"]
)
def clear_history():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    connection = get_db_connection()

    connection.execute(
        """
        DELETE FROM predictions
        WHERE user_id = ?
        """,
        (session["user_id"],)
    )

    connection.commit()

    connection.close()

    return redirect(
        url_for("history")
    )


# ============================================================
# MY PROFILE
# ============================================================

@app.route("/profile")
def profile():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    connection = get_db_connection()

    user = connection.execute(
        """
        SELECT
            id,
            name,
            email,
            created_at
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    connection.close()

    if user is None:

        session.clear()

        return redirect(
            url_for("login")
        )

    return render_template(
        "profile.html",
        user=user
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    init_database()

    app.run(
        debug=True
    )