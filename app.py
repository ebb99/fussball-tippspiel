from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os
# =======================
# Flask-App & Config
# =======================
app = Flask(__name__)
app.secret_key = 'ein_geheimes_schluesselwort'  # Session für Admin-Login



app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://fussball_tippspiel_db_user:nzgK6hIMjHMr1A5g5rAes0wo2EKGeaLN@dpg-d3vsltf5r7bs73cg5lp0-a/fussball_tippspiel_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# =======================
# Datenbank
# =======================
db = SQLAlchemy(app)

# =======================
# Datenbankmodelle
# =======================
class Spiel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team1 = db.Column(db.String(50), nullable=False)
    team2 = db.Column(db.String(50), nullable=False)
    erg_team1 = db.Column(db.Integer, nullable=False)
    erg_team2 = db.Column(db.Integer, nullable=False)

class Tipp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    spiel_id = db.Column(db.Integer, db.ForeignKey('spiel.id'), nullable=False)
    tipp_team1 = db.Column(db.Integer, nullable=False)
    tipp_team2 = db.Column(db.Integer, nullable=False)

# =======================
# Admin-Passwort
# =======================
ADMIN_PASSWORD = "admin123"

# =======================
# Tabellen erstellen & Beispielspiele
# =======================
with app.app_context():
    db.create_all()
    if Spiel.query.count() == 0:
        beispiel_spiele = [
            Spiel(team1="Deutschland", team2="Frankreich", erg_team1=2, erg_team2=1),
            Spiel(team1="Spanien", team2="Italien", erg_team1=1, erg_team2=1),
            Spiel(team1="England", team2="Portugal", erg_team1=0, erg_team2=2)
        ]
        db.session.add_all(beispiel_spiele)
        db.session.commit()

# =======================
# Routen: Spieler
# =======================
@app.route('/')
def index():
    spiele = Spiel.query.all()
    return render_template('index.html', spiele=spiele)

@app.route('/tipp', methods=['POST'])
def tipp():
    name = request.form['name']
    spiel_id = int(request.form['spiel_id'])
    team1_tipp = int(request.form['team1'])
    team2_tipp = int(request.form['team2'])

    neuer_tipp = Tipp(name=name, spiel_id=spiel_id, tipp_team1=team1_tipp, tipp_team2=team2_tipp)
    db.session.add(neuer_tipp)
    db.session.commit()
    return redirect(url_for('rangliste'))

@app.route('/rangliste')
def rangliste():
    tipps = Tipp.query.all()
    spiele = {s.id: s for s in Spiel.query.all()}
    punkte = {}

    for t in tipps:
        spiel = spiele.get(t.spiel_id)
        if not spiel:
            continue

        if t.tipp_team1 == spiel.erg_team1 and t.tipp_team2 == spiel.erg_team2:
            p = 3
        elif (t.tipp_team1 - t.tipp_team2) * (spiel.erg_team1 - spiel.erg_team2) > 0:
            p = 1
        elif t.tipp_team1 == t.tipp_team2 and spiel.erg_team1 == spiel.erg_team2:
            p = 1
        else:
            p = 0

        punkte[t.name] = punkte.get(t.name, 0) + p

    rangliste = sorted(punkte.items(), key=lambda x: x[1], reverse=True)
    return render_template('rangliste.html', rangliste=rangliste)

# =======================
# Routen: Admin
# =======================
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form['password']
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash("Falsches Passwort!", "error")
    return render_template('admin_login.html')

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    spiele = Spiel.query.all()
    return render_template('admin.html', spiele=spiele)

@app.route('/admin/edit/<int:spiel_id>', methods=['POST'])
def edit_spiel(spiel_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    spiel = Spiel.query.get_or_404(spiel_id)
    spiel.team1 = request.form['team1']
    spiel.team2 = request.form['team2']
    spiel.erg_team1 = int(request.form['erg_team1'])
    spiel.erg_team2 = int(request.form['erg_team2'])
    db.session.commit()
    flash("Spiel aktualisiert!", "success")
    return redirect(url_for('admin_panel'))

@app.route('/admin/add', methods=['POST'])
def add_spiel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    team1 = request.form['team1']
    team2 = request.form['team2']
    erg_team1 = int(request.form['erg_team1'])
    erg_team2 = int(request.form['erg_team2'])

    neues_spiel = Spiel(team1=team1, team2=team2, erg_team1=erg_team1, erg_team2=erg_team2)
    db.session.add(neues_spiel)
    db.session.commit()
    flash("Neues Spiel hinzugefügt!", "success")
    return redirect(url_for('admin_panel'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

# =======================
# App starten
# =======================
if __name__ == '__main__':
    app.run(debug=True)