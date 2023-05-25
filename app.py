import pandas as pd
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import pickle
from flask_mysqldb import MySQL

app = Flask(__name__)
model = pickle.load(open('linear_regression_model_sc.pkl', 'rb'))
app.secret_key = 'app_secret_key_here'


# MySQL Configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "your_password_here"
app.config["MYSQL_DB"] = "graduate_admission_predictor"
mysql = MySQL(app)

@app.route('/')
def home():
    if "user_id" in session:
        return render_template("index.html", username=session["username"])
    else:
        return redirect(url_for("login"))


# Login Code
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        if user:
            
            session["user_id"] = user[0]
            session["username"] = user[1]
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid email or password")
    else:
        return render_template("login.html")
    
# Register Code

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if user already exists
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        user = cur.fetchone()
        cur.close()

        if user:
            # Return error message if username or email already exists
            return render_template('register.html', error='Username or email already exists')
        else:
            # Insert new user into database
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
            mysql.connection.commit()
            cur.close()

            # Return success message
            return render_template('register.html', success='User created successfully')

    # Render registration form
    return render_template('register.html')

# Logout Code
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route('/predict', methods=['GET','post'])
def predict():
		username=session["username"]
		GRE_Score = int(request.form['GRE Score'])
		TOEFL_Score = int(request.form['TOEFL Score'])
		University_Rating = int(request.form['University Rating'])
		SOP = float(request.form['SOP'])
		LOR = float(request.form['LOR'])
		CGPA = float(request.form['CGPA'])
		Research = int(request.form['Research'])
	
		final_features = pd.DataFrame([[GRE_Score, TOEFL_Score, University_Rating, SOP, LOR, CGPA, Research]])
	
		predict = model.predict(final_features)
	
		output = predict[0]
        
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO user_data (username, GRE_Score, TOEFL_Score, University_Rating, SOP, LOR, CGPA, Research, Admission_Prediction) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (username, GRE_Score, TOEFL_Score, University_Rating, SOP, LOR, CGPA, Research, format(output)))
		mysql.connection.commit()
		cur.close()
	
		return render_template('index.html', username=username,  prediction_text='Admission chances are {}'.format(output), GRE_Score=GRE_Score, TOEFL_Score=TOEFL_Score, University_Rating=University_Rating, SOP=SOP, LOR=LOR, CGPA=CGPA, Research=Research)
	
if __name__ == "__main__":
	app.run(debug=True)
