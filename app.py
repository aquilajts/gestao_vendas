from flask import Flask, request, jsonify, render_template_string, redirect, session
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'
DATABASE = 'vendas_atualizado.db'

MASTER_IDS = ['master123', 'admin123', 'trindade123']

HTML = open("templates/index.html", encoding="utf-8").read()


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def login():
    return render_template_string(open("templates/login.html", encoding="utf-8").read())


@app.route('/login', methods=['POST'])
def realizar_login():
    data = request.get_json()
    user_id = data.get('id')
    if user_id and 5 <= len(user_id) <= 20:
        session['usuario_id'] = user_id
        return '', 200
    return 'ID inválido', 400


@app.route('/painel')
def painel():
    if 'usuario_id' not in session:
        return redirect('/')

    usuario_id = session['usuario_id']
    conn = get_db_connection()
    cur = conn.cursor()

    if usuario_id in MASTER_IDS:
        cur.execute("SELECT * FROM vendas ORDER BY data DESC")
    else:
        cur.execute("SELECT * FROM vendas WHERE usuario_id = ? ORDER BY data DESC", (usuario_id,))

    vendas = cur.fetchall()
    conn.close()

    return render_template_string(HTML, vendas=vendas, usuario_id=usuario_id, master=usuario_id in MASTER_IDS)


@app.route('/salvar', methods=['POST'])
def salvar():
    if 'usuario_id' not in session:
        return 'Não autorizado', 403

    data = request.get_json()
    venda = (
        datetime.now().strftime('%d/%m/%Y %H:%M'),
        data.get('cliente'),
        data.get('telefone'),
        data.get('veiculo'),
        data.get('placa'),
        data.get('fipe'),
        data.get('mensalidade_original'),
        data.get('mensalidade_desconto'),
        data.get('participacao'),
        data.get('desconto'),
        data.get('observacoes'),
        session['usuario_id']
    )

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO vendas (data, cliente, telefone, veiculo, placa, fipe, mensalidade_original, mensalidade_desconto, participacao, desconto, observacoes, usuario_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, venda)
    conn.commit()
    conn.close()

    return '', 200


@app.route('/excluir', methods=['POST'])
def excluir():
    if 'usuario_id' not in session:
        return 'Não autorizado', 403

    venda_id = request.get_json().get('id')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM vendas WHERE id = ?", (venda_id,))
    conn.commit()
    conn.close()
    return '', 200


@app.route('/editar', methods=['POST'])
def editar():
    if 'usuario_id' not in session:
        return 'Não autorizado', 403

    data = request.get_json()
    venda_id = data.get('id')

    campos = [
        'cliente', 'telefone', 'veiculo', 'placa', 'fipe',
        'mensalidade_original', 'mensalidade_desconto', 'participacao', 'desconto', 'observacoes'
    ]
    valores = [data.get(campo) for campo in campos]

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"""
        UPDATE vendas SET
            cliente = ?, telefone = ?, veiculo = ?, placa = ?, fipe = ?,
            mensalidade_original = ?, mensalidade_desconto = ?,
            participacao = ?, desconto = ?, observacoes = ?
        WHERE id = ?
    """, valores + [venda_id])

    conn.commit()
    conn.close()
    return '', 200


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
