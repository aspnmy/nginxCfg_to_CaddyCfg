#!/usr/bin/env python3
"""
测试脚本：用于测试 Nginx 配置到 Caddy 配置的转换功能
"""
import os
from converter.nginx2caddy import NginxToCaddyConverter


def test_nginx_to_caddy_conversion():
    # 读取测试用的 nginx.conf 文件
    nginx_conf_path = os.path.join('test', 'nginx.conf')
    
    try:
        with open(nginx_conf_path, 'r', encoding='utf-8') as f:
            nginx_config = f.read()
            
        print(f"读取到 nginx.conf 文件，共 {len(nginx_config)} 字符")
        
        # 创建转换器实例
        converter = NginxToCaddyConverter()
        
        # 执行转换
        print("开始转换 Nginx 配置到 Caddy 配置...")
        caddy_config = converter.convert(nginx_config)
        
        # 输出转换结果
        print("\n=== 转换结果 ===")
        print(caddy_config)
        
        # 保存转换结果到文件
        output_path = os.path.join('test', 'caddy_result.conf')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(caddy_config)
        
        print(f"\n转换成功！结果已保存到 {output_path}")
        return True
        
    except Exception as e:
        print(f"转换失败: {str(e)}")
        return False


if __name__ == "__main__":
    print("=== Nginx 配置到 Caddy 配置转换测试 ===")
    success = test_nginx_to_caddy_conversion()
    print(f"\n测试 {'成功' if success else '失败'}")