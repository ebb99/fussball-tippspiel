from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Beispielspiele
spiele = [
    {"id": 1, "team1": "Deutschland", "team2": "Frankreich", "ergebnis": (2, 1)},
    {"id": 2, "team1": "Spanien", "team2": "Italien", "ergebnis": (1, 1)},
    {"id": 3, "team1": "England", "team2": "Portugal", "ergebnis": (0, 2)}
]

# Tipps werden im Speicher gehalten (noch keine DB)
tipps = []

@app.route('/')
def index():
    return render_template('index.html', spiele=spiele)

@app.route('/tipp', methods=['POST'])
def tipp():
    name = request.form['name']
    spiel_id = int(request.form['spiel_id'])
    team1_tipp = int(request.form['team1'])
    team2_tipp = int(request.form['team2'])
    tipps.append({
        "name": name,
        "spiel_id": spiel_id,
        "tipp": (team1_tipp, team2_tipp)
    })
    return redirect(url_for('rangliste'))

@app.route('/rangliste')
def rangliste():
    # Punkteberechnung (1 Punkt richtige Tendenz, 3 Punkte genau richtig)
    punkte = {}
    for t in tipps:
        spiel = next((s for s in spiele if s["id"] == t["spiel_id"]), None)
        if not spiel:
            continue
        name = t["name"]
        tipp_t1, tipp_t2 = t["tipp"]
        erg_t1, erg_t2 = spiel["ergebnis"]

        if tipp_t1 == erg_t1 and tipp_t2 == erg_t2:
            p = 3
        elif (tipp_t1 - tipp_t2) * (erg_t1 - erg_t2) > 0:
            p = 1
        elif tipp_t1 == tipp_t2 and erg_t1 == erg_t2:
            p = 1
        else:
            p = 0

        punkte[name] = punkte.get(name, 0) + p

    rangliste = sorted(punkte.items(), key=lambda x: x[1], reverse=True)
    return render_template('rangliste.html', rangliste=rangliste)

if __name__ == '__main__':
    app.run(debug=True)
