from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from datetime import datetime
import os
from werkzeug.security import generate_password_hash


from functools import wraps
from flask import session, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'templates'))
DB_NAME = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function



from flask import session

app.secret_key = 'nagyontitkoskulcs'  # Ez fontos a session működéséhez

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?',
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('index'))  # vagy ahova szeretnénk belépés után
        else:
            return render_template('login.html', error='Hibás felhasználónév vagy jelszó.')

    return render_template('login.html')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tanker', methods=['GET', 'POST'])
@login_required
def tanker():
    conn = get_db_connection()

    if request.method == 'POST':
        ceg = request.form['ceg']
        liter = float(request.form['liter'])

        # Létezik-e már a cég a készlet táblában?
        existing = conn.execute('SELECT * FROM keszlet WHERE ceg = ?', (ceg,)).fetchone()
        if existing:
            # ha igen, növeljük az értékét
            conn.execute('UPDATE keszlet SET liter = liter + ? WHERE ceg = ?', (liter, ceg))
        else:
            # ha nem, új sort szúrunk be
            conn.execute('INSERT INTO keszlet (ceg, liter) VALUES (?, ?)', (ceg, liter))

        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('tanker.html')


@app.route('/tankolas', methods=['GET', 'POST'])
@login_required
def tankolas():
    conn = get_db_connection()

    # Elérhető készlet lekérdezése
    keszlet_sorok = conn.execute('SELECT * FROM keszlet').fetchall()
    keszlet = conn.execute('SELECT * FROM keszlet').fetchall()


    if request.method == 'POST':
        datum = request.form['datum']
        gep_neve = request.form['gep_neve']
        uzemora = int(request.form['uzemora'])
        liter = float(request.form['liter'])
        gepkezelo = request.form['gepkezelo']
        sofor = request.form['sofor']
        signature = request.form['signature']


        # Ideiglenesen mindig az első készletből vonjuk le
        keszlet_ceg = keszlet[0]['ceg']



        # Kivonás
        conn.execute(
            'UPDATE keszlet SET liter = liter - ? WHERE ceg = ?',
            (liter, keszlet_ceg)
        )

        # Mentés a tankolas táblába
        signature = request.form['signature']

        conn.execute(
        'INSERT INTO tankolas (datum, gep_neve, uzemora, liter, gepkezelo, sofor, signature) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (datum, gep_neve, uzemora, liter, gepkezelo, sofor, signature)
    )

        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    # Ha GET kérés, megjelenítjük a tankolás oldalt
    return render_template('tankolas.html', keszlet=keszlet, datum=datetime.today().strftime('%Y-%m-%d'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

from flask import abort



@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
            (username, hashed_password, role)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/tankolas-jelentes', methods=['GET', 'POST'])
def tankolas_jelentes():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    tankolasok = []
    if request.method == 'POST':
        tol_datum = request.form.get('tol_datum')
        ig_datum = request.form.get('ig_datum')

        conn = get_db_connection()
        tankolasok = conn.execute(
            'SELECT * FROM tankolas WHERE datum BETWEEN ? AND ? ORDER BY datum',
            (tol_datum, ig_datum)
        ).fetchall()
        conn.close()

    return render_template('tankolas_jelentes.html', tankolasok=tankolasok)


@app.route('/felhasznalok')
def felhasznalok():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    felhasznalok = conn.execute('SELECT id, username, role FROM users').fetchall()
    conn.close()

    return render_template('templates_felhasznalok.html', felhasznalok=felhasznalok)





if __name__ == '__main__':
    app.run(debug=True)
