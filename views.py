from flask import render_template, request, redirect, url_for, flash, session   
from form_red_senha import enviar_email, esqueci_senha
from cadastro import inserir_usuario, get_db_connection
from login import autenticar_usuario
from redefinir_senha import redefinir_senha
from publicar_servico import publicar_servico
from db_config import get_db_connection

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
    
    @app.route('/chat/<int:id_servico>/<int:id_destinatario>', methods=['GET', 'POST'])
    def chat(id_servico, id_destinatario):
        conn = get_db_connection()
        cursor = conn.cursor()
        id_remetente = session.get('usuario_id')
        if "usuario_id" not in session:
            return redirect(url_for("login")), flash("Você precisa estar logado para utilizar o chat!")
        
        if id_remetente == id_destinatario:
            return redirect(url_for("homepage"))

        if request.method == 'POST':
            conteudo = request.form['mensagem']
            if conteudo.strip():
             cursor.execute('''
                    INSERT INTO mensagens (id_remetente, id_destinatario, id_servico, conteudo)
                    VALUES (%s, %s, %s, %s)
                ''', (id_remetente, id_destinatario, id_servico, conteudo))
            conn.commit()
            return redirect(url_for('chat', id_servico=id_servico, id_destinatario=id_destinatario))

    # Carregar mensagens do chat atual
        cursor.execute('''
            SELECT * FROM mensagens 
            WHERE id_servico = %s AND (
                (id_remetente = %s AND id_destinatario = %s)
                OR
                (id_remetente = %s AND id_destinatario = %s)
            )
       
            ORDER BY data_envio ASC
        ''', (id_servico, id_remetente, id_destinatario, id_destinatario, id_remetente))
        mensagens = cursor.fetchall()

        return render_template('chat.html', mensagens=mensagens, id_servico=id_servico, id_destinatario=id_destinatario)

    @app.route('/meus-servicos')
    def meus_servicos():
        if "usuario_id" not in session:
           flash("Você precisa estar logado para acessar esta página.", "warning")
           return redirect(url_for("login"))

        id_usuario = session["usuario_id"]
        conn = get_db_connection()
        cursor = conn.cursor()

    # Buscar serviços publicados por este usuário
        cursor.execute('''
            SELECT s.id, s.titulo, s.valor, s.localizacao, s.imagem
            FROM servicos s
            WHERE s.id_usuario = %s
            ''', (id_usuario,))
        servicos = cursor.fetchall()

    # Buscar conversas iniciadas para os serviços desse usuário
        cursor.execute('''
            SELECT DISTINCT
            m.id_servico,
            s.titulo AS servico_titulo,
            CASE 
            WHEN m.id_remetente = %s THEN m.id_destinatario
            ELSE m.id_remetente
            END AS id_outro_usuario,
            u.nome AS nome_outro_usuario,
            MAX(m.data_envio) AS ultima_mensagem
            FROM mensagens m
            JOIN servicos s ON m.id_servico = s.id
            JOIN usuarios u ON u.id = CASE 
                                    WHEN m.id_remetente = %s THEN m.id_destinatario
                                    ELSE m.id_remetente
                                  END
            WHERE m.id_remetente = %s OR m.id_destinatario = %s
            GROUP BY m.id_servico, id_outro_usuario, u.nome, s.titulo
            ORDER BY ultima_mensagem DESC
        ''', (id_usuario, id_usuario, id_usuario, id_usuario))
        chats = cursor.fetchall()


        conn.close()

        return render_template('meus_servicos.html', servicos=servicos, chats=chats)
