"""
Excel题库查询模块
支持多sheet、自定义列配置的灵活题库查询
使用模糊匹配提高查询准确率
"""

import logging
import os
from typing import List, Dict, Optional, Tuple, Any
import pandas as pd
from fuzzywuzzy import fuzz, process
import re

from utils import ConfigManager, safe_execute


class ExcelHandler:
    """Excel题库处理器"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.excel_file = self.config.get('excel.file_path', 'questions.xlsx')
        self.sheets_config = self.config.get('excel.sheets_config', {})
        self.fuzzy_config = self.config.get('excel.fuzzy_match', {})
        
        # 缓存加载的数据
        self._cache = {}
        self._load_excel_data()
    
    def _load_excel_data(self) -> None:
        """加载Excel数据到缓存"""
        try:
            if not os.path.exists(self.excel_file):
                logging.warning(f"Excel文件不存在: {self.excel_file}")
                return
            
            # 读取所有sheet
            excel_file = pd.ExcelFile(self.excel_file)
            logging.info(f"发现Excel sheets: {excel_file.sheet_names}")
            
            for sheet_name in excel_file.sheet_names:
                try:
                    df = pd.read_excel(self.excel_file, sheet_name=sheet_name)
                    
                    # 清理数据
                    df = self._clean_dataframe(df)
                    
                    self._cache[sheet_name] = df
                    logging.info(f"已加载sheet '{sheet_name}': {len(df)} 行数据")
                    
                except Exception as e:
                    logging.error(f"加载sheet '{sheet_name}' 失败: {e}")
            
            logging.info(f"Excel数据加载完成，共 {len(self._cache)} 个sheets")
            
        except Exception as e:
            logging.error(f"加载Excel文件失败: {e}")
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        清理DataFrame数据
        
        Args:
            df: 原始DataFrame
            
        Returns:
            清理后的DataFrame
        """
        # 移除完全空白的行
        df = df.dropna(how='all')
        
        # 清理字符串列的空白
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
            # 将 'nan' 字符串替换为空字符串
            df[col] = df[col].replace('nan', '')
        
        # 重置索引
        df = df.reset_index(drop=True)
        
        return df
    
    def reload_excel(self) -> bool:
        """
        重新加载Excel文件
        
        Returns:
            是否加载成功
        """
        try:
            self._cache.clear()
            self._load_excel_data()
            return True
        except Exception as e:
            logging.error(f"重新加载Excel失败: {e}")
            return False
    
    def search_question(self, question_text: str) -> List[Dict[str, Any]]:
        """
        在所有配置的sheet中搜索题目
        
        Args:
            question_text: 题目文本
            
        Returns:
            匹配结果列表
        """
        all_results = []
        
        for sheet_name, sheet_config in self.sheets_config.items():
            if sheet_name not in self._cache:
                logging.warning(f"Sheet '{sheet_name}' 未加载")
                continue
            
            results = self._search_in_sheet(question_text, sheet_name, sheet_config)
            all_results.extend(results)
        
        # 按匹配度排序
        all_results.sort(key=lambda x: x['match_score'], reverse=True)
        
        # 限制返回结果数量
        max_results = self.fuzzy_config.get('max_results', 3)
        return all_results[:max_results]
    
    def _search_in_sheet(self, question_text: str, sheet_name: str, sheet_config: Dict) -> List[Dict[str, Any]]:
        """
        在特定sheet中搜索题目
        
        Args:
            question_text: 题目文本
            sheet_name: sheet名称
            sheet_config: sheet配置
            
        Returns:
            匹配结果列表
        """
        try:
            df = self._cache[sheet_name]
            question_column = sheet_config.get('question_column')
            
            if not question_column or question_column not in df.columns:
                logging.warning(f"Sheet '{sheet_name}' 中未找到题目列 '{question_column}'")
                return []
            
            results = []
            
            # 清理输入问题文本
            cleaned_question = self._clean_question_text(question_text)
            
            # 遍历所有题目
            for idx, row in df.iterrows():
                db_question = str(row[question_column])
                if not db_question or db_question == 'nan':
                    continue
                
                # 清理数据库中的题目文本
                cleaned_db_question = self._clean_question_text(db_question)
                
                # 计算匹配度
                match_score = self._calculate_match_score(cleaned_question, cleaned_db_question)
                
                # 检查是否达到阈值
                threshold = self.fuzzy_config.get('threshold', 0.8)
                if match_score >= threshold:
                    # 提取答案信息
                    answer_info = self._extract_answer_info(row, sheet_config)
                    
                    result = {
                        'sheet_name': sheet_name,
                        'row_index': idx,
                        'question': db_question,
                        'match_score': match_score,
                        'answer_info': answer_info,
                        'matched_method': 'fuzzy'
                    }
                    results.append(result)
            
            # 尝试精确匹配
            exact_matches = self._exact_search_in_sheet(cleaned_question, sheet_name, sheet_config)
            results.extend(exact_matches)
            
            return results
            
        except Exception as e:
            logging.error(f"在sheet '{sheet_name}' 中搜索失败: {e}")
            return []
    
    def _exact_search_in_sheet(self, question_text: str, sheet_name: str, sheet_config: Dict) -> List[Dict[str, Any]]:
        """
        在sheet中进行精确搜索
        
        Args:
            question_text: 题目文本
            sheet_name: sheet名称
            sheet_config: sheet配置
            
        Returns:
            精确匹配结果列表
        """
        try:
            df = self._cache[sheet_name]
            question_column = sheet_config.get('question_column')
            
            results = []
            
            # 精确匹配
            exact_matches = df[df[question_column].str.contains(
                re.escape(question_text), case=False, na=False
            )]
            
            for idx, row in exact_matches.iterrows():
                answer_info = self._extract_answer_info(row, sheet_config)
                
                result = {
                    'sheet_name': sheet_name,
                    'row_index': idx,
                    'question': str(row[question_column]),
                    'match_score': 1.0,  # 精确匹配得分最高
                    'answer_info': answer_info,
                    'matched_method': 'exact'
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            logging.error(f"精确搜索失败: {e}")
            return []
    
    def _extract_answer_info(self, row: pd.Series, sheet_config: Dict) -> Dict[str, Any]:
        """
        从行数据中提取答案信息
        
        Args:
            row: 数据行
            sheet_config: sheet配置
            
        Returns:
            答案信息字典
        """
        answer_info = {
            'options': {},
            'correct_answer': '',
            'answer_text': ''
        }
        
        try:
            # 提取选项
            answer_columns = sheet_config.get('answer_columns', [])
            for i, col in enumerate(answer_columns):
                if col in row.index and pd.notna(row[col]):
                    option_label = chr(65 + i)  # A, B, C, D...
                    answer_info['options'][option_label] = str(row[col])
            
            # 提取正确答案
            correct_column = sheet_config.get('correct_answer_column')
            if correct_column and correct_column in row.index and pd.notna(row[correct_column]):
                answer_info['correct_answer'] = str(row[correct_column])
                
                # 如果正确答案是选项标号，获取对应的选项文本
                correct_answer = answer_info['correct_answer'].upper()
                if correct_answer in answer_info['options']:
                    answer_info['answer_text'] = answer_info['options'][correct_answer]
                else:
                    answer_info['answer_text'] = answer_info['correct_answer']
            
        except Exception as e:
            logging.error(f"提取答案信息失败: {e}")
        
        return answer_info
    
    def _clean_question_text(self, text: str) -> str:
        """
        清理题目文本用于匹配
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 移除特殊字符
        text = re.sub(r'[^\w\s\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', '', text)
        
        return text.lower()
    
    def _calculate_match_score(self, query: str, target: str) -> float:
        """
        计算两个文本的匹配度
        
        Args:
            query: 查询文本
            target: 目标文本
            
        Returns:
            匹配度分数 (0-1)
        """
        if not query or not target:
            return 0.0
        
        # 使用多种算法计算匹配度
        ratio = fuzz.ratio(query, target) / 100.0
        partial_ratio = fuzz.partial_ratio(query, target) / 100.0
        token_sort_ratio = fuzz.token_sort_ratio(query, target) / 100.0
        token_set_ratio = fuzz.token_set_ratio(query, target) / 100.0
        
        # 加权平均
        weights = [0.2, 0.3, 0.25, 0.25]
        scores = [ratio, partial_ratio, token_sort_ratio, token_set_ratio]
        
        return sum(w * s for w, s in zip(weights, scores))
    
    def add_question(self, sheet_name: str, question: str, options: List[str], correct_answer: str) -> bool:
        """
        向题库添加新题目
        
        Args:
            sheet_name: sheet名称
            question: 题目文本
            options: 选项列表
            correct_answer: 正确答案
            
        Returns:
            是否添加成功
        """
        try:
            if sheet_name not in self.sheets_config:
                logging.error(f"未配置的sheet: {sheet_name}")
                return False
            
            sheet_config = self.sheets_config[sheet_name]
            
            # 准备新行数据
            new_row = {}
            
            # 添加题目
            question_col = sheet_config.get('question_column')
            if question_col:
                new_row[question_col] = question
            
            # 添加选项
            answer_columns = sheet_config.get('answer_columns', [])
            for i, option in enumerate(options):
                if i < len(answer_columns):
                    new_row[answer_columns[i]] = option
            
            # 添加正确答案
            correct_col = sheet_config.get('correct_answer_column')
            if correct_col:
                new_row[correct_col] = correct_answer
            
            # 更新缓存
            if sheet_name in self._cache:
                self._cache[sheet_name] = pd.concat([
                    self._cache[sheet_name],
                    pd.DataFrame([new_row])
                ], ignore_index=True)
            
            # 保存到Excel文件
            self._save_to_excel()
            
            logging.info(f"成功添加新题目到 {sheet_name}")
            return True
            
        except Exception as e:
            logging.error(f"添加题目失败: {e}")
            return False
    
    def _save_to_excel(self) -> None:
        """保存缓存数据到Excel文件"""
        try:
            with pd.ExcelWriter(self.excel_file, engine='openpyxl') as writer:
                for sheet_name, df in self._cache.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            logging.info("Excel文件保存成功")
            
        except Exception as e:
            logging.error(f"保存Excel文件失败: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取题库统计信息
        
        Returns:
            统计信息字典
        """
        stats = {
            'total_sheets': len(self._cache),
            'sheets': {},
            'total_questions': 0
        }
        
        for sheet_name, df in self._cache.items():
            sheet_stats = {
                'total_rows': len(df),
                'columns': list(df.columns),
                'configured': sheet_name in self.sheets_config
            }
            
            if sheet_name in self.sheets_config:
                question_col = self.sheets_config[sheet_name].get('question_column')
                if question_col in df.columns:
                    non_empty_questions = df[question_col].notna().sum()
                    sheet_stats['valid_questions'] = non_empty_questions
                    stats['total_questions'] += non_empty_questions
            
            stats['sheets'][sheet_name] = sheet_stats
        
        return stats


def create_sample_excel():
    """创建示例Excel文件"""
    # 示例数据
    sample_data = {
        '数学问题': pd.DataFrame({
            'A': ['1+1等于多少？', '2*3等于多少？', '10除以2等于多少？'],
            'B': ['1', '5', '4'],
            'C': ['2', '6', '5'],
            'D': ['3', '7', '6'],
            'E': ['4', '8', '7'],
            'F': ['B', 'B', 'C']
        }),
        '语言问题': pd.DataFrame({
            'A': ['「おはよう」の意味は？', '「ありがとう」の意味は？'],
            'B': ['こんばんは', 'すみません'],
            'C': ['おはよう', 'ありがとう'],
            'D': ['こんにちは', 'さようなら'],
            'E': ['C', 'C']
        })
    }
    
    # 保存到Excel文件
    with pd.ExcelWriter('questions.xlsx', engine='openpyxl') as writer:
        for sheet_name, df in sample_data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print("示例Excel文件已创建: questions.xlsx")


def test_excel_handler():
    """测试Excel处理器"""
    config = ConfigManager()
    excel_handler = ExcelHandler(config)
    
    # 获取统计信息
    stats = excel_handler.get_statistics()
    print(f"题库统计: {stats}")
    
    # 测试搜索
    test_questions = ["1+1", "おはよう"]
    for question in test_questions:
        results = excel_handler.search_question(question)
        print(f"\n搜索 '{question}' 的结果:")
        for result in results:
            print(f"  匹配度: {result['match_score']:.2f}")
            print(f"  题目: {result['question']}")
            print(f"  答案: {result['answer_info']}")


if __name__ == "__main__":
    # 创建示例文件（如果不存在）
    if not os.path.exists('questions.xlsx'):
        create_sample_excel()
    
    test_excel_handler()
