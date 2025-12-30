from flask import Flask,Blueprint,render_template,session
from werkzeug.exceptions import HTTPException
from database import init_db, get_db,close_db
from auth import auth_bp
from students import students_bp
from waitress import serve
import os 

def create_App():
    app = Flask(__name__)
    
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY','dev_secret')
    @app.errorhandler(HTTPException)
    def error_handle(error):
        app.logger.error(f"{error.code}-{error.description}")
        return render_template('error.html',code =error.code, message = error.description),error.code
    

    app.register_blueprint(auth_bp)
    app.register_blueprint(students_bp)


    app.teardown_appcontext(close_db)

    return app

app = create_App()

if __name__ == '__main__':
    with app.app_context():
        init_db()

    serve(app,host = '127.0.0.1', port = 8000)