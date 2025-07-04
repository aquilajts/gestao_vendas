from flask import Flask, request, jsonify, render_template, redirect, session
from flask_cors import CORS
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'chave-secreta'
CORS(app)

DB_PATH = 'vendas.db'
MASTERS = ['Confiautomaster', 'Acessorestrito']

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS vendas (
                id TEXT,
                cliente TEXT,
                telefone TEXT,
                veiculo TEXT,
                placa TEXT,
                fipe REAL,
                mensalidade REAL,
                desconto REAL,
                participacao REAL,
                descTexto TEXT,
                obs TEXT,
                data TEXT
            )
        ''')
        conn.commit()

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def fazer_login():
    id = request.json.get('id')
    if id and 5 <= len(id) <= 20:
        session['id'] = id
        return '', 200
    return 'ID inválido.', 401

@app.route('/painel')
def painel():
    if 'id' not in session:
        return redirect('/')
    return render_template('index.html')

@app.route('/salvar', methods=['POST'])
def salvar():
    if 'id' not in session:
        return 'Não autorizado', 401

    id_usuario = session['id']
    if id_usuario in MASTERS:
        return 'Masters não podem salvar', 403

    dados = request.form
    cliente = dados['cliente']
    telefone = dados['telefone']
    veiculo = dados.get('veiculo', '')
    placa = dados.get('placa', '')
    fipe = float(dados.get('fipe', 0))
    mensalidade = float(dados.get('mensalidade', 0))
    desconto = float(dados.get('desconto', 0))
    participacao = float(dados.get('participacao', 0))
    descTexto = dados.get('descTexto', '')
    obs = dados.get('obs', '')
    data = datetime.now().strftime('%d/%m/%Y %H:%M')

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM vendas WHERE telefone = ? AND id = ?", (telefone, id_usuario))
        c.execute('''
            INSERT INTO vendas (
                id, cliente, telefone, veiculo, placa, fipe,
                mensalidade, desconto, participacao,
                descTexto, obs, data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (id_usuario, cliente, telefone, veiculo, placa, fipe,
              mensalidade, desconto, participacao, descTexto, obs, data))
        conn.commit()

    return 'OK'

@app.route('/vendas')
def listar():
    if 'id' not in session:
        return jsonify([])

    id_usuario = session['id']
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        if id_usuario in MASTERS:
            c.execute("SELECT * FROM vendas ORDER BY data DESC")
        else:
            c.execute("SELECT * FROM vendas WHERE id = ? ORDER BY data DESC", (id_usuario,))
        vendas = c.fetchall()

    return jsonify([{
        'cliente': v[1],
        'telefone': v[2],
        'veiculo': v[3],
        'placa': v[4],
        'fipe': v[5],
        'mensalidade': v[6],
        'desconto': v[7],
        'participacao': v[8],
        'descTexto': v[9],
        'obs': v[10],
        'data': v[11],
        'id': v[0]
    } for v in vendas])

@app.route('/excluir', methods=['DELETE'])
def excluir():
    if 'id' not in session:
        return 'Não autorizado', 401

    id_usuario = session['id']
    if id_usuario in MASTERS:
        return 'Masters não podem excluir', 403

    placa = request.args.get('placa')
    data = request.args.get('data')
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM vendas WHERE id = ? AND placa = ? AND data = ?", (id_usuario, placa, data))
        conn.commit()
    return 'Excluído'

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
