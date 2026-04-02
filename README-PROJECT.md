# AI代码审查平台 - 项目结构分析

## 📋 项目概述

**AI-Codereview-Gitlab** 是一个基于大模型的自动化代码审查工具，支持 GitLab、GitHub 和 Gitea 平台，能够自动对提交的代码进行智能审查。

## 🏗️ 项目架构

### 1. 核心目录结构

```
AI-Codereview-Gitlab/
├── api.py              # API服务入口
├── ui.py               # Streamlit Dashboard界面
├── biz/                # 核心业务逻辑
│   ├── api/           # API路由处理
│   ├── cmd/           # 命令行工具
│   ├── entity/        # 数据实体
│   ├── event/         # 事件管理
│   ├── llm/           # LLM客户端
│   ├── platforms/     # 平台适配
│   ├── queue/         # 队列处理
│   ├── service/       # 业务服务
│   └── utils/         # 工具类
├── conf/              # 配置文件
├── data/              # 数据存储
├── doc/               # 文档
├── fonts/             # 字体文件
├── log/               # 日志目录
└── scripts/           # 部署脚本
```

### 2. 核心模块分析

#### **API服务层 (`api.py`)**
- Flask应用入口，负责接收Webhook请求
- 端口配置：默认5001
- 集成定时任务调度器

#### **用户界面层 (`ui.py`)**
- 基于Streamlit的可视化Dashboard
- 用户认证系统
- 数据统计和图表展示
- 支持项目、开发者、时间范围的筛选

#### **业务逻辑层 (`biz/`)**

**LLM客户端 (`biz/llm/client/`)**
- 支持多种大模型：DeepSeek、OpenAI、ZhipuAI、Qwen、Ollama、Anthropic
- 统一的客户端工厂模式

**平台适配层 (`biz/platforms/`)**
- GitLab、GitHub、Gitea三个平台的Webhook处理
- 统一的接口设计，便于扩展

**代码审查核心 (`biz/utils/code_reviewer.py`)**
- 基于模板的提示词系统
- 支持4种审查风格：专业型、讽刺型、温和型、幽默型
- 自动评分机制

**数据服务层 (`biz/service/review_service.py`)**
- SQLite数据库管理
- 审查日志的增删改查
- 数据统计分析

#### **配置管理 (`conf/`)**
- 环境变量配置模板
- 提示词模板配置
- 定时任务配置

## 🔧 功能特性

### 1. 多平台支持
- **GitLab**: 完整的Merge Request和Push事件处理
- **GitHub**: Pull Request和Push事件支持  
- **Gitea**: 开源Git服务适配

### 2. 审查风格多样化
- **专业型** 🤵: 严谨专业的技术评审
- **讽刺型** 😈: 毒舌吐槽，增加趣味性
- **温和型** 🌸: 温柔建议，鼓励式反馈
- **幽默型** 🤪: 幽默点评，轻松氛围

### 3. 消息通知集成
- 钉钉机器人
- 企业微信
- 飞书
- 自定义Webhook

### 4. 数据可视化
- 项目提交统计
- 开发者活跃度分析
- 代码质量评分趋势
- 代码行数变化图表

## 📊 数据库设计

### 主要表结构
1. **mr_review_log**: Merge Request审查日志
2. **push_review_log**: Push事件审查日志

### 关键字段
- 项目名称、开发者、分支信息
- 审查分数、结果详情
- 代码变更行数统计
- 时间戳索引

## ⚙️ 配置项分析

### 核心配置参数
- **LLM_PROVIDER**: 大模型供应商选择
- **SUPPORTED_EXTENSIONS**: 支持审查的文件类型
- **REVIEW_STYLE**: 审查风格设置
- **PUSH_REVIEW_ENABLED**: Push事件审查开关
- **DASHBOARD_USER/PASSWORD**: 管理界面认证

## 🚀 部署方式

### 1. Docker部署
```bash
docker-compose up -d
```

### 2. 本地Python环境部署
```bash
pip install -r requirements.txt
python api.py  # API服务
streamlit run ui.py  # Dashboard
```

## 🔍 无用文件分析

### 1. **测试文件** (可删除)
- `biz/platforms/*/test_webhook_handler.py`: 单元测试文件，在生产环境中非必需

### 2. **开发环境文件** (建议gitignore)
- `venv/`: Python虚拟环境目录，建议在.gitignore中排除
- `.github/`: GitHub相关配置，仅对开源项目有用

### 3. **字体文件** (可选删除)
- `fonts/SourceHanSansCN-Regular.otf`: 中文字体文件，7.95MB较大，对核心功能非必需

### 4. **文档图片** (可删除)
- `doc/img/`: 文档图片文件，对核心功能非必需

## 📁 详细文件结构

### 核心文件
- `api.py` - 主API服务入口
- `ui.py` - 用户界面Dashboard
- `biz/` - 核心业务逻辑目录
- `conf/` - 配置文件目录

### 业务模块
- `biz/api/` - API路由和控制器
- `biz/entity/` - 数据模型实体
- `biz/event/` - 事件处理机制
- `biz/llm/` - 大模型客户端
- `biz/platforms/` - 平台适配器
- `biz/queue/` - 异步任务队列
- `biz/service/` - 业务服务层
- `biz/utils/` - 工具类函数

### 配置文件
- `conf/.env.dist` - 环境变量模板
- `conf/config.yml` - 应用配置
- `conf/prompt_templates.yml` - 提示词模板

### 依赖管理
- `requirements.txt` - Python依赖包
- `Dockerfile` - Docker镜像构建
- `docker-compose.yml` - Docker编排

## 🎯 项目优势

1. **架构清晰**: 模块化设计，职责分离明确
2. **扩展性强**: 支持多平台、多模型，易于定制
3. **用户体验好**: 可视化Dashboard，多种审查风格
4. **部署灵活**: 支持Docker和本地部署
5. **文档完善**: 详细的使用说明和FAQ

## 💡 改进建议

1. **配置文件管理**: 可以考虑使用更安全的配置管理方式
2. **数据库优化**: SQLite适合小规模使用，大规模可考虑迁移到PostgreSQL
3. **缓存机制**: 可添加Redis缓存提升性能
4. **监控告警**: 增加系统健康检查和告警机制

## 📊 项目统计

- **总文件数**: 57个Python文件
- **核心模块**: 9个主要业务模块
- **支持平台**: 3个代码托管平台
- **支持模型**: 6个大模型供应商
- **审查风格**: 4种不同审查风格

---

*最后更新: 2026年4月2日*
*项目版本: AI代码审查平台 v1.0*