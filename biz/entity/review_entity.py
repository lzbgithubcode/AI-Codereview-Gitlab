class MergeRequestReviewEntity:
    def __init__(self, project_name: str, author: str, source_branch: str, target_branch: str, updated_at: int,
                 commits: list, score: float, url: str, review_result: str, url_slug: str, webhook_data: dict,
                 additions: int, deletions: int, last_commit_id: str,
                 total_issues: int = 0, critical_issues: int = 0, high_issues: int = 0,
                 medium_issues: int = 0, low_issues: int = 0, suggestion_issues: int = 0,
                 estimated_time_hours: float = 0.0):
        self.project_name = project_name
        self.author = author
        self.source_branch = source_branch
        self.target_branch = target_branch
        self.updated_at = updated_at
        self.commits = commits
        self.score = score
        self.url = url
        self.review_result = review_result
        self.url_slug = url_slug
        self.webhook_data = webhook_data
        self.additions = additions
        self.deletions = deletions
        self.last_commit_id = last_commit_id
        
        # 结构化审查结果字段
        self.total_issues = total_issues
        self.critical_issues = critical_issues
        self.high_issues = high_issues
        self.medium_issues = medium_issues
        self.low_issues = low_issues
        self.suggestion_issues = suggestion_issues
        self.estimated_time_hours = estimated_time_hours

    @property
    def commit_messages(self):
        # 合并所有 commit 的 message 属性，用分号分隔
        return "; ".join(commit["message"].strip() for commit in self.commits)


class PushReviewEntity:
    def __init__(self, project_name: str, author: str, branch: str, updated_at: int, commits: list, score: float,
                 review_result: str, url_slug: str, webhook_data: dict, additions: int, deletions: int,
                 total_issues: int = 0, critical_issues: int = 0, high_issues: int = 0,
                 medium_issues: int = 0, low_issues: int = 0, suggestion_issues: int = 0,
                 estimated_time_hours: float = 0.0):
        self.project_name = project_name
        self.author = author
        self.branch = branch
        self.updated_at = updated_at
        self.commits = commits
        self.score = score
        self.review_result = review_result
        self.url_slug = url_slug
        self.webhook_data = webhook_data
        self.additions = additions
        self.deletions = deletions
        
        # 结构化审查结果字段
        self.total_issues = total_issues
        self.critical_issues = critical_issues
        self.high_issues = high_issues
        self.medium_issues = medium_issues
        self.low_issues = low_issues
        self.suggestion_issues = suggestion_issues
        self.estimated_time_hours = estimated_time_hours

    @property
    def commit_messages(self):
        # 合并所有 commit 的 message 属性，用分号分隔
        return "; ".join(commit["message"].strip() for commit in self.commits)

