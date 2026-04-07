# 车载电驱动MCU自动化接口表

**文档编号**：AI-EV-MCU-2026-001  
**版本**：V1.0  
**日期**：2026-04-07

---

## 1. 概述

本文档定义 MCU 自动化测试系统的接口规范，用于 HIL 台架和自动化测试系统调用。

---

## 2. 硬件接口

### 2.1 CAN接口
| 接口 | 参数 | 说明 |
|------|------|------|
| CAN1 | 500kbps, 11-bit ID | 整车通信 |
| CAN2 | 500kbps, 11-bit ID | 诊断通信 |
| CAN3 | 500kbps, 29-bit ID | 自动化测试专用 |

### 2.2 IO接口
| 信号名称 | 类型 | 方向 | 说明 |
|----------|------|------|------|
| DI_01 | 数字输入 | IN | 使能信号模拟 |
| DI_02 | 数字输入 | IN | 方向信号模拟 |
| DI_03 | 数字输入 | IN | 急停信号模拟 |
| DO_01 | 数字输出 | OUT | 故障输出监测 |
| DO_02 | 数字输出 | OUT | 就绪信号监测 |
| AI_01 | 模拟输入 | IN | 扭矩请求模拟(0-10V) |
| AI_02 | 模拟输入 | IN | 转速请求模拟(0-10V) |
| AO_01 | 模拟输出 | OUT | 扭矩反馈监测 |
| AO_02 | 模拟输出 | OUT | 转速反馈监测 |

### 2.3 传感器模拟接口
| 信号名称 | 类型 | 范围 | 说明 |
|----------|------|------|------|
| Resolver_S1 | 差分 | ±10V | 旋变正弦信号 |
| Resolver_S2 | 差分 | ±10V | 旋变余弦信号 |
| Resolver_Exc | 输出 | 10Vpp, 10kHz | 旋变激励信号 |
| I_Sensor_U | 电流 | 0-5V | U相电流传感器 |
| I_Sensor_W | 电流 | 0-5V | W相电流传感器 |

---

## 3. CAN自动化测试接口

### 3.1 测试控制报文 (0x501)

**请求报文（测试系统→MCU）**
| 字节 | 信号 | 类型 | 说明 |
|------|------|------|------|
| 0 | Test_ID | uint8 | 测试用例ID |
| 1 | Test_Mode | uint8 | 0:停止, 1:开始, 2:暂停, 3:恢复 |
| 2 | Test_Param1_H | uint8 | 测试参数1高位 |
| 3 | Test_Param1_L | uint8 | 测试参数1低位 |
| 4 | Test_Param2_H | uint8 | 测试参数2高位 |
| 5 | Test_Param2_L | uint8 | 测试参数2低位 |
| 6 | Test_Param3_H | uint8 | 测试参数3高位 |
| 7 | Test_Param3_L | uint8 | 测试参数3低位 |

### 3.2 测试响应报文 (0x502)

**响应报文（MCU→测试系统）**
| 字节 | 信号 | 类型 | 说明 |
|------|------|------|------|
| 0 | Test_ID | uint8 | 测试用例ID |
| 1 | Test_Status | uint8 | 0:空闲, 1:运行, 2:完成, 3:失败 |
| 2 | Test_Result | uint8 | 0:PASS, 1:FAIL, 2:ERROR, 3:NA |
| 3 | Error_Code | uint8 | 错误码 |
| 4-5 | Measured_Value1 | int16 | 测量值1 |
| 6-7 | Measured_Value2 | int16 | 测量值2 |

### 3.3 测试数据上报 (0x503)

**数据上报（MCU→测试系统）**
| 字节 | 信号 | 类型 | 说明 |
|------|------|------|------|
| 0 | Test_ID | uint8 | 测试用例ID |
| 1 | Data_Index | uint8 | 数据索引 |
| 2-3 | Data_Value1 | int16 | 数据值1 |
| 4-5 | Data_Value2 | int16 | 数据值2 |
| 6-7 | Data_Value3 | int16 | 数据值3 |

---

## 4. 测试用例接口定义

### 4.1 功能测试接口

#### TC-001: 扭矩控制测试
| 参数 | 类型 | 说明 |
|------|------|------|
| Test_Param1 | int16 | 目标扭矩(Nm, 0.1x) |
| Test_Param2 | int16 | 扭矩斜率(Nm/s) |
| Test_Param3 | int16 | 稳定时间(ms) |
| Measured_Value1 | int16 | 实际扭矩(Nm, 0.1x) |
| Measured_Value2 | int16 | 响应时间(ms) |

#### TC-002: 转速控制测试
| 参数 | 类型 | 说明 |
|------|------|------|
| Test_Param1 | int16 | 目标转速(rpm) |
| Test_Param2 | int16 | 加速度(rpm/s) |
| Test_Param3 | int16 | 稳定时间(ms) |
| Measured_Value1 | int16 | 实际转速(rpm) |
| Measured_Value2 | int16 | 转速偏差(rpm) |

#### TC-003: 通信测试
| 参数 | 类型 | 说明 |
|------|------|------|
| Test_Param1 | int16 | 报文ID |
| Test_Param2 | int16 | 发送周期(ms) |
| Test_Param3 | int16 | 测试次数 |
| Measured_Value1 | int16 | 接收计数 |
| Measured_Value2 | int16 | 错误计数 |

### 4.2 保护测试接口

#### TC-010: 过流保护测试
| 参数 | 类型 | 说明 |
|------|------|------|
| Test_Param1 | int16 | 触发电流(A, 0.1x) |
| Test_Param2 | int16 | 保护延迟(us) |
| Test_Param3 | int16 | 恢复时间(ms) |
| Measured_Value1 | int16 | 实际触发电流(A) |
| Measured_Value2 | int16 | 实际响应时间(us) |

#### TC-011: 过温保护测试
| 参数 | 类型 | 说明 |
|------|------|------|
| Test_Param1 | int16 | 触发温度(℃) |
| Test_Param2 | int16 | 保持时间(s) |
| Test_Param3 | int16 | 预期动作 |
| Measured_Value1 | int16 | 实际触发温度(℃) |
| Measured_Value2 | int16 | 降功率比例(%) |

### 4.3 诊断测试接口

#### TC-020: DTC测试
| 参数 | 类型 | 说明 |
|------|------|------|
| Test_Param1 | int16 | 触发的DTC码(高字节) |
| Test_Param2 | int16 | 触发的DTC码(低字节) |
| Test_Param3 | int16 | 预期状态 |
| Measured_Value1 | int16 | DTC状态字节 |
| Measured_Value2 | int16 | 快照数据 |

---

## 5. Python API接口

### 5.1 测试控制类

```python
class MCUTestController:
    """MCU自动化测试控制器"""
    
    def __init__(self, can_channel: int = 0):
        """初始化测试控制器"""
        pass
    
    def start_test(self, test_id: int, params: dict) -> bool:
        """
        启动测试
        Args:
            test_id: 测试用例ID
            params: 测试参数字典
        Returns:
            是否启动成功
        """
        pass
    
    def stop_test(self, test_id: int) -> bool:
        """停止测试"""
        pass
    
    def get_test_result(self, test_id: int) -> dict:
        """
        获取测试结果
        Returns:
            {
                'status': int,  # 0:空闲, 1:运行, 2:完成, 3:失败
                'result': int,  # 0:PASS, 1:FAIL, 2:ERROR
                'measured_values': list,
                'error_code': int
            }
        """
        pass
    
    def read_test_data(self, test_id: int) -> list:
        """读取测试数据"""
        pass
```

### 5.2 信号模拟类

```python
class SignalSimulator:
    """信号模拟器"""
    
    def set_torque_request(self, torque_nm: float):
        """设置扭矩请求"""
        pass
    
    def set_speed_request(self, speed_rpm: float):
        """设置转速请求"""
        pass
    
    def set_enable(self, enable: bool):
        """设置使能信号"""
        pass
    
    def set_direction(self, forward: bool):
        """设置方向信号"""
        pass
    
    def inject_fault(self, fault_type: str, value: float):
        """注入故障"""
        pass
```

### 5.3 数据采集类

```python
class DataAcquisition:
    """数据采集器"""
    
    def start_recording(self, duration_s: float):
        """开始记录数据"""
        pass
    
    def stop_recording(self):
        """停止记录"""
        pass
    
    def get_torque_data(self) -> list:
        """获取扭矩数据"""
        pass
    
    def get_speed_data(self) -> list:
        """获取转速数据"""
        pass
    
    def get_temperature_data(self) -> dict:
        """获取温度数据"""
        pass
    
    def export_to_csv(self, filepath: str):
        """导出数据到CSV"""
        pass
```

---

## 6. 测试序列接口

### 6.1 测试序列文件格式 (YAML)

```yaml
test_sequence:
  name: "MCU功能验证序列"
  version: "1.0"
  preconditions:
    - hv_voltage: "300-450V"
    - lv_voltage: "11-15V"
    - temperature: "-40~85°C"
  
  test_cases:
    - id: TC-001
      name: "扭矩控制基本功能"
      params:
        target_torque: 100  # Nm
        ramp_rate: 50       # Nm/s
        hold_time: 2000     # ms
      criteria:
        torque_error: "<5Nm"
        response_time: "<50ms"
      
    - id: TC-002
      name: "转速控制基本功能"
      params:
        target_speed: 3000  # rpm
        acceleration: 1000  # rpm/s
        hold_time: 5000     # ms
      criteria:
        speed_error: "<50rpm"
        stability: "<1%"
```

### 6.2 测试结果文件格式 (JSON)

```json
{
  "test_sequence": "MCU功能验证序列",
  "execution_time": "2026-04-07T10:00:00",
  "total_cases": 10,
  "passed": 8,
  "failed": 2,
  "results": [
    {
      "test_id": "TC-001",
      "name": "扭矩控制基本功能",
      "status": "PASS",
      "duration_ms": 2100,
      "measured_values": {
        "torque_actual": 99.5,
        "response_time_ms": 42
      },
      "criteria_met": true
    }
  ]
}
```

---

## 7. 接口版本管理

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| 1.0 | 2026-04-07 | 初始版本 |
