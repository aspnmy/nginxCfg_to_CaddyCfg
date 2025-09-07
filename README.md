# nginxCfg_to_CaddyCfg
# Nginx配置转Caddy配置工具

这是一个简单的Web工具，可以帮助您将Nginx配置文件自动转换为Caddy 2配置文件。

## 功能特点

- 支持基本的Nginx服务器块配置转换
- 支持静态文件服务配置转换
- 支持反向代理配置转换
- 提供简单的Web界面进行文件上传或文本输入
- 容器化支持，可通过Docker快速部署

## 项目结构

```
├── app.py                 # Flask应用主文件
├── converter/             # 转换器模块
│   └── nginx2caddy.py     # Nginx到Caddy配置转换逻辑
├── templates/             # HTML模板
│   └── index.html         # 主页面模板
├── uploads/               # 上传文件临时存储目录
├── requirements.txt       # Python依赖包列表
├── Dockerfile             # Docker构建文件
├── .gitignore             # Git忽略规则
└── README.md              # 项目说明文档
```

## 快速开始

### 本地开发运行

1. 确保您已安装Python 3.10或更高版本

2. 克隆项目代码

3. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

4. 运行应用
   ```bash
   python app.py
   ```

5. 在浏览器中访问 http://localhost:5000

### 使用Docker运行

1. 构建Docker镜像
   ```bash
   docker build -t nginx2caddy .
   ```

2. 运行Docker容器
   ```bash
   docker run -p 5000:5000 nginx2caddy
   ```

3. 在浏览器中访问 http://localhost:5000

## 使用方法

1. 在Web界面中，您可以选择两种方式输入Nginx配置：
   - 上传Nginx配置文件（.conf文件）
   - 直接在文本框中粘贴Nginx配置内容

2. 点击"转换"按钮

3. 查看并复制转换后的Caddy配置

## 转换支持范围

当前支持转换的Nginx配置项包括：

- `server_name` - 转换为Caddy站点名称
- `listen` - （当前版本有限支持，默认使用80端口）
- `root` - 转换为Caddy的`root *`指令
- `location` - 转换为Caddy的`handle`指令
- `proxy_pass` - 转换为Caddy的`reverse_proxy`指令

## 注意事项

- 此工具提供基本的配置转换功能，复杂的Nginx配置可能需要手动调整
- 对于不支持的配置项，转换后的Caddy配置可能需要您手动添加
- Caddy和Nginx的配置哲学有所不同，请理解两者之间的差异

## 开发说明

如果您想扩展此工具的功能，可以修改`converter/nginx2caddy.py`文件中的转换逻辑。

## 许可证

MIT License

## 致谢

- Flask - 轻量级Web框架
- Caddy - 强大的现代Web服务器
- Nginx - 高性能的开源Web服务器
