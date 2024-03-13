from flask import Flask, render_template, request
from flask_paginate import Pagination
import mysql.connector
import base64
from datetime import date

banco = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "labhugo",
    database = "pokemon"
)
cursor = banco.cursor()

app = Flask(__name__)

PER_PAGE = 6

@app.route('/home') #Página Principal do site
def home():
    cursor.execute("SELECT nome, imagem FROM pokemon ORDER BY codigo DESC LIMIT 5;")
    resultados = cursor.fetchall()

    dados_pokemon = []
    for linha in resultados:
        nome_pokemon = linha[0]
        imagem_pokemon = linha[1]
        imagem_base64 = base64.b64encode(imagem_pokemon).decode('utf-8')

        pokemon = {"nome": nome_pokemon, "foto": imagem_base64}
        dados_pokemon.append(pokemon)

    return render_template("principal.html", pokemons=dados_pokemon)

@app.route('/cadastro', methods=['GET', 'POST']) #Cadastro de usuários do site
def cadastro():
    if request.method == 'POST':
        email = request.form['mail']
        nome = request.form['nome']
        senha = request.form['senha']
        nascimento = request.form['nascimento']

        cursor.execute(f"SELECT * FROM usuario WHERE email = '{email}';")
        linha = cursor.fetchone()

        if linha is not None: #Caso já exista um valor com o mesmo e-mail
            return render_template("negativa1.html", mensagem="Parece que já existe um usuário com essas credenciais. Confira seus dados e tente novamente!")
        else:
            cursor.execute(f"INSERT INTO usuario VALUES (%s, %s, %s, %s);", (email, nome, nascimento, senha))
            banco.commit()
            return render_template("positiva1.html", mensagem="Obrigado por se cadastrar na plataforma! Sinta-se a vontade para explorar nossos pokemons cadastrados e cadastrar um pokemon também.")    
    else:
        return render_template("cadastrar.html")

@app.route('/login', methods=['GET', 'POST']) #Exibição dos dados dos usuários do site
def dados():
    if request.method == 'POST':
        mail_pesquisa = request.form['mail']
        senha_pesquisa = request.form['senha']
        cursor.execute(f"SELECT nome, email, nascimento FROM usuario WHERE email = '{mail_pesquisa}' AND senha = '{senha_pesquisa}';")

        linha = cursor.fetchone()

        if linha is not None:
            nomeee = linha[0]
            mailll = linha[1]
            nascimentooo = linha[2]

            if isinstance(nascimentooo, date):
                nascimentooo = nascimentooo.strftime('%Y-%m-%d')

            datas = nascimentooo.split('-')
            ano = datas[0]
            mes = datas[1]
            dia = datas[2]

            data = dia + '/' + mes + '/' + ano

            return render_template("exibicao.html", nome2=nomeee, mail2=mailll, nascimento2=data)            
        else:
            return render_template("negativa1.html", mensagem="Parece que não existe um usuário com essas credenciais. Confira seus dados e tente novamente!")
    else:
        return render_template("login.html")

@app.route('/atualizar', methods=['GET', 'POST']) #Página de atualização de senhas de usuários do site
def atualizar():
    if request.method == 'POST':
        email_atualizar = request.form['mail']
        senha_atual = request.form['senha_atual']
        senha_nova = request.form['nova_senha']

        cursor.execute(f"SELECT senha FROM usuario WHERE email = '{email_atualizar}';")

        linha = cursor.fetchone()

        if linha is not None: #Caso o usuário com o devido e-mail já exista
            if linha[0] == senha_atual:
                cursor.execute(f"UPDATE usuario SET senha = %s WHERE email = %s;", (senha_nova, email_atualizar))
                banco.commit()
                return render_template("positiva1.html", mensagem="Você acabou de atualizar sua senha! Continue explorando nossa plataforma e divirta-se.")
            else:
                return render_template("negativa1.html", mensagem="Parece que sua senha está incorreta. Confira seus dados e tente novamente!")
        else:
            return render_template("negativa1.html", mensagem="Parece que não existe um usuário com essas credenciais. Confira seus dados e tente novamente!")
    else:
        return render_template("atualizacao.html")
    
temp_nome = None
temp_tipo = None
temp_raridade = None
temp_foto = None
    
@app.route('/inserir', methods=['GET', 'POST']) #Página onde o usuário pode inserir um pokemon
def inserir():
    global temp_nome, temp_tipo, temp_raridade, temp_foto

    if request.method == 'POST':
        nome = request.form['nome']
        tipo = request.form['tipo']
        raridade = request.form['raridade']
        foto = request.files['imagem']

        imagem = foto.read() #Converter a imagem em binário

        cursor.execute(f"SELECT * FROM pokemon WHERE nome = '{nome}';")
        linha = cursor.fetchone()

        if linha is not None: #Caso o pokemom com as caracteristicas acima já exista
            return render_template("negativa1.html", mensagem="Parece que já existe um pokemon com essas características. Confira seus dados e tente novamente!")
        else: #Armazenar as informações nas variáveis globais
            temp_nome = nome
            temp_tipo = tipo
            temp_raridade = raridade
            temp_foto = imagem
            return render_template("validacao.html")
    else:
        return render_template("inserir.html")
    
@app.route('/validar', methods=['GET', 'POST']) #Página de confirmação de dados
def validar_dados():
    global temp_nome, temp_tipo, temp_raridade, temp_foto

    if request.method == 'POST':
        mail_pesquisa = request.form['mail']
        senha_pesquisa = request.form['senha']

        nome = temp_nome
        tipo = temp_tipo
        raridade = temp_raridade
        imagem = temp_foto

        cursor.execute(f"SELECT email, senha FROM usuario WHERE email = '{mail_pesquisa}';")

        linha = cursor.fetchone()

        if linha is not None: #Caso o usuário com o devido e-mail já exista
            senha = linha[1]
            if (senha_pesquisa == senha):
                cursor.execute(f"INSERT INTO pokemon(nome, tipo, raridade, imagem) VALUES (%s, %s, %s, %s);", (nome, tipo, raridade, imagem))
                cursor.execute(f"SELECT codigo FROM pokemon WHERE nome = '{nome}';")
                linha = cursor.fetchone()
                cod = linha[0]
                cursor.execute(f"INSERT INTO cadastra VALUES (%s, %s);", (cod, mail_pesquisa))
                banco.commit()
                return render_template("positiva1.html", mensagem="Obrigado por nos mostrar outro pokemon! Sinta-se a vontade para explorar nossos pokemons cadastrados e cadastrar outro pokemon também.")
            else:
                return render_template("negativa1.html", mensagem="Parece que sua senha está incorreta. Confira seus dados e tente novamente!")
        else:
            return render_template("negativa1.html", mensagem="Parece que não existe um usuário com essas credenciais. Confira seus dados e tente novamente!")
    else:
        return render_template("validacao.html")
    
@app.route('/pokemon', methods=['GET', 'POST']) #Página onde serão exibidas as informações do pokemons pesquisado no form
def mostrar_pokemon():
    if request.method == 'POST':
        nomepokemon = request.form['search']
        cursor.execute(f"SELECT nome, tipo, raridade, imagem FROM pokemon WHERE nome = '{nomepokemon}';")

        linha = cursor.fetchone()

        if linha:
            nomepoke = linha[0]
            tipopoke = linha[1]
            raridadepoke = linha[2]
            fotopoke = linha[3]
            fotopoke2 = base64.b64encode(fotopoke).decode('utf-8') #Converter os dados binários em uma imagem

            return render_template("mostrarpokemon.html", nome2=nomepoke, tipo2=tipopoke, raridade2=raridadepoke, foto2 = fotopoke2)
        else:
            return render_template("negativa1.html", mensagem="Parece que não existe um pokemon com essas características. Confira seus dados e tente novamente!")
    else:
        return render_template("mostrarpokemon.html", nome2="", tipo2="", raridade2="", foto2="")
    
@app.route('/pokemon/<nome>', methods=['GET']) #Página onde serão exibidas as informações do pokemons pesquisado nos cards
def mostrar_pokemons(nome):
    cursor.execute(f"SELECT nome, tipo, raridade, imagem FROM pokemon WHERE nome = '{nome}';")

    linha = cursor.fetchone()

    if linha:
        nomepoke = linha[0]
        tipopoke = linha[1]
        raridadepoke = linha[2]
        fotopoke = linha[3]
        fotopoke2 = base64.b64encode(fotopoke).decode('utf-8') #Converter os dados binários em uma imagem

        return render_template("mostrarpokemon.html", nome2=nomepoke, tipo2=tipopoke, raridade2=raridadepoke, foto2 = fotopoke2)
    else:
        return render_template("negativa1.html", mensagem="Parece que não existe um pokemon com essas características. Confira seus dados e tente novamente!")
    
@app.route('/pokemons', methods=['GET', 'POST']) #Tela de exibição de pokemons(Com filtros)
def pokemons():
    if request.method == 'POST':
        tipopokemon = request.form['tipo']
        raridadepokemon = request.form['raridade']

        if tipopokemon == "Todos" and raridadepokemon == "Todos":
            page = request.args.get('page', 1, type=int) # Página atual (por padrão, será a primeira página)

            offset = (page - 1) * PER_PAGE # Obtém os itens da página atual
            cursor.execute(f"SELECT nome, imagem FROM pokemon LIMIT {PER_PAGE} OFFSET {offset};")
            resultados = cursor.fetchall()

            dados_pokemon = []
            for linha in resultados:
                nome_pokemon = linha[0]
                imagem_pokemon = linha[1]
                imagem_base64 = base64.b64encode(imagem_pokemon).decode('utf-8')

                pokemon = {"nome": nome_pokemon, "foto": imagem_base64}
                dados_pokemon.append(pokemon)

            cursor.execute("SELECT COUNT(*) FROM pokemon;")
            result = cursor.fetchone()
            total_pokemons = result[0] if result else 0

            pagination = Pagination(page=page, per_page=PER_PAGE, total=total_pokemons, css_framework='bootstrap3') # Configuração da paginação

            return render_template("pokemons.html", pokemons=dados_pokemon, pagination=pagination)
        
        elif tipopokemon != "Todos" and raridadepokemon == "Todos":
            page = request.args.get('page', 1, type=int) # Página atual (por padrão, será a primeira página)

            offset = (page - 1) * PER_PAGE # Obtém os itens da página atual
            cursor.execute(f"SELECT nome, imagem FROM pokemon WHERE tipo = '{tipopokemon}' LIMIT {PER_PAGE} OFFSET {offset};")
            resultados = cursor.fetchall()

            dados_pokemon = []
            for linha in resultados:
                nome_pokemon = linha[0]
                imagem_pokemon = linha[1]
                imagem_base64 = base64.b64encode(imagem_pokemon).decode('utf-8')

                pokemon = {"nome": nome_pokemon, "foto": imagem_base64}
                dados_pokemon.append(pokemon)

            cursor.execute(f"SELECT COUNT(*) FROM pokemon WHERE tipo = '{tipopokemon}';")
            result = cursor.fetchone()
            total_pokemons = result[0] if result else 0

            pagination = Pagination(page=page, per_page=PER_PAGE, total=total_pokemons, css_framework='bootstrap3') # Configuração da paginação

            return render_template("pokemons.html", pokemons=dados_pokemon, pagination=pagination)
        
        elif raridadepokemon != "Todos" and tipopokemon == "Todos":
            page = request.args.get('page', 1, type=int) # Página atual (por padrão, será a primeira página)

            offset = (page - 1) * PER_PAGE # Obtém os itens da página atual
            cursor.execute(f"SELECT nome, imagem FROM pokemon WHERE raridade = '{raridadepokemon}' LIMIT {PER_PAGE} OFFSET {offset};")
            resultados = cursor.fetchall()

            dados_pokemon = []
            for linha in resultados:
                nome_pokemon = linha[0]
                imagem_pokemon = linha[1]
                imagem_base64 = base64.b64encode(imagem_pokemon).decode('utf-8')

                pokemon = {"nome": nome_pokemon, "foto": imagem_base64}
                dados_pokemon.append(pokemon)

            cursor.execute(f"SELECT COUNT(*) FROM pokemon WHERE raridade = '{raridadepokemon}';")
            result = cursor.fetchone()
            total_pokemons = result[0] if result else 0

            pagination = Pagination(page=page, per_page=PER_PAGE, total=total_pokemons, css_framework='bootstrap3') # Configuração da paginação

            return render_template("pokemons.html", pokemons=dados_pokemon, pagination=pagination)
        
        else:
            page = request.args.get('page', 1, type=int) # Página atual (por padrão, será a primeira página)

            offset = (page - 1) * PER_PAGE # Obtém os itens da página atual
            cursor.execute(f"SELECT nome, imagem FROM pokemon WHERE raridade = '{raridadepokemon}' AND tipo = '{tipopokemon}' LIMIT {PER_PAGE} OFFSET {offset};")
            resultados = cursor.fetchall()

            dados_pokemon = []
            for linha in resultados:
                nome_pokemon = linha[0]
                imagem_pokemon = linha[1]
                imagem_base64 = base64.b64encode(imagem_pokemon).decode('utf-8')

                pokemon = {"nome": nome_pokemon, "foto": imagem_base64}
                dados_pokemon.append(pokemon)

            cursor.execute(f"SELECT COUNT(*) FROM pokemon WHERE raridade = '{raridadepokemon}' AND tipo = '{tipopokemon}';")
            result = cursor.fetchone()
            total_pokemons = result[0] if result else 0

            pagination = Pagination(page=page, per_page=PER_PAGE, total=total_pokemons, css_framework='bootstrap3') # Configuração da paginação

            return render_template("pokemons.html", pokemons=dados_pokemon, pagination=pagination)
    else:
        page = request.args.get('page', 1, type=int) # Página atual (por padrão, será a primeira página)

        offset = (page - 1) * PER_PAGE # Obtém os itens da página atual
        cursor.execute(f"SELECT nome, imagem FROM pokemon LIMIT {PER_PAGE} OFFSET {offset};")
        resultados = cursor.fetchall()

        dados_pokemon = []
        for linha in resultados:
            nome_pokemon = linha[0]
            imagem_pokemon = linha[1]
            imagem_base64 = base64.b64encode(imagem_pokemon).decode('utf-8')

            pokemon = {"nome": nome_pokemon, "foto": imagem_base64}
            dados_pokemon.append(pokemon)

        cursor.execute("SELECT COUNT(*) FROM pokemon;")
        result = cursor.fetchone()
        total_pokemons = result[0] if result else 0

        pagination = Pagination(page=page, per_page=PER_PAGE, total=total_pokemons, css_framework='bootstrap3') # Configuração da paginação

        return render_template("pokemons.html", pokemons=dados_pokemon, pagination=pagination)

if __name__ == "__main__":
    app.run(debug=True)