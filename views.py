from flask import render_template, request, redirect, url_for, flash, session   
from form_red_senha import enviar_email, esqueci_senha
from cadastro import inserir_usuario, get_db_connection
from login import autenticar_usuario
from redefinir_senha import redefinir_senha
from publicar_servico import publicar_servico

def setup_routes(app):

    # PÁGINAS PRINCIPAIS
    @app.route('/')
    def homepage():
        conexao = get_db_connection()
        with conexao.cursor() as cursor:
            sql = """
                SELECT s.*, u.nome AS nome_usuario
                FROM servicos s
                JOIN usuarios u ON s.id_usuario = u.id
                ORDER BY s.id DESC
            """
            cursor.execute(sql)
            servicos = cursor.fetchall()
        conexao.close()
        return render_template('index.html', session = session, servicos=servicos)

    @app.route('/clientes')
    def clientes():
        return render_template('clientes.html')

    @app.route('/cadastro', methods=["GET", "POST"])
    def cadastro():
        return render_template("cadastro.html")
    
    @app.route('/esqueci-senha', methods=["GET", "POST"])
    def esqueciSenha():
        if request.method == "POST":
            return esqueci_senha()
        return render_template("esqueci-senha.html")
    
    @app.route('/redefinir-senha/<token>', methods=["GET", "POST"])
    def redefinirSenha(token):
        if request.method == "POST":
            print("Metodo post encontrado!")
            return redefinir_senha(token)
        return render_template("redefinir-senha.html")

    # LOGIN / REGISTRO
    @app.route('/login', methods=["GET", "POST"])
    def login():
        if session.get('logged_in'):
            flash(f"Você já está logado, {session.get('usuario_nome')}.", "info")
            return redirect(url_for('homepage'))

        if request.method == "POST":
            usuario = autenticar_usuario()
            if usuario:
                session['logged_in'] = True
                session['usuario_id'] = usuario['id']
                session['usuario_nome'] = usuario['nome']
                flash(f"Login efetuado com sucesso! Bem Vindo, {session['usuario_nome']}", "success")
                return redirect(url_for('homepage'))
            else:
                flash(f"E-mail ou senha incorretas. Tente novamente.", "danger")
                
        return render_template("login.html")
    
    @app.route('/register', methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            flash("Conta criada com sucesso!", "success")
            return inserir_usuario()
        return redirect(url_for("register"))

    # FORMULÁRIO
    @app.route('/publicar-servico', methods=['GET', 'POST'])
    def formulario():
        if request.method == 'POST':

            return publicar_servico()
        return render_template('formulario_servicos.html')
    
    @app.route("/logout")
    def logout():
        session.pop('logged_in', None)
        session.pop('usuario_id', None)
        session.pop('usuario_nome', None)
        flash("Você foi desconectado com sucesso!", "info")
        return redirect(url_for('homepage'))
