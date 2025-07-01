from flask import Flask, render_template, request, jsonify
from datetime import datetime
import sqlite3

app = Flask(__name__)

# Banco de dados
def init_db():
    conn = sqlite3.connect('vendas.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    )''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/salvar', methods=['POST'])
def salvar():
    dados = request.form
    conn = sqlite3.connect('vendas.db')
    c = conn.cursor()
    c.execute('INSERT INTO vendas (data, cliente, telefone, veiculo, placa, fipe, mensalidade, desconto, participacao, descTexto, obs) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
              (datetime.now().strftime('%d/%m/%Y %H:%M'),
               dados['cliente'], dados['telefone'], dados['veiculo'], dados['placa'],
               dados['fipe'], dados['mensalidade'], dados['desconto'], dados['participacao'],
               dados['descTexto'], dados['obs']))
    conn.commit()
    conn.close()
    return ('', 204)

@app.route('/vendas')
def vendas():
    conn = sqlite3.connect('vendas.db')
    c = conn.cursor()
    c.execute('SELECT data, cliente, telefone, veiculo, placa, fipe, mensalidade, desconto, participacao, descTexto, obs FROM vendas ORDER BY id DESC')
    rows = c.fetchall()
    conn.close()
    vendas = [dict(zip(['data','cliente','telefone','veiculo','placa','fipe','mensalidade','desconto','participacao','descTexto','obs'], r)) for r in rows]
    return jsonify(vendas)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
