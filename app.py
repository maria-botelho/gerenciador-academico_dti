from flask import Flask, render_template, request, redirect
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
    
class Notas(db.Model):
    not_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    alu_id = db.Column(db.Integer, db.ForeignKey('aluno.alu_id'), nullable=False)
    dis_id = db.Column(db.Integer, db.ForeignKey('disciplina') ,nullable=False)
    
	# Novo campo para o valor da nota
    not_valor = db.Column(db.Float, nullable=False)

    # Relações para facilitar o acesso no template
    aluno = db.relationship('Aluno', backref='notas_aluno')
    disciplina = db.relationship('Disciplina', backref='notas_disciplina')


# Reader Alunos
@app.route('/')
def index():
    alunos = Aluno.query.all()
    disciplinas = Disciplina.query.all()
    notas = Notas.query.all()
    return render_template('index.html', alunos=alunos, disciplinas=disciplinas, notas=notas)

# Create aluno
@app.route('/create_aluno', methods=['POST'])
def create_aluno():
		nome = request.form['nome_aluno']
		frequencia = request.form['frequencia']
		new_aluno = Aluno(
			alu_nome = nome,
			alu_frequencia = frequencia
		)
		db.session.add(new_aluno)
		db.session.commit()
		return redirect('/')

# Create disciplina
@app.route('/create_disciplina', methods=['POST'])
def create_disciplina():
		nome = request.form['nome_disciplina']
		new_disciplina = Disciplina(
			dis_nome = nome,
		)
		db.session.add(new_disciplina)
		db.session.commit()
		return redirect('/')

# Create nota
@app.route('/create_nota', methods=['POST'])
def create_nota():
    # Os valores recebidos são os IDs e o valor da nota
    aluno_id = request.form['aluno_id']
    disciplina_id = request.form['disciplina_id']
    nota_valor = request.form['nota_valor']
    
    try:
        # Tenta converter os IDs e o valor para os tipos corretos
        alu_id = int(aluno_id)
        dis_id = int(disciplina_id)
        not_valor = float(nota_valor)
        
        new_nota = Notas(
            alu_id = alu_id,
            dis_id = dis_id,
            not_valor = not_valor
        )
        db.session.add(new_nota)
        db.session.commit()
    except ValueError:
        # Lidar com erro se a conversão falhar (ex: nota não é um número)
        print("Erro: IDs ou valor da nota inválidos.")
    
    return redirect('/')
	
# Delete aluno
@app.route('/delete_aluno/<int:alu_id>', methods=['POST'])
def delete_aluno(alu_id):
		alunos = Aluno.query.get(alu_id)
		
		if alunos:
			db.session.delete(alunos)
			db.session.commit()
		return redirect('/')
# Update aluno
@app.route('/update_aluno/<int:alu_id>', methods=['POST'])
def update_aluno(alu_id):
		alunos = Aluno.query.get(alu_id)
		
		if alunos:
			alunos.alu_nome = request.form['nome']
			alunos.frequencia = request.form['frequencia']
			db.session.commit()
		return redirect('/')
	
if __name__ == '__main__':
    with app.app_context():
        #db.drop_all()
        db.create_all()

    app.run(debug=True, port=5153)
		
	
