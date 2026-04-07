"""
AI提示验证器
用于验证AI提示格式和响应质量
"""

import re
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class PromptValidator:
    """AI提示验证器"""
    
    @staticmethod
    def validate_prompt_format(prompt_content: str) -> Dict[str, Any]:
        """
        验证AI提示格式是否符合要求
        
        Args:
            prompt_content: 要发送给AI的提示内容
            
        Returns:
            验证结果字典
        """
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": []
        }
        
        # 检查是否包含格式要求说明
        if "<!-- JSON_DATA_START -->" not in prompt_content:
            validation_result["warnings"].append("提示中未明确包含JSON数据开始标记说明")
        
        if "<!-- JSON_DATA_END -->" not in prompt_content:
            validation_result["warnings"].append("提示中未明确包含JSON数据结束标记说明")
        
        # 检查是否包含格式禁止说明
        if "禁止输出无意义的字符" not in prompt_content:
            validation_result["warnings"].append("提示中未明确禁止无意义字符输出")
        
        # 检查是否包含15个核心要素说明
        if "15个核心要素" not in prompt_content:
            validation_result["warnings"].append("提示中未明确15个核心要素要求")
        
        # 检查是否包含位置准确性要求
        if "@@" not in prompt_content and "行号" not in prompt_content:
            validation_result["warnings"].append("提示中未明确GitLab diff行号定位要求")
        
        return validation_result
    
    @staticmethod
    def validate_ai_response(ai_response: str) -> Dict[str, Any]:
        """
        验证AI响应质量
        
        Args:
            ai_response: AI返回的响应内容
            
        Returns:
            验证结果字典
        """
        validation_result = {
            "valid": True,
            "quality_score": 0,
            "warnings": [],
            "errors": [],
            "suggestions": []
        }
        
        # 检查基本格式要求
        format_checks = PromptValidator._check_basic_format(ai_response)
        validation_result["warnings"].extend(format_checks["warnings"])
        validation_result["errors"].extend(format_checks["errors"])
        
        # 检查内容质量
        quality_checks = PromptValidator._check_content_quality(ai_response)
        validation_result["warnings"].extend(quality_checks["warnings"])
        validation_result["errors"].extend(quality_checks["errors"])
        validation_result["suggestions"].extend(quality_checks["suggestions"])
        
        # 计算质量分数
        validation_result["quality_score"] = PromptValidator._calculate_quality_score(
            ai_response, format_checks, quality_checks
        )
        
        # 如果有错误，标记为无效
        if validation_result["errors"]:
            validation_result["valid"] = False
        
        return validation_result
    
    @staticmethod
    def _check_basic_format(response: str) -> Dict[str, List[str]]:
        """检查基本格式要求"""
        result = {"warnings": [], "errors": []}
        
        # 检查格式分隔符
        if "<!-- JSON_DATA_START -->" not in response:
            result["errors"].append("缺少JSON数据开始标记")
        
        if "<!-- JSON_DATA_END -->" not in response:
            result["errors"].append("缺少JSON数据结束标记")
        
        # 检查随机字符串
        if re.search(r'[a-f0-9]{8,}|[A-F0-9]{8,}', response):
            result["errors"].append("检测到随机字符串")
        
        # 检查模板变量残留
        if re.search(r'\{\{.*?\}\}', response):
            result["errors"].append("检测到未处理的模板变量")
        
        # 检查JSON数据位置
        json_start = response.find('<!-- JSON_DATA_START -->')
        json_end = response.find('<!-- JSON_DATA_END -->')
        
        if json_start != -1 and json_end != -1:
            if json_end <= json_start:
                result["errors"].append("JSON数据标记位置错误")
            
            # 检查JSON数据是否为空
            json_content = response[json_start + len('<!-- JSON_DATA_START -->'):json_end].strip()
            if not json_content or json_content.isspace():
                result["errors"].append("JSON数据内容为空")
        
        return result
    
    @staticmethod
    def _check_content_quality(response: str) -> Dict[str, List[str]]:
        """检查内容质量"""
        result = {"warnings": [], "errors": [], "suggestions": []}
        
        # 检查问题描述的完整性
        if "问题 #" not in response and "问题：" not in response:
            result["warnings"].append("问题描述结构不完整")
        
        # 检查位置信息
        if "位置" not in response and "文件" not in response:
            result["warnings"].append("缺少位置信息描述")
        
        # 检查严重程度分类
        severity_levels = ["严重", "高", "中", "低", "建议"]
        severity_found = any(level in response for level in severity_levels)
        if not severity_found:
            result["warnings"].append("严重程度分类不明确")
        
        # 检查代码片段
        code_block_count = len(re.findall(r'```[\w]*\n.*?\n```', response, re.DOTALL))
        if code_block_count < 1:
            result["warnings"].append("缺少代码片段示例")
        
        # 检查修改建议
        if "修改建议" not in response and "修复建议" not in response:
            result["warnings"].append("缺少修改建议")
        
        # 检查Before/After对比
        if ("Before" not in response and "修改前" not in response) or \
           ("After" not in response and "修改后" not in response):
            result["suggestions"].append("建议添加Before/After代码对比")
        
        return result
    
    @staticmethod
    def _calculate_quality_score(response: str, format_checks: Dict, quality_checks: Dict) -> int:
        """计算AI响应质量分数（0-100）"""
        score = 100
        
        # 格式错误扣分
        score -= len(format_checks["errors"]) * 20
        score -= len(format_checks["warnings"]) * 5
        
        # 内容质量扣分
        score -= len(quality_checks["errors"]) * 15
        score -= len(quality_checks["warnings"]) * 3
        
        # 额外加分项
        if "🔴" in response or "🟠" in response:  # 表情符号使用
            score += 5
        
        if "```" in response:  # 代码块使用
            score += 10
        
        if "表格" in response or "|" in response:  # 表格使用
            score += 5
        
        # 确保分数在0-100之间
        return max(0, min(100, score))
    
    @staticmethod
    def generate_improvement_suggestions(validation_result: Dict[str, Any]) -> str:
        """生成改进建议"""
        suggestions = []
        
        if validation_result["quality_score"] < 60:
            suggestions.append("❌ 响应质量较差，建议重新生成或调整提示")
        
        if validation_result["errors"]:
            suggestions.append("⚠️ 存在格式错误，需要修复")
            for error in validation_result["errors"]:
                suggestions.append(f"   - {error}")
        
        if validation_result["warnings"]:
            suggestions.append("💡 存在格式警告，建议优化")
            for warning in validation_result["warnings"]:
                suggestions.append(f"   - {warning}")
        
        if validation_result["suggestions"]:
            suggestions.append("✨ 优化建议：")
            for suggestion in validation_result["suggestions"]:
                suggestions.append(f"   - {suggestion}")
        
        if not suggestions:
            suggestions.append("✅ 响应质量良好，无需改进")
        
        return "\n".join(suggestions)


# 测试函数
if __name__ == "__main__":
    # 测试数据
    test_response = """
    ## 代码审查报告
    
    ### 问题统计
    - 严重：0个 | 高：0个 | 中：0个 | 低：0个 | 建议：0个
    
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
    <!-- JSON_DATA_END -->
    """
    
    validator = PromptValidator()
    result = validator.validate_ai_response(test_response)
    print("验证结果:", result)
    print("改进建议:")
    print(validator.generate_improvement_suggestions(result))