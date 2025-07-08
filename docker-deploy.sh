#!/bin/bash

# IntelliCLI Docker 部署脚本
# 用于快速部署和管理IntelliCLI Docker环境

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker和Docker Compose
check_requirements() {
    log_info "检查系统要求..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装。请先安装Docker。"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装。请先安装Docker Compose。"
        exit 1
    fi
    
    log_success "系统要求检查通过"
}

# 初始化环境
init_environment() {
    log_info "初始化环境..."
    
    # 创建必要的目录
    mkdir -p config data workspace
    log_success "创建目录完成"
    
    # 复制环境变量文件
    if [ ! -f .env ]; then
        if [ -f env.example ]; then
            cp env.example .env
            log_success "已创建 .env 文件，请编辑填入您的API密钥"
        else
            log_warning "env.example 文件不存在，请手动创建 .env 文件"
        fi
    else
        log_info ".env 文件已存在"
    fi
    
    log_success "环境初始化完成"
}

# 构建镜像
build_image() {
    log_info "构建Docker镜像..."
    docker-compose build intellicli
    log_success "镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    docker-compose up -d
    log_success "服务启动完成"
    
    # 等待服务就绪
    log_info "等待服务就绪..."
    sleep 10
    
    # 检查服务状态
    docker-compose ps
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    docker-compose down
    log_success "服务已停止"
}

# 重启服务
restart_services() {
    log_info "重启服务..."
    docker-compose restart
    log_success "服务重启完成"
}

# 查看日志
show_logs() {
    log_info "显示服务日志..."
    docker-compose logs -f intellicli
}

# 进入交互式会话
enter_session() {
    log_info "进入IntelliCLI交互式会话..."
    docker-compose exec intellicli python main.py session
}

# 执行配置向导
run_config_wizard() {
    log_info "运行配置向导..."
    docker-compose exec intellicli python main.py config-wizard
}

# 显示服务状态
show_status() {
    log_info "服务状态："
    docker-compose ps
    
    echo ""
    log_info "健康检查："
    docker-compose exec intellicli python -c "import intellicli; print('IntelliCLI 运行正常')" 2>/dev/null || log_warning "IntelliCLI 服务可能未正常运行"
}

# 清理资源
cleanup() {
    log_warning "这将删除所有容器、镜像和数据卷！"
    read -p "确认要继续吗？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "清理Docker资源..."
        docker-compose down -v
        docker rmi intellicli:latest 2>/dev/null || true
        log_success "清理完成"
    else
        log_info "取消清理操作"
    fi
}

# 显示帮助
show_help() {
    cat << EOF
IntelliCLI Docker 部署脚本

用法: $0 [命令]

命令:
  init        初始化环境（创建目录和配置文件）
  build       构建Docker镜像
  start       启动所有服务
  stop        停止所有服务
  restart     重启所有服务
  logs        查看服务日志
  session     进入交互式会话
  config      运行配置向导
  status      显示服务状态
  cleanup     清理所有资源（危险操作）
  help        显示此帮助信息

示例:
  $0 init         # 初始化环境
  $0 start        # 启动服务
  $0 session      # 进入交互式会话
  $0 logs         # 查看日志

EOF
}

# 主函数
main() {
    case "${1:-help}" in
        init)
            check_requirements
            init_environment
            ;;
        build)
            check_requirements
            build_image
            ;;
        start)
            check_requirements
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        logs)
            show_logs
            ;;
        session)
            enter_session
            ;;
        config)
            run_config_wizard
            ;;
        status)
            show_status
            ;;
        cleanup)
            cleanup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 