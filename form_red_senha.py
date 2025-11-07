from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
import uuid
import smtplib
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from email.mime.text import MIMEText
#Import da função de conexão com o Banco de Dados
from db_config import get_db_connection

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")


# Configuração do e-mail 
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_REMETENTE = 'ploy.online.services@gmail.com'
EMAIL_SENHA = os.environ.get("EMAIL_PASSWORD")  # Senha de App do gmail

@app.route('/esqueci-senha', methods=['GET', 'POST'])
def esqueci_senha():
    if request.method == 'POST':
        email = request.form['email']

        conexao = get_db_connection()
        with conexao.cursor() as cursor:
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user:
                token = str(uuid.uuid4())
                expiracao = datetime.now() + timedelta(hours=1)
                cursor.execute(
                    "INSERT INTO reset_tokens (user_id, token, expiracao) VALUES (%s, %s, %s)",
                    (user['id'], token, expiracao)
                )
                conexao.commit()

                link = f'http://localhost:5002/redefinir-senha/{token}'
                enviar_email(email, link)
                flash('Um link de redefinição foi enviado ao seu e-mail.', 'info')
            else:
                print("E-mail não encontrado")
        conexao.close()

    return render_template('esqueci-senha.html')

def enviar_email(destinatario, link):
    msg = MIMEText(f"Clique no link para redefinir sua senha: {link}")
    msg['Subject'] = 'Recuperação de Senha'
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = destinatario

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_REMETENTE, EMAIL_SENHA)
        server.send_message(msg)

