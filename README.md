# gameops-agent-test-platform

## 项目背景

`gameops-agent-test-platform` 是一个面向测试开发 / SDET 实习简历展示的后端项目。项目核心场景是“游戏运营活动配置与质量保障平台”，用于逐步沉淀活动配置、质量校验、接口测试、性能测试与测试报告能力。

当前为 Day 1，只完成 FastAPI 基础服务、健康检查接口、项目配置与基础测试，不包含活动、奖励、Agent、JMeter 等后续功能实现。

## 技术栈

- Python 3.9+
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy
- Pytest
- Pytest-Cov
- HTTPX
- Allure Pytest

## 本地启动方式

创建并激活虚拟环境：

```bash
python -m venv .venv
.venv\Scripts\activate
```

安装依赖：

```bash
python -m pip install -e ".[dev]"
```

启动服务：

```bash
uvicorn app.main:app --reload
```

健康检查：

```bash
curl http://127.0.0.1:8000/api/health
```

期望返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "status": "ok"
  }
}
```

## 测试运行方式

运行全部测试：

```bash
python -m pytest -q
```

运行覆盖率测试：

```bash
python -m pytest --cov=app
```
