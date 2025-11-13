from flask import Flask, request, redirect, render_template,url_for, session
import os
from werkzeug.utils import secure_filename
from db_config import get_db_connection
import pymysql

# Configurações de upload
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB limit

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH




# Pasta onde as imagens serão salvas
UPLOAD_FOLDER = 'static/imagens'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configurações de upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_MIME_TYPE = {'image/png', 'image/jpg', 'image/jpeg', 'image/gif'}


def allowed_file(filename, mimetype):

    if mimetype not in ALLOWED_MIME_TYPE:
        return False
    
    if not filename:
        return False
    
    if len(filename) > 255:  # Prevent too long filenames
        return False
    
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route("/publicar-servico", methods=["GET", "POST"])
def publicar_servico():
   if "usuario_id" not in session:
       print("Você precisa estar logado para publicar um serviço")
       return redirect("/login")

   if request.method == "POST":
        id_usuario = session["usuario_id"]
        titulo = request.form.get("titulo")
        dias = request.form.get("dias")
        horarios = request.form.get("horarios")
        tipoValor = request.form.get("tipagem")
        valorHora = request.form.get("horaValue")
        valorDia = request.form.get("diaValue")
        descricao = request.form.get("descricao")
        atendimento = request.form.get("atendimento")
        endereco = request.form.get("endereco")
        valor = ""

        print(id_usuario)
        if valorHora:
            valorHora.replace(",", ".")
        elif valorDia:
            valorDia.replace(",", ".")

        # Define o valor da localização caso seja atendimento a domicílio
        if atendimento == "domicilio":
            localizacao = "Atendimento a domicílio"
        else:
            localizacao = endereco if endereco else "Não informado"

        #Define valor com base no que foi selecionado pelo usuário
        if tipoValor == "valorCombinar":
            valor = "Valor a combinar!"
        elif tipoValor == "valorHora":
            valor = valorHora + "/h"
        elif tipoValor == "valorDia":
            valor = valorDia + "/d"

        # Processar a imagem
        imagem = request.files.get("imagens")
        nome_arquivo = None

        if imagem and allowed_file(imagem.filename, imagem.mimetype):
            filename = secure_filename(imagem.filename)
            caminho_imagem = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            imagem.save(caminho_imagem)
            nome_arquivo = filename
            print(nome_arquivo)

        # Inserir no banco
        try:
             conexao = get_db_connection();
             with conexao.cursor() as cursor:
                 sql = """
                    INSERT INTO servicos (id_usuario, titulo, dias, horarios, valor, descricao, imagem, localizacao)
                    VALUES (%s , %s, %s, %s, %s, %s, %s, %s)
                    """ 
                 cursor.execute(sql, (id_usuario, titulo, dias, horarios, valor, descricao, nome_arquivo, localizacao))
                 conexao.commit()
              
        except Exception as e:
            print("Erro:", e)
        
        return redirect(url_for("homepage"))

   return render_template("formulario_servicos.html")


if __name__ == "__main__":
    app.run(debug=True)