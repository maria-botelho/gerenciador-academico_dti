from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Boa prática para desligar rastreamento

db = SQLAlchemy(app)

# Tabelas do Banco de Dados
class Aluno(db.Model):
    alu_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    alu_nome = db.Column(db.String(100), nullable=False)
    alu_frequencia = db.Column(db.Float, nullable=False)

class Disciplina(db.Model):
    dis_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dis_nome = db.Column(db.String(100), nullable=False)
    
class Notas(db.Model):
    not_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # ondelete='CASCADE' garante que notas sejam deletadas se o aluno/disciplina for excluído
    alu_id = db.Column(db.Integer, db.ForeignKey('aluno.alu_id', ondelete='CASCADE'), nullable=False)
    dis_id = db.Column(db.Integer, db.ForeignKey('disciplina.dis_id', ondelete='CASCADE'),nullable=False)
    
    # Campo para o valor da nota
    not_valor = db.Column(db.Float, nullable=False)

    # Relações para facilitar o acesso no template
    aluno = db.relationship('Aluno', backref='notas_aluno')
    disciplina = db.relationship('Disciplina', backref='notas_disciplina')


# ROTA PRINCIPAL (INDEX)
@app.route('/')
def index():
    alunos = Aluno.query.all()
    disciplinas = Disciplina.query.all()
    # Eager loading (joinedload) das relações para otimizar
    notas = Notas.query.options(db.joinedload(Notas.aluno), db.joinedload(Notas.disciplina)).all()

    # 1. CRIAR DICIONÁRIO DE MÉDIAS POR DISCIPLINA (Para lógica de filtragem)
    medias_disciplinas_raw = db.session.query(
        Disciplina.dis_nome, 
        func.avg(Notas.not_valor).label('media_nota')
    ).join(Notas).group_by(Disciplina.dis_nome).all()
    
    medias_por_disciplina = {
        media.dis_nome: media.media_nota 
        for media in medias_disciplinas_raw
    }
    
    # --- LÓGICA DE FILTRAGEM: Alunos acima da média em TUDO ---
    alunos_aprovados_em_tudo = {}
    
    # 2. AGRUPAR NOTAS POR ALUNO E VERIFICAR
    for nota in notas:
        aluno_id = nota.aluno.alu_id
        
        if aluno_id not in alunos_aprovados_em_tudo:
            alunos_aprovados_em_tudo[aluno_id] = {
                'nome': nota.aluno.alu_nome,
                'status': True, # Assume aprovado até que uma nota reprove
                'detalhes': []
            }
        
        # 3. VERIFICAÇÃO INDIVIDUAL DA NOTA
        dis_nome = nota.disciplina.dis_nome
        media = medias_por_disciplina.get(dis_nome, 0.0) # Usa 0.0 se não houver média (evita crash)
        
        nota_acima_da_media = nota.not_valor > media
        
        # Se a nota for abaixo ou igual à média, o aluno FALHA no critério estrito
        if not nota_acima_da_media:
            alunos_aprovados_em_tudo[aluno_id]['status'] = False
            
        # Adiciona detalhes para visualização no template
        alunos_aprovados_em_tudo[aluno_id]['detalhes'].append({
            'disciplina': dis_nome,
            'nota': nota.not_valor,
            'media': media,
            'aprovado': nota_acima_da_media
        })

    # 4. FILTRAR APENAS OS ALUNOS COM STATUS = True
    lista_final_acima_media = [
        aluno_info for aluno_info in alunos_aprovados_em_tudo.values()
        if aluno_info['status'] is True
    ]

    return render_template('index.html', 
                            alunos=alunos, 
                            disciplinas=disciplinas, 
                            notas=notas, 
                            medias_disciplinas=medias_disciplinas_raw,
                            alunos_acima_de_todas_medias=lista_final_acima_media)

# Rotas de Criação
# Create aluno
@app.route('/create_aluno', methods=['POST'])
def create_aluno():
    try:
        nome = request.form['nome_aluno']
        frequencia = float(request.form['frequencia']) # Converte diretamente para float
        new_aluno = Aluno(
            alu_nome = nome,
            alu_frequencia = frequencia
        )
        db.session.add(new_aluno)
        db.session.commit()
    except Exception as e:
        print(f"Erro ao criar aluno: {e}")
        db.session.rollback()
    return redirect(url_for('index'))

# Create disciplina
@app.route('/create_disciplina', methods=['POST'])
def create_disciplina():
    try:
        nome = request.form['nome_disciplina']
        new_disciplina = Disciplina(
            dis_nome = nome,
        )
        db.session.add(new_disciplina)
        db.session.commit()
    except Exception as e:
        print(f"Erro ao criar disciplina: {e}")
        db.session.rollback()
    return redirect(url_for('index'))

# Create nota
@app.route('/create_nota', methods=['POST'])
def create_nota():
    try:
        aluno_id = int(request.form['aluno_id'])
        disciplina_id = int(request.form['disciplina_id'])
        
        # Trata vírgula como separador decimal, se necessário
        nota_valor_str = request.form['nota_valor'].replace(',', '.')
        not_valor = float(nota_valor_str)
        
        new_nota = Notas(
            alu_id = aluno_id,
            dis_id = disciplina_id,
            not_valor = not_valor
        )
        db.session.add(new_nota)
        db.session.commit()
    except ValueError:
        print("Erro: IDs ou valor da nota inválidos.")
    except Exception as e:
        print(f"Erro ao criar nota: {e}")
        db.session.rollback()
    
    return redirect(url_for('index'))


# ROTA UNIFICADA DE ATUALIZAÇÃO (CORREÇÃO DO BuildError)
@app.route('/update_entidade/<string:entidade_nome>/<int:entidade_id>', methods=['POST'])
def update_entidade(entidade_nome, entidade_id):
    """
    Rota unificada para atualizar Aluno, Disciplina ou Nota.
    """
    try:
        if entidade_nome == 'aluno':
            aluno = Aluno.query.get_or_404(entidade_id)
            
            # Atualiza Aluno
            aluno.alu_nome = request.form['nome']
            
            # Tenta converter frequência para float (lidando com strings)
            try:
                aluno.alu_frequencia = float(request.form['frequencia'])
            except ValueError:
                # Se a conversão falhar, mantém o valor antigo ou lida de outra forma
                pass 
                
            db.session.commit()
            
        elif entidade_nome == 'disciplina':
            disciplina = Disciplina.query.get_or_404(entidade_id)
            
            # Atualiza Disciplina
            disciplina.dis_nome = request.form['nome_disciplina']
            db.session.commit()
            
        elif entidade_nome == 'nota':
            nota = Notas.query.get_or_404(entidade_id)
            
            # Atualiza Nota
            try:
                # Trata vírgula como separador decimal, se necessário
                novo_valor_nota_str = request.form['novo_valor_nota'].replace(',', '.')
                nota.not_valor = float(novo_valor_nota_str)
            except ValueError:
                pass
                
            db.session.commit()
            
        else:
            return "Erro: Entidade de atualização inválida.", 400

        return redirect(url_for('index'))

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar {entidade_nome}: {e}")
        return "Ocorreu um erro ao processar a atualização.", 500

# ROTA UNIFICADA DE DELEÇÃO
@app.route('/delete_entidade/<string:entidade_nome>/<int:entidade_id>', methods=['POST'])
def delete_entidade(entidade_nome, entidade_id):
    """
    Rota unificada para deletar Aluno, Disciplina ou Nota.
    """
    try:
        entity = None
        if entidade_nome == 'aluno':
            entity = Aluno.query.get_or_404(entidade_id)
        elif entidade_nome == 'disciplina':
            entity = Disciplina.query.get_or_404(entidade_id)
        elif entidade_nome == 'nota':
            entity = Notas.query.get_or_404(entidade_id)
        else:
            return "Erro: Entidade de exclusão inválida.", 400
            
        db.session.delete(entity)
        db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao deletar {entidade_nome}: {e}")
        return "Ocorreu um erro ao processar a exclusão.", 500

# --- ROTAS ANTIGAS REMOVIDAS ---
# As rotas 'delete_aluno', 'delete_disciplina', 'delete_nota' e 'update_aluno'
# foram removidas para evitar conflito e garantir que o HTML chame apenas as rotas unificadas.

if __name__ == '__main__':
    with app.app_context():
        #db.drop_all() 
        db.create_all()

    app.run(debug=True, port=5153)