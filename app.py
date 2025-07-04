from flask import Flask, request, jsonify, render_template, redirect, session, url_for
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.secret_key = "chave-secreta-simples"  # Troque isso por algo mais seguro em produção


# Banco de dados
def init_db():
    with sqlite3.connect('vendas.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS vendas (
                        id TEXT,
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


@app.route('/')
def login_page():
    return render_template("login.html")


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    id_digitado = data.get('id', '').strip()
    if 5 <= len(id_digitado) <= 20:
        session['id'] = id_digitado
        return '', 200
    return 'ID inválido', 401


@app.route('/logout')
def logout():
    session.pop('id', None)
    return redirect(url_for('login_page'))


@app.route('/painel')
def painel():
    if 'id' not in session:
        return redirect('/')
    return render_template("index.html")


@app.route('/usuario')
def usuario():
    if 'id' not in session:
        return jsonify({"id": None})
    return jsonify({"id": session['id']})


@app.route('/salvar', methods=['POST'])
def salvar():
    if 'id' not in session or session['id'] in ["Confiautomaster", "Acessorestrito"]:
        return 'Acesso negado', 403

    dados = request.form
    id_usuario = session['id']
    telefone = dados['telefone']

    with sqlite3.connect('vendas.db') as conn:
        c = conn.cursor()
        c.execute("DELETE FROM vendas WHERE telefone = ? AND id = ?", (telefone, id_usuario))

        c.execute('''INSERT INTO vendas (
                        id, cliente, telefone, veiculo, placa, fipe, mensalidade, desconto,
                        participacao, descTexto, obs, data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (id_usuario,
                   dados['cliente'],
                   telefone,
                   dados.get('veiculo', ''),
                   dados.get('placa', ''),
                   dados.get('fipe', 0),
                   dados.get('mensalidade', 0),
                   dados.get('desconto', 0),
                   dados.get('participacao', 0),
                   dados.get('descTexto', ''),
                   dados.get('obs', ''),
                   datetime.now().strftime('%d/%m/%Y %H:%M')))
        conn.commit()
    return 'OK'


@app.route('/vendas')
def listar_vendas():
    if 'id' not in session:
        return jsonify([])

    id_atual = session['id']

    with sqlite3.connect('vendas.db') as conn:
        c = conn.cursor()
        if id_atual in ["Confiautomaster", "Acessorestrito"]:
            c.execute("SELECT cliente, telefone, veiculo, placa, fipe, mensalidade, desconto, participacao, descTexto, obs, data FROM vendas ORDER BY data DESC")
        else:
            c.execute("SELECT cliente, telefone, veiculo, placa, fipe, mensalidade, desconto, participacao, descTexto, obs, data FROM vendas WHERE id = ? ORDER BY data DESC", (id_atual,))
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
    if 'id' not in session or session['id'] in ["Confiautomaster", "Acessorestrito"]:
        return 'Acesso negado', 403

    placa = request.args.get('placa')
    data = request.args.get('data')
    id_usuario = session['id']

    with sqlite3.connect('vendas.db') as conn:
        c = conn.cursor()
        c.execute("DELETE FROM vendas WHERE placa = ? AND data = ? AND id = ?", (placa, data, id_usuario))
        conn.commit()
    return 'Excluído'


if __name__ == '__main__':
    init_db()
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
