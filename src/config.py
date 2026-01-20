"""应用配置"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置

    所有配置项都可以通过环境变量或 .env 文件设置
    """

    # ==================== LLM配置 ====================
    # LLM服务商选择: "claude"、"openai" 或 "zhipu"
    # - "claude": Claude (Anthropic)
    # - "openai": OpenAI或兼容服务（通义千问、Kimi等）
    # - "zhipu": 智谱AI原生SDK（推荐用于GLM-4V）
    llm_provider: str = "claude"

    # ==================== API密钥 ====================
    # Claude (Anthropic) API密钥
    claude_api_key: Optional[str] = None

    # OpenAI API密钥 (或兼容OpenAI格式的服务密钥，如智谱AI、通义千问、Kimi等)
    openai_api_key: Optional[str] = None

    # Moonshot (Kimi) API密钥 (备用字段，可选)
    moonshot_api_key: Optional[str] = None

    # 通义千问 API密钥 (备用字段，可选)
    qwen_api_key: Optional[str] = None

    # ==================== 模型配置 ====================
    # Claude模型名称
    claude_model: str = "claude-3-5-sonnet-20241022"

    # OpenAI模型名称 (或兼容服务的模型名称)
    # 示例:
    #   - OpenAI: "gpt-4o", "gpt-4o-mini"
    #   - 通义千问: "qwen-plus", "qwen-vl-plus", "qwen-max"
    #   - Kimi: "moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"
    #   - 智谱AI: "glm-4", "glm-4v"
    openai_model: str = "gpt-4o-mini"

    # ==================== 自定义端点 ====================
    # OpenAI兼容服务的API端点 (用于国内服务或私有部署)
    # 示例:
    #   - 通义千问: "https://dashscope.aliyuncs.com/compatible-mode/v1"
    #   - Kimi: "https://api.moonshot.cn/v1"
    #   - 智谱AI: "https://open.bigmodel.cn/api/paas/v4"
    openai_base_url: Optional[str] = None

    # 数据库
    database_url: str = "sqlite:///./exam_questions.db"

    # 路径配置
    pdf_dir: str = "data/pdfs"
    image_dir: str = "data/images"

    # 日志
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
