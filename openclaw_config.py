#!/usr/bin/env python3
"""
OpenClaw Config Adapter
轻松切换 OpenClaw 大模型配置的可视化工具

用法: python3 openclaw_config.py
然后浏览器打开 http://localhost:7890
"""

import json
import os
import shutil
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"
PORT = 7890

# ─── 内置 Provider 模板 ─────────────────────────────────────────────────────

PROVIDERS = {
    "moonshot": {
        "label": "Moonshot (Kimi)",
        "icon": "🌙",
        "baseUrl": "https://api.moonshot.cn/v1",
        "auth": "api-key",
        "api": "openai-completions",
        "authHeader": False,
        "models": [
            {"id": "kimi-k2.5",           "name": "Kimi K2.5",          "contextWindow": 256000, "maxTokens": 8192},
            {"id": "kimi-latest",         "name": "Kimi Latest",        "contextWindow": 256000, "maxTokens": 8192},
            {"id": "kimi-k1-5",           "name": "Kimi K1.5",          "contextWindow": 128000, "maxTokens": 8192, "reasoning": True},
            {"id": "moonshot-v1-8k",      "name": "Moonshot v1 8K",     "contextWindow": 8000,   "maxTokens": 8000},
            {"id": "moonshot-v1-32k",     "name": "Moonshot v1 32K",    "contextWindow": 32000,  "maxTokens": 8000},
            {"id": "moonshot-v1-128k",    "name": "Moonshot v1 128K",   "contextWindow": 128000, "maxTokens": 8000},
        ],
    },
    "deepseek": {
        "label": "DeepSeek",
        "icon": "🔵",
        "baseUrl": "https://api.deepseek.com/v1",
        "auth": "api-key",
        "api": "openai-completions",
        "authHeader": False,
        "models": [
            {"id": "deepseek-chat",       "name": "DeepSeek V3",        "contextWindow": 64000,  "maxTokens": 8192},
            {"id": "deepseek-reasoner",   "name": "DeepSeek R1",        "contextWindow": 64000,  "maxTokens": 8192, "reasoning": True},
        ],
    },
    "openai": {
        "label": "OpenAI",
        "icon": "🤖",
        "baseUrl": "https://api.openai.com/v1",
        "auth": "api-key",
        "api": "openai-completions",
        "authHeader": False,
        "models": [
            {"id": "gpt-4o",              "name": "GPT-4o",              "contextWindow": 128000, "maxTokens": 16384},
            {"id": "gpt-4o-mini",         "name": "GPT-4o Mini",         "contextWindow": 128000, "maxTokens": 16384},
            {"id": "o1",                  "name": "o1",                  "contextWindow": 200000, "maxTokens": 100000, "reasoning": True},
            {"id": "o1-mini",             "name": "o1 Mini",             "contextWindow": 128000, "maxTokens": 65536,  "reasoning": True},
            {"id": "o3",                  "name": "o3",                  "contextWindow": 200000, "maxTokens": 100000, "reasoning": True},
            {"id": "o3-mini",             "name": "o3-mini",             "contextWindow": 200000, "maxTokens": 100000, "reasoning": True},
        ],
    },
    "anthropic": {
        "label": "Anthropic (Claude)",
        "icon": "🧠",
        "baseUrl": "https://api.anthropic.com/v1",
        "auth": "api-key",
        "api": "anthropic-messages",
        "authHeader": False,
        "models": [
            {"id": "claude-opus-4-6",              "name": "Claude Opus 4.6",          "contextWindow": 200000, "maxTokens": 32000},
            {"id": "claude-sonnet-4-6",            "name": "Claude Sonnet 4.6",        "contextWindow": 200000, "maxTokens": 16000},
            {"id": "claude-opus-4-5-20251101",     "name": "Claude Opus 4.5",          "contextWindow": 200000, "maxTokens": 32000},
            {"id": "claude-sonnet-4-5-20250929",   "name": "Claude Sonnet 4.5",        "contextWindow": 200000, "maxTokens": 16000},
            {"id": "claude-3-5-haiku-20241022",    "name": "Claude 3.5 Haiku",         "contextWindow": 200000, "maxTokens": 8096},
        ],
    },
    "gemini": {
        "label": "Google Gemini",
        "icon": "✨",
        "baseUrl": "https://generativelanguage.googleapis.com/v1beta/openai",
        "auth": "api-key",
        "api": "openai-completions",
        "authHeader": False,
        "models": [
            {"id": "gemini-2.5-pro",         "name": "Gemini 2.5 Pro",        "contextWindow": 1000000, "maxTokens": 65536},
            {"id": "gemini-2.5-flash",        "name": "Gemini 2.5 Flash",       "contextWindow": 1000000, "maxTokens": 65536},
            {"id": "gemini-2.5-flash-lite",   "name": "Gemini 2.5 Flash Lite",  "contextWindow": 1000000, "maxTokens": 32768},
            {"id": "gemini-2.0-flash-001",    "name": "Gemini 2.0 Flash",       "contextWindow": 1048576, "maxTokens": 8192},
        ],
    },
    "openrouter": {
        "label": "OpenRouter",
        "icon": "🔀",
        "baseUrl": "https://openrouter.ai/api/v1",
        "auth": "api-key",
        "api": "openai-completions",
        "authHeader": False,
        "models": [
            {"id": "google/gemini-2.5-pro",                  "name": "Gemini 2.5 Pro",      "contextWindow": 1000000, "maxTokens": 65536},
            {"id": "anthropic/claude-opus-4-6",              "name": "Claude Opus 4.6",     "contextWindow": 200000,  "maxTokens": 32000},
            {"id": "openai/o3",                              "name": "OpenAI o3",           "contextWindow": 200000,  "maxTokens": 100000, "reasoning": True},
            {"id": "openai/gpt-4o",                          "name": "GPT-4o",              "contextWindow": 128000,  "maxTokens": 16384},
            {"id": "deepseek/deepseek-chat",                 "name": "DeepSeek V3",         "contextWindow": 64000,   "maxTokens": 8192},
            {"id": "meta-llama/llama-4-maverick",            "name": "Llama 4 Maverick",    "contextWindow": 524288,  "maxTokens": 16384},
        ],
    },
    "groq": {
        "label": "Groq",
        "icon": "🚀",
        "baseUrl": "https://api.groq.com/openai/v1",
        "auth": "api-key",
        "api": "openai-completions",
        "authHeader": False,
        "models": [
            {"id": "llama-3.3-70b-versatile",       "name": "Llama 3.3 70B",           "contextWindow": 128000, "maxTokens": 32768},
            {"id": "llama-3.1-8b-instant",          "name": "Llama 3.1 8B Instant",    "contextWindow": 128000, "maxTokens": 8192},
            {"id": "deepseek-r1-distill-llama-70b", "name": "DeepSeek R1 Distill 70B", "contextWindow": 128000, "maxTokens": 16384, "reasoning": True},
            {"id": "qwen-2.5-coder-32b",            "name": "Qwen2.5 Coder 32B",       "contextWindow": 128000, "maxTokens": 16384},
            {"id": "gemma2-9b-it",                  "name": "Gemma2 9B",               "contextWindow": 8192,   "maxTokens": 8192},
        ],
    },
    "siliconflow": {
        "label": "SiliconFlow",
        "icon": "🌊",
        "baseUrl": "https://api.siliconflow.cn/v1",
        "auth": "api-key",
        "api": "openai-completions",
        "authHeader": False,
        "models": [
            {"id": "Qwen/Qwen3-235B-A22B-Instruct-2507", "name": "Qwen3 235B MoE",    "contextWindow": 131072, "maxTokens": 16384},
            {"id": "Qwen/Qwen2.5-72B-Instruct",          "name": "Qwen2.5 72B",        "contextWindow": 131072, "maxTokens": 8192},
            {"id": "deepseek-ai/DeepSeek-V3",            "name": "DeepSeek V3",        "contextWindow": 64000,  "maxTokens": 8192},
            {"id": "deepseek-ai/DeepSeek-R1",            "name": "DeepSeek R1",        "contextWindow": 64000,  "maxTokens": 8192, "reasoning": True},
            {"id": "Qwen/QwQ-32B",                       "name": "QwQ-32B",            "contextWindow": 131072, "maxTokens": 8192, "reasoning": True},
        ],
    },
    "zhipu": {
        "label": "智谱 ZhipuAI",
        "icon": "🇨🇳",
        "baseUrl": "https://open.bigmodel.cn/api/paas/v4",
        "auth": "api-key",
        "api": "openai-completions",
        "authHeader": False,
        "models": [
            {"id": "glm-4-plus",      "name": "GLM-4 Plus",     "contextWindow": 128000,  "maxTokens": 4096},
            {"id": "glm-4-long",      "name": "GLM-4 Long",     "contextWindow": 1000000, "maxTokens": 4096},
            {"id": "glm-4-flash",     "name": "GLM-4 Flash",    "contextWindow": 128000,  "maxTokens": 4096},
            {"id": "glm-z1-preview",  "name": "GLM Z1 (推理)",  "contextWindow": 32000,   "maxTokens": 4096, "reasoning": True},
        ],
    },
    "ollama": {
        "label": "Ollama (本地)",
        "icon": "🦙",
        "baseUrl": "http://localhost:11434/v1",
        "auth": "none",
        "api": "openai-completions",
        "authHeader": False,
        "models": [
            {"id": "llama4",       "name": "Llama 4",       "contextWindow": 524288, "maxTokens": 8192},
            {"id": "llama3.3",     "name": "Llama 3.3 70B", "contextWindow": 131072, "maxTokens": 8192},
            {"id": "qwen3",        "name": "Qwen3",         "contextWindow": 131072, "maxTokens": 8192},
            {"id": "deepseek-r1",  "name": "DeepSeek R1",   "contextWindow": 32768,  "maxTokens": 4096, "reasoning": True},
            {"id": "gemma3",       "name": "Gemma 3",       "contextWindow": 131072, "maxTokens": 8192},
            {"id": "phi4",         "name": "Phi-4",         "contextWindow": 16384,  "maxTokens": 4096},
        ],
    },
    "custom": {
        "label": "自定义 OpenAI 兼容",
        "icon": "⚙️",
        "baseUrl": "",
        "auth": "api-key",
        "api": "openai-completions",
        "authHeader": False,
        "models": [],
    },
}

# ─── HTML 前端 ──────────────────────────────────────────────────────────────

HTML_PATH = Path(__file__).parent / "index.html"


def read_html() -> str:
    """从 index.html 读取前端页面（每次请求都重新读，改HTML无需重启）"""
    if not HTML_PATH.exists():
        return "<h1>找不到 index.html，请确保它与 openclaw_config.py 在同一目录</h1>"
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        return f.read()


# ─── HTTP Server ────────────────────────────────────────────────────────────

def read_config():
    """读取 openclaw.json，返回 dict。
    openclaw.json 实际上是标准 JSON，直接解析即可。
    仅在 JSONDecodeError 时尝试去掉行注释（兼容 JSON5）。
    """
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # 仅对真正的行注释做处理：只去掉以 // 开头（前面没有 : 或引号）的注释行
        import re
        # 只匹配行首的 // 注释（宽松版）
        stripped = re.sub(r'^\s*//[^\n]*', '', content, flags=re.MULTILINE)
        return json.loads(stripped)


def write_config(cfg: dict):
    """备份后写入 openclaw.json"""
    if CONFIG_PATH.exists():
        # 找一个不重复的备份名
        ts = time.strftime("%Y%m%d_%H%M%S")
        bak = CONFIG_PATH.parent / f"openclaw.json.bak.tool.{ts}"
        shutil.copy2(CONFIG_PATH, bak)
        print(f"[backup] {bak}")
    # 原子写：先写临时文件，再 replace，避免崩溃导致半写入 JSON
    tmp = CONFIG_PATH.with_suffix(CONFIG_PATH.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, CONFIG_PATH)
    print(f"[write ] {CONFIG_PATH}")

def redact_config(cfg):
    """脱敏返回给前端的配置（不包含任何 API key）。"""
    if isinstance(cfg, dict):
        out = {}
        for k, v in cfg.items():
            if k == "apiKey":
                continue
            out[k] = redact_config(v)
        return out
    if isinstance(cfg, list):
        return [redact_config(x) for x in cfg]
    return cfg


def is_same_origin_request(handler: BaseHTTPRequestHandler) -> bool:
    """仅允许同源页面发起写操作，降低 localhost CSRF 风险。
    同源 fetch 通常带 Origin；命令行/脚本可能不带 Origin，这里也允许。
    """
    origin = handler.headers.get("Origin")
    if not origin:
        return True
    allowed = {f"http://localhost:{PORT}", f"http://127.0.0.1:{PORT}"}
    return origin in allowed


def validate_switch_payload(payload: dict):
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    for key in ("provider", "modelId", "baseUrl"):
        if key not in payload:
            raise ValueError(f"missing field: {key}")
    provider = payload["provider"]
    if not isinstance(provider, str) or not provider.strip():
        raise ValueError("provider must be a non-empty string")
    model_id = payload["modelId"]
    if not isinstance(model_id, str) or not model_id.strip():
        raise ValueError("modelId must be a non-empty string")
    base_url = payload["baseUrl"]
    if not isinstance(base_url, str) or not base_url.strip():
        raise ValueError("baseUrl must be a non-empty string")

    parsed = urlparse(base_url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("baseUrl must be a valid http(s) URL")

    # Provider 允许内置模板或 custom；其他一律拒绝，避免随意污染配置结构
    if provider not in PROVIDERS:
        raise ValueError(f"unsupported provider: {provider}")


def apply_switch(payload: dict) -> dict:
    """根据前端 payload 更新配置，返回新配置"""
    cfg = read_config()

    validate_switch_payload(payload)
    provider = payload["provider"].strip()
    model_id = payload["modelId"].strip()
    base_url = payload["baseUrl"].strip()
    api_key = payload.get("apiKey")     # None 表示不更改
    api_type = payload.get("api", "openai-completions")
    auth_header = payload.get("authHeader", False)
    desired_auth = payload.get("auth")  # "api-key" | "none" (由前端根据 provider 模板传入)
    models = payload.get("models", [])

    # ── models.providers ──
    cfg.setdefault("models", {})
    cfg["models"].setdefault("mode", "merge")
    cfg["models"].setdefault("providers", {})

    existing_prov = cfg["models"]["providers"].get(provider, {})

    # 构建新 provider 配置
    # auth 选择：优先使用前端传入的模板值；若用户提供了 apiKey，则强制 api-key
    auth_mode = desired_auth if desired_auth in ("api-key", "none") else existing_prov.get("auth") or PROVIDERS.get(provider, {}).get("auth") or "api-key"
    if api_key:
        auth_mode = "api-key"

    new_prov = {
        "baseUrl": base_url,
        "auth": auth_mode,
        "api": api_type,
        "authHeader": auth_header,
        "models": [
            {
                "id": m["id"],
                "name": m.get("name", m["id"]),
                "reasoning": m.get("reasoning", False),
                "input": m.get("input", ["text", "image"]),
                "cost": m.get("cost", {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0}),
                "contextWindow": m.get("contextWindow", 128000),
                "maxTokens": m.get("maxTokens", 8192),
            }
            for m in models
        ],
    }

    # API Key：只有明确提供才更新
    if api_key:
        new_prov["apiKey"] = api_key
    elif "apiKey" in existing_prov:
        new_prov["apiKey"] = existing_prov["apiKey"]

    cfg["models"]["providers"][provider] = new_prov

    # ── auth.profiles ──
    # 仅在需要 api-key 的 provider 上写入 profile；避免把 auth=none 的 provider 强行写成 api_key
    if auth_mode != "none":
        cfg.setdefault("auth", {}).setdefault("profiles", {})
        cfg["auth"]["profiles"][f"{provider}:default"] = {
            "provider": provider,
            "mode": "api_key",
        }

    # ── agents.defaults.model ──
    primary = f"{provider}/{model_id}"
    cfg.setdefault("agents", {}).setdefault("defaults", {})
    cfg["agents"]["defaults"].setdefault("model", {})
    cfg["agents"]["defaults"]["model"]["primary"] = primary

    # ── agents.defaults.models (alias) ──
    cfg["agents"]["defaults"].setdefault("models", {})
    model_info = next((m for m in models if m["id"] == model_id), None)
    alias = model_info.get("name", model_id) if model_info else model_id
    cfg["agents"]["defaults"]["models"][primary] = {"alias": alias}

    # ── meta ──
    from datetime import datetime, timezone
    cfg.setdefault("meta", {})
    cfg["meta"]["lastTouchedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    write_config(cfg)
    return cfg, primary


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[http ] {self.address_string()} {format % args}")

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, html: str):
        body = html.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        # 不启用跨站 CORS：避免任意网页读写 localhost 配置
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self.send_html(read_html())
        elif path == "/api/config":
            try:
                self.send_json(redact_config(read_config()))
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
        elif path == "/api/providers":
            self.send_json(PROVIDERS)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body) if body else {}
        except Exception:
            self.send_json({"error": "invalid JSON"}, 400)
            return

        if path == "/api/switch":
            try:
                if not is_same_origin_request(self):
                    self.send_json({"error": "forbidden"}, 403)
                    return
                cfg, primary = apply_switch(payload)
                self.send_json({"ok": True, "primary": primary, "config": redact_config(cfg)})
            except Exception as e:
                import traceback
                traceback.print_exc()
                msg = str(e) or "error"
                # 基本输入问题返回 400，避免前端看到 500
                if isinstance(e, ValueError):
                    self.send_json({"error": msg}, 400)
                else:
                    self.send_json({"error": msg}, 500)
        else:
            self.send_response(404)
            self.end_headers()


# ─── Main ──────────────────────────────────────────────────────────────────

def main():
    if not CONFIG_PATH.exists():
        print(f"⚠️  未找到配置文件: {CONFIG_PATH}")
        print("   请先运行 OpenClaw 完成初始设置，再使用本工具。")
        return

    server = HTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://localhost:{PORT}"
    print(f"🦞 OpenClaw 大模型切换器")
    print(f"   配置文件: {CONFIG_PATH}")
    print(f"   监听地址: {url}")
    print(f"   按 Ctrl+C 退出\n")

    # 自动打开浏览器
    import threading, webbrowser
    threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已退出。")


if __name__ == "__main__":
    main()
