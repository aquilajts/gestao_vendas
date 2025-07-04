import os
import sqlite3
from flask import Flask, request, jsonify, render_template, redirect, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = "minha_chave_secreta"

# Caminho absoluto para o banco
DATABASE = os.path.join(os.path.dirname(__file__), 'vendas.db')

# IDs mestre
IDS_MESTRE = {"master123", "adm001", "gerente01"}

def conectar():
    return sqlite3.connect(DATABASE)

def criar_tabela():
    with conectar() as con:
        con.execute('''
            CREATE TABLE IF NOT EXISTS vendas (
                id TEXT,
                data TEXT,
                cliente TEXT,
                telefone TEXT,
                veiculo TEXT,
                placa TEXT,
                fipe REAL,
                mensalidade REAL,
                desconto REAL,
                participacao REAL,
                descTexto TEXT,
                obs TEXT
            )
        ''')

@app.route("/")
def login_page():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    id_usuario = data.get("id", "").strip()
    if not id_usuario:
        return "ID inválido", 400

    session["id"] = id_usuario
    return jsonify({"ok": True})

@app.route("/painel")
def painel():
    if "id" not in session:
        return redirect("/")
    return render_template("index.html")

@app.route("/id")
def get_id():
    id_usuario = session.get("id", "")
    return jsonify({"id": id_usuario, "isMaster": id_usuario in IDS_MESTRE})

@app.route("/vendas")
def listar_vendas():
    id_usuario = session.get("id", "")
    is_master = id_usuario in IDS_MESTRE

    with conectar() as con:
        cursor = con.cursor()
        if is_master:
            cursor.execute("SELECT * FROM vendas ORDER BY rowid DESC")
        else:
            cursor.execute("SELECT * FROM vendas WHERE id = ? ORDER BY rowid DESC", (id_usuario,))
        dados = cursor.fetchall()

    vendas = []
    for linha in dados:
        vendas.append({
            "id": linha[0],
            "data": linha[1],
            "cliente": linha[2],
            "telefone": linha[3],
            "veiculo": linha[4],
            "placa": linha[5],
            "fipe": linha[6],
            "mensalidade": linha[7],
            "desconto": linha[8],
            "participacao": linha[9],
            "descTexto": linha[10],
            "obs": linha[11],
        })
    return jsonify(vendas)

@app.route("/salvar", methods=["POST"])
def salvar_venda():
    if "id" not in session:
        return "Não autorizado", 403

    id_usuario = session["id"]
    data = datetime.now().strftime("%d/%m/%Y %H:%M")

    campos = [
        "cliente", "telefone", "veiculo", "placa", "fipe",
        "mensalidade", "desconto", "participacao", "descTexto", "obs"
    ]
    valores = [request.form.get(campo, "").strip() for campo in campos]

    with conectar() as con:
        con.execute("""
            INSERT INTO vendas (
                id, data, cliente, telefone, veiculo, placa, fipe,
                mensalidade, desconto, participacao, descTexto, obs
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_usuario, data, *valores))

    return redirect("/painel")

@app.route("/excluir", methods=["DELETE"])
def excluir():
    if "id" not in session:
        return "Não autorizado", 403

    id_usuario = session["id"]
    placa = request.args.get("placa", "").strip()
    data = request.args.get("data", "").strip()

    if not placa or not data:
        return "Parâmetros inválidos", 400

    with conectar() as con:
        if id_usuario in IDS_MESTRE:
            con.execute("DELETE FROM vendas WHERE placa = ? AND data = ?", (placa, data))
        else:
            con.execute("DELETE FROM vendas WHERE id = ? AND placa = ? AND data = ?", (id_usuario, placa, data))

    return "Excluído com sucesso", 200

if __name__ == "__main__":
    criar_tabela()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
