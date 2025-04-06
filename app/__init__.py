from flask import Flask, render_template
from flask_cors import CORS
from app.models.db import engine, create_database, create_tables
from app.main.routes import main
from app.stations.routes import stations
from app.login.routes import users
import os

def create_app():
    app = Flask(__name__)

    # Session configuration
    app.secret_key = os.urandom(24)  # For session management
    app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes

    #create custom error pages
    #invalid URL 
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"),404
    #Internal Server Error
    @app.errorhandler(500)
    def page_not_found(e):
        return render_template("500.html"),500
    
    
    # 加载配置
    app.config.from_object('config.Config')
    
    # 初始化 CORS
    CORS(app)
    
    # 初始化数据库
    create_database()
    create_tables()
    
    # 注册路由
    app.register_blueprint(main,name="main")
    app.register_blueprint(stations,name="stations")
    app.register_blueprint(users,name="users")
    


    return app