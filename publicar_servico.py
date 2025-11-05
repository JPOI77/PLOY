from flask import Flask, request, redirect, render_template,url_for, session
import os
from werkzeug.utils import secure_filename
from cadastro import get_db_connection
import pymysql

app = Flask(__name__)



# Pasta onde as imagens serão salvas
UPLOAD_FOLDER = 'static/imagens'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Extensões permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    print("Teste da função de segurança!")
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
        valor = request.form.get("valor")
        descricao = request.form.get("descricao")
        atendimento = request.form.get("atendimento")
        endereco = request.form.get("endereco")

        print(id_usuario)
        if valor:
            valor.replace(",", ".")

        # Define o valor da localização
        if atendimento == "domicilio":
            localizacao = "Atendimento a domicílio"
        else:
            localizacao = endereco if endereco else "Não informado"

        # Processar a imagem
        imagem = request.files.get("imagens")
        nome_arquivo = None

        if imagem and allowed_file(imagem.filename):
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