---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022100c51cea64f415f4d02678c77c72fadb74caf54fe917ab06f317f791ba12b18d19022073d6b46d3df2f76c387f364ab7854ce59433a4baeb11e4b745c8939d84c9e851
    ReservedCode2: 3045022100b234a66ded9f1f9a1bfd3af6888cb9f7ef0a3b4d9888d52d32780ea8895721360220345dced78a33119658116f1a85d98c5746c7ca2bc81967c451248de8c1b0cf3e
---

# 车载控制器测试AI平台 - 后端服务

## 概述

本目录包含车载控制器测试AI平台的后端服务代码，基于Python Flask框架构建，提供RESTful API接口，支持AI生成、项目管理、文件处理等功能。

## 功能特性

- **项目管理**: 创建、读取、更新、删除测试项目
- **文件上传**: 支持多种格式文件上传和管理
- **AI生成服务**: 测试策略、测试设计、测试用例、测试脚本等自动生成
- **日志解析**: 自动化解析测试日志，提取DTC和问题
- **报告生成**: 自动生成测试评估和测试报告
- **看板管理**: 测试台架管理、自动化任务调度

## 技术栈

- Python 3.10+
- Flask 3.0
- Flask-CORS
- Gunicorn (生产环境)

## 快速开始

### 本地开发

1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 运行服务:
```bash
python app.py
```

服务将在 http://localhost:5000 启动

### Docker部署

1. 构建镜像:
```bash
docker build -t vehicletestai-backend ./backend
```

2. 运行容器:
```bash
docker run -d -p 5000:5000 vehicletestai-backend
```

### Docker Compose部署

```bash
docker-compose up -d
```

## API文档

### 健康检查

```
GET /api/health
```

响应:
```json
{
    "status": "healthy",
    "service": "VehicleTestAI Backend",
    "version": "1.0.0"
}
```

### 项目管理

#### 获取项目列表
```
GET /api/projects
```

#### 创建项目
```
POST /api/projects
Body: { "name": "项目名称" }
```

#### 获取项目详情
```
GET /api/projects/{project_id}
```

#### 更新项目
```
PUT /api/projects/{project_id}
Body: { "name": "新名称", ... }
```

#### 删除项目
```
DELETE /api/projects/{project_id}
```

### 文件上传

```
POST /api/upload/{project_id}/{file_type}
Content-Type: multipart/form-data
Body: file
```

### AI生成接口

#### 生成测试策略
```
POST /api/ai/generate-strategy
Body: {
    "project_id": "项目ID",
    "requirements": "需求内容",
    "system_design": "系统设计内容",
    "skills": ["技能1", "技能2"],
    "engineer_requirements": "工程师要求"
}
```

#### 生成测试设计
```
POST /api/ai/generate-design
Body: {
    "project_id": "项目ID",
    "requirements": "需求内容"
}
```

#### 生成测试用例
```
POST /api/ai/generate-testcases
Body: {
    "project_id": "项目ID",
    "requirements": "需求内容",
    "designs": ["设计1", "设计2"]
}
```

#### 生成测试脚本
```
POST /api/ai/generate-scripts
Body: {
    "project_id": "项目ID",
    "testcases": ["用例1", "用例2"],
    "framework": "pytest"
}
```

#### 解析测试日志
```
POST /api/ai/parse-log
Body: {
    "project_id": "项目ID",
    "log_content": "日志内容"
}
```

#### 生成测试评估
```
POST /api/ai/generate-evaluation
Body: {
    "project_id": "项目ID",
    "test_results": {},
    "metrics": {}
}
```

#### 生成测试报告
```
POST /api/ai/generate-report
Body: {
    "project_id": "项目ID",
    "report_type": "综合报告"
}
```

#### 分析需求
```
POST /api/ai/analyze-requirements
Body: {
    "project_id": "项目ID",
    "content": "需求内容"
}
```

#### 审查报告
```
POST /api/ai/review-report
Body: {
    "report_content": "报告内容"
}
```

#### 优化脚本
```
POST /api/ai/optimize-script
Body: {
    "project_id": "项目ID",
    "script_content": "脚本内容"
}
```

#### AI助手对话
```
POST /api/ai/chat
Body: {
    "message": "用户消息",
    "context": {
        "currentPage": "当前页面",
        "projectName": "项目名称",
        "hasUploadedFile": true/false,
        "functionPointCount": 数量
    },
    "history": [
        {"role": "user/assistant", "content": "消息内容"}
    ]
}
```

#### 审核需求文档
```
POST /api/ai/review-requirements
Body: {
    "project_id": "项目ID",
    "file_name": "需求文件名",
    "file_content": "需求内容",
    "function_points": [功能点列表]
}
```

### AI统计接口

#### 获取AI使用统计
```
GET /api/ai/stats
```

响应:
```json
{
    "success": true,
    "stats": {
        "total_calls": 10,
        "hours_saved": 1.0,
        "adoption_rate": 100,
        "active_skills": 5
    },
    "skill_usage": {...},
    "history": [...]
}
```

#### 重置AI统计
```
POST /api/ai/stats/reset
```

### 项目文件同步

#### 同步项目文件
```
POST /api/projects/{project_id}/sync
```

响应:
```json
{
    "success": true,
    "message": "文件同步完成",
    "files": {
        "requirement": {...},
        "strategy": {...},
        ...
    }
}
```

### 看板接口

#### 获取测试台架
```
GET /api/benchmarks
```

#### 添加测试台架
```
POST /api/benchmarks
Body: { "name": "台架名称", ... }
```

#### 获取自动化任务
```
GET /api/automation/jobs
```

#### 创建自动化任务
```
POST /api/automation/jobs
Body: { "name": "任务名称", ... }
```

#### 执行自动化任务
```
POST /api/automation/jobs/{job_id}/run
```

## 目录结构

```
backend/
├── app.py              # 主应用文件
├── requirements.txt    # Python依赖
├── Dockerfile          # Docker配置
├── services/
│   ├── __init__.py
│   └── ai_service.py   # AI服务模块
├── uploads/            # 上传文件目录
└── data/               # 数据存储目录
```

## AI服务配置

后端支持多种AI服务，可以通过环境变量配置:

### Mock服务（默认）
使用模拟AI服务，返回预设的测试文档模板。

### MiniMax服务
```bash
export MINIMAX_API_KEY=your_api_key
```

### 自定义AI服务
可以通过继承 `AIServiceBase` 类实现自定义AI服务集成。

## 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| FLASK_APP | Flask应用名 | app |
| FLASK_ENV | 运行环境 | production |
| SECRET_KEY | 应用密钥 | random |
| MINIMAX_API_KEY | MiniMax API密钥 | - |

## 数据存储

- **项目数据**: `data/projects.json`
- **上传文件**: `uploads/`
- **日志**: 服务启动时自动记录

## 开发指南

### 添加新的AI生成功能

1. 在 `app.py` 中添加新的API端点:
```python
@app.route('/api/ai/new-feature', methods=['POST'])
def new_ai_feature():
    data = request.json
    # 处理请求
    result = generate_new_feature(data)
    return jsonify({'success': True, 'result': result})
```

2. 在 `services/ai_service.py` 中添加生成逻辑:
```python
def generate_new_feature(params):
    prompt = f"生成新功能: {params}"
    return ai_service.generate(prompt)
```

## 测试

运行单元测试:
```bash
pytest tests/
```

## 许可证

MIT License
