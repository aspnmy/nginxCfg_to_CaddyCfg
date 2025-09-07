import re
from collections import defaultdict

class NginxToCaddyConverter:
    def __init__(self):
        self.ast = []
        self.current_block = None
        self.block_stack = []
        self.directive_mapping = self._init_directive_mapping()
        self.unsupported_directives = {
            'limit_req_zone': '使用 Caddy 的 rate_limit 中间件',
            'stub_status': 'Caddy 原生提供 /metrics 端点'
        }
        self.variable_map = {
            r'\$host': '{http.host}',
            r'\$remote_addr': '{http.request.remote}',
            r'\$request_uri': '{http.request.uri}',
            r'\$uri': '{http.request.uri.path}',
            r'\$document_root': '{http.root}',
            r'\$fastcgi_script_name': '{http.request.uri.path}',
            r'\$fastcgi_path_info': '{http.request.uri.path}',
            r'\$query_string': '{http.request.uri.query}'
        }

    def convert(self, nginx_config):
        """主转换入口"""
        self._parse_nginx_config(nginx_config)
        return self._generate_caddy_config()

    def _init_directive_mapping(self):
        """初始化指令转换规则"""
        return {
            'listen': lambda v: ('# listen', v),  # 我们将在 _server_sni 中处理 listen
            'server_name': lambda v: ('# server_name', v),  # 我们将在 _server_sni 中处理 server_name
            'root': lambda v: ('root', f'* {v}'),
            'proxy_pass': lambda v: ('reverse_proxy', self._convert_upstream(v)),
            'fastcgi_pass': lambda v: ('php_fastcgi', v),
            'deny': lambda _: ('respond', '403'),
            'error_log': lambda v: ('errors', v.split()[0]),
            'access_log': lambda v: ('log', f'access {{\n    output file {v.split()[0]}\n}}'),
            'index': lambda v: ('file_server', f'index {v}'),
            'try_files': lambda v: ('try_files', v),
            'add_header': lambda v: ('header', v),
            'client_max_body_size': lambda v: ('request_body', f'max_size {v}'),
            'server_tokens': lambda v: ('# server_tokens', v),
            'fastcgi_hide_header': lambda v: ('header', f'-{v}'),
            'include': lambda v: ('# include', v),
            'fastcgi_param': lambda v: ('# fastcgi_param', v),
            'gzip_static': lambda v: ('encode', 'gzip'),
            'default': lambda k, v: (f'# 未转换指令: {k}', f'{v}')
        }

    def _parse_nginx_config(self, config):
        """解析 Nginx 配置生成 AST"""
        lines = [line.strip() for line in config.split('\n') if line.strip()]
        
        for line in lines:
            if line.startswith('#'):
                continue

            # 识别块结构
            if line.endswith('{'):
                self._enter_block(line)
            elif line == '}':
                self._exit_block()
            else:
                self._parse_directive(line)

    def _enter_block(self, line):
        """处理块结构开始"""
        block_type = re.match(r'(\w+)\s*.*\{', line).group(1)
        new_block = {
            'type': block_type,
            'directives': [],
            'children': []
        }
        
        if self.current_block:
            self.current_block['children'].append(new_block)
            self.block_stack.append(self.current_block)
        else:
            self.ast.append(new_block)
            
        self.current_block = new_block

    def _exit_block(self):
        """处理块结构结束"""
        if self.block_stack:
            self.current_block = self.block_stack.pop()

    def _parse_directive(self, line):
        """解析单行指令"""
        line = re.sub(r';$', '', line)
        match = re.match(r'(\w+)\s+(.+)$', line)
        if not match:
            return
            
        key, value = match.groups()
        self.current_block['directives'].append((key, value))

    def _generate_caddy_config(self):
        """生成 Caddy 配置"""
        output = []
        self._traverse_ast(self.ast, output)
        return '\n'.join(output)

    def _traverse_ast(self, nodes, output, indent=0):
        """递归遍历 AST 生成配置"""
        for node in nodes:
            # 处理指令
            for directive in node['directives']:
                key, value = directive
                conv_func = self.directive_mapping.get(key, 
                    lambda x: self.directive_mapping['default'](key, x))
                
                if key in ['http', 'server', 'location']:
                    continue  # 块结构已单独处理
                
                # 变量替换
                for nginx_var, caddy_var in self.variable_map.items():
                    value = re.sub(nginx_var, caddy_var, value)
                
                # 生成配置行
                caddy_key, caddy_value = conv_func(value)
                output.append(' ' * indent + f'{caddy_key} {caddy_value}')

            # 处理子块
            if node['type'] == 'http':
                self._traverse_ast(node['children'], output, indent)
            elif node['type'] == 'server':
                output.append(' ' * indent + self._server_sni(node))
                self._traverse_ast(node['children'], output, indent + 2)
                output.append(' ' * indent + '}')
            elif node['type'] == 'location':
                output.append(' ' * indent + f"handle {self._location_matcher(node)} {{")
                self._traverse_ast(node['children'], output, indent + 2)
                output.append(' ' * indent + '}')

    def _server_sni(self, node):
        """生成 server 块头"""
        port = '80'
        domains = []
        for key, value in node['directives']:
            if key == 'listen':
                port = value.split()[0]
            elif key == 'server_name':
                domains = value.split()
                
        return f"{' '.join(domains)}:{port} {{" if domains else f":{port} {{"

    def _location_matcher(self, node):
        """生成路径匹配规则"""
        for key, value in node['directives']:
            if key == 'location':
                parts = value.split()
                if parts[0] in ('~*', '~', '='):
                    return self._convert_regex(parts)
                else:
                    return f"path {value}"
        return "*"  # 默认匹配所有路径

    def _convert_regex(self, parts):
        """转换正则表达式"""
        regex_type, pattern = parts
        go_regex = pattern
        if regex_type == '~*':
            go_regex = f'(?i){pattern}'
        return f"@re_{hash(pattern)} {{\n    expression {go_regex}\n}}"

    def _convert_upstream(self, value):
        """转换 upstream 配置"""
        return f"to {value.replace(';', ' ')}"

# 提供给外部调用的函数
def convert_nginx_to_caddy(nginx_config):
    """
    将Nginx配置转换为Caddy配置
    
    Args:
        nginx_config (str): Nginx配置文件内容
        
    Returns:
        str: 转换后的Caddy配置
    """
    converter = NginxToCaddyConverter()
    return converter.convert(nginx_config)

# 使用示例
if __name__ == "__main__":
    sample_nginx = """
    http {
        server {
            listen 80;
            server_name example.com;
            root /var/www/html;

            location /api/ {
                proxy_pass http://backend;
            }

        
        }
    }
    """

    converter = NginxToCaddyConverter()
    caddy_config = converter.convert(sample_nginx)
    print("生成的 Caddyfile:\n")
    print(caddy_config)
