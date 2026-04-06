#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel数据处理工具 - 示例项目
功能：数据清洗、格式转换、报表生成
作者：进化者 (The Evolver)
联系：caijun2019@qq.com
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path

class ExcelDataProcessor:
    """Excel数据处理工具"""
    
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.df = None
        self.load_data()
    
    def load_data(self):
        """加载Excel数据"""
        try:
            self.df = pd.read_excel(self.file_path)
            return True
        except Exception as e:
            print(f"加载失败: {e}")
            return False
    
    def clean_data(self):
        """数据清洗"""
        if self.df is None:
            return False
        
        # 删除完全重复的行
        before_count = len(self.df)
        self.df = self.df.drop_duplicates()
        after_count = len(self.df)
        
        # 删除空值过多的行（超过50%为空）
        self.df = self.df.dropna(thresh=len(self.df.columns) * 0.5)
        
        # 去除字符串列的前后空格
        for col in self.df.select_dtypes(include=['object']).columns:
            self.df[col] = self.df[col].astype(str).str.strip()
        
        return {
            'duplicates_removed': before_count - after_count,
            'final_count': len(self.df)
        }
    
    def convert_format(self, output_format='csv'):
        """格式转换"""
        if self.df is None:
            return False
        
        output_path = self.file_path.with_suffix(f'.{output_format}')
        
        try:
            if output_format == 'csv':
                self.df.to_csv(output_path, index=False, encoding='utf-8-sig')
            elif output_format == 'json':
                self.df.to_json(output_path, orient='records', force_ascii=False)
            elif output_format == 'xlsx':
                self.df.to_excel(output_path, index=False)
            
            return str(output_path)
        except Exception as e:
            print(f"转换失败: {e}")
            return False
    
    def generate_report(self):
        """生成数据报告"""
        if self.df is None:
            return None
        
        report = {
            'file_name': self.file_path.name,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_rows': len(self.df),
                'total_columns': len(self.df.columns),
                'columns': list(self.df.columns)
            },
            'data_types': self.df.dtypes.to_dict(),
            'missing_values': self.df.isnull().sum().to_dict(),
            'numeric_summary': {}
        }
        
        # 数值列统计
        numeric_cols = self.df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            report['numeric_summary'][col] = {
                'min': self.df[col].min(),
                'max': self.df[col].max(),
                'mean': self.df[col].mean(),
                'median': self.df[col].median()
            }
        
        return report
    
    def save_report(self, output_path=None):
        """保存报告为JSON"""
        report = self.generate_report()
        if report is None:
            return False
        
        if output_path is None:
            output_path = self.file_path.with_suffix('.report.json')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return str(output_path)


def main():
    """示例用法"""
    print("Excel数据处理工具")
    print("=" * 50)
    print("功能：")
    print("1. 数据清洗（去重、去空、格式统一）")
    print("2. 格式转换（Excel ↔ CSV ↔ JSON）")
    print("3. 数据报告生成")
    print("4. 批量处理")
    print("=" * 50)
    print("联系：caijun2019@qq.com")
    print("定制开发：¥200-500")
    
    # 使用示例
    # processor = ExcelDataProcessor("data.xlsx")
    # processor.clean_data()
    # processor.convert_format('csv')
    # processor.save_report()


if __name__ == "__main__":
    main()
