import os
from blinker import Signal

from biz.entity.review_entity import MergeRequestReviewEntity, PushReviewEntity
from biz.service.review_service import ReviewService
from biz.utils.im import notifier
from biz.utils.code_reviewer import CodeReviewer

# 定义全局事件管理器（事件信号）
event_manager = {
    "merge_request_reviewed": Signal(),
    "push_reviewed": Signal(),
}


# 定义事件处理函数
def on_merge_request_reviewed(mr_review_entity: MergeRequestReviewEntity):
    # 检查当没有问题时是否发送通知（默认关闭）
    notify_when_no_issues = os.environ.get('NOTIFY_WHEN_NO_ISSUES_ENABLED', '0') == '1'
    
    # 构建问题统计信息
    total_issues = mr_review_entity.total_issues or 0
    
    # 如果没有问题且未开启"没有问题也通知"，则只记录数据库，不发送通知
    if total_issues == 0 and not notify_when_no_issues:
        # 记录到数据库
        ReviewService().insert_mr_review_log(mr_review_entity)
        return
    
    # 移除JSON部分，只保留Markdown审查报告
    markdown_result = CodeReviewer.strip_json_section(mr_review_entity.review_result) if mr_review_entity.review_result else ""
    
    critical_issues = mr_review_entity.critical_issues or 0
    high_issues = mr_review_entity.high_issues or 0
    medium_issues = mr_review_entity.medium_issues or 0
    low_issues = mr_review_entity.low_issues or 0
    suggestion_issues = mr_review_entity.suggestion_issues or 0
    
    # 发送IM消息通知（与企业微信评论格式保持一致）
    if total_issues > 0:
        # 有问题时，添加AI审查详情（重点标记问题代码和修改建议）
        im_msg = f"""🤖 **AI代码审查报告**

📋 **项目合并请求信息**

- 📁项目名称: {mr_review_entity.project_name}
- 👤提交人: {mr_review_entity.author}
- 🌿合并分支: 源{mr_review_entity.source_branch} → 目标{mr_review_entity.target_branch}
- 📊代码变更: +{mr_review_entity.additions or 0} / -{mr_review_entity.deletions or 0} 

----------------------------------------------------------------------------
⚠️ **AI审查详情**（有问题需要关注）

{markdown_result}

----------------------------------------------------------------------------
*由AI代码审查系统自动生成*"""
    else:
        # 没有问题时，按正常报告格式输出
        im_msg = f"""🤖 **AI代码审查报告**
        
📋 **项目合并请求信息**

- 📁项目名称: {mr_review_entity.project_name}
- 👤提交人: {mr_review_entity.author}
- 🌿分支: 源{mr_review_entity.source_branch} → 目标{mr_review_entity.target_branch}
- 📊代码变更: +{mr_review_entity.additions or 0} / -{mr_review_entity.deletions or 0} 

📊 **问题统计**: 🔴0 🟠0 🟡0 🔵0 💡0 | **总计: 0**

✅ **审查结果**: 代码审查通过，未发现问题

----------------------------------------------------------------------------
*由AI代码审查系统自动生成*"""
    
    notifier.send_notification(content=im_msg, msg_type='markdown', title='Merge Request Review',
                               project_name=mr_review_entity.project_name, url_slug=mr_review_entity.url_slug,
                               webhook_data=mr_review_entity.webhook_data)

    # 记录到数据库
    ReviewService().insert_mr_review_log(mr_review_entity)


def on_push_reviewed(entity: PushReviewEntity):
    # 检查当没有问题时是否发送通知（默认关闭）
    notify_when_no_issues = os.environ.get('NOTIFY_WHEN_NO_ISSUES_ENABLED', '0') == '1'
    
    # 构建问题统计信息
    total_issues = entity.total_issues or 0
    
    # 如果没有问题且未开启"没有问题也通知"，则只记录数据库，不发送通知
    if total_issues == 0 and not notify_when_no_issues:
        # 记录到数据库
        ReviewService().insert_push_review_log(entity)
        return
    
    # 移除JSON部分，只保留Markdown审查报告
    markdown_result = CodeReviewer.strip_json_section(entity.review_result) if entity.review_result else ""
    
    critical_issues = entity.critical_issues or 0
    high_issues = entity.high_issues or 0
    medium_issues = entity.medium_issues or 0
    low_issues = entity.low_issues or 0
    suggestion_issues = entity.suggestion_issues or 0
    
    # 发送IM消息通知（与企业微信评论格式保持一致）
    if total_issues > 0:
        # 有问题时，添加AI审查详情（重点标记问题代码和修改建议）
        im_msg = f"""🤖 **AI代码审查报告**
📋 **项目基本信息**
- 📁项目名称: {entity.project_name}
- 👤提交人: {entity.author}
- 🌿提交分支: {entity.branch}
- 📊代码变更: +{entity.additions or 0} / -{entity.deletions or 0}
----------------------------------------------------------------------------
⚠️ **AI审查详情**（有问题需要关注）

{markdown_result}

----------------------------------------------------------------------------
*由AI代码审查系统自动生成*"""
    else:
        # 没有问题时，按正常报告格式输出
        im_msg = f"""🤖 **AI代码审查报告**

📋 **项目信息**
- 📁项目名称: {entity.project_name}
- 👤提交人: {entity.author}
- 🌿提交分支: {entity.branch}
- 📊代码变更: +{entity.additions or 0} / -{entity.deletions or 0}

✅ **审查结果**: 代码审查通过，未发现问题

---
*由AI代码审查系统自动生成*"""
    
    notifier.send_notification(content=im_msg, msg_type='markdown', title=f"{entity.project_name} Push Event",
                               project_name=entity.project_name, url_slug=entity.url_slug,
                               webhook_data=entity.webhook_data)

    # 记录到数据库
    ReviewService().insert_push_review_log(entity)


# 连接事件处理函数到事件信号
event_manager["merge_request_reviewed"].connect(on_merge_request_reviewed)
event_manager["push_reviewed"].connect(on_push_reviewed)
