import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # MySQL connection string, e.g.
    # mysql+pymysql://root:password@localhost:3306/hcp_crm
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "mysql+pymysql://root:root@localhost:3306/hcp_crm"
    )

    # Groq API key -> https://console.groq.com
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # Main model used for the agent (fast + cheap)
    PRIMARY_MODEL: str = os.getenv("PRIMARY_MODEL", "openai/gpt-oss-20b")

    # Larger model used when more context / reasoning is needed
    CONTEXT_MODEL: str = os.getenv("CONTEXT_MODEL", "openai/gpt-oss-120b")


settings = Settings()
