from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Banco de dados
def init_db():
    with sqlite3.connect('vendas.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS vendas (
                        cliente TEXT,
                        telefone TEXT UNIQUE,
                        veiculo TEXT,
                        placa TEXT,
                        fipe REAL,
                        mensalidade REAL,
                        desconto REAL,
                        participacao REAL,
                        descTexto TEXT,
                        obs TEXT,
                        data TEXT
                    )''')
        conn.commit()

@app.route('/salvar', methods=['POST'])
def salvar():
    dados = request.form
    cliente = dados['cliente']
    telefone = dados['telefone']
    veiculo = dados.get('veiculo', '')
    placa = dados.get('placa', '')
    fipe = dados.get('fipe', 0)
    mensalidade = dados.get('mensalidade', 0)
    desconto = dados.get('desconto', 0)
    participacao = dados.get('participacao', 0)
    descTexto = dados.get('descTexto', '')
    obs = dados.get('obs', '')

    data = datetime.now().strftime('%d/%m/%Y %H:%M')

    with sqlite3.connect('vendas.db') as conn:
        c = conn.cursor()
        # remove venda antiga com mesmo telefone
        c.execute("DELETE FROM vendas WHERE telefone = ?", (telefone,))
        c.execute('''INSERT INTO vendas (
                        cliente, telefone, veiculo, placa, fipe, mensalidade, desconto, participacao, descTexto, obs, data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (cliente, telefone, veiculo, placa, fipe, mensalidade, desconto, participacao, descTexto, obs, data))
        conn.commit()

    return 'OK'

@app.route('/vendas')
def listar_vendas():
    with sqlite3.connect('vendas.db') as conn:
        c = conn.cursor()
        c.execute("SELECT cliente, telefone, veiculo, placa, fipe, mensalidade, desconto, participacao, descTexto, obs, data FROM vendas ORDER BY data DESC")
        vendas = c.fetchall()
    return jsonify([{
        'cliente': v[0],
        'telefone': v[1],
        'veiculo': v[2],
        'placa': v[3],
        'fipe': v[4],
        'mensalidade': v[5],
        'desconto': v[6],
        'participacao': v[7],
        'descTexto': v[8],
        'obs': v[9],
        'data': v[10]
    } for v in vendas])

@app.route('/excluir', methods=['DELETE'])
def excluir():
    placa = request.args.get('placa')
    data = request.args.get('data')
    with sqlite3.connect('vendas.db') as conn:
        c = conn.cursor()
        c.execute("DELETE FROM vendas WHERE placa = ? AND data = ?", (placa, data))
        conn.commit()
    return 'Excluído'

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
