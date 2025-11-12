#!/usr/bin/env python
import os
import sys
from dotenv import load_dotenv


def main():
    # 安全加载环境变量
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "user_center.settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(...) from exc

    # 从环境变量获取端口，默认8080
    if len(sys.argv) == 1:
        port = os.getenv("DJANGO_PORT", "8080")
        sys.argv += ["runserver", f"0.0.0.0:{port}"]

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
