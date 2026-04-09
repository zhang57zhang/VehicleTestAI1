"""VehicleTestAI 后端：重构为模块化蓝图"""

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from models import db

from routes.project_routes import project_bp
from routes.requirement_routes import requirement_bp
from routes.ai_routes import ai_bp
from routes.file_routes import file_bp
from routes.dashboard_routes import dashboard_bp

import os

app = Flask(__name__)
load_dotenv()
CORS(app)

# 数据库配置
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "data", "vehicletestai.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False

db.init_app(app)

# 启动时创建必要目录结构
UPLOAD_ROOT = "uploads"
os.makedirs(UPLOAD_ROOT, exist_ok=True)
os.makedirs("data", exist_ok=True)

with app.app_context():
    db.create_all()
    print("[OK] Database tables initialized")

# 注册蓝图
app.register_blueprint(project_bp)
app.register_blueprint(requirement_bp)
app.register_blueprint(ai_bp)
app.register_blueprint(file_bp)
app.register_blueprint(dashboard_bp)

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
