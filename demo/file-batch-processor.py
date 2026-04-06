#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件批量处理器 - 示例项目
功能：批量重命名、格式转换、文件整理
作者：进化者 (The Evolver)
联系：caijun2019@qq.com
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

class FileBatchProcessor:
    """文件批量处理器"""
    
    def __init__(self, source_dir):
        self.source_dir = Path(source_dir)
        self.results = []
    
    def batch_rename(self, pattern="{name}_{index}{ext}", start_index=1):
        """
        批量重命名文件
        pattern: 命名模式，支持 {name}, {index}, {ext}, {date}
        """
        files = [f for f in self.source_dir.iterdir() if f.is_file()]
        files.sort()
        
        for i, file_path in enumerate(files, start=start_index):
            new_name = pattern.format(
                name=file_path.stem,
                index=i,
                ext=file_path.suffix,
                date=datetime.now().strftime("%Y%m%d")
            )
            new_path = file_path.parent / new_name
            
            try:
                file_path.rename(new_path)
                self.results.append({
                    'old': str(file_path),
                    'new': str(new_path),
                    'status': 'success'
                })
            except Exception as e:
                self.results.append({
                    'old': str(file_path),
                    'new': str(new_path),
                    'status': 'error',
                    'error': str(e)
                })
        
        return self.results
    
    def organize_by_extension(self):
        """按文件扩展名整理文件到不同文件夹"""
        files = [f for f in self.source_dir.iterdir() if f.is_file()]
        
        for file_path in files:
            ext = file_path.suffix.lower() or 'no_extension'
            target_dir = self.source_dir / ext.lstrip('.')
            target_dir.mkdir(exist_ok=True)
            
            try:
                shutil.move(str(file_path), str(target_dir / file_path.name))
                self.results.append({
                    'file': str(file_path),
                    'moved_to': str(target_dir),
                    'status': 'success'
                })
            except Exception as e:
                self.results.append({
                    'file': str(file_path),
                    'status': 'error',
                    'error': str(e)
                })
        
        return self.results
    
    def get_summary(self):
        """获取处理摘要"""
        total = len(self.results)
        success = len([r for r in self.results if r.get('status') == 'success'])
        errors = total - success
        
        return {
            'total': total,
            'success': success,
            'errors': errors
        }


def main():
    """示例用法"""
    # 使用示例
    processor = FileBatchProcessor("./test_files")
    
    # 批量重命名
    # processor.batch_rename("文档_{index:03d}{ext}")
    
    # 按扩展名整理
    # processor.organize_by_extension()
    
    # 打印摘要
    # print(processor.get_summary())
    
    print("文件批量处理器")
    print("=" * 50)
    print("功能：")
    print("1. 批量重命名文件")
    print("2. 按扩展名整理文件")
    print("3. 自定义命名模式")
    print("=" * 50)
    print("联系：caijun2019@qq.com")
    print("定制开发：¥100-300")


if __name__ == "__main__":
    main()
