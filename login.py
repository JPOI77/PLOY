
from flask import Flask, render_template, request, redirect, url_for, g

import pymysql.cursors

app = Flask(__name__)
app.secret_key = "Sasuke321!"

db_config = { 
    "host": "localhost",
    "user": "PLOY",
    "password": "Naruto123!",
    "database": "PLOY"
}

def get_db_connection():
    return pymysql.connect(
        host = db_config["host"],
        user = db_config["user"],
        password= db_config["password"],
        database= db_config["database"],
        cursorclass = pymysql.cursors.DictCursor
    )

def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

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




