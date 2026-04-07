# VehicleTestAI - 车载控制器测试AI平台

## 项目简介

VehicleTestAI 是一个基于AI的车载控制器测试平台，支持从需求分析到测试报告生成的完整测试流程。

## 当前状态

**测试通过率**: 38/49 (77.6%)  
**AI模型**: GLM-4.7 (智谱AI)  
**数据库**: SQLite  
**后端**: Flask 3.0  
**前端**: 原生HTML/JS  

## 快速开始

### 1. 配置AI服务

在 `backend/.env` 文件中配置GLM-4.7 API:

```env
GLM_API_KEY=your_api_key_here
GLM_MODEL=glm-4.7
```

### 2. 启动服务

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
cd backend && python3 app.py &
python3 -m http.server 8080
```

### 3. 访问平台

- 前端: http://localhost:8080/index.html
- 后端API: http://localhost:5000/api/health

## 功能模块

### 1. 需求分析页面
- ✅ 需求文档导入
- ✅ AI解析需求
- ✅ 手动添加功能点
- ✅ 查询功能点列表
- ✅ 需求审核

### 2. 测试策略页面
- ✅ 上传需求文档
- ✅ 读取需求分析结果
- ✅ 上传系统设计
- ✅ 上传自定义章节
- ⚠️ 生成测试策略 (AI需要时间)

### 3. 测试设计页面
- ✅ 读取功能点列表
- ✅ 读取测试策略
- ⚠️ 生成测试设计 (AI需要时间)

### 4. 测试用例页面
- ✅ 上传测试方案
- ✅ 上传功能点列表
- ✅ 上传DBC信号
- ✅ 上传通信矩阵
- ✅ 上传告警列表
- ✅ 上传诊断列表
- ⚠️ 生成测试用例 (AI需要时间)
- ✅ 手动添加用例
- ✅ 查询用例列表

### 5. 测试脚本页面
- ✅ 上传测试用例
- ✅ 上传自动化接口表
- ✅ 上传自动化规则
- ✅ 上传DBC信号
- ✅ 上传告警列表
- ⚠️ 上传脚本模板 (需添加.py支持)
- ⚠️ 执行目录配置
- ⚠️ 生成测试脚本 (AI需要时间)

### 6. 测试日志页面
- ✅ BLF日志导入
- ✅ ASC日志导入
- ✅ CSV日志导入
- ✅ MF4日志导入
- ✅ DBC文件导入
- ✅ ARXML文件导入
- ✅ 测试用例匹配
- ⚠️ 分析日志 (AI需要时间)
- ⚠️ 生成DTS
- ✅ 导出分析

### 7. 测试评估页面
- ✅ 读取需求文件
- ✅ 读取缺陷DTS
- ✅ 读取执行情况
- ⚠️ 生成测试评估 (AI需要时间)

### 8. 测试报告页面
- ✅ 读取报告模板
- ✅ 读取测试结果
- ⚠️ 生成测试报告 (AI需要时间)

## API端点状态

### 已实现的API (38个)

**项目管理 (5个)**
- `GET /api/health` - 健康检查
- `GET /api/projects` - 获取项目列表
- `POST /api/projects` - 创建项目
- `GET /api/projects/{id}` - 获取项目详情
- `DELETE /api/projects/{id}` - 删除项目

**需求管理 (3个)**
- `POST /api/requirements` - 添加需求
- `GET /api/requirements/{project_id}` - 获取需求列表
- `POST /api/ai/parse-requirements` - AI解析需求

**文件上传 (15个)**
- `POST /api/upload/{project_id}/{file_type}` - 通用文件上传
- 支持文件类型: requirements, systemDesign, customSection, testPlan, functionPoints, dbc, alarmList, diagnosisList, automationInterface, automationRules, blf, asc, csv, mf4, arxml

**测试用例 (3个)**
- `POST /api/testcases` - 添加测试用例
- `GET /api/testcases/{project_id}` - 获取测试用例列表
- `POST /api/ai/match-testcases` - 测试用例匹配

**测试结果 (3个)**
- `GET /api/test-results/{project_id}` - 读取测试结果
- `GET /api/execution-status/{project_id}` - 读取执行情况
- `GET /api/dts/{project_id}` - 读取缺陷DTS

**AI生成 (7个)**
- `POST /api/ai/generate-strategy` - 生成测试策略
- `POST /api/ai/generate-design` - 生成测试设计
- `POST /api/ai/generate-testcases` - 生成测试用例
- `POST /api/ai/generate-scripts` - 生成测试脚本
- `POST /api/ai/parse-log` - 分析日志
- `POST /api/ai/generate-evaluation` - 生成测试评估
- `POST /api/ai/generate-report` - 生成测试报告

**导出 (2个)**
- `GET /api/export/analysis/{project_id}` - 导出分析报告
- `POST /api/ai/generate-dts` - 生成DTS缺陷报告

### 待完善的API (4个)
- `POST /api/upload/{project_id}/scriptTemplate` - 上传脚本模板 (需添加.py文件支持)
- `POST /api/automation/config` - 执行目录配置
- `POST /api/ai/review-requirements` - 需求审核 (代码已添加)
- `POST /api/ai/generate-dts` - 生成DTS (代码已添加)

## 技术栈

**后端:**
- Python 3.10+
- Flask 3.0
- Flask-SQLAlchemy 3.1.1
- SQLite 3

**前端:**
- 原生 HTML5/CSS3/JavaScript
- Bootstrap 5
- Fetch API

**AI服务:**
- GLM-4.7 (智谱AI)
- 支持Mock模式

## 目录结构

```
VehicleTestAI1/
├── backend/
│   ├── app.py              # 主应用文件
│   ├── requirements.txt    # Python依赖
│   ├── .env               # 环境变量配置
│   ├── services/
│   │   └── ai_service.py  # AI服务模块
│   ├── uploads/           # 上传文件目录
│   └── data/              # 数据库目录
├── frontend/
│   ├── index.html         # 主页面
│   ├── css/               # 样式文件
│   └── js/                # JavaScript文件
├── tests/
│   ├── test_complete_functions.py  # 完整功能测试
│   └── COMPLETE_FUNCTION_TEST.json # 测试报告
├── docs/
│   ├── ARCHITECTURE.md    # 架构文档
│   └── TESTING_GUIDE.md   # 测试指南
├── start.bat              # Windows启动脚本
└── README.md              # 本文件
```

## 测试

运行完整功能测试:
```bash
cd VehicleTestAI1
python3 tests/test_complete_functions.py
```

## 已知问题

1. **服务稳定性**: Flask开发服务器在测试过程中不稳定，建议使用Gunicorn
2. **AI超时**: GLM-4.7响应时间约50秒-3分钟，部分AI生成功能可能超时
3. **文件类型**: 脚本模板上传需要添加.py文件支持

## 更新日志

### 2026-04-07
- ✅ 配置GLM-4.7 API
- ✅ 创建MCU电驱动测试资料 (10个文件)
- ✅ 修复7个缺失API
- ✅ 通过率从63.3%提升到77.6%
- ✅ 更新所有文档

### 2026-04-06
- ✅ 初始项目搭建
- ✅ SQLite数据库实现
- ✅ 20+ API端点实现
- ✅ 前端集成真实API

## 许可证

MIT License

## 联系方式

GitHub: https://github.com/zhang57zhang/VehicleTestAI1
