from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
import sysconfig
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost:5432/todoapp'
db = SQLAlchemy(app)

# sets up migration
migrate = Migrate(app, db)


class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'


@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_ID):
    try:
        completed = request.get_json()['completed']
        print('completed', completed)
        todo = Todo.query.get(todo_ID)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))

@app.route('/todos/create', methods=['POST'])
def create_todo():
    # set error flag to false
    error = False
    body = {}
    try:
        # the description comes to us as a dictionary with the key "description"
        description = request.get_json()['description']

        #todo variable = Todo table's description field, which we link to the description variable
        todo = Todo(description=description)
        
        #add and commit the description to the table
        db.session.add(todo)
        db.session.commit()
        body['description'] = todo.description

        return jsonify({
            'description': todo.description
        })
    # if there's a problem
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort (400)
    else:
        return jsonify(body)

@app.route('/')
def index():
    return render_template('index.html', data=Todo.query.order_by('id').all())
