import pymysql.cursors
from db_config import get_db_connection
from flask import Flask, render_template, request, redirect,url_for,g
from dotenv import load_dotenv
import os
from criptobcrypt import hash_senha

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

def inserir_usuario():
        print("REQUEST METHOD:", request.method)
        print("FORM DATA:", request.form)
        if request.method == 'POST':
            username = request.form.get('nome', '').strip()
            email = request.form.get('email', '').strip().lower()
            senha = hash_senha(request.form.get('senha', ''))

        # Validações básicas

        if len(senha) < 5:
            return redirect(url_for("register", message='Senha deve ter ao menos 5 caracteres.'))


        db = get_db_connection()
        try:
            with db.cursor() as cur:
                # Checa se o nome ou o email já existem no banco
                sql_check = "SELECT id FROM usuarios WHERE email=%s OR nome=%s LIMIT 1"
                cur.execute(sql_check, (email, username))
                existing = cur.fetchone()
                if existing:
                    return redirect(url_for("register", message='Usuário ou email já cadastrado.'))

                # Insere novo usuário ao banco de dados
                sql_insert = "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)"
                cur.execute(sql_insert, (username, email, senha))
                db.commit()

            return redirect(url_for('login'))
        
        except Exception as e:
            db.rollback()

            app.logger.exception("Erro ao inserir usuário")
            return redirect(url_for("register", message='Erro ao cadastrar. Tente novamente.'))
        else:
            return redirect(url_for("register"))
        
