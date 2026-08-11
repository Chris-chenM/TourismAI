# TourismAI — 智能旅游规划助手

一个基于 **LLM Agent + 地图工具调用 + 约束规划** 的智能旅游规划系统。

用户输入：

* 目的地
* 出行天数
* 预算
* 兴趣偏好

系统通过 AI Agent 调用地图服务，自动搜索景点、规划路线，并生成结构化旅行方案。

---

# 当前版本

## Sprint 1 — AI旅游规划 Agent MVP

目标：

> 打通「用户需求 → LLM Agent → 工具调用 → 生成旅行计划」完整闭环。

当前实现：

✅ FastAPI 后端
✅ LangGraph Agent 编排
✅ DeepSeek/OpenAI兼容模型调用
✅ 高德地图 API Tool
✅ POI 景点搜索
✅ 地理编码
✅ 路线规划
✅ Swagger API 调试
✅ 简单 HTML Demo 页面
✅ React 前端（高德地图可视化 + 时间线）

暂未实现：

❌ 用户系统
❌ 数据库存储
❌ 酒店/火车票查询
❌ 浏览器 Agent
❌ 多 Agent 协作

---

## Sprint 2 — 产品化基础

目标：

> 完善前端体验，支持实时进度反馈。

当前实现：

✅ React 前端
✅ 高德地图可视化
✅ 行程时间线
✅ SSE 实时进度推送（analyzing → searching_poi → routing → generating_plan → done）

---

# 系统架构

```
                 用户
                  |
                  |
             React 前端 / Demo
                  |
        ┌─────────┴─────────┐
        |                   |
    POST /api/plan     POST /api/plan/stream
     (同步)              (SSE 流式推送)
        |                   |
        └─────────┬─────────┘
                  |
              FastAPI
                  |
                  |
            LangGraph Agent
                  |
           ┌──────┴──────┐
          |                |
        LLM             Tools
     DeepSeek          高德Tool
                          |
                    高德地图API
                          |
                    POI / 路线数据
                          |
                    JSON旅行计划
```

---

# 技术栈

## 后端

| 技术           | 用途        |
| ------------- | ---------- |
| FastAPI       | Web API 服务 |
| LangGraph     | Agent流程编排  |
| LangChain     | Tool封装     |
| httpx         | 调用外部API    |
| Pydantic      | 数据校验       |
| python-dotenv | 环境变量管理     |

## 前端

| 技术 | 用途 |
| ---- | ---- |
| React 18 | UI 框架 |
| TypeScript | 类型安全 |
| Vite | 构建工具 |
| TailwindCSS | 样式 |
| Zustand | 状态管理 |
| React Query | 数据请求 |
| React Hook Form + Zod | 表单校验 |
| @amap/amap-jsapi-loader | 高德地图 |

## AI模型

支持所有 OpenAI API 格式兼容模型：

目前推荐：

* DeepSeek Chat
* 通义千问
* OpenAI GPT

配置：

```
LLM_BASE_URL
LLM_API_KEY
LLM_MODEL
```

---

# 项目结构

```
tourismai/
│
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI入口
│   │   │
│   │   ├── api/
│   │   │   ├── planning.py      # 行程生成接口（同步 + SSE流式）
│   │   │   └── settings.py      # 配置接口
│   │   │
│   │   ├── agents/
│   │   │   ├── planner.py       # LangGraph Agent + SSE流式执行器
│   │   │   ├── state.py         # Agent状态
│   │   │   └── prompts.py       # System Prompt
│   │   │
│   │   ├── tools/
│   │   │   ├── amap.py          # 高德工具
│   │   │   └── base.py          # Tool接口
│   │   │
│   │   ├── services/
│   │   │   └── amap_client.py   # 高德HTTP客户端
│   │   │
│   │   └── core/
│   │       └── config.py        # 配置管理
│   │
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                    # React 前端
│   ├── src/
│   │   ├── api/                 # API 请求（含 SSE 流式）
│   │   ├── components/          # 组件（地图/时间线/表单/进度）
│   │   ├── hooks/               # 自定义 Hook
│   │   ├── pages/               # 页面
│   │   ├── router/              # 路由
│   │   ├── store/               # Zustand 状态
│   │   └── types/               # TypeScript 类型
│   ├── package.json
│   └── .env.example
│
├── demo/
│   └── index.html               # 简单测试页面
│
└── README.md
```

---

# 环境配置

## 后端

### 1. 创建虚拟环境

```bash
python -m venv venv
```

激活：

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

### 2. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
```

修改 `.env`：

```env
# LLM配置
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_API_KEY=your_api_key
LLM_MODEL=deepseek-chat

# 高德地图
AMAP_KEY=your_amap_key

# 开发模式
MOCK_AMAP=false
```

---

## 前端

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

修改 `.env` 填入高德 Web JS API Key（与后端 AMAP_KEY 不同，需单独申请）：

```env
VITE_AMAP_WEB_KEY=your_amap_web_key_here
```

### 3. 启动

```bash
npm run dev
```

启动成功：

```
http://localhost:5173
```

---

# 启动服务

进入：

```bash
cd backend
```

运行：

```bash
uvicorn app.main:app --reload
```

启动成功：

```
http://127.0.0.1:8000
```

---

# API接口

## 生成旅行计划（同步）

POST:

```
/api/plan
```

请求：

```json
{
    "destination":"杭州",
    "days":3,
    "budget":2000,
    "interests":"历史文化、美食"
}
```

返回：

```json
{
    "destination":"杭州",
    "itinerary":[
        {
            "day":1,
            "activities":[
                {
                    "name":"西湖",
                    "location":"杭州西湖",
                    "description":"..."
                }
            ]
        }
    ]
}
```

---

## 生成旅行计划（SSE 流式）

POST:

```
/api/plan/stream
```

请求体同上。通过 SSE（Server-Sent Events）实时推送 Agent 执行进度：

```
event: phase
data: {"phase":"analyzing","message":"正在分析需求…","progress":10}

event: phase
data: {"phase":"searching_poi","message":"正在搜索景点…","progress":30}

event: phase
data: {"phase":"routing","message":"正在计算路线…","progress":50}

event: phase
data: {"phase":"generating_plan","message":"正在生成旅行计划…","progress":70}

event: result
data: {"destination":"杭州","days":3,"itinerary":[...]}

event: error
data: {"message":"规划失败：..."}
```

| phase | progress | 含义 |
| ----- | -------- | ---- |
| `analyzing` | 10% | LLM 首次分析用户需求 |
| `searching_poi` | 30% | 调用高德搜索景点 / 地理编码 |
| `routing` | 50% | 计算景点间交通路线 |
| `generating_plan` | 70% | LLM 整理生成最终旅行方案 |
| `done` | 100% | 推送 `result` 事件，包含完整 JSON |

---

# Agent工作流程

```
用户需求
→
Planner Agent
→
分析旅游约束
→
调用工具

    ├── search_poi
    |
    ├── geocode
    |
    └── route_plan

→
LLM整理
→
结构化旅行方案
```

---

# 高德工具

当前提供：

## search_poi

功能：

搜索景点、餐厅、酒店等 POI。

输入：

```
关键词
城市
```

---

## geocode

功能：

地址转换为经纬度。

例如：

```
西湖
→
120.15,30.24
```

---

## route_plan

功能：

计算地点之间交通路线。

---

# 开发原则

## 1. Agent负责决策，不负责底层执行

正确：

```
Agent
→
调用Tool
→
获取数据
```

错误：

```
Agent自己爬网页
Agent自己处理数据库
```

---

## 2. 所有外部能力工具化

未来扩展：

```
tools/
├── amap.py
├── train.py
├── hotel.py
└── browser.py
```

---

# 后续开发计划

## Sprint 3

目标：

多数据源

计划：

* 酒店查询
* 火车票查询
* 数据库
* 用户旅行记录

---

## Sprint 4

目标：

Agent增强

计划：

* browser-use接入
* 12306自动查询
* 携程网页Agent
* Human-in-the-loop验证码处理

---

# 设计理念

本项目不是简单的旅游问答机器人。

目标是构建：

> 一个能够理解用户需求、调用外部工具、获取真实世界数据并完成规划任务的旅游 Agent。

核心能力：

```
LLM推理
+
Tool调用
+
真实数据
+
任务规划
```

---

# License

MIT License
