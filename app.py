from flask import session, render_template, Flask, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dataclasses import dataclass
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__)) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
db = SQLAlchemy(app)

class Ativo(db.Model):
    __tablename__ = "ativos"
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(7), unique=True)
    tipo = db.Column(db.String(10), unique=False)
    descricao = db.Column(db.String(255), unique=False)
    data = db.Column(db.DateTime, default=db.func.now())

    def __init__(self, codigo, tipo, descricao, data):
        self.codigo = codigo
        self.tipo = tipo
        self.descricao = descricao
        self.data = data
        
    
    def __str__(self) -> str:
        return f"Código: {self.codigo}\n Tipo: {self.tipo} \n Descrição: {self.descricao} \n Data: {self.data}"


class Negociacao(db.Model):
    __tablename__ = "negociacoes"
    id = db.Column(db.Integer, primary_key=True)
    ativo = db.relationship('Ativo', backref='ativos')
    quantidade = db.Column(db.Float(10), unique=False)
    valor = db.Column(db.Float(10), unique=False)
    tipo = db.Column(db.String(7), unique=False)
    data = db.Column(db.DateTime, default=db.func.now())
    user = db.relationship('User', backref='users')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ativo_id = db.Column(db.Integer, db.ForeignKey('ativos.id'), nullable=False)

    def __init__(self, ativo_id, user_id, quantidade, tipo, valor, data):
        self.ativo_id = ativo_id
        self.user_id = user_id
        self.quantidade = quantidade
        self.tipo = tipo
        self.valor = valor
        self.data = data
        
    
    def __str__(self) -> str:
        return f"Quantidade: {self.quantidade}\n Tipo: {self.tipo} \n Valor: {self.valor} \n Data: {self.data}"

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50), nullable=False)
    def __init__(self, username="", password=""):
        self.username = username
        self.password = password


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' in session:
        return render_template("gerenciador.html", username=session["username"])
    
    return render_template("register.html", msg = 'Fazer registro')

@app.route('/al', methods=['GET', 'POST'])
def index1():
      
    return render_template("login.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = db.session.query(User).filter_by(username=username).first()
        if user and user.password == request.form['password']:
            if user.username == 'admin' and  user.password == 'admin':
                return redirect('/users')
            else:
                session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template("login.html", msg = 'usuario ou senha invalidos ou nao existem')
        
    return render_template("login.html")

@app.route('/logout', methods=["POST"])
def logout():

    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        new_user = User(username=request.form['username'], password=request.form['password'])
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    else:
        return render_template('register.html')

@app.route('/users')
def list_users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/editar_users', methods=['GET', 'POST'])
def edit_user_form():
    if 'username' in session:
        username = session['username']
        user = db.session.query(User).filter_by(username=username).first()
        return render_template('edit_user.html', user=user)


@app.route('/edit-user/<int:id>', methods=['POST'])
def edit_user(id):
    user = User.query.get(id)
    user.username = request.form['username']
    user.password = request.form['password']
    db.session.commit()
    session.pop('username', None)
    return redirect('/login')

@app.route('/listar_ativos/<int:id>', methods=['DELETE', 'GET', 'POST'])
def delete_ativo(id):
    ativo = Ativo.query.get(id)

    db.session.delete(ativo)

    db.session.commit()
    return redirect('/listar_ativos')

@app.route('/delete-user', methods=['GET','POST'])
def delete_user():
    username = session['username']
    session.pop('username', None)
    user = db.session.query(User).filter_by(username=username).first()
    negociacoes = Negociacao.query.filter_by(user_id=user.id).all()
    for negociacao in negociacoes:
        db.session.delete(negociacao)
    
    db.session.delete(user)
    db.session.commit()
    return redirect('/login')

@app.route('/delete-user2', methods=['GET','POST'])
def delete_user2():
    username = request.form['username']
    session.pop('username', None)
    user = User.query.filter_by(username=username).first()
    negociacoes = Negociacao.query.filter_by(user_id=user.id).all()
    for negociacao in negociacoes:
        db.session.delete(negociacao)
    
    db.session.delete(user)
    db.session.commit()
    return redirect('/users')



@app.route("/editar_ativo/<int:id>", methods=["GET", "POST"])
def editar_ativo(id):
    if 'username' in session:
        ativo = Ativo.query.get(id)
        return render_template("edit_ativo.html", ativo=ativo)
    return redirect(url_for('index'))


@app.route('/edit-ativo/<int:id>', methods=['POST'])
def edit_ativo(id):
  ativo = Ativo.query.get(id)
  ativo.tipo = request.form['tipo']
  ativo.codigo = request.form['codigo']
  ativo.descricao = request.form['descricao']
  ativo.data = datetime.strptime(request.form['data'], "%Y-%m-%d")
  db.session.commit()
  return redirect('/listar_ativos')



@app.route("/cadastrar_ativo", methods=["GET"])
def cadastrar_ativo():
    if 'username' in session:
        return render_template("cadastro_ativo.html", username=session["username"])
    return redirect(url_for('index'))


@app.route("/salvar_ativo", methods=["POST"])
def salvar_ativo():
    if "username" in session:
        tipo = request.form['tipo']
        codigo = request.form['codigo']
        descricao = request.form['descricao']
        data = request.form['data']
        novoativo = Ativo(codigo, tipo, descricao, datetime.strptime(data, "%Y-%m-%d"))
        db.session.add(novoativo)
        db.session.commit()
        return render_template("cadastro_ativo.html", msg="Cadastro realizado com sucesso!")
    return redirect(url_for('index'))

@app.route("/listar_ativos", methods=["GET", "POST"])
def listar_ativos():
    if 'username' in session:
        ativos = []
        query = db.session.query(Ativo).all()
        for ativo in query:
            ativos.append(ativo)
        return render_template("gerenciador.html", ativos=ativos, username=session["username"])
    return redirect(url_for('index'))


@app.route("/cadastrar_negociacao", methods=["GET", "POST"])
def cadastrar_negociacao():
    if 'username' in session:
        ativos = Ativo.query.all()
        return render_template("cadastro_negociacao.html", username=session["username"], ativos=ativos)
    return redirect(url_for('index'))

@app.route('/create-negociacao', methods=['POST', 'GET'])
def create_negociacao():
    username = session['username']
    user = User.query.filter_by(username=username).first()
    user_id = user.id
    ativo_id = request.form['ativo_id']
    quantidade = float(request.form['quantidade'])
    valor = float(request.form['valor'])
    tipo = request.form['tipo']
    data = request.form['data']
  
    negociacao = Negociacao(ativo_id, user_id, quantidade, tipo, valor, datetime.strptime(data, "%Y-%m-%d"))
    db.session.add(negociacao)
    db.session.commit()
    ativos = Ativo.query.all()
    return render_template("cadastro_negociacao.html", username=session["username"], ativos=ativos, msg='Negociacao cadastrada com sucesso')

@app.route("/listar-negociacoes", methods=["GET", "POST"])
def list_negociacoes():
    username = session['username']
    user = User.query.filter_by(username=username).first()
    negociacoes = Negociacao.query.filter_by(user_id=user.id).all()
    return render_template("gerenciador.html", negociacoes=negociacoes, username=session["username"])
    

@app.route("/editar_negociacao/<int:id>", methods=["GET", "POST"])
def editar_negociacao(id):
    if 'username' in session:
        negociacao = Negociacao.query.get(id)
        ativos = Ativo.query.all()
        return render_template("edit-negociacao.html", negociacao=negociacao, ativos=ativos, username=session['username'])
    return redirect(url_for('index'))

@app.route('/edit-negociacao/<int:id>', methods=['POST'])
def edit_negociacao(id):
  negociacao = Negociacao.query.get(id)
  negociacao.ativo_id = request.form['ativo_id']
  negociacao.quantidade = request.form['quantidade']
  negociacao.valor = request.form['valor']
  negociacao.tipo = request.form['tipo']
  negociacao.data = datetime.strptime(request.form['data'], "%Y-%m-%d")
  db.session.commit()
  return redirect('/listar-negociacoes')


@app.route('/listar_negociacoes/<int:id>', methods=['DELETE', 'GET', 'POST'])
def delete_negociacao(id):
    negociacao = Negociacao.query.get(id)

    db.session.delete(negociacao)

    db.session.commit()
    return redirect('/listar-negociacoes')



if __name__ == '__main__':
    with app.app_context():
        """db.create_all()
        try:
           db.drop_all()
           db.create_all()
        except:
            db.session.rollback()"""   
       
    app.run(debug=True)