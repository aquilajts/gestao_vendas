from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, session, url_for
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.secret_key = 'chave_super_secreta_para_sessao'

# Banco de dados
def init_db():
    with sqlite3.connect('vendas.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS vendas (
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
                        data TEXT,
                        usuario TEXT
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        usuario TEXT PRIMARY KEY,
                        senha TEXT
                    )''')
        # Inserir contas master se não existirem
        c.execute("INSERT OR IGNORE INTO usuarios (usuario, senha) VALUES (?, ?)", ("Masterconf", "Masterconf"))
        c.execute("INSERT OR IGNORE INTO usuarios (usuario, senha) VALUES (?, ?)", ("Confiauto", "Confiauto"))
        conn.commit()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']

        if len(usuario) < 3 or len(usuario) > 12 or len(senha) < 3 or len(senha) > 12:
            return 'Usuário e senha devem ter entre 3 e 12 caracteres'

        with sqlite3.connect('vendas.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario,))
            user = c.fetchone()
            if user:
                if user[1] == senha:
                    session['usuario'] = usuario
                    return redirect(url_for('index'))
                else:
                    return 'Senha incorreta'
            else:
                c.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (usuario, senha))
                conn.commit()
                session['usuario'] = usuario
                return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/index')
def index():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/salvar', methods=['POST'])
def salvar():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    dados = request.form
    cliente = dados['cliente']
    telefone = dados['telefone']
    veiculo = dados['veiculo']
    placa = dados['placa']
    fipe = dados['fipe']
    mensalidade = dados['mensalidade']
    desconto = dados['desconto']
    participacao = dados['participacao']
    descTexto = dados['descTexto']
    obs = dados['obs']
    usuario = session['usuario']

    data = datetime.now().strftime('%d/%m/%Y %H:%M')

    with sqlite3.connect('vendas.db') as conn:
        c = conn.cursor()
        if placa:
            c.execute("DELETE FROM vendas WHERE placa = ?", (placa,))
        c.execute('''INSERT INTO vendas (
                        cliente, telefone, veiculo, placa, fipe, mensalidade, desconto, participacao, descTexto, obs, data, usuario
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (cliente, telefone, veiculo, placa, fipe, mensalidade, desconto, participacao, descTexto, obs, data, usuario))
        conn.commit()

    return 'OK'

@app.route('/vendas')
def listar_vendas():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    usuario = session['usuario']
    with sqlite3.connect('vendas.db') as conn:
        c = conn.cursor()
        if usuario in ['Masterconf', 'Confiauto']:
            c.execute("SELECT cliente, telefone, veiculo, placa, fipe, mensalidade, desconto, participacao, descTexto, obs, data FROM vendas ORDER BY data DESC")
        else:
            c.execute("SELECT cliente, telefone, veiculo, placa, fipe, mensalidade, desconto, participacao, descTexto, obs, data FROM vendas WHERE usuario = ? ORDER BY data DESC", (usuario,))
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
    if 'usuario' not in session:
        return redirect(url_for('login'))

    placa = request.args.get('placa')
    data = request.args.get('data')
    with sqlite3.connect('vendas.db') as conn:
        c = conn.cursor()
        c.execute("DELETE FROM vendas WHERE placa = ? AND data = ?", (placa, data))
        conn.commit()
    return 'Excluído'

if __name__ == '__main__':
    init_db()
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
