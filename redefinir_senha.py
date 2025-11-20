from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
from db_config import get_db_connection
from dotenv import load_dotenv
import os
<<<<<<< HEAD
from criptobcrypt import hash_senha
=======
import re
>>>>>>> 6dc3728 (Exigência de requisitos para criação e redefinição de senhas(Segurança))

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

def validar_senha(senha):
     padrao = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{5,}$"
     return bool(re.match(padrao, senha))

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

            if not validar_senha(nova_senha):
                flash("A senha deve conter ao menos: 1 letra maiúscula, 1 minúscula, 1 número, 1 caractere especial e ter no mínimo 8 caracteres.")
                return render_template("redefinir-senha.html")

            cursor.execute("UPDATE usuarios SET senha = %s WHERE id = %s",
                           (nova_senha, dados_token['user_id']))
            cursor.execute("DELETE FROM reset_tokens WHERE token = %s", (token,))
            conexao.commit()

            print('Senha redefinida com sucesso! Faça login novamente.')
            return redirect(url_for('login'))

    conexao.close()
    return render_template('redefinir-senha.html')