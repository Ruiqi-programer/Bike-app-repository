from flask import Flask
from flask_cors import CORS
from app.models.db import engine, create_database, create_tables

def create_app():
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object('config.Config')
    
    # 初始化 CORS
    CORS(app)
    
    # 初始化数据库
    create_database()
    create_tables()
    
    # 注册路由
    from app.routes import main
    app.register_blueprint(main)
    
    return app