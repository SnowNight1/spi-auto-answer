"""
大模型API调用模块
专门用于调用Azure OpenAI API解答SPI题目
包含针对日文SPI题目优化的prompt
"""

import logging
import json
import time
from typing import Dict, Any, Optional, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from utils import ConfigManager, safe_execute


class APIHandler:
    """API调用处理器"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.session = self._create_session()
        self._validate_config()
    
    def _create_session(self) -> requests.Session:
        """创建带重试机制的请求会话"""
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _validate_config(self) -> None:
        """验证API配置"""
        required_keys = ['api.api_key', 'api.api_endpoint']
        missing_keys = []
        
        for key in required_keys:
            if not self.config.get(key):
                missing_keys.append(key)
        
        if missing_keys:
            logging.error(f"API配置缺失: {missing_keys}")
            raise ValueError(f"缺少必要的API配置: {missing_keys}")
    
    def solve_question(self, question_text: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        使用大模型解答题目
        
        Args:
            question_text: 题目文本
            context: 额外上下文信息
            
        Returns:
            解答结果字典
        """
        try:
            # 构建prompt
            prompt = self._build_prompt(question_text, context)
            
            # 调用API
            response = self._call_api(prompt)
            
            if response and 'choices' in response:
                answer_text = response['choices'][0]['message']['content']
                
                # 解析答案
                parsed_answer = self._parse_answer(answer_text)
                
                return {
                    'success': True,
                    'answer': parsed_answer,
                    'raw_response': answer_text,
                    'usage': response.get('usage', {}),
                    'model': response.get('model', ''),
                    'source': 'api'
                }
            else:
                return {
                    'success': False,
                    'error': 'API响应格式错误',
                    'source': 'api'
                }
                
        except Exception as e:
            logging.error(f"API调用失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'source': 'api'
            }
    
    def _build_prompt(self, question_text: str, context: Optional[Dict] = None) -> str:
        """
        构建专门针对日文SPI题目的快速响应prompt
        
        Args:
            question_text: 题目文本
            context: 上下文信息
            
        Returns:
            构建的prompt
        """
        # 快速响应prompt模板
        base_prompt = """あなたは日本のSPIテストの専門家です。以下の問題に素早く正確に答えてください。

【重要】簡潔に答えてください。長い説明は不要です。

【回答形式】
思考過程: [簡潔な解法・考え方]
答え: [最終答案]

【問題】
{question}"""
        
        # 上下文信息（保持简洁）
        if context and 'question_type' in context:
            base_prompt += f"\n\n【参考】問題タイプ: {context['question_type']}"
        
        prompt = base_prompt.format(question=question_text)
        
        # 根据问题类型添加简短的专门指导
        if self._detect_math_question(question_text):
            prompt += "\n\n【数学】計算ミスに注意。"
        elif self._detect_language_question(question_text):
            prompt += "\n\n【言語】語彙の意味を正確に。"
        elif self._detect_logic_question(question_text):
            prompt += "\n\n【論理】前提条件を整理。"
        
        return prompt
    
    def _detect_math_question(self, text: str) -> bool:
        """数学問題かどうかを判定"""
        math_keywords = ['計算', '数値', '+', '-', '×', '÷', '=', '%', '割合', '確率', '平均']
        return any(keyword in text for keyword in math_keywords)
    
    def _detect_language_question(self, text: str) -> bool:
        """言語問題かどうかを判定"""
        lang_keywords = ['意味', '読み方', '漢字', 'ひらがな', 'カタカナ', '語彙', '文法', '敬語']
        return any(keyword in text for keyword in lang_keywords)
    
    def _detect_logic_question(self, text: str) -> bool:
        """論理問題かどうかを判定"""
        logic_keywords = ['論理', '推論', '条件', 'ならば', 'すべて', '一部', '関係', '順序']
        return any(keyword in text for keyword in logic_keywords)
    
    def _call_api(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Azure OpenAI APIを呼び出す
        
        Args:
            prompt: 送信するプロンプト
            
        Returns:
            API応答またはNone
        """
        try:
            # API設定取得
            api_key = self.config.get('api.api_key')
            api_endpoint = self.config.get('api.api_endpoint')
            api_version = self.config.get('api.api_version', '2024-02-01')
            deployment_name = self.config.get('api.deployment_name', 'gpt-4')
            
            # URL構築
            url = f"{api_endpoint.rstrip('/')}/openai/deployments/{deployment_name}/chat/completions"
            
            # ヘッダー設定
            headers = {
                'Content-Type': 'application/json',
                'api-key': api_key
            }
            
            # リクエストボディ構築（快速响应优化）
            data = {
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': self.config.get('api.max_tokens', 500),  # 减少到500，快速响应
                'temperature': self.config.get('api.temperature', 0.3),  # 稍微提高创造性但保持准确性
                'top_p': 0.8,  # 降低采样范围，提高一致性
                'frequency_penalty': 0.1,  # 轻微避免重复
                'presence_penalty': 0.1   # 鼓励简洁回答
            }
            
            # パラメータに api-version を追加
            params = {'api-version': api_version}
            
            logging.info(f"API请求 URL: {url}")
            logging.debug(f"API请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            # API調用
            start_time = time.time()
            response = self.session.post(
                url,
                headers=headers,
                json=data,
                params=params,
                timeout=30
            )
            end_time = time.time()
            
            logging.info(f"API响应时间: {end_time - start_time:.2f}秒")
            logging.info(f"API响应状态: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logging.debug(f"API响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
                return result
            else:
                logging.error(f"API错误: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logging.error("API请求超时")
            return None
        except requests.exceptions.RequestException as e:
            logging.error(f"API请求异常: {e}")
            return None
        except Exception as e:
            logging.error(f"API调用异常: {e}")
            return None
    
    def _parse_answer(self, response_text: str) -> Dict[str, Any]:
        """
        解析API返回的简洁答案
        
        Args:
            response_text: API返回的文本
            
        Returns:
            解析后的答案信息
        """
        result = {
            'question_type': '',
            'reasoning': '',
            'answer': '',
            'correct_option': '',
            'confidence': 0.9  # 快速模式下提高默认置信度
        }
        
        try:
            lines = response_text.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                
                # 解析新的简洁格式
                if line.startswith('思考過程:') or line.startswith('思考过程:'):
                    result['reasoning'] = line.split(':', 1)[1].strip()
                elif line.startswith('答え:') or line.startswith('答案:'):
                    result['answer'] = line.split(':', 1)[1].strip()
                # 兼容旧格式
                elif line.startswith('問題の種類:') or line.startswith('问题类型:'):
                    result['question_type'] = line.split(':', 1)[1].strip()
                elif line.startswith('解法・考え方:') or line.startswith('解答过程:'):
                    result['reasoning'] = line.split(':', 1)[1].strip()
                elif line.startswith('正解:') or line.startswith('正确答案:'):
                    result['correct_option'] = line.split(':', 1)[1].strip()
            
            # 如果没有找到结构化信息，将整个回复作为答案
            if not result['answer'] and not result['correct_option']:
                # 尝试找到最后一行非空内容作为答案
                non_empty_lines = [line.strip() for line in lines if line.strip()]
                if non_empty_lines:
                    result['answer'] = non_empty_lines[-1]
                else:
                    result['answer'] = response_text.strip()
            
            # 尝试从答案中提取选项（A、B、C、D等）
            if not result['correct_option']:
                import re
                # 查找单独的字母选项
                option_match = re.search(r'\b([A-Da-d])\b', result['answer'])
                if option_match:
                    result['correct_option'] = option_match.group(1).upper()
                # 查找"答案是X"或"正解：X"格式
                elif re.search(r'[答正解].*[：:]\s*([A-Da-d])', result['answer']):
                    option_match = re.search(r'[答正解].*[：:]\s*([A-Da-d])', result['answer'])
                    result['correct_option'] = option_match.group(1).upper()
            
        except Exception as e:
            logging.error(f"解析答案失败: {e}")
            result['answer'] = response_text.strip()
        
        return result
    
    def test_connection(self) -> bool:
        """
        测试API连接（快速模式）
        
        Returns:
            连接是否成功
        """
        try:
            # 使用更简单的测试prompt
            test_prompt = "テスト。「はい」と答えてください。"
            
            # 临时降低token限制以加快测试
            original_max_tokens = self.config.get('api.max_tokens', 500)
            self.config.config.setdefault('api', {})['max_tokens'] = 50
            
            result = self.solve_question(test_prompt)
            
            # 恢复原始配置
            self.config.config['api']['max_tokens'] = original_max_tokens
            
            if result['success']:
                logging.info("API连接测试成功")
                return True
            else:
                logging.error(f"API连接测试失败: {result.get('error')}")
                return False
                
        except Exception as e:
            logging.error(f"API连接测试异常: {e}")
            return False
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """
        获取API使用统计（需要在实际使用中累积）
        
        Returns:
            使用统计信息
        """
        # 这里可以实现使用统计的持久化存储
        return {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_tokens_used': 0,
            'average_response_time': 0.0
        }


def test_api_handler():
    """测试API处理器 - 快速响应模式"""
    config = ConfigManager()
    
    # 检查API配置
    if not config.get('api.api_key') or config.get('api.api_key') == 'YOUR_AZURE_OPENAI_API_KEY':
        print("请在config.json中配置正确的API密钥")
        return
    
    api_handler = APIHandler(config)
    
    # 测试连接
    print("测试API连接...")
    if api_handler.test_connection():
        print("✓ API连接测试成功")
        
        # 测试快速解题
        test_questions = [
            "12 + 8 = ?",
            "「こんにちは」の意味として最も適切なものはどれですか？\nA. おはよう\nB. こんにちは\nC. こんばんは\nD. さようなら",
            "AはBより背が高く、BはCより背が高い。最も背が高いのは誰ですか？"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n=== 测试题目 {i} ===")
            print(f"题目: {question}")
            
            import time
            start_time = time.time()
            result = api_handler.solve_question(question)
            end_time = time.time()
            
            if result['success']:
                answer_data = result['answer']
                print(f"解答时间: {end_time - start_time:.2f}秒")
                print(f"思考过程: {answer_data.get('reasoning', 'N/A')}")
                print(f"最终答案: {answer_data.get('answer', 'N/A')}")
                if answer_data.get('correct_option'):
                    print(f"选项: {answer_data['correct_option']}")
                print(f"置信度: {answer_data.get('confidence', 'N/A')}")
            else:
                print(f"✗ 解题失败: {result['error']}")
                
        # 显示使用统计
        print(f"\n=== 使用统计 ===")
        stats = api_handler.get_usage_statistics()
        print(f"总请求数: {stats['total_requests']}")
        print(f"成功请求: {stats['successful_requests']}")
        print(f"失败请求: {stats['failed_requests']}")
        
    else:
        print("✗ API连接测试失败，请检查配置")


def benchmark_api_response():
    """API响应速度基准测试"""
    config = ConfigManager()
    
    if not config.get('api.api_key') or config.get('api.api_key') == 'YOUR_AZURE_OPENAI_API_KEY':
        print("请配置API密钥后再进行基准测试")
        return
    
    api_handler = APIHandler(config)
    
    # 简单测试题目
    test_questions = [
        "3 × 7 = ?",
        "「ありがとう」の意味は？",
        "A > B, B > C. 最大は？"
    ]
    
    print("=== API响应速度基准测试 ===")
    total_time = 0
    successful_calls = 0
    
    for i, question in enumerate(test_questions):
        print(f"\n测试 {i+1}: {question}")
        
        import time
        start_time = time.time()
        result = api_handler.solve_question(question)
        end_time = time.time()
        
        response_time = end_time - start_time
        total_time += response_time
        
        if result['success']:
            successful_calls += 1
            print(f"  响应时间: {response_time:.2f}秒")
            print(f"  答案: {result['answer']['answer']}")
        else:
            print(f"  失败: {result['error']}")
    
    if successful_calls > 0:
        avg_time = total_time / successful_calls
        print(f"\n=== 基准测试结果 ===")
        print(f"成功调用: {successful_calls}/{len(test_questions)}")
        print(f"平均响应时间: {avg_time:.2f}秒")
        print(f"总时间: {total_time:.2f}秒")
        
        if avg_time <= 3:
            print("✓ 响应速度优秀")
        elif avg_time <= 5:
            print("○ 响应速度良好")
        else:
            print("⚠ 响应速度较慢，建议检查网络或API配置")
    else:
        print("✗ 所有API调用都失败了")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--benchmark":
        benchmark_api_response()
    else:
        test_api_handler()
