import sqlite3
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS adherents (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 code TEXT UNIQUE, 
                 nom TEXT, 
                 prenom TEXT, 
                 adresse TEXT, 
                 tel TEXT, 
                 type TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS documents (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 titre TEXT, 
                 auteur TEXT, 
                 type TEXT, 
                 disponible BOOLEAN DEFAULT 1)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS emprunts (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 adherent_id INTEGER,
                 document_id INTEGER,
                 date_emprunt TEXT DEFAULT CURRENT_TIMESTAMP,
                 date_retour TEXT,
                 status TEXT DEFAULT 'en_cours',
                 FOREIGN KEY (adherent_id) REFERENCES adherents(id),
                 FOREIGN KEY (document_id) REFERENCES documents(id))''')
    
    conn.commit()
    conn.close()

@app.route('/adherents', methods=['GET', 'POST'])
def handle_adherents():
    conn = get_db_connection()
    c = conn.cursor()
    
    if request.method == 'POST':
        data = request.get_json()
        try:
            c.execute('''INSERT INTO adherents (code, nom, prenom, adresse, tel, type)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (data['code'], data['nom'], data['prenom'], 
                       data['adresse'], data['tel'], data['type']))
            conn.commit()
            return jsonify({"message": "Adherent ajouté avec succès"}), 201
        except sqlite3.IntegrityError:
            return jsonify({"error": "Code adhérent déjà existant"}), 400
    
    c.execute('SELECT * FROM adherents')
    adherents = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(adherents)

@app.route('/documents', methods=['GET', 'POST'])
def handle_documents():
    conn = get_db_connection()
    c = conn.cursor()
    
    if request.method == 'POST':
        data = request.get_json()
        c.execute('''INSERT INTO documents (titre, auteur, type, disponible)
                     VALUES (?, ?, ?, ?)''',
                  (data['titre'], data['auteur'], data['type'], 1))
        conn.commit()
        return jsonify({"message": "Document ajouté avec succès"}), 201
    
    c.execute('SELECT * FROM documents')
    documents = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(documents)

@app.route('/emprunts', methods=['GET', 'POST'])
def handle_emprunts():
    conn = get_db_connection()
    c = conn.cursor()
    
    if request.method == 'POST':
        data = request.get_json()
        c.execute('''INSERT INTO emprunts (adherent_id, document_id, date_retour, status)
                     VALUES (?, ?, ?, ?)''',
                  (data['adherent_id'], data['document_id'], data['date_retour'], 'en_cours'))
        c.execute('''UPDATE documents SET disponible = 0 WHERE id = ?''', (data['document_id'],))
        conn.commit()
        return jsonify({"message": "Emprunt enregistré avec succès"}), 201
    
    c.execute('''SELECT e.*, a.nom AS nom_adherent, a.prenom AS prenom_adherent, d.titre AS titre_document
                 FROM emprunts e
                 JOIN adherents a ON e.adherent_id = a.id
                 JOIN documents d ON e.document_id = d.id''')
    emprunts = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(emprunts)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
