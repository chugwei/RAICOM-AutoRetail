# 🤖 Robuster — 自主移动抓取机器人系统



---

## 📋 项目简介

本项目为 **睿抗机器人大赛** 参赛作品，实现了一套全自主移动抓取机器人系统。机器人在未知环境中自主完成 **建图 → 导航 → 视觉搜索 → 抓取 → 分类放置** 的全流程作业。

### 主要功能

1. **SLAM 建图** — 基于 GMapping 算法构建环境栅格地图
2. **自主导航** — 使用 ROS `move_base` 实现全局/局部路径规划与避障
3. **视觉目标检测** — 基于 YOLOv5 实时识别苹果、时钟、香蕉等物体
4. **精准抓取** — 6 轴机械臂配合超声波测距闭环实现厘米级抓取
5. **分类放置** — 将不同物体放置到指定区域

### 核心流程

```
SLAM 建图 → 导航定位 → YOLO 视觉搜索 → 机械臂抓取 → 转身返回 → 分类放置 → 循环
```

---

## 🏗️ 目录结构

```
zcw_robuster/
├── src/                          # 源代码
│   ├── core/                     # ★ 核心系统（国赛最终版）
│   │   ├── main.py               #   主程序入口
│   │   ├── Basic.py              #   MyCobot 机械臂基础控制
│   │   ├── GrabParams.py         #   系统参数配置与标定
│   │   ├── movement.py           #   ROS 底盘移动控制 (cmd_vel)
│   │   ├── obj_detect.py         #   YOLOv5 目标检测
│   │   ├── obj_follow.py         #   视觉伺服跟踪
│   │   ├── sonor.py              #   HC-SR04 超声波传感器驱动
│   │   └── mobile_to_goal.py     #   导航目标点发布
│   ├── server/                   # Flask 远程任务服务器
│   │   ├── server.py             #   Flask API 服务端
│   │   ├── move_to_goal.py       #   服务端导航控制
│   │   └── save_goal_*.py        #   目标点保存工具
│   ├── teleop/                   # 手柄遥控
│   │   ├── logitech_teleop_node.cpp  # 罗技手柄遥操作节点 (C++)
│   │   └── teleop_loadmap.py     #   加载地图遥操作
│   └── utils/                    # 工具与测试脚本
├── config/                       # 配置文件
│   └── goal_*.txt                # 预录导航目标点坐标
├── tools/ngrok/                  # ngrok 内网穿透工具
├── docs/                         # 文档
│   ├── 睿抗机器人_简历项目介绍.md        # 项目简历介绍
│   └── BR280机械臂Python_API说明书.pdf   # 机械臂 API 手册
├── archive/                      # 开发历史存档
│   ├── phase1_initial/           #   早期机械臂控制实验
│   └── phase2_integration/       #   系统集成原型
├── README.md                     # 本文件
├── LICENSE                       # MIT 许可证
└── .gitignore                    # Git 忽略规则
```

---

## ⚙️ 技术栈

| 模块 | 技术 | 说明 |
|------|------|------|
| **目标检测** | YOLOv5s + ONNX | 5 类物体实时检测，320×320 输入 |
| **SLAM 建图** | GMapping | 激光雷达栅格地图构建 |
| **自主导航** | ROS move_base | 全局/局部路径规划与避障 |
| **机械臂控制** | PyMyCobot | 6 轴机械臂控制、夹爪操作 |
| **距离测量** | HC-SR04 超声波 | 精度 < 2cm |
| **图像处理** | OpenCV | 图像预处理与坐标映射 |

---

## 🚀 快速开始

### 环境依赖

- ROS Kinetic / Melodic
- Python 2.7
- MyCobot 机械臂
- USB 摄像头
- 激光雷达（如 RPLIDAR）
- HC-SR04 超声波传感器

### 安装

```bash
git clone https://github.com/your-username/zcw_robuster.git
cd zcw_robuster
chmod +x src/**/*.py
```

### 硬件连接

1. 机械臂通过 USB 连接（默认设备 `/dev/arm`）
2. USB 摄像头连接（默认设备号 2）
3. 超声波传感器 HC-SR04 接线
4. 确保 ROS master 已启动

### 运行

```bash
# 1. 启动 SLAM 建图
roslaunch your_package gmapping.launch

# 2. 启动主检测抓取系统
python src/core/main.py


### 参数配置

核心参数在 `src/core/GrabParams.py` 中调整：

| 参数 | 说明 |
|------|------|
| `ratio` | 像素到实际坐标转换比例 |
| `height_bias` | 机械臂抓取高度偏移 |
| `x_bias` / `y_bias` | X/Y 轴标定偏移 |
| `linear_range_low/high` | 宽度-距离映射区间 |
| `coords_ready` / `coords_finish` | 机械臂归位/完成姿态 |
| `coords_place_apple` / `coords_place_clock` | 物体放置坐标 |

---

## 🧠 核心算法

### 宽度-距离映射

将检测到的物体像素宽度映射为实际距离，支持三种模式：

| 模式 | ID | 说明 |
|------|----|------|
| 三段式 | 0 | 远/中/近三个离散距离档位 |
| 线性映射 | 1 | 在标定区间内线性插值 |
| 阶梯映射 | 2 | 可配置阶梯数量的分段映射 |

### 视觉伺服抓取流程

```
摄像头采集 → YOLO 推理 → 坐标变换 → 机械臂移动 → 超声波确认 → 夹爪抓取
```

### 导航流程

```
加载地图 → 设置目标点 → move_base 导航 → 到达确认 → 视觉搜索 → 抓取
```

---

## 📂 归档说明

`archive/` 目录保留了项目的开发历程：

- **`phase1_initial/`** — 早期机械臂控制和坐标读写实验
- **`phase2_integration/`** — 检测与抓取集成的中间版本
- **`code_left_experiments/`** — 开发过程中探索的不同实现方案

`src/core/` 中的代码为比赛最终版本。


*睿抗机器人大赛 2024 · 自主移动抓取机器人系统*
