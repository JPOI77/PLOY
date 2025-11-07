
from flask import Flask, render_template, request, redirect, url_for, g
import os
from dotenv import load_dotenv
import pymysql.cursors
from db_config import get_db_connection

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

def autenticar_usuario():
        print("REQUEST METHOD:", request.method)
        print("FORM DATA:", request.form)
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('password', '').strip()

        db = get_db_connection()
        
        
        try:
             with db.cursor() as cursor:
                  sql_checagem = "SELECT * FROM usuarios WHERE email = %s LIMIT 1"
                  cursor.execute(sql_checagem, (email,))
                  usuario = cursor.fetchone()

                  print("jujuba")
                  if usuario:
                    print("Seu email foi encontrado")
                    print(usuario['nome'])
                    print(usuario['senha'])
                    print(senha)
                    if senha == usuario['senha']:
                       print("deu certo<3")
                       return usuario
                    else:
                       print("senha incorreta")
                       return None
                  else:
                      print("seu email não existe :(")
        except Exception as e:
             import logging
             logging.exception("Database error while authenticating user")
             return None 
        finally:
            if db:
                db.close()




