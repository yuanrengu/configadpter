<div align="right">

[English](README.md)

</div>

<div align="center">

# 🦞 OpenClaw 大模型切换器

**OpenClaw LLM Model Switcher**

一个轻量级 Web 工具，通过浏览器界面轻松切换 [OpenClaw](https://openclaw.ai) 的大模型配置，无需手动编辑 JSON 文件。

*A lightweight web-based tool to easily switch LLM providers and models for OpenClaw — no JSON editing required.*

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey)

</div>

---

## 截图

<div align="center">

![首页 — 当前配置状态与 Provider 选择](docs/screenshot_home.png)

*首页：实时显示当前模型，一键选择 Provider*

![切换到 DeepSeek — 配置表单](docs/screenshot_deepseek.png)

*切换 Provider 后，自动填充 Base URL 和模型列表*

</div>

---

## 🚀 快速开始

**前提：已安装并配置过 [OpenClaw](https://openclaw.ai)**（需存在 `~/.openclaw/openclaw.json`）

```bash
# 克隆项目
git clone https://github.com/<your-username>/openclaw-model-switcher.git
cd openclaw-model-switcher

# 启动工具（零依赖，直接运行）
python3 openclaw_config.py
# 浏览器会自动打开 http://localhost:7890
```

```bash
# 停止：终端内按 Ctrl+C
# 若进程已在后台，可用以下命令终止：
lsof -ti :7890 | xargs kill -9
```

> **Requirements**: Python 3.8+，仅用标准库，无需 `pip install` 任何依赖。

---

## 功能特性

| 功能 | 说明 |
|------|------|
| 📊 当前状态一览 | 实时显示当前 provider、model、base URL 及 OpenClaw 版本 |
| 🎛️ Provider 快速切换 | 点击卡片即可选择，自动填入 Base URL 和模型列表 |
| 🔑 API Key 保护 | 留空则保留已有 Key，不会被清空或覆盖 |
| 🗂️ 模型管理 | 从模板中选择，或手动输入自定义模型 ID |
| 💾 自动备份 | 每次应用前自动备份，格式 `openclaw.json.bak.tool.YYYYMMDD_HHMMSS` |
| 🔍 预览 JSON | 应用前可预览将写入的配置片段 |
| ♻️ 热重载前端 | 修改 `index.html` 后刷新浏览器即生效，无需重启服务 |

---

## 支持的 Provider

| Provider | Base URL | 说明 |
|----------|----------|------|
| 🌙 Moonshot (Kimi) | `api.moonshot.cn` | 国内可用，kimi-k2.5 等 |
| 🔵 DeepSeek | `api.deepseek.com` | 高性价比，国内可用 |
| 🤖 OpenAI | `api.openai.com` | GPT-4o, o1, o3-mini |
| 🧠 Anthropic | `api.anthropic.com` | Claude Opus/Sonnet/Haiku |
| 🔀 OpenRouter | `openrouter.ai/api` | 多模型聚合路由 |
| ⚡ SiliconFlow | `api.siliconflow.cn` | 国内多模型加速平台 |
| 🇨🇳 ZhipuAI | `open.bigmodel.cn` | GLM-4 系列 |
| 🦙 Ollama | `localhost:11434` | 本地离线运行的模型 |
| ⚙️ 自定义 | 任意 URL | 任意 OpenAI 兼容接口 |

---

## 工作原理

切换模型时，工具会**先备份**当前配置，然后**仅修改** `~/.openclaw/openclaw.json` 中以下 4 个字段区域：

### 修改的 4 个区域

```
models.providers.<provider>          ← 重建目标 provider 的连接配置
auth.profiles.<provider>:default     ← 添加/更新认证 profile
agents.defaults.model.primary        ← 替换为 "provider/modelId"（核心字段）
agents.defaults.models.<primary>     ← 添加模型 alias（显示名称）
```

**API Key 的处理**：若输入框留空，则从已有配置继承，Key 不会丢失。

### 完全不会触碰的区域

```
channels.*    ← Telegram / Discord 等频道配置
gateway.*     ← 端口、auth token、节点设置
tools.*       ← 工具 profile
commands.*    ← 命令行设置
session.*     ← 会话配置
hooks.*       ← 内部 hook 配置
wizard.*      ← 向导状态
其他 provider 的配置
```

### 界面版本号说明

右上角显示的版本号（如 `v2026.3.2`）来自 `meta.lastTouchedVersion`，由 OpenClaw 自身维护，本工具只读取展示，不会修改。

### 配置生效与重启

**通常无需重启**：OpenClaw Gateway 会自动监视 `openclaw.json` 的变化。每次你通过本工具应用配置（更新了 `primary` 等字段），OpenClaw 都能**热重载并立即生效**。

> *注：只有在切换到之前**从未配置过的新 Provider** 时，OpenClaw 可能需要一点时间初始化新连接。如果发现新模型没有立即生效，可在 OpenClaw Web 控制台确认，或手动重启一次 OpenClaw 进程。*

---

## 使用示例

### 切换到 DeepSeek
1. 点击 **🔵 DeepSeek** 卡片
2. 填入 DeepSeek API Key（`sk-...`）
3. 选择模型（如 DeepSeek Chat V3）
4. 点击 **✅ 应用配置**

### 切回 Moonshot（已配置过）
1. 点击 **🌙 Moonshot (Kimi)** 卡片（显示 "✓ 当前"）
2. API Key 留空（自动继承已有 Key）
3. 选择模型，点击应用

### 接入任意 OpenAI 兼容接口
1. 点击 **⚙️ 自定义** 卡片
2. 填写 Base URL（如 `https://your-api.com/v1`）和 API Key
3. 在下方输入模型 ID 和显示名称，点击 **添加**
4. 选中该模型，点击应用

---

## 项目结构

```
.
├── openclaw_config.py   # 后端：Provider 模板 + HTTP 服务器 + 配置读写逻辑
├── index.html           # 前端：Web UI（HTML / CSS / JS，深色主题）
├── docs/
│   ├── screenshot_home.png
│   └── screenshot_deepseek.png
└── README.md
```

**OpenClaw 相关路径：**
- 配置文件：`~/.openclaw/openclaw.json`
- 备份目录：`~/.openclaw/openclaw.json.bak.tool.*`

---

## 安全说明

- 服务仅监听本地 `127.0.0.1:7890`，不对外网暴露
- 每次写入前自动备份，随时可从 `~/.openclaw/` 恢复
- API Key 不预填到表单、不打印到终端日志

---

## License

[MIT](LICENSE)
