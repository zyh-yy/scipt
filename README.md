# 脚本管控平台 (Script Management Platform)

一个功能完善的脚本管理和自动化执行平台，支持多种脚本语言，参数化执行和脚本链接。本平台是一个本科毕业设计项目，实现了脚本上传、执行、链式调用等功能。

## 项目概述

脚本管控平台是一个集中式的脚本管理解决方案，它允许用户：

- 上传、管理和执行各种类型的脚本（Python、Shell、Batch、PowerShell、JavaScript）
- 为脚本配置自定义参数
- 将多个脚本链接在一起按顺序执行，前一个脚本的输出可作为后一个脚本的输入
- 查看脚本执行历史和结果
- 通过直观的Web界面管理所有功能

## 系统特点

- **多类型脚本支持**：支持Python (.py)、Shell (.sh)、Batch (.bat)、PowerShell (.ps1)和JavaScript (.js)脚本
- **参数化执行**：支持为脚本配置多种类型的参数（字符串、数字、布尔值、选择项）
- **脚本链执行**：支持创建脚本链，按顺序执行多个脚本
- **链式数据传递**：前一个脚本的输出可以作为后一个脚本的输入
- **执行历史记录**：记录所有脚本执行的历史，包括输入参数、输出结果和错误信息
- **安全执行机制**：脚本执行时间限制和错误处理
- **响应式界面**：基于Vue.js和Element UI的现代化Web界面
- **低耦合高内聚**：模块化设计，易于扩展和维护

## 技术架构

### 后端架构
- **编程语言**：Python
- **Web框架**：Flask
- **数据库**：SQLite
- **API设计**：RESTful API
- **跨域支持**：Flask-CORS

### 前端架构
- **框架**：Vue.js 2.x
- **UI库**：Element UI
- **状态管理**：Vuex
- **路由管理**：Vue Router
- **HTTP客户端**：Axios

### 系统架构图

```
┌─────────────┐    HTTP/REST    ┌─────────────┐     ┌─────────────┐
│   前端      │<--------------->│   后端      │<--->│  SQLite     │
│  (Vue.js)   │                 │  (Flask)    │     │  数据库     │
└─────────────┘                 └─────────────┘     └─────────────┘
                                      │
                                      │ 执行
                                      ▼
                               ┌─────────────┐
                               │  脚本执行器  │
                               └─────────────┘
                                      │
                                      │ 调用
                                      ▼
                               ┌─────────────┐
                               │ 用户脚本文件 │
                               └─────────────┘
```

## 安装与配置

### 系统要求
- Python 3.6+
- Node.js 12+
- npm 6+

### 后端安装
1. 克隆仓库并进入项目目录
```bash
git clone <repository_url>
cd script-management-platform
```

2. 创建并激活Python虚拟环境（推荐）
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

3. 安装后端依赖
```bash
pip install -r requirements.txt
```

4. 启动后端服务
```bash
cd backend
python app.py
```
后端服务将在 http://localhost:5000 上运行

### 前端安装
1. 进入前端目录
```bash
cd frontend
```

2. 安装前端依赖
```bash
npm install
```

3. 开发模式启动前端服务
```bash
npm run serve
```
前端开发服务将在 http://localhost:8080 上运行

4. 构建生产版本
```bash
npm run build
```
构建完成后，生产文件将输出到 `dist` 目录

## 使用指南

### 脚本管理

1. **添加新脚本**
   - 点击"脚本管理"页面中的"添加脚本"按钮
   - 输入脚本名称和描述
   - 上传脚本文件（支持.py, .sh, .bat, .ps1, .js）
   - 配置脚本参数（如果需要）
   - 点击"保存"按钮完成添加

2. **编辑脚本**
   - 在脚本列表中找到目标脚本
   - 点击"编辑"按钮
   - 修改名称、描述或参数
   - 点击"保存"按钮完成编辑

3. **删除脚本**
   - 在脚本列表中找到目标脚本
   - 点击"删除"按钮
   - 确认删除操作

### 脚本执行

1. **执行单个脚本**
   - 在脚本列表或详情页面中找到目标脚本
   - 点击"执行"按钮
   - 输入必要的参数
   - 点击"执行"按钮开始执行
   - 查看执行结果

### 脚本链管理

1. **创建脚本链**
   - 点击"脚本链管理"页面中的"添加脚本链"按钮
   - 输入脚本链名称和描述
   - 点击"添加脚本"按钮选择要添加的脚本
   - 通过上下移动按钮调整脚本执行顺序
   - 点击"保存"按钮完成创建

2. **执行脚本链**
   - 在脚本链列表或详情页面中找到目标脚本链
   - 点击"执行"按钮
   - 输入必要的参数
   - 点击"执行"按钮开始执行
   - 查看每个脚本的执行结果

### 执行历史查看

1. **查看执行历史列表**
   - 点击导航栏中的"执行历史"
   - 查看所有脚本和脚本链的执行记录

2. **查看执行详情**
   - 在执行历史列表中点击目标记录
   - 查看详细的执行信息，包括参数、输出和错误信息

## API文档

### 脚本管理 API

| 路径 | 方法 | 描述 |
|-----|-----|-----|
| `/api/scripts` | GET | 获取所有脚本列表 |
| `/api/scripts/<id>` | GET | 获取指定脚本详情 |
| `/api/scripts` | POST | 添加新脚本 |
| `/api/scripts/<id>` | PUT | 更新脚本信息 |
| `/api/scripts/<id>/file` | PUT | 更新脚本文件 |
| `/api/scripts/<id>` | DELETE | 删除脚本 |

### 脚本执行 API

| 路径 | 方法 | 描述 |
|-----|-----|-----|
| `/api/execution/script/<id>` | POST | 执行指定脚本 |
| `/api/execution/chain/<id>` | POST | 执行指定脚本链 |
| `/api/execution/history` | GET | 获取执行历史列表 |
| `/api/execution/history/<id>` | GET | 获取执行历史详情 |

### 脚本链管理 API

| 路径 | 方法 | 描述 |
|-----|-----|-----|
| `/api/chains` | GET | 获取所有脚本链列表 |
| `/api/chains/<id>` | GET | 获取指定脚本链详情 |
| `/api/chains` | POST | 添加新脚本链 |
| `/api/chains/<id>` | PUT | 更新脚本链信息 |
| `/api/chains/<id>` | DELETE | 删除脚本链 |

## 开发者指南

### 项目结构

```
script-management-platform/
├── backend/              # 后端代码
│   ├── routes/           # API路由
│   │   ├── __init__.py
│   │   ├── scripts.py    # 脚本管理API
│   │   ├── execution.py  # 脚本执行API
│   │   └── chains.py     # 脚本链管理API
│   ├── utils/            # 工具类
│   │   ├── __init__.py
│   │   └── script_runner.py  # 脚本执行器
│   ├── app.py            # 应用入口
│   ├── config.py         # 配置文件
│   └── models.py         # 数据库模型
├── frontend/             # 前端代码
│   ├── public/           # 静态资源
│   └── src/              # 源代码
│       ├── assets/       # 资源文件
│       ├── components/   # Vue组件
│       ├── router/       # 路由配置
│       ├── store/        # Vuex状态管理
│       ├── views/        # 页面视图
│       ├── App.vue       # 根组件
│       └── main.js       # 入口文件
├── database/             # 数据库文件
├── scripts/              # 用户上传的脚本
├── requirements.txt      # 后端依赖
└── README.md             # 项目文档
```

### 扩展指南

#### 添加新的脚本类型支持

1. 在`config.py`中更新`ALLOWED_EXTENSIONS`集合
2. 在`utils/script_runner.py`中添加对应脚本类型的执行方法
3. 更新前端代码中的相关组件，如上传限制和类型标签

#### 添加新的参数类型支持

1. 在模型中的参数类型枚举中添加新类型
2. 在前端表单组件中添加新的参数类型输入控件

#### 修改数据库结构

1. 更新`models.py`中的数据库表结构
2. 创建数据库迁移脚本（如果需要）
3. 更新相应的模型方法

## 贡献指南

1. Fork该项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 常见问题解答

**Q: 如何处理脚本执行超时？**
A: 在`config.py`中可以设置`SCRIPT_TIMEOUT`变量来控制脚本执行的最大时间。

**Q: 支持哪些脚本类型？**
A: 目前支持Python (.py)、Shell (.sh)、Batch (.bat)、PowerShell (.ps1)和JavaScript (.js)脚本。

**Q: 如何在脚本之间传递数据？**
A: 在脚本链中，前一个脚本的标准输出会作为特殊参数`__prev_output`传递给下一个脚本。

**Q: 如何处理敏感参数？**
A: 当前版本未实现参数加密，处理敏感数据时请谨慎使用。

## 许可证

该项目基于MIT许可证发布 - 详情请参阅LICENSE文件。

## 关于作者

本项目作为本科毕业设计开发，旨在提供一个易用的脚本管理和自动化执行平台。
