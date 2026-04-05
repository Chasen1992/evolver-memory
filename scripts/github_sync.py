#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Memory Sync Script
将本地记忆同步到GitHub，确保永不丢失
使用标准库，无需外部依赖
"""

import os
import sys
import json
import base64
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# 配置
WORKSPACE_PATH = Path("C:/Users/Admin/.stepclaw/workspace-main-3")
MEMORY_PATH = WORKSPACE_PATH / "memory"
GITHUB_API = "https://api.github.com"
REPO_NAME = "evolver-memory"

def load_config():
    """加载配置"""
    config_path = WORKSPACE_PATH / ".evolver-config.json"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def get_github_token():
    """获取GitHub Token"""
    # 优先从环境变量获取
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        return token
    
    # 从.env文件获取
    env_path = WORKSPACE_PATH / ".env"
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('GITHUB_TOKEN='):
                    return line.strip().split('=', 1)[1]
    
    print("Error: GitHub Token not found!")
    sys.exit(1)

def create_headers(token):
    """创建GitHub API请求头"""
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Evolver-Memory-Sync"
    }

def api_request(url, headers, method="GET", data=None):
    """发送API请求"""
    req = urllib.request.Request(url, method=method)
    
    for key, value in headers.items():
        req.add_header(key, value)
    
    if data:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(data).encode('utf-8')
    
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8'))
    except Exception as e:
        return 0, {"error": str(e)}

def get_or_create_repo(headers, repo_name):
    """获取或创建仓库"""
    # 获取用户仓库列表
    repos_url = f"{GITHUB_API}/user/repos"
    status, repos = api_request(repos_url, headers)
    
    if status != 200:
        print(f"Error fetching repos: {repos}")
        return None
    
    repo = next((r for r in repos if r['name'] == repo_name), None)
    
    if repo:
        print(f"Using existing repository: {repo['html_url']}")
        return repo
    
    # 创建新仓库
    create_url = f"{GITHUB_API}/user/repos"
    body = {
        "name": repo_name,
        "description": "Evolver AI Memory Sync - From zero to billionaire",
        "private": False,
        "auto_init": True
    }
    
    status, repo = api_request(create_url, headers, method="POST", data=body)
    
    if status == 201:
        print(f"Created repository: {repo['html_url']}")
        return repo
    else:
        print(f"Error creating repo: {repo}")
        return None

def get_file_sha(headers, repo_full_name, path):
    """获取文件SHA（如果存在）"""
    file_url = f"{GITHUB_API}/repos/{repo_full_name}/contents/{path}"
    status, data = api_request(file_url, headers)
    
    if status == 200:
        return data.get('sha')
    return None

def sync_file(headers, repo_full_name, file_path, relative_path, message):
    """同步单个文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 转换为base64
        content_bytes = content.encode('utf-8')
        content_base64 = base64.b64encode(content_bytes).decode('utf-8')
        
        # 获取现有文件SHA
        sha = get_file_sha(headers, repo_full_name, relative_path)
        
        # 准备请求体
        body = {
            "message": f"{message} - {relative_path}",
            "content": content_base64,
            "branch": "main"
        }
        
        if sha:
            body["sha"] = sha
        
        # 提交文件
        file_url = f"{GITHUB_API}/repos/{repo_full_name}/contents/{relative_path}"
        status, data = api_request(file_url, headers, method="PUT", data=body)
        
        if status in [200, 201]:
            print(f"[OK] Synced: {relative_path}")
            return True
        else:
            print(f"[FAIL] Failed to sync {relative_path}: {data}")
            return False
            
    except Exception as e:
        print(f"[ERR] Error syncing {relative_path}: {e}")
        return False

def find_files_to_sync():
    """查找需要同步的文件"""
    files = []
    
    # 根目录重要文件
    root_files = [
        "MEMORY.md",
        "SESSION-STATE.md",
        "IDENTITY.md",
        "SOUL.md",
        "USER.md",
        "HEARTBEAT.md",
        ".evolver-config.json"
    ]
    
    for filename in root_files:
        file_path = WORKSPACE_PATH / filename
        if file_path.exists():
            files.append(file_path)
    
    # memory目录下的所有.md文件
    if MEMORY_PATH.exists():
        for file_path in MEMORY_PATH.rglob("*.md"):
            if file_path.is_file():
                files.append(file_path)
        
        # memory目录下的所有.json文件
        for file_path in MEMORY_PATH.rglob("*.json"):
            if file_path.is_file():
                files.append(file_path)
    
    # scripts目录
    scripts_path = WORKSPACE_PATH / "scripts"
    if scripts_path.exists():
        for file_path in scripts_path.glob("*.py"):
            if file_path.is_file():
                files.append(file_path)
    
    return files

def main():
    """主函数"""
    print("[SYNC] GitHub Memory Sync Starting...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # 获取Token
    token = get_github_token()
    headers = create_headers(token)
    
    # 获取或创建仓库
    repo = get_or_create_repo(headers, REPO_NAME)
    if not repo:
        print("Failed to setup repository!")
        sys.exit(1)
    
    repo_full_name = repo['full_name']
    
    # 查找文件
    files = find_files_to_sync()
    print(f"\nFound {len(files)} files to sync")
    print("-" * 50)
    
    # 同步文件
    message = sys.argv[1] if len(sys.argv) > 1 else "Auto-sync memory"
    synced = 0
    failed = 0
    
    for file_path in files:
        relative_path = str(file_path.relative_to(WORKSPACE_PATH)).replace('\\', '/')
        if sync_file(headers, repo_full_name, file_path, relative_path, message):
            synced += 1
        else:
            failed += 1
    
    # 记录同步日志
    sync_log = {
        "timestamp": datetime.now().isoformat(),
        "repo": repo_full_name,
        "files_synced": synced,
        "files_failed": failed,
        "total_files": len(files)
    }
    
    log_path = MEMORY_PATH / "sync-log.json"
    logs = []
    if log_path.exists():
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except:
            logs = []
    
    logs.append(sync_log)
    
    # 只保留最近100条日志
    if len(logs) > 100:
        logs = logs[-100:]
    
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)
    
    print("-" * 50)
    print(f"\n[DONE] Sync completed!")
    print(f"Files synced: {synced}")
    print(f"Files failed: {failed}")
    print(f"Repository: https://github.com/{repo_full_name}")
    
    # 保存repo信息到配置
    config = load_config()
    if 'memory' not in config:
        config['memory'] = {}
    config['memory']['github_repo'] = repo_full_name
    config['memory']['last_sync'] = datetime.now().isoformat()
    
    with open(WORKSPACE_PATH / ".evolver-config.json", 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    # 返回结果
    return {
        "success": failed == 0,
        "synced": synced,
        "failed": failed,
        "repo_url": f"https://github.com/{repo_full_name}"
    }

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result["success"] else 1)
