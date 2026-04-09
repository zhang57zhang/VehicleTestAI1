# VehicleTestAI1 - 项目架构文档

## 概述

车载控制器测试AI平台，提供需求分析、测试策略生成、测试用例设计、测试脚本生成等AI辅助功能。

## 技术栈

- **后端**: Python 3.10+, Flask, SQLAlchemy
- **前端**: 原生 JavaScript, CSS
- **AI**: 智谱GLM-4.7
- **数据库**: SQLite

## 目录结构

```
VehicleTestAI1/
├── backend/                 # 后端服务
│   ├── app.py              # Flask主应用入口
│   ├── models.py           # 数据库模型定义
│   ├── routes/             # API路由模块
│   │   ├── __init__.py
│   │   ├── project_routes.py    # 项目管理API
│   │   ├── requirement_routes.py # 需求管理API
│   │   ├── ai_routes.py         # AI相关API
│   │   ├── file_routes.py       # 文件上传API
│   │   └── dashboard_routes.py  # 看板API
│   ├── services/           # 业务逻辑层
│   │   ├── ai_service.py   # AI服务封装
│   │   ├── log_analysis_service.py # 日志分析
│   │   └── dbc_service.py  # DBC文件处理
│   ├── data/               # 数据库文件存储
│   └── uploads/            # 上传文件存储
│
├── frontend/               # 前端资源
│   ├── index.html          # 主页面
│   ├── api-service.js      # API调用封装
│   ├── css/                # 样式文件
│   │   └── main.css        # 主样式
│   └── js/                 # JavaScript模块
│       ├── app.js          # 主应用逻辑
│       ├── core/           # 核心模块
│       │   ├── app-core.js      # 核心初始化
│       │   ├── project-manager.js # 项目管理
│       │   ├── file-manager.js  # 文件操作
│       │   ├── page-renderer.js # 页面渲染
│       │   └── ai-integration.js # AI集成
│       ├── pages/          # 页面渲染模块
│       │   ├── requirements-page.js
│       │   ├── strategy-page.js
│       │   ├── design-page.js
│       │   ├── testcase-page.js
│       │   ├── script-page.js
│       │   ├── log-page.js
│       │   ├── evaluation-page.js
│       │   ├── report-page.js
│       │   └── resource-page.js
│       └── utils/          # 工具函数
│           ├── helpers.js
│           ├── ui-utils.js
│           └── error-handler.js
│
├── start.bat               # Windows启动脚本
├── AGENTS.md               # 本文档
└── old_不要读取/           # 过时代码存档
```

## API端点

### 项目管理 (/api/projects)
| 方法 | 端点 | 描述 |
|------|------|------|
| GET | /api/projects | 获取项目列表 |
| POST | /api/projects | 创建项目 |
| GET | /api/projects/<id> | 获取项目详情 |
| PUT | /api/projects/<id> | 更新项目 |
| DELETE | /api/projects/<id> | 删除项目 |
| POST | /api/projects/<id>/sync | 同步项目文件 |

### 需求管理 (/api/requirements)
| 方法 | 端点 | 描述 |
|------|------|------|
| GET | /api/requirements/<project_id> | 获取需求列表 |
| POST | /api/requirements | 创建需求 |
| PUT | /api/requirements/<id> | 更新需求 |
| DELETE | /api/requirements/<id> | 删除需求 |

### AI功能 (/api/ai)
| 方法 | 端点 | 描述 |
|------|------|------|
| GET | /api/ai/config | 获取AI配置 |
| POST | /api/ai/chat | AI对话 |
| POST | /api/ai/parse-requirements | AI解析需求 |
| POST | /api/ai/generate-strategy | 生成测试策略 |
| POST | /api/ai/generate-design | 生成测试设计 |
| POST | /api/ai/generate-testcases | 生成测试用例 |
| POST | /api/ai/generate-scripts | 生成测试脚本 |
| POST | /api/ai/generate-evaluation | 生成评估报告 |
| POST | /api/ai/generate-report | 生成测试报告 |

### 文件操作 (/api/upload)
| 方法 | 端点 | 描述 |
|------|------|------|
| POST | /api/upload/<project_id>/<type> | 上传文件 |

## 数据模型

### Project (项目)
```python
- id: UUID           # 项目唯一标识
- name: String       # 项目名称
- description: Text  # 项目描述
- created_at: DateTime # 创建时间
```

### Requirement (需求/功能点)
```python
- id: UUID           # 需求唯一标识
- project_id: UUID   # 所属项目ID
- name: String       # 功能点名称
- description: Text  # 详细描述
- category: String   # 分类 (功能需求/性能需求/安全需求)
- priority: String   # 优先级 (P0/P1/P2/P3)
- source: String     # 来源 (AI解析/手动添加)
```

### TestStrategy (测试策略)
```python
- id: UUID           # 策略唯一标识
- project_id: UUID   # 所属项目ID
- content: Text      # 策略内容
- created_at: DateTime # 创建时间
```

### TestCase (测试用例)
```python
- id: UUID           # 用例唯一标识
- project_id: UUID   # 所属项目ID
- name: String       # 用例名称
- content: Text      # 用例内容
- created_at: DateTime # 创建时间
```

## 前端模块说明

### 核心模块 (core/)

#### app-core.js
- 应用核心初始化
- 模块注册表管理
- 全局状态管理

#### project-manager.js
- 项目创建、打开、保存
- 项目列表刷新
- 项目文件同步

#### file-manager.js
- 文件上传到后端
- 文件内容读取
- 文件列表渲染

#### page-renderer.js
- 页面内容渲染
- 标签页切换
- 项目树渲染

#### ai-integration.js
- AI策略生成
- AI设计生成
- AI用例生成
- AI报告生成

### 页面模块 (pages/)
每个页面对应一个模块，负责该页面的HTML渲染和交互逻辑。

### 工具模块 (utils/)
- `helpers.js`: 通用辅助函数
- `ui-utils.js`: UI操作工具
- `error-handler.js`: 错误处理

## 启动方式

### Windows
```bash
# 双击运行
start.bat

# 或手动启动
cd backend && python app.py      # 后端 :5000
python -m http.server 8080       # 前端 :8080
```

### 访问地址
- 前端: http://localhost:8080/index.html
- 后端: http://localhost:5000

## 配置

### 环境变量 (backend/.env)
```
GLM_API_KEY=your_api_key_here
GLM_MODEL=glm-4.7
```

### 支持的文件类型
```
.txt, .md, .pdf, .doc, .docx, .xlsx, .xls
.dbc, .arxml, .blf, .asc, .csv, .mf4
.py, .json
```

## 开发规范

### 代码规范
1. **代码行数**: 单文件不超过1200行
2. **注释量**: 保持30%以上
3. **模块化**: 高内聚、低耦合

### 命名规范
| 语言 | 规范 | 示例 |
|------|------|------|
| Python | snake_case | `get_projects()` |
| JavaScript | camelCase | `renderPage()` |
| CSS | kebab-case | `.ai-sidebar` |
| 常量 | UPPER_SNAKE_CASE | `UPLOAD_FOLDER` |

### 文件命名
- Python模块: `module_name.py`
- JavaScript模块: `module-name.js`
- 路由文件: `*_routes.py`
- 页面文件: `*-page.js`

## 工作流程

### 需求分析流程
1. 创建/打开项目
2. 上传需求文档
3. 点击"AI解析"生成功能点
4. 编辑/删除/添加功能点
5. 导出需求文档

### 测试生成流程
1. 完成需求分析
2. 生成测试策略
3. 生成测试设计
4. 生成测试用例
5. 生成测试脚本
6. 执行测试并记录日志
7. 生成评估报告
8. 生成测试报告

## 更新日志

### 2026-04-09
- 项目重构，拆分模块
- 后端API模块化 (routes/)
- 前端核心模块化 (core/)
- 移动过时代码到 old_不要读取/
- 创建架构文档

## 常见问题

### Q: 后端启动失败？
A: 检查 `backend/.env` 文件是否存在，确保 `GLM_API_KEY` 已配置。

### Q: 前端API调用失败？
A: 确保后端服务在 `localhost:5000` 运行，检查CORS配置。

### Q: 文件上传失败？
A: 检查文件类型是否在允许列表中，检查 `backend/uploads/` 目录权限。
