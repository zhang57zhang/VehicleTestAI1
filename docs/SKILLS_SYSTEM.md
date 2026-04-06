---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3044022047aae3986fc4297c726d3559acd72de5ee3b70beea5e11bed50bfe5761cfeb7102207800f74a98638d600be785e6e5377aef31dada27bd2742769be925e8aa991906
    ReservedCode2: 304402205602b77eddd59fb4affe6e0e5f286113f971bd112b36762aeffc684c097a6f0402205afdd3721e6ee39b6ccd888575cbcc56265696c0435daf5903927233c55d71af
---

# 测试策略Skills系统设计

## 一、Skills概述

Skills是预定义的AI提示词模板系统，用于标准化AI Agent的输出质量和一致性。每个Skill针对特定的测试活动，包含完整的系统提示词、上下文模板和输出格式规范。

## 二、Skills类型定义

### 2.1 基础测试策略Skill

```json
{
    "id": "test-strategy-skill",
    "name": "测试策略生成",
    "description": "根据需求和设计文档生成完整的测试策略",
    "version": "1.0",
    "applicable": ["VCU", "BMS", "MCU", "BCU", "EPS", "ESC"]
}
```

### 2.2 Skills模板结构

每个Skill包含以下核心组成部分：

**System Prompt（系统提示词）**：定义AI Agent的角色定位、能力范围和行为准则。

**Context Template（上下文模板）**：预定义需要填入的变量和上下文信息。

**Input Schema（输入模式）**：规定Skill接受的数据格式和必填字段。

**Output Schema（输出模式）**：规定Skill返回数据的结构和格式。

**Quality Criteria（质量标准）**：定义输出需要满足的质量要求。

## 三、测试策略Skills详细定义

### 3.1 ISO26262功能安全Skill

适用于安全相关的测试策略生成：

```
【适用场景】
- ASIL B及以上级别的控制器测试
- 安全功能验证
- 故障注入测试

【核心要素】
1. 安全目标分解
2. 硬件指标测试
3. 软件指标测试
4. 故障树分析
5. 诊断覆盖率分析
```

### 3.2 ASPICE过程模型Skill

适用于软件过程评估相关的测试：

```
【适用场景】
- ASPICE认证准备
- 过程改进评估
- 供应商能力评估

【核心要素】
1. 过程能力等级评估
2. 工作产品完整性检查
3. 过程执行证据验证
```

### 3.3 HIL测试规范Skill

硬件在环测试专项规范：

```
【适用场景】
- HIL台架测试
- 实时仿真测试
- 闭环测试

【核心要素】
1. 传感器信号仿真
2. 执行器驱动测试
3. CAN/LIN通信测试
4. 故障注入测试
5. 边界条件测试
```

### 3.4 MIL/SIL测试规范Skill

模型在环和软件在环测试规范：

```
【适用场景】
- 模型算法验证
- 代码单元测试
- 覆盖率分析

【核心要素】
1. 算法正确性验证
2. 边界条件测试
3. 代码覆盖率分析
4. MC/DC覆盖率分析
```

### 3.5 动力系统测试Skill

针对VCU动力管理功能的专项测试：

```
【适用场景】
- 扭矩请求测试
- 功率限制测试
- 能量回收测试
- 驾驶模式切换

【核心要素】
1. 扭矩特性曲线测试
2. 功率限值测试
3. 能量流向测试
4. 模式切换响应测试
```

### 3.6 底盘测试Skill

针对底盘控制器的专项测试：

```
【适用场景】
- BCU制动测试
- EPS转向测试
- ESC稳定性测试

【核心要素】
1. 制动响应测试
2. 助力特性测试
3. 车身稳定控制测试
4. 故障安全功能测试
```

## 四、Skill选择机制

### 4.1 自动推荐

系统根据项目配置自动推荐适合的Skills：

```
项目类型: VCU
    ↓
推荐Skills:
    - test-strategy-skill (必需)
    - iso26262-skill (如果ASILD)
    - hil-skill (必需)
    - power-skill (必需)
```

### 4.2 手动选择

用户可以在测试策略生成界面手动选择需要的Skills：

```
可选Skills:
☐ ISO26262功能安全
☐ ASPICE过程模型
☐ HIL测试规范
☐ MIL测试规范
☐ SIL测试规范
☐ 动力系统测试
☐ 底盘测试
```

### 4.3 Skill组合策略

多Skills组合时，系统自动处理冲突和优先级：

```
高优先级: iso26262 > aspice
测试级别: hil > sil > mil
功能域: power > chassis > body
```

## 五、输出质量控制

### 5.1 质量检查清单

每个Skill输出后自动执行质量检查：

```
□ 内容完整性检查
□ 格式规范性检查
□ 专业术语一致性检查
□ 可执行性检查
□ 风险识别完整性检查
```

### 5.2 质量评分标准

```
A级 (90-100分): 完整、专业、可直接使用
B级 (75-89分): 基本完整、需少量修订
C级 (60-74分): 框架可用、需较多修订
D级 (<60分):  需要重新生成
```

### 5.3 迭代优化流程

```
初次生成 → 质量评分 → 工程师审核 →
反馈问题 → 优化调整 → 重新评分 →
通过则保存，否则继续迭代
```

## 六、Skills扩展机制

### 6.1 自定义Skill

用户可以创建自定义Skill：

```
自定义Skill模板:
{
    "id": "custom-xxx",
    "name": "自定义Skill名称",
    "system_prompt": "...",
    "context_template": "...",
    "output_schema": "..."
}
```

### 6.2 Skill导入导出

支持Skill的导入导出功能：

```
导出: skill.toJSON() → 文件
导入: JSON.parse(文件) → Skill对象
```
