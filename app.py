from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'

db = SQLAlchemy(app)

#tabelas
class Aluno(db.Model):
    alu_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    alu_nome = db.Column(db.String(100), nullable=False)
    alu_frequencia = db.Column(db.Float, nullable=False)

class Disciplina(db.Model):
    dis_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dis_nome = db.Column(db.String(100), nullable=False)
    dis_nota = db.Column(db.Float, nullable=False)
    alu_id = db.Column(db.Integer, db.ForeignKey('aluno.alu_id'), nullable=False)


# comandos crud -> reader
@app.route('/')
def index():
    alunos = Aluno.query.all()
    return render_template('index.html', alunos=alunos)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True, port=5153)
