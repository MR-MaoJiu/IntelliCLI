#!/usr/bin/env python3
"""
IntelliCLI 主入口点
向后兼容的入口点，委托给新的 CLI 模块
"""

from intellicli.cli import main

if __name__ == "__main__":
    main()