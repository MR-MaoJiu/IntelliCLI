# IntelliCLI Docker Makefile
# 提供便捷的Docker管理命令

.PHONY: help init build start stop restart logs session config status cleanup clean

# 默认目标
.DEFAULT_GOAL := help

# 颜色定义
BLUE = \033[0;34m
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

# 项目名称
PROJECT_NAME = intellicli

help: ## 显示帮助信息
	@echo "$(BLUE)IntelliCLI Docker 管理命令$(NC)"
	@echo ""
	@echo "$(GREEN)可用命令:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-12s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(GREEN)使用示例:$(NC)"
	@echo "  make init      # 初始化环境"
	@echo "  make start     # 启动服务"
	@echo "  make session   # 进入交互式会话"
	@echo "  make logs      # 查看日志"

init: ## 初始化环境（创建目录和配置文件）
	@echo "$(BLUE)[INFO]$(NC) 初始化环境..."
	@mkdir -p config data workspace
	@if [ ! -f .env ]; then \
		if [ -f env.example ]; then \
			cp env.example .env; \
			echo "$(GREEN)[SUCCESS]$(NC) 已创建 .env 文件，请编辑填入您的API密钥"; \
		else \
			echo "$(YELLOW)[WARNING]$(NC) env.example 文件不存在，请手动创建 .env 文件"; \
		fi \
	else \
		echo "$(BLUE)[INFO]$(NC) .env 文件已存在"; \
	fi
	@echo "$(GREEN)[SUCCESS]$(NC) 环境初始化完成"

build: ## 构建Docker镜像
	@echo "$(BLUE)[INFO]$(NC) 构建Docker镜像..."
	@docker-compose build $(PROJECT_NAME)
	@echo "$(GREEN)[SUCCESS]$(NC) 镜像构建完成"

start: ## 启动所有服务
	@echo "$(BLUE)[INFO]$(NC) 启动服务..."
	@docker-compose up -d
	@echo "$(GREEN)[SUCCESS]$(NC) 服务启动完成"
	@echo "$(BLUE)[INFO]$(NC) 等待服务就绪..."
	@sleep 10
	@docker-compose ps

stop: ## 停止所有服务
	@echo "$(BLUE)[INFO]$(NC) 停止服务..."
	@docker-compose down
	@echo "$(GREEN)[SUCCESS]$(NC) 服务已停止"

restart: ## 重启所有服务
	@echo "$(BLUE)[INFO]$(NC) 重启服务..."
	@docker-compose restart
	@echo "$(GREEN)[SUCCESS]$(NC) 服务重启完成"

logs: ## 查看服务日志
	@echo "$(BLUE)[INFO]$(NC) 显示服务日志..."
	@docker-compose logs -f $(PROJECT_NAME)

session: ## 进入交互式会话
	@echo "$(BLUE)[INFO]$(NC) 进入IntelliCLI交互式会话..."
	@docker-compose exec $(PROJECT_NAME) python main.py session

config: ## 运行配置向导
	@echo "$(BLUE)[INFO]$(NC) 运行配置向导..."
	@docker-compose exec $(PROJECT_NAME) python main.py config-wizard

review-config: ## 配置复盘功能
	@echo "$(BLUE)[INFO]$(NC) 配置复盘功能..."
	@docker-compose exec $(PROJECT_NAME) python main.py review-config

status: ## 显示服务状态
	@echo "$(BLUE)[INFO]$(NC) 服务状态："
	@docker-compose ps
	@echo ""
	@echo "$(BLUE)[INFO]$(NC) 健康检查："
	@docker-compose exec $(PROJECT_NAME) python -c "import intellicli; print('IntelliCLI 运行正常')" 2>/dev/null || echo "$(YELLOW)[WARNING]$(NC) IntelliCLI 服务可能未正常运行"

cleanup: ## 清理所有资源（危险操作）
	@echo "$(RED)[WARNING]$(NC) 这将删除所有容器、镜像和数据卷！"
	@read -p "确认要继续吗？(y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo "$(BLUE)[INFO]$(NC) 清理Docker资源..."
	@docker-compose down -v
	@docker rmi $(PROJECT_NAME):latest 2>/dev/null || true
	@echo "$(GREEN)[SUCCESS]$(NC) 清理完成"

clean: ## 清理构建缓存
	@echo "$(BLUE)[INFO]$(NC) 清理构建缓存..."
	@docker system prune -f
	@echo "$(GREEN)[SUCCESS]$(NC) 缓存清理完成"

# 开发相关命令
dev-build: ## 开发模式构建（不使用缓存）
	@echo "$(BLUE)[INFO]$(NC) 开发模式构建..."
	@docker-compose build --no-cache $(PROJECT_NAME)
	@echo "$(GREEN)[SUCCESS]$(NC) 开发构建完成"

dev-shell: ## 进入容器shell
	@echo "$(BLUE)[INFO]$(NC) 进入容器shell..."
	@docker-compose exec $(PROJECT_NAME) /bin/bash

# 快速启动组合命令
quick-start: init build start ## 快速启动（初始化+构建+启动）
	@echo "$(GREEN)[SUCCESS]$(NC) 快速启动完成！"
	@echo "$(BLUE)[INFO]$(NC) 使用 'make session' 进入交互式会话"

# 完整重新部署
redeploy: stop build start ## 完整重新部署
	@echo "$(GREEN)[SUCCESS]$(NC) 重新部署完成！" 