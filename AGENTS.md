# VehicleTestAI3 - 项目架构文档

## 概述

车载控制器测试AI平台，提供需求分析、测试策略生成、测试用例设计、测试脚本生成等AI辅助功能。基于test_system文档规范，支持完整的测试活动生命周期管理。

## 技术栈

- **后端**: Python 3.10+, Flask, SQLAlchemy
- **前端**: 原生 JavaScript, CSS
- **AI**: 智谱GLM-4.7 (支持多模型回退)
- **数据库**: SQLite (支持索引优化)

## 测试活动体系

基于test_system文档规范，系统支持以下测试活动：

| 活动代码 | 活动名称 | 说明 |
|----------|----------|------|
| RA | 需求分析 | Requirement Analysis |
| TS | 测试策略 | Test Strategy |
| TD | 测试设计 | Test Design |
| TC | 测试用例 | Test Cases |
| TScr | 测试脚本 | Test Scripts |
| TE | 测试执行 | Test Execution |
| TL | 测试日志 | Test Logs |
| TEval | 测试评估 | Test Evaluation |
| TR | 测试报告 | Test Reports |

## 目录结构

```
VehicleTestAI3/
├── backend/                 # 后端服务
│   ├── app.py              # Flask主应用入口
│   ├── models.py           # 数据库模型定义 (已优化: 索引、关系)
│   ├── routes/             # API路由模块
│   │   ├── __init__.py
│   │   ├── project_routes.py    # 项目管理API
│   │   ├── requirement_routes.py # 需求管理API
│   │   ├── ai_routes.py         # AI相关API (已优化: 统一响应格式)
│   │   ├── file_routes.py       # 文件上传API
│   │   └── dashboard_routes.py  # 看板API
│   ├── services/           # 业务逻辑层
│   │   ├── ai_service.py   # AI服务封装
│   │   ├── enhanced_ai_service_v2.py  # 增强版AI服务 (新增)
│   │   ├── prompt_templates.py        # AI提示词模板 (新增)
│   │   ├── log_analysis_service.py # 日志分析
│   │   └── dbc_service.py  # DBC文件处理
│   ├── utils/              # 工具模块 (新增)
│   │   ├── response.py     # 统一API响应格式
│   │   ├── error_handler.py # 错误处理系统
│   │   ├── cache_manager.py # 缓存管理
│   │   └── db_optimizer.py  # 数据库优化
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
│       │   ├── ai-integration.js # AI集成
│       │   ├── enhanced-api-service.js # 增强版API服务 (新增)
│       │   └── test-activity-manager.js # 测试活动管理器 (新增)
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
├── test_system/            # 测试系统文档规范
│   ├── 00_overview/        # 总览文档
│   ├── 01_requirement_analysis/  # 需求分析活动
│   ├── 02_test_strategy/   # 测试策略活动
│   ├── 03_test_design/     # 测试设计活动
│   ├── 04_test_cases/      # 测试用例活动
│   ├── 05_test_scripts/    # 测试脚本活动
│   ├── 06_test_execution/  # 测试执行活动
│   ├── 07_test_logs/       # 测试日志活动
│   ├── 08_test_evaluation/ # 测试评估活动
│   ├── 09_test_report/     # 测试报告活动
│   └── 10_templates/       # 模板文件
│
├── start.bat               # Windows启动脚本
└── AGENTS.md               # 本文档

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
| 方法 | 端点 | 活动代码 | 描述 |
|------|------|----------|------|
| GET | /api/ai/config | - | 获取AI配置 |
| POST | /api/ai/chat | - | AI对话 |
| POST | /api/ai/parse-requirements | RA | AI解析需求 |
| POST | /api/ai/review-requirements | RA | 需求审核 |
| POST | /api/ai/generate-strategy | TS | 生成测试策略 |
| POST | /api/ai/generate-design | TD | 生成测试设计 |
| POST | /api/ai/generate-testcases | TC | 生成测试用例 |
| POST | /api/ai/generate-scripts | TScr | 生成测试脚本 |
| POST | /api/ai/parse-log | TL | 解析测试日志 |
| POST | /api/ai/generate-evaluation | TEval | 生成评估报告 |
| POST | /api/ai/generate-report | TR | 生成测试报告 |

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
- status: String     # 状态 (active/archived/deleted)
- created_at: DateTime # 创建时间
- updated_at: DateTime # 更新时间
```

### Requirement (需求/功能点)
```python
- id: UUID           # 需求唯一标识
- project_id: UUID   # 所属项目ID
- name: String       # 功能点名称
- category: String   # 分类 (功能需求/性能需求/安全需求/接口需求)
- priority: String   # 优先级 (P0/P1/P2/P3)
- asil_level: String # ASIL等级 (A/B/C/D)
- source: String     # 来源 (AI解析/手动添加)
```

### TestStrategy (测试策略)
```python
- id: UUID           # 策略唯一标识
- project_id: UUID   # 所属项目ID
- name: String       # 策略名称
- content: Text      # 策略内容
- test_environment: String # 测试环境 (HIL/SIL/DIL)
- status: String     # 状态 (draft/reviewed/approved)
```

### TestCase (测试用例)
```python
- id: UUID           # 用例唯一标识
- project_id: UUID   # 所属项目ID
- name: String       # 用例名称
- module: String     # 测试模块
- priority: String   # 优先级
- test_type: String  # 测试类型
- auto: Boolean      # 是否可自动化
- executed: Boolean  # 是否已执行
```

### ActivityState (活动状态) - 新增
```python
- id: UUID           # 状态唯一标识
- project_id: UUID   # 所属项目ID
- activity_code: String # 活动代码 (RA/TS/TD/TC/TScr/TE/TL/TEval/TR)
- status: String     # 状态 (not_started/in_progress/completed/failed)
- progress: Integer  # 进度 (0-100)
```

## 前端模块说明

### 核心模块 (core/)

#### app-core.js
- 应用核心初始化
- 模块注册表管理
- 全局状态管理

#### enhanced-api-service.js (新增)
- 统一API调用封装
- 错误处理和重试机制
- 请求缓存和队列管理

#### test-activity-manager.js (新增)
- 测试活动状态管理
- 依赖关系检查
- 流程进度跟踪

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

## 后端服务说明

### AI服务层

#### ai_service.py
- 基础AI服务封装
- 支持GLM、MiniMax等模型
- Mock服务用于开发测试

#### enhanced_ai_service_v2.py (新增)
- 增强版AI服务
- 集成提示词模板系统
- 响应解析和结构化输出
- 自动重试机制

#### prompt_templates.py (新增)
- 标准化提示词模板
- 基于test_system文档规范
- 支持所有测试活动类型

### 工具模块

#### response.py (新增)
- 统一API响应格式
- 标准化错误响应
- 分页响应支持

#### error_handler.py
- 错误分类和追踪
- 结构化日志
- 降级策略

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
1. 完成需求分析 (RA)
2. 生成测试策略 (TS)
3. 生成测试设计 (TD)
4. 生成测试用例 (TC)
5. 生成测试脚本 (TScr)
6. 执行测试并记录日志 (TE/TL)
7. 生成评估报告 (TEval)
8. 生成测试报告 (TR)

## 更新日志

### 2026-04-10
- 后端架构优化：统一响应格式、错误处理
- AI服务优化：提示词模板系统、响应解析
- 数据库优化：添加索引、新增活动状态模型
- 前端优化：增强版API服务、测试活动管理器

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

### Q: AI生成失败？
A: 检查API Key是否有效，查看后端日志了解详细错误信息。系统会自动回退到Mock服务。
