import abc
import os
import re
from typing import Dict, Any, List

import yaml
from jinja2 import Template

from biz.llm.factory import Factory
from biz.utils.log import logger
from biz.utils.token_util import count_tokens, truncate_text_by_tokens
from biz.utils.review_result_parser import ReviewResultParser
from biz.utils.prompt_validator import PromptValidator


class BaseReviewer(abc.ABC):
    """代码审查基类"""

    def __init__(self, prompt_key: str):
        self.client = Factory().getClient()
        self.prompts = self._load_prompts(prompt_key, os.getenv("REVIEW_STYLE", "professional"))
        self.optimization_config = self._load_optimization_config()

    def _load_prompts(self, prompt_key: str, style="professional") -> Dict[str, Any]:
        """加载提示词配置"""
        prompt_templates_file = "conf/prompt_templates.yml"
        try:
            # 在打开 YAML 文件时显式指定编码为 UTF-8，避免使用系统默认的 GBK 编码。
            with open(prompt_templates_file, "r", encoding="utf-8") as file:
                prompts = yaml.safe_load(file).get(prompt_key, {})

                # 使用Jinja2渲染模板
                def render_template(template_str: str) -> str:
                    # 创建示例issue对象，用于模板渲染测试
                    example_issue = {
                        'title': '示例问题标题',
                        'severity': '低',
                        'category': '代码规范',
                        'location': {'file': 'src/example.py', 'line': 1},
                        'impact_scope': '仅当前函数',
                        'confidence': '高 (90%+)',
                        'estimated_time': '5分钟',
                        'action': '建议修复',
                        'description': '这是示例问题描述',
                        'language': 'python',
                        'code_snippet': 'print("hello")',
                        'explanation': '这是问题解释',
                        'suggestion': '这是修改建议',
                        'before_code': 'print("hello")',
                        'after_code': 'print("Hello, World!")'
                    }
                    
                    # 传递所有必要的模板变量，避免渲染错误
                    template_vars = {
                        'style': style,
                        'issues_by_severity': {},
                        'issues_count': {'严重': 0, '高': 0, '中': 0, '低': 0, '建议': 0},
                        'issues': {
                            '严重': [],
                            '高': [],
                            '中': [],
                            '低': [],
                            '建议': []
                        },
                        'total_issues': 0,
                        'estimated_time_hours': 0.0,
                        # 提供示例issue用于循环测试
                        'issue': example_issue
                    }
                    return Template(template_str).render(**template_vars)

                system_prompt = render_template(prompts["system_prompt"])
                user_prompt = render_template(prompts["user_prompt"])

                return {
                    "system_message": {"role": "system", "content": system_prompt},
                    "user_message": {"role": "user", "content": user_prompt},
                }
        except (FileNotFoundError, KeyError, yaml.YAMLError) as e:
            logger.error(f"加载提示词配置失败: {e}")
            raise Exception(f"提示词配置加载失败: {e}")
    
    def _load_optimization_config(self) -> Dict[str, Any]:
        """加载优化配置"""
        config_file = "conf/ai_prompt_optimization.yml"
        try:
            with open(config_file, "r", encoding="utf-8") as file:
                return yaml.safe_load(file)
        except (FileNotFoundError, yaml.YAMLError) as e:
            logger.warning(f"加载优化配置失败，使用默认配置: {e}")
            # 返回默认配置
            return {
                "quality_scoring": {
                    "thresholds": {"acceptable": 60}
                },
                "retry_config": {
                    "max_retries": 3
                }
            }

    def call_llm(self, messages: List[Dict[str, Any]]) -> str:
        """调用 LLM 进行代码审核，包含格式验证和重试机制"""
        max_retries = 3
        retry_count = 0
        
        # 验证提示格式
        validator = PromptValidator()
        prompt_validation = validator.validate_prompt_format(messages[1]["content"])
        
        if prompt_validation["warnings"]:
            logger.warning(f"提示格式警告: {prompt_validation['warnings']}")
        
        while retry_count < max_retries:
            try:
                logger.info(f"向 AI 发送代码 Review 请求 (第{retry_count + 1}次尝试)")
                review_result = self.client.completions(messages=messages)
                logger.info(f"收到 AI 返回结果，长度: {len(review_result)} 字符")
                
                # 验证AI响应质量
                response_validation = validator.validate_ai_response(review_result)
                
                if response_validation["valid"] and response_validation["quality_score"] >= 60:
                    logger.info(f"AI响应验证通过，质量分数: {response_validation['quality_score']}")
                    return review_result
                else:
                    logger.warning(f"AI响应验证失败，质量分数: {response_validation['quality_score']}")
                    
                    # 生成改进建议
                    suggestions = validator.generate_improvement_suggestions(response_validation)
                    logger.warning(f"改进建议: {suggestions}")
                    
                    # 如果是最后一次尝试，返回降级结果
                    if retry_count == max_retries - 1:
                        logger.error("达到最大重试次数，返回降级结果")
                        return self._get_fallback_response()
                    
                    # 增加重试计数器
                    retry_count += 1
                    logger.info(f"准备第{retry_count + 1}次重试...")
                    
            except Exception as e:
                logger.error(f"调用AI失败: {e}")
                retry_count += 1
                
                if retry_count == max_retries:
                    logger.error("达到最大重试次数，返回降级结果")
                    return self._get_fallback_response()
        
        # 理论上不会执行到这里
        return self._get_fallback_response()
    
    def _get_fallback_response(self) -> str:
        """获取降级响应"""
        fallback_response = """## 🔍 代码审查报告

### 📊 审查统计
- 严重：0个 | 高：0个 | 中：0个 | 低：0个 | 建议：0个
- 预计修复时间：0小时

### 审查说明
AI审查服务暂时不可用，请人工检查代码质量。

<!-- JSON_DATA_START -->
{
  "total_issues": 0,
  "critical_issues": 0,
  "high_issues": 0,
  "medium_issues": 0,
  "low_issues": 0,
  "suggestion_issues": 0,
  "estimated_time_hours": 0.0,
  "issues": []
}
<!-- JSON_DATA_END -->"""
        return fallback_response

    @abc.abstractmethod
    def review_code(self, *args, **kwargs) -> str:
        """抽象方法，子类必须实现"""
        pass


class CodeReviewer(BaseReviewer):
    """代码 Diff 级别的审查"""

    def __init__(self):
        super().__init__("code_review_prompt")

    def review_and_strip_code(self, changes_text: str, commits_text: str = "") -> str:
        """
        Review判断changes_text超出取前REVIEW_MAX_TOKENS个token，超出则截断changes_text，
        调用review_code方法，返回review_result，如果review_result是markdown格式，则去掉头尾的```
        :param changes_text:
        :param commits_text:
        :return:
        """
        # 如果超长，取前REVIEW_MAX_TOKENS个token
        review_max_tokens = int(os.getenv("REVIEW_MAX_TOKENS", 10000))
        # 如果changes为空,打印日志
        if not changes_text:
            logger.info("代码为空, diffs_text = %", str(changes_text))
            return "代码为空"

        # 计算tokens数量，如果超过REVIEW_MAX_TOKENS，截断changes_text
        tokens_count = count_tokens(changes_text)
        if tokens_count > review_max_tokens:
            changes_text = truncate_text_by_tokens(changes_text, review_max_tokens)

        review_result = self.review_code(changes_text, commits_text).strip()
        
        # 清理Markdown代码块格式
        if review_result.startswith("```markdown") and review_result.endswith("```"):
            review_result = review_result[11:-3].strip()
        elif review_result.startswith("```") and review_result.endswith("```"):
            review_result = review_result[3:-3].strip()
        
        # 确保审查结果不为空
        if not review_result or review_result == "代码为空":
            review_result = "## 🔍 代码审查报告\n\n### 📊 审查统计\n- 严重：0个 | 高：0个 | 中：0个 | 低：0个 | 建议：0个\n- 预计修复时间：0小时\n\n### 审查说明\n未发现需要修复的问题，代码质量良好。"
        
        return review_result

    def review_code(self, diffs_text: str, commits_text: str = "") -> str:
        """Review 代码并返回结果"""
        messages = [
            self.prompts["system_message"],
            {
                "role": "user",
                "content": self.prompts["user_message"]["content"].format(
                    diffs_text=diffs_text, commits_text=commits_text
                ),
            },
        ]
        return self.call_llm(messages)

    @staticmethod
    def parse_review_score(review_text: str) -> int:
        """解析 AI 返回的 Review 结果，返回评分"""
        if not review_text:
            return 0
        match = re.search(r"总分[:：]\s*(\d+)分?", review_text)
        return int(match.group(1)) if match else 0

    @staticmethod
    def parse_review_result(review_text: str) -> Dict[str, Any]:
        """
        解析 AI 返回的 Review 结果，返回结构化数据
        
        Args:
            review_text: AI返回的Markdown格式审查结果
            
        Returns:
            包含结构化审查数据的字典
        """
        parser = ReviewResultParser()
        return parser.parse_review_result(review_text)

    def review_code_with_stats(self, diffs_text: str, commits_text: str = "") -> Dict[str, Any]:
        """
        Review 代码并返回包含结构化统计信息的结果
        
        Args:
            diffs_text: 代码差异文本
            commits_text: 提交信息文本
            
        Returns:
            包含审查结果和统计信息的字典
        """
        # 获取原始审查结果
        review_result = self.review_code(diffs_text, commits_text)
        
        # 清理Markdown代码块格式
        if review_result.startswith("```markdown") and review_result.endswith("```"):
            review_result = review_result[11:-3].strip()
        elif review_result.startswith("```") and review_result.endswith("```"):
            review_result = review_result[3:-3].strip()
        
        # 确保审查结果不为空
        if not review_result or review_result == "代码为空":
            review_result = "## 🔍 代码审查报告\n\n### 📊 审查统计\n- 严重：0个 | 高：0个 | 中：0个 | 低：0个 | 建议：0个\n- 预计修复时间：0小时\n\n### 审查说明\n未发现需要修复的问题，代码质量良好。"
        
        # 解析结构化数据
        structured_data = self.parse_review_result(review_result)
        
        return {
            "review_result": review_result,
            "structured_data": structured_data
        }

