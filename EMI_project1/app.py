from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import math

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database setup
def init_sqlite_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS emi_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        principal REAL,
                        rate REAL,
                        tenure INTEGER,
                        emi REAL,
                        result REAL)''')  # Store the result of EMI calculations
    conn.commit()
    conn.close()

init_sqlite_db()

@app.route('/')
def home():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return 'Invalid credentials!'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# EMI Calculator Route
@app.route('/emi_calculator', methods=['GET', 'POST'])
def emi_calculator():
    if 'username' not in session:
        return redirect(url_for('login'))

    result = None
    if request.method == 'POST':
        p = request.form.get('principal')
        r = request.form.get('rate')
        n = request.form.get('tenure')
        emi = request.form.get('emi')

        try:
            if p and r and n:
                # Calculate EMI
                p = float(p)
                r = float(r) / 12 / 100
                n = int(n)
                result = (p * r * (1 + r) ** n) / ((1 + r) ** n - 1)
            elif emi and r and n:
                # Calculate Principal
                emi = float(emi)
                r = float(r) / 12 / 100
                n = int(n)
                result = emi * ((1 + r) ** n - 1) / (r * (1 + r) ** n)
            elif p and emi and n:
                # Calculate Rate of Interest
                p = float(p)
                emi = float(emi)
                n = int(n)
                r = (emi * n / p - 1) * 12 * 100 / n
                result = r
            elif p and emi and r:
                # Calculate Tenure
                p = float(p)
                emi = float(emi)
                r = float(r) / 12 / 100
                result = math.log(emi / (emi - p * r)) / math.log(1 + r)
        except ValueError:
            result = 'Invalid input!'

        # Save calculation to history if there's a result
        if result is not None:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO emi_history (username, principal, rate, tenure, emi, result) VALUES (?, ?, ?, ?, ?, ?)', 
                           (session['username'], p, r * 12 * 100, n, emi, result))
            conn.commit()
            conn.close()

    # Fetch user history
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM emi_history WHERE username = ?', (session['username'],))
    history = cursor.fetchall()
    conn.close()

    return render_template('emi_calculator.html', result=result, username=session['username'], history=history)

@app.route('/delete_history/<int:id>', methods=['GET'])
def delete_history(id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM emi_history WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('emi_calculator'))
    
if __name__ == '__main__':
    app.run(debug=True)
