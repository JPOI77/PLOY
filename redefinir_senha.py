from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
from db_config import get_db_connection
from dotenv import load_dotenv
import os
from criptobcrypt import hash_senha

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

@app.route('/redefinir-senha/<token>', methods=['GET', 'POST'])
def redefinir_senha(token):
    conexao = get_db_connection()
    with conexao.cursor() as cursor:
        cursor.execute("SELECT * FROM reset_tokens WHERE token = %s", (token,))
        dados_token = cursor.fetchone()
        print("Estou fazendo a conexão com o banco")
        if not dados_token or datetime.now() > dados_token['expiracao']:
            print('Token inválido ou expirado.')

            if request.method == 'POST':
                cursor.execute("DELETE FROM reset_tokens WHERE token = %s", (token,))
                conexao.commit()
                
                return redirect(url_for('homepage'))

        if request.method == 'POST':
            nova_senha = hash_senha(request.form['nova_senha'])

            cursor.execute("UPDATE usuarios SET senha = %s WHERE id = %s",
                           (nova_senha, dados_token['user_id']))
            cursor.execute("DELETE FROM reset_tokens WHERE token = %s", (token,))
            conexao.commit()

            print('Senha redefinida com sucesso! Faça login novamente.')
            return redirect(url_for('login'))

    conexao.close()
    return render_template('redefinir-senha.html')