---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 30450220782130061e7f6c9f9259175c77123fea64425fb28016e0bca8632c160568f098022100a91af9accb5c66b408c3fc543b55ee0d52423e16905593cc5b7a449270b755c8
    ReservedCode2: 3046022100f26283511235c7bcf58647994a6622c1f8587ae066454d0abd24c0a3904176ea022100e0dea6c30e1abff7b5e7b1f13e877501bd4627386cc0fd2781b9807ce0712093
---

# 车载动力/底盘控制器测试AI Agent辅助网站 - 系统架构设计

## 一、项目概述

本系统是一个面向车载动力/底盘控制器测试的端到端AI Agent辅助平台，通过智能化的方式帮助工程师完成从需求分析到测试报告的全流程测试工作。

## 二、系统架构

### 2.1 技术架构

```
前端技术栈:
├── HTML5 + CSS3 + JavaScript (ES6+)
├── TailwindCSS (UI框架)
├── Web Components (组件化)
└── LocalStorage / IndexedDB (本地存储)

后端技术栈:
├── Node.js / Express
├── RESTful API
├── File System API
└── AI Agent Integration

AI技术栈:
├── LLM (Claude/GPT-4)
├── Prompt Engineering
├── Skills System
└── Multi-Agent Collaboration
```

### 2.2 模块划分

```
VehicleTestAI/
├── index.html                 # 主入口文件
├── css/
│   ├── main.css              # 主样式
│   ├── components.css        # 组件样式
│   └── pages/                # 各页面样式
│       ├── test-strategy.css
│       ├── test-case.css
│       └── ...
├── js/
│   ├── core/
│   │   ├── app.js            # 主应用
│   │   ├── router.js         # 路由管理
│   │   ├── state.js          # 状态管理
│   │   ├── file-system.js    # 文件系统
│   │   └── event-bus.js      # 事件总线
│   ├── pages/                # 页面模块
│   │   ├── base-page.js      # 页面基类
│   │   ├── test-strategy.js
│   │   ├── test-case.js
│   │   └── ...
│   ├── agents/               # AI Agent
│   │   ├── base-agent.js
│   │   ├── test-strategy-agent.js
│   │   └── ...
│   └── utils/
│       ├── ai-client.js
│       └── helpers.js
└── assets/
    └── icons/
```

## 三、子页面挂接规范

### 3.1 页面注册机制

```javascript
// 页面必须在 PAGE_CONFIG 中注册
const PAGE_CONFIG = {
    pageId: {
        name: '页面显示名称',
        icon: '图标类名',
        fileType: '关联文件类型',
        component: PageClass,  // 页面组件类
        defaultContent: {}     // 默认内容
    }
};
```

### 3.2 生命周期接口

| 生命周期钩子 | 调用时机 | 用途 |
|-------------|---------|------|
| onInit() | 组件初始化 | 初始化状态、加载资源 |
| onMount() | DOM挂载完成 | 绑定事件、初始化UI |
| onActivate() | 页面激活 | 加载数据、恢复状态 |
| onDeactivate() | 页面失活 | 保存状态、释放资源 |
| onDestroy() | 组件销毁 | 清理事件、释放内存 |
| validate() | 提交前验证 | 验证表单输入 |
| execute(agent) | 执行AI操作 | 调用AI Agent |

### 3.3 数据流

```
用户操作 → 页面组件 → 状态更新 → UI响应
                │
                ▼
          文件系统 → 保存到项目
                │
                ▼
          AI Agent → 生成结果 → 更新页面
```

## 四、AI Agent 设计

### 4.1 Agent 基类

```javascript
class BaseAgent {
    constructor(config) {
        this.name = config.name;
        this.description = config.description;
        this.requiredInputs = config.requiredInputs;
        this.prompt = config.prompt;
    }

    async execute(context) {
        // 1. 验证输入
        // 2. 构建提示词
        // 3. 调用LLM
        // 4. 处理响应
        // 5. 返回结果
    }
}
```

### 4.2 Skills 系统

Skills 是预定义的AI提示词模板，用于特定测试活动：

| Skill | 用途 | 输入 | 输出 |
|-------|-----|------|------|
| test-strategy-skill | 生成测试策略 | 需求、设计、风险 | 测试策略文档 |
| test-case-skill | 生成测试用例 | 需求、策略 | 测试用例集 |
| test-script-skill | 生成测试脚本 | 用例、环境 | 可执行脚本 |
| risk-analysis-skill | 风险分析 | 项目信息 | 风险清单 |
| report-skill | 生成报告 | 测试数据 | 测试报告 |

## 五、文件存储结构

### 5.1 项目结构

```
项目名称/
├── .project.json              # 项目配置文件
├── 需求/
│   ├── 需求文档_v1.0.pdf
│   └── 需求追溯矩阵.xlsx
├── 策略/
│   └── 测试策略_v1.json
├── 设计/
│   └── 系统设计_v1.pdf
├── 用例/
│   ├── 功能测试用例.json
│   └── 性能测试用例.json
├── 脚本/
│   ├── HIL测试脚本/
│   └── MIL测试脚本/
├── 日志/
│   └── 测试执行日志/
├── 评估/
│   └── 测试评估报告.json
├── 报告/
│   └── 测试报告_v1.docx
├── 资源/
│   ├── 设备清单.json
│   └── 人员清单.json
└── 配置/
    └── 项目配置.json
```

### 5.2 版本管理

所有生成的文件都采用版本号管理：
- `测试策略_v1.json` → `测试策略_v2.json`
- 保留历史版本，支持回滚

## 六、页面功能矩阵

| 页面 | 核心功能 | AI Agent | 输出文件 |
|------|---------|----------|----------|
| 需求分析 | 需求导入、结构化 | 需求分析Agent | 需求规格.json |
| 测试策略 | 策略生成、优化 | 测试策略Agent | 测试策略.json |
| 测试设计 | 测试方案设计 | 测试设计Agent | 测试方案.json |
| 测试用例 | 用例生成、维护 | 测试用例Agent | 测试用例.json |
| 测试脚本 | 脚本生成、执行 | 测试脚本Agent | 测试脚本/ |
| 测试日志 | 日志管理、分析 | 日志分析Agent | 日志文件/ |
| 测试评估 | 评估分析、改进 | 评估Agent | 评估报告.json |
| 测试报告 | 报告生成、导出 | 报告Agent | 测试报告.docx |
| 测试资源 | 资源管理、分配 | 资源优化Agent | 资源清单.json |
| 测试台架看板 | 实时监控、数据展示 | 监控Agent | - |
| 测试进度看板 | 进度跟踪、预警 | 进度Agent | - |
| 自动化看板 | 自动化状态、统计 | 自动化Agent | - |
| AI辅助看板 | AI使用统计、效率 | 分析Agent | - |
| 待使用1-5 | 预留扩展 | - | - |

## 七、界面布局规范

### 7.1 整体布局

```
┌──────────────────────────────────────────────────────────────┐
│  顶部工具栏 (64px)                                            │
├────────────┬─────────────────────────────────────────────────┤
│            │  标签栏 (48px)                                    │
│  左侧      ├─────────────────────────────────────────────────┤
│  项目树    │                                                  │
│  (280px)   │  主内容区                                         │
│            │  (flex-1)                                        │
│            │                                                  │
│            │                                                  │
│            ├─────────────────────────────────────────────────┤
│            │  底部状态栏 (32px)                                │
└────────────┴─────────────────────────────────────────────────┘
```

### 7.2 响应式设计

- 桌面端 (≥1200px): 完整三栏布局
- 平板端 (768-1199px): 可折叠侧边栏
- 移动端 (<768px): 底部导航 + 全屏内容

## 八、安全考虑

- 本地数据加密存储
- AI调用频率限制
- 敏感信息脱敏
- 操作日志审计
