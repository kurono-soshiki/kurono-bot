# filepath: /Users/ytm/kurono-bot/src/comment_connecter/exceptions.py
"""
Comment Connector module exceptions
"""

class CommentConnectorError(Exception):
    """Base exception for Comment Connector module"""
    pass

class GitHubAPIError(CommentConnectorError):
    """GitHub API related errors"""
    pass

class DiscordAPIError(CommentConnectorError):
    """Discord API related errors"""
    pass

class ConfigurationError(CommentConnectorError):
    """Configuration related errors"""
    pass

class WebHookError(CommentConnectorError):
    """WebHook related errors"""
    pass

class MappingError(CommentConnectorError):
    """User/Channel mapping related errors"""
    pass