"""
智能代理类 - 整合规划、执行和复盘功能
"""

import yaml
from typing import List, Dict, Any, Optional
from .planner import Planner
from .executor import Executor
from .task_reviewer import TaskReviewer
from ..ui.display import ui

class Agent:
    """智能代理，整合任务规划、执行和复盘功能"""
    
    def __init__(self, model_client, config: Dict[str, Any] = None):
        """
        初始化智能代理
        
        Args:
            model_client: 模型客户端
            config: 配置信息
        """
        self.model_client = model_client
        self.config = config or {}
        
        # 初始化核心组件
        self.planner = Planner(model_client)
        self.executor = Executor(model_client)
        self.task_reviewer = TaskReviewer(model_client)
        
        # 获取复盘配置
        self.review_config = self.config.get('task_review', {
            'enabled': False,
            'auto_review': False,
            'review_threshold': 0.8,
            'max_iterations': 3
        })
        
        # 执行历史记录
        self.execution_history = []
    
    def execute_task(self, goal: str, enable_review: bool = None) -> Dict[str, Any]:
        """
        执行任务，包含规划、执行和可选的复盘
        
        Args:
            goal: 任务目标
            enable_review: 是否启用复盘（覆盖配置）
            
        Returns:
            执行结果
        """
        ui.print_section_header("开始执行任务", "🚀")
        ui.print_info(f"任务目标: {goal}")
        
        # 确定是否启用复盘
        should_review = enable_review if enable_review is not None else self.review_config.get('enabled', False)
        
        # 执行主要任务
        result = self._execute_main_task(goal)
        
        # 如果启用复盘，进行任务复盘
        if should_review:
            result = self._perform_task_review(goal, result)
        
        # 记录执行历史
        self.execution_history.append({
            'goal': goal,
            'result': result,
            'reviewed': should_review
        })
        
        return result
    
    def _execute_main_task(self, goal: str) -> Dict[str, Any]:
        """执行主要任务"""
        # 1. 规划阶段
        ui.print_section_header("任务规划", "📋")
        tools = self.executor.get_tool_info()
        plan = self.planner.create_plan(goal, tools)
        
        if not plan:
            return {
                'status': 'failed',
                'error': '无法生成有效的执行计划',
                'plan': [],
                'results': []
            }
        
        ui.print_success(f"生成了 {len(plan)} 个执行步骤")
        
        # 2. 执行阶段
        ui.print_section_header("任务执行", "⚙️")
        results = self.executor.execute_plan(plan)
        
        # 3. 分析执行结果
        execution_status = self._analyze_execution_results(results)
        
        return {
            'status': execution_status['status'],
            'success_rate': execution_status['success_rate'],
            'plan': plan,
            'results': results,
            'summary': execution_status['summary']
        }
    
    def _analyze_execution_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析执行结果"""
        total_steps = len(results)
        successful_steps = len([r for r in results if r.get('status') == 'completed'])
        failed_steps = len([r for r in results if r.get('status') == 'failed'])
        
        success_rate = (successful_steps / total_steps) if total_steps > 0 else 0
        
        if success_rate == 1.0:
            status = 'completed'
            summary = f"任务完全成功！所有 {total_steps} 个步骤都执行成功。"
        elif success_rate >= 0.8:
            status = 'mostly_completed'
            summary = f"任务基本成功！{successful_steps}/{total_steps} 个步骤成功，{failed_steps} 个步骤失败。"
        elif success_rate >= 0.5:
            status = 'partially_completed'
            summary = f"任务部分成功！{successful_steps}/{total_steps} 个步骤成功，{failed_steps} 个步骤失败。"
        else:
            status = 'failed'
            summary = f"任务执行失败！仅 {successful_steps}/{total_steps} 个步骤成功。"
        
        return {
            'status': status,
            'success_rate': success_rate,
            'summary': summary,
            'total_steps': total_steps,
            'successful_steps': successful_steps,
            'failed_steps': failed_steps
        }
    
    def _perform_task_review(self, goal: str, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务复盘"""
        ui.print_section_header("任务复盘", "🔍")
        
        success_rate = execution_result.get('success_rate', 0)
        review_threshold = self.review_config.get('review_threshold', 0.8)
        max_iterations = self.review_config.get('max_iterations', 3)
        
        # 判断是否需要复盘
        needs_review = success_rate < review_threshold
        auto_review = self.review_config.get('auto_review', False)
        
        if not needs_review and not auto_review:
            ui.print_success("任务执行成功，无需复盘")
            return execution_result
        
        ui.print_info(f"开始复盘分析（成功率: {success_rate:.1%}，阈值: {review_threshold:.1%}）")
        
        # 执行复盘分析
        review_result = self.task_reviewer.review_task_execution(
            original_goal=goal,
            execution_plan=execution_result.get('plan', []),
            execution_results=execution_result.get('results', [])
        )
        
        # 显示复盘结果
        self._display_review_results(review_result)
        
        # 如果有补充计划且需要改进，执行补充计划
        supplementary_plan = review_result.get('supplementary_plan')
        if supplementary_plan and needs_review:
            execution_result = self._execute_supplementary_plan(
                goal, execution_result, supplementary_plan, max_iterations
            )
        
        # 添加复盘信息到结果
        execution_result['review'] = review_result
        
        return execution_result
    
    def _display_review_results(self, review_result: Dict[str, Any]):
        """显示复盘结果"""
        overall_assessment = review_result.get('overall_assessment', {})
        
        ui.print_info(f"📊 整体评分: {overall_assessment.get('overall_score', 0)}/100")
        ui.print_info(f"🏆 评级: {overall_assessment.get('grade', '未知')}")
        ui.print_info(f"📝 总结: {overall_assessment.get('summary', '无')}")
        
        # 显示目标达成情况
        goal_achievement = review_result.get('goal_achievement', {})
        ui.print_info(f"🎯 目标达成度: {goal_achievement.get('achievement_percentage', 0)}%")
        
        # 显示问题列表
        issues = review_result.get('issues_identified', [])
        if issues:
            ui.print_warning(f"⚠️ 发现 {len(issues)} 个问题:")
            for issue in issues[:3]:  # 只显示前3个问题
                ui.print_info(f"   - {issue.get('description', '未知问题')}")
        
        # 显示改进建议
        suggestions = review_result.get('improvement_suggestions', [])
        if suggestions:
            ui.print_info(f"💡 改进建议:")
            for suggestion in suggestions[:3]:  # 只显示前3个建议
                ui.print_info(f"   - {suggestion.get('suggestion', '无建议')}")
    
    def _execute_supplementary_plan(
        self, 
        goal: str, 
        original_result: Dict[str, Any], 
        supplementary_plan: List[Dict[str, Any]], 
        max_iterations: int
    ) -> Dict[str, Any]:
        """执行补充计划"""
        ui.print_section_header("执行补充计划", "🔧")
        
        iteration = 0
        current_result = original_result
        
        while iteration < max_iterations and supplementary_plan:
            iteration += 1
            ui.print_info(f"第 {iteration} 次改进迭代")
            
            # 执行补充计划
            supplement_results = self.executor.execute_plan(supplementary_plan)
            
            # 分析补充执行结果
            supplement_analysis = self._analyze_execution_results(supplement_results)
            
            # 更新整体结果
            current_result['supplementary_results'] = current_result.get('supplementary_results', [])
            current_result['supplementary_results'].append({
                'iteration': iteration,
                'plan': supplementary_plan,
                'results': supplement_results,
                'analysis': supplement_analysis
            })
            
            # 检查是否达到满意的结果
            if supplement_analysis['success_rate'] >= self.review_config.get('review_threshold', 0.8):
                ui.print_success(f"第 {iteration} 次改进成功！")
                break
            
            # 如果还有迭代次数，重新生成补充计划
            if iteration < max_iterations:
                ui.print_info("生成新的补充计划...")
                try:
                    new_review = self.task_reviewer.review_task_execution(
                        original_goal=goal,
                        execution_plan=supplementary_plan,
                        execution_results=supplement_results
                    )
                    supplementary_plan = new_review.get('supplementary_plan', [])
                    if not supplementary_plan:
                        ui.print_info("无法生成更多补充计划，停止改进")
                        break
                except Exception as e:
                    ui.print_error(f"生成补充计划时出错: {e}")
                    break
        
        return current_result
    
    def manual_review(self, goal: str = None) -> Optional[Dict[str, Any]]:
        """手动执行复盘"""
        if not self.execution_history:
            ui.print_warning("没有可复盘的任务历史")
            return None
        
        # 如果没有指定目标，使用最近的任务
        if not goal:
            last_execution = self.execution_history[-1]
            goal = last_execution['goal']
            execution_result = last_execution['result']
        else:
            # 查找指定目标的任务
            execution_result = None
            for history in reversed(self.execution_history):
                if goal in history['goal']:
                    execution_result = history['result']
                    break
            
            if not execution_result:
                ui.print_error(f"未找到目标为 '{goal}' 的任务记录")
                return None
        
        ui.print_section_header("手动复盘", "🔍")
        ui.print_info(f"复盘目标: {goal}")
        
        # 执行复盘分析
        review_result = self.task_reviewer.review_task_execution(
            original_goal=goal,
            execution_plan=execution_result.get('plan', []),
            execution_results=execution_result.get('results', [])
        )
        
        # 显示复盘结果
        self._display_review_results(review_result)
        
        # 询问是否执行补充计划
        supplementary_plan = review_result.get('supplementary_plan')
        if supplementary_plan:
            ui.print_info("\n发现可执行的补充计划:")
            for i, step in enumerate(supplementary_plan, 1):
                ui.print_info(f"  {i}. {step.get('description', step.get('tool', '未知步骤'))}")
            
            execute_supplement = ui.get_user_input("\n是否执行补充计划？(y/N)").lower()
            if execute_supplement in ['y', 'yes', '是']:
                max_iterations = self.review_config.get('max_iterations', 3)
                updated_result = self._execute_supplementary_plan(
                    goal, execution_result, supplementary_plan, max_iterations
                )
                
                # 更新历史记录
                for history in self.execution_history:
                    if history['goal'] == goal:
                        history['result'] = updated_result
                        history['reviewed'] = True
                        break
                
                return updated_result
        
        return review_result
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return self.execution_history
    
    def clear_history(self):
        """清空执行历史"""
        self.execution_history = []
        ui.print_success("执行历史已清空") 