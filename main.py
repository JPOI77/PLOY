from flask import Flask
from views import setup_routes  # importa as rotas
import pymysql  

app = Flask(__name__)
app.secret_key = "Sasuke321!"

# Registra todas as rotas
setup_routes(app)

if __name__ == '__main__':
    app.run(debug=True, port=5002)


