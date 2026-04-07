"""
AI审查结果解析器
用于从AI返回的Markdown格式审查结果中提取结构化数据
支持JSON格式数据提取
"""

import re
import json
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class ReviewResultParser:
    """AI审查结果解析器"""
    
    @staticmethod
    def parse_review_result(review_result: str) -> Dict:
        """
        解析AI审查结果，提取结构化数据
        优先从JSON数据中提取，若不存在则使用正则表达式解析
        
        Args:
            review_result: AI返回的Markdown格式审查结果
            
        Returns:
            包含结构化数据的字典
        """
        try:
            # 首先尝试从JSON数据中提取
            json_data = ReviewResultParser._extract_json_data(review_result)
            if json_data:
                logger.info("从JSON数据中解析审查结果")
                return json_data
            
            # 如果JSON数据不存在，使用正则表达式解析
            return ReviewResultParser._parse_with_regex(review_result)
            
        except Exception as e:
            logger.error(f"解析审查结果失败: {e}")
            # 返回默认值
            return {
                'total_issues': 0,
                'critical_issues': 0,
                'high_issues': 0,
                'medium_issues': 0,
                'low_issues': 0,
                'suggestion_issues': 0,
                'estimated_time_hours': 0.0,
                'issues': []
            }
    
    @staticmethod
    def _extract_json_data(review_result: str) -> Dict[str, Any]:
        """从审查结果中提取JSON格式数据"""
        try:
            # 查找JSON数据标记
            json_start = review_result.find('<!-- JSON_DATA_START -->')
            json_end = review_result.find('<!-- JSON_DATA_END -->')
            
            if json_start != -1 and json_end != -1:
                json_text = review_result[json_start + len('<!-- JSON_DATA_START -->'):json_end].strip()
                
                # 处理模板变量（将Jinja2模板变量替换为实际值）
                json_text = json_text.replace('{{ total_issues }}', '0')
                json_text = json_text.replace('{{ issues_count[\'严重\'] }}', '0')
                json_text = json_text.replace('{{ issues_count[\'高\'] }}', '0')
                json_text = json_text.replace('{{ issues_count[\'中\'] }}', '0')
                json_text = json_text.replace('{{ issues_count[\'低\'] }}', '0')
                json_text = json_text.replace('{{ issues_count[\'建议\'] }}', '0')
                json_text = json_text.replace('{{ estimated_time_hours }}', '0.0')
                
                # 解析JSON数据
                data = json.loads(json_text)
                
                # 确保数据结构完整
                if 'issues' not in data:
                    data['issues'] = []
                
                return data
            
            return None
            
        except Exception as e:
            logger.warning(f"提取JSON数据失败，将使用正则表达式解析: {e}")
            return None
    
    @staticmethod
    def _parse_with_regex(review_result: str) -> Dict[str, Any]:
        """使用正则表达式解析Markdown格式的审查结果"""
        # 初始化结构化数据
        structured_data = {
            'total_issues': 0,
            'critical_issues': 0,
            'high_issues': 0,
            'medium_issues': 0,
            'low_issues': 0,
            'suggestion_issues': 0,
            'estimated_time_hours': 0.0,
            'issues': []
        }
        
        # 解析审查统计
        stats_match = re.search(r'严重：(\d+)个.*高：(\d+)个.*中：(\d+)个.*低：(\d+)个.*建议：(\d+)个', review_result)
        if stats_match:
            structured_data['critical_issues'] = int(stats_match.group(1))
            structured_data['high_issues'] = int(stats_match.group(2))
            structured_data['medium_issues'] = int(stats_match.group(3))
            structured_data['low_issues'] = int(stats_match.group(4))
            structured_data['suggestion_issues'] = int(stats_match.group(5))
            structured_data['total_issues'] = sum([
                structured_data['critical_issues'],
                structured_data['high_issues'],
                structured_data['medium_issues'],
                structured_data['low_issues'],
                structured_data['suggestion_issues']
            ])
        
        # 解析预计修复时间
        time_match = re.search(r'预计修复时间：(\d+\.?\d*)小时', review_result)
        if time_match:
            structured_data['estimated_time_hours'] = float(time_match.group(1))
        
        # 解析问题列表（简化版，主要提取问题数量）
        # 这里可以根据需要扩展更详细的解析逻辑
        
        logger.info(f"使用正则表达式解析审查结果: 总共{structured_data['total_issues']}个问题，预计修复时间{structured_data['estimated_time_hours']}小时")
        
        return structured_data
    
    @staticmethod
    def extract_issue_statistics(review_result: str) -> Dict[str, int]:
        """
        从审查结果中提取问题统计信息
        
        Args:
            review_result: AI返回的Markdown格式审查结果
            
        Returns:
            问题统计字典
        """
        try:
            statistics = {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'suggestion': 0,
                'total': 0
            }
            
            # 使用正则表达式匹配问题统计行
            pattern = r'严重：(\d+)个.*高：(\d+)个.*中：(\d+)个.*低：(\d+)个.*建议：(\d+)个'
            match = re.search(pattern, review_result)
            
            if match:
                statistics['critical'] = int(match.group(1))
                statistics['high'] = int(match.group(2))
                statistics['medium'] = int(match.group(3))
                statistics['low'] = int(match.group(4))
                statistics['suggestion'] = int(match.group(5))
                statistics['total'] = sum([
                    statistics['critical'],
                    statistics['high'],
                    statistics['medium'],
                    statistics['low'],
                    statistics['suggestion']
                ])
            
            return statistics
            
        except Exception as e:
            logger.error(f"提取问题统计失败: {e}")
            return statistics
    
    @staticmethod
    def extract_estimated_time(review_result: str) -> float:
        """
        从审查结果中提取预计修复时间
        
        Args:
            review_result: AI返回的Markdown格式审查结果
            
        Returns:
            预计修复时间（小时）
        """
        try:
            pattern = r'预计修复时间：(\d+\.?\d*)小时'
            match = re.search(pattern, review_result)
            
            if match:
                return float(match.group(1))
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"提取预计修复时间失败: {e}")
            return 0.0


# 测试函数
if __name__ == "__main__":
    # 测试数据
    test_review = """
    ## 🔍 代码审查报告
    
    ### 📊 审查统计
    - 严重：2个 | 高：3个 | 中：1个 | 低：0个 | 建议：2个
    - 预计修复时间：1.5小时
    
    ### 问题列表
    
    ### 🔴 严重级别问题
    
    #### 问题 #1：SQL 注入风险
    
    - **位置**：`src/user/login.py` 第 23-25 行
    - **严重程度**：严重
    - **问题分类**：安全漏洞 - SQL 注入
    - **影响范围**：影响所有调用该登录接口的请求
    - **置信度**：高 (95%)
    - **修复工作量**：S（5 分钟）
    - **处理建议**：必须修复（阻断合并）
    """
    
    parser = ReviewResultParser()
    result = parser.parse_review_result(test_review)
    print("解析结果:", result)