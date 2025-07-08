"""
任务复盘分析器
分析任务执行结果，识别问题并提供改进建议
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime

class TaskReviewer:
    """任务复盘分析器"""
    
    def __init__(self, model_client):
        """
        初始化复盘分析器
        
        Args:
            model_client: 模型客户端，用于分析和生成建议
        """
        self.model_client = model_client
        
    def review_task_execution(
        self, 
        original_goal: str,
        execution_plan: List[Dict[str, Any]],
        execution_results: List[Dict[str, Any]],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        对任务执行进行全面复盘
        
        Args:
            original_goal: 原始任务目标
            execution_plan: 执行计划
            execution_results: 执行结果
            context: 额外上下文信息
            
        Returns:
            复盘分析结果
        """
        context = context or {}
        
        # 基础分析
        basic_analysis = self._analyze_execution_basics(execution_plan, execution_results)
        
        # 目标达成度分析
        goal_achievement = self._analyze_goal_achievement(
            original_goal, execution_plan, execution_results, context
        )
        
        # 问题识别
        issues_identified = self._identify_issues(execution_plan, execution_results)
        
        # 改进建议
        improvement_suggestions = self._generate_improvement_suggestions(
            original_goal, execution_plan, execution_results, issues_identified
        )
        
        # 补充方案
        supplementary_plan = self._generate_supplementary_plan(
            original_goal, execution_results, issues_identified
        )
        
        review_result = {
            "review_timestamp": datetime.now().isoformat(),
            "original_goal": original_goal,
            "basic_analysis": basic_analysis,
            "goal_achievement": goal_achievement,
            "issues_identified": issues_identified,
            "improvement_suggestions": improvement_suggestions,
            "supplementary_plan": supplementary_plan,
            "overall_assessment": self._generate_overall_assessment(
                basic_analysis, goal_achievement, issues_identified
            )
        }
        
        return review_result
    
    def _analyze_execution_basics(
        self, 
        execution_plan: List[Dict[str, Any]], 
        execution_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """分析执行基础指标"""
        total_steps = len(execution_plan)
        completed_steps = len([r for r in execution_results if r.get('status') == 'completed'])
        failed_steps = len([r for r in execution_results if r.get('status') == 'failed'])
        
        success_rate = (completed_steps / total_steps * 100) if total_steps > 0 else 0
        
        # 分析失败步骤的类型
        failed_tools = []
        failed_reasons = []
        for result in execution_results:
            if result.get('status') == 'failed':
                failed_tools.append(result.get('tool', 'unknown'))
                failed_reasons.append(result.get('error', 'unknown error'))
        
        return {
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "failed_steps": failed_steps,
            "success_rate": round(success_rate, 2),
            "failed_tools": failed_tools,
            "failed_reasons": failed_reasons
        }
    
    def _analyze_goal_achievement(
        self,
        original_goal: str,
        execution_plan: List[Dict[str, Any]],
        execution_results: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """分析目标达成度"""
        # 构建分析提示
        analysis_prompt = f"""
作为一个专业的任务分析师，请分析以下任务执行情况是否达成了原始目标。

原始目标：
{original_goal}

执行计划：
{json.dumps(execution_plan, ensure_ascii=False, indent=2)}

执行结果：
{json.dumps(execution_results, ensure_ascii=False, indent=2)}

请从以下维度进行分析：
1. 目标达成度（0-100%）
2. 关键要求是否满足
3. 输出质量评估
4. 用户满意度预期

请以JSON格式返回分析结果：
{{
    "achievement_percentage": 数字,
    "key_requirements_met": ["已满足的要求"],
    "key_requirements_missing": ["未满足的要求"],
    "output_quality_score": 数字(1-10),
    "quality_assessment": "质量评估说明",
    "user_satisfaction_prediction": "满意度预测",
    "detailed_analysis": "详细分析说明"
}}
"""
        
        try:
            response = self.model_client.generate(analysis_prompt)
            # 尝试解析JSON响应
            if response.strip().startswith('{'):
                analysis_result = json.loads(response)
            else:
                # 如果不是JSON格式，提取关键信息
                analysis_result = self._extract_achievement_info(response)
        except Exception as e:
            analysis_result = {
                "achievement_percentage": 50,
                "key_requirements_met": [],
                "key_requirements_missing": ["分析失败"],
                "output_quality_score": 5,
                "quality_assessment": f"分析过程出错: {e}",
                "user_satisfaction_prediction": "无法预测",
                "detailed_analysis": f"目标达成度分析失败: {e}"
            }
        
        return analysis_result
    
    def _identify_issues(
        self,
        execution_plan: List[Dict[str, Any]],
        execution_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """识别执行过程中的问题"""
        issues = []
        
        # 1. 直接失败的步骤
        for i, result in enumerate(execution_results):
            if result.get('status') == 'failed':
                issues.append({
                    "type": "execution_failure",
                    "step_number": i + 1,
                    "tool": result.get('tool', 'unknown'),
                    "error": result.get('error', 'unknown error'),
                    "severity": "high",
                    "description": f"步骤 {i + 1} ({result.get('tool')}) 执行失败"
                })
        
        # 2. 计划质量问题
        plan_issues = self._analyze_plan_quality(execution_plan, execution_results)
        issues.extend(plan_issues)
        
        # 3. 工具使用问题
        tool_issues = self._analyze_tool_usage(execution_plan, execution_results)
        issues.extend(tool_issues)
        
        return issues
    
    def _analyze_plan_quality(
        self,
        execution_plan: List[Dict[str, Any]],
        execution_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """分析计划质量问题"""
        issues = []
        
        # 检查计划是否过于简单或复杂
        if len(execution_plan) == 1:
            issues.append({
                "type": "plan_quality",
                "severity": "medium",
                "description": "计划可能过于简单，缺乏必要的步骤分解",
                "suggestion": "考虑将复杂任务分解为更多细化步骤"
            })
        elif len(execution_plan) > 10:
            issues.append({
                "type": "plan_quality",
                "severity": "medium",
                "description": "计划可能过于复杂，步骤过多",
                "suggestion": "考虑合并相关步骤或简化流程"
            })
        
        # 检查步骤依赖关系
        has_dependency_issues = False
        for i, step in enumerate(execution_plan):
            args = step.get('arguments', {})
            if '<PREVIOUS_STEP_OUTPUT>' in str(args) and i == 0:
                has_dependency_issues = True
                break
        
        if has_dependency_issues:
            issues.append({
                "type": "plan_quality",
                "severity": "high",
                "description": "第一步不应依赖前一步的输出",
                "suggestion": "检查步骤依赖关系的逻辑"
            })
        
        return issues
    
    def _analyze_tool_usage(
        self,
        execution_plan: List[Dict[str, Any]],
        execution_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """分析工具使用问题"""
        issues = []
        
        # 统计工具使用情况
        tool_usage = {}
        for step in execution_plan:
            tool = step.get('tool')
            if tool:
                tool_usage[tool] = tool_usage.get(tool, 0) + 1
        
        # 检查是否有工具使用过于频繁
        for tool, count in tool_usage.items():
            if count > 3:
                issues.append({
                    "type": "tool_usage",
                    "severity": "medium",
                    "description": f"工具 {tool} 使用过于频繁 ({count} 次)",
                    "suggestion": f"考虑优化 {tool} 的使用方式或合并相关操作"
                })
        
        return issues
    
    def _generate_improvement_suggestions(
        self,
        original_goal: str,
        execution_plan: List[Dict[str, Any]],
        execution_results: List[Dict[str, Any]],
        issues: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """生成改进建议"""
        # 构建改进建议提示
        suggestions_prompt = f"""
作为一个专业的流程优化专家，请基于以下任务执行情况提供改进建议。

原始目标：{original_goal}

识别的问题：
{json.dumps(issues, ensure_ascii=False, indent=2)}

执行统计：
- 总步骤：{len(execution_plan)}
- 成功步骤：{len([r for r in execution_results if r.get('status') == 'completed'])}
- 失败步骤：{len([r for r in execution_results if r.get('status') == 'failed'])}

请提供3-5个具体的改进建议，每个建议应包含：
1. 改进类型（plan_optimization/tool_selection/error_handling/efficiency）
2. 优先级（high/medium/low）
3. 具体建议内容
4. 预期效果

请以JSON数组格式返回建议。
"""
        
        try:
            response = self.model_client.generate(suggestions_prompt)
            suggestions = self._extract_suggestions(response)
        except Exception as e:
            # 提供默认建议
            suggestions = [
                {
                    "type": "error_handling",
                    "priority": "high",
                    "suggestion": "增强错误处理机制，提供更详细的错误信息",
                    "expected_effect": "减少任务失败率，提高调试效率"
                },
                {
                    "type": "plan_optimization",
                    "priority": "medium",
                    "suggestion": "优化任务分解策略，确保步骤之间的逻辑连贯性",
                    "expected_effect": "提高任务执行成功率"
                }
            ]
        
        return suggestions
    
    def _generate_supplementary_plan(
        self,
        original_goal: str,
        execution_results: List[Dict[str, Any]],
        issues: List[Dict[str, Any]]
    ) -> Optional[List[Dict[str, Any]]]:
        """生成补充计划"""
        # 检查是否需要补充计划
        failed_steps = [r for r in execution_results if r.get('status') == 'failed']
        high_priority_issues = [i for i in issues if i.get('severity') == 'high']
        
        if not failed_steps and not high_priority_issues:
            return None
        
        # 构建补充计划提示
        supplement_prompt = f"""
基于以下任务执行情况，生成一个补充计划来解决未完成的部分。

原始目标：{original_goal}

失败的步骤：
{json.dumps(failed_steps, ensure_ascii=False, indent=2)}

关键问题：
{json.dumps(high_priority_issues, ensure_ascii=False, indent=2)}

请生成一个补充计划，包含2-4个步骤来：
1. 修复失败的操作
2. 完成未达成的目标
3. 解决识别的关键问题

请以JSON数组格式返回计划，每个步骤包含：
- step: 步骤编号
- tool: 工具名称
- arguments: 参数字典
- description: 步骤描述

常用工具：write_file, read_file, shell, integrate_content, web_search
"""
        
        try:
            response = self.model_client.generate(supplement_prompt)
            supplement_plan = self._extract_plan(response)
        except Exception as e:
            supplement_plan = [
                {
                    "step": 1,
                    "tool": "integrate_content",
                    "arguments": {
                        "content": "请检查任务执行结果",
                        "requirement": "分析任务完成情况并提供改进建议"
                    },
                    "description": "分析任务执行情况"
                }
            ]
        
        return supplement_plan
    
    def _generate_overall_assessment(
        self,
        basic_analysis: Dict[str, Any],
        goal_achievement: Dict[str, Any],
        issues: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """生成整体评估"""
        success_rate = basic_analysis.get('success_rate', 0)
        achievement_percentage = goal_achievement.get('achievement_percentage', 0)
        high_issues = len([i for i in issues if i.get('severity') == 'high'])
        
        # 计算整体评分
        overall_score = (success_rate * 0.4 + achievement_percentage * 0.5 - high_issues * 10)
        overall_score = max(0, min(100, overall_score))
        
        # 确定评级
        if overall_score >= 90:
            grade = "优秀"
            summary = "任务执行非常成功，达到预期目标"
        elif overall_score >= 75:
            grade = "良好"
            summary = "任务基本完成，有小幅改进空间"
        elif overall_score >= 60:
            grade = "及格"
            summary = "任务部分完成，需要重点改进"
        else:
            grade = "需改进"
            summary = "任务执行存在重大问题，需要全面优化"
        
        return {
            "overall_score": round(overall_score, 1),
            "grade": grade,
            "summary": summary,
            "recommendation": self._get_recommendation(overall_score, high_issues)
        }
    
    def _get_recommendation(self, score: float, high_issues: int) -> str:
        """获取改进建议"""
        if score >= 90:
            return "继续保持当前的执行策略，可考虑优化效率"
        elif score >= 75:
            return "重点关注失败步骤的优化，提升整体稳定性"
        elif score >= 60:
            return "需要重新审视任务分解策略和工具选择"
        else:
            return "建议重新规划任务，优化执行流程"
    
    def _extract_achievement_info(self, response: str) -> Dict[str, Any]:
        """从文本响应中提取目标达成信息"""
        # 简单的文本解析，提取关键信息
        return {
            "achievement_percentage": 70,  # 默认值
            "key_requirements_met": ["基本功能完成"],
            "key_requirements_missing": ["需进一步分析"],
            "output_quality_score": 7,
            "quality_assessment": "基于文本分析的评估",
            "user_satisfaction_prediction": "中等",
            "detailed_analysis": response[:500]  # 截取前500字符
        }
    
    def _extract_suggestions(self, response: str) -> List[Dict[str, Any]]:
        """从响应中提取改进建议"""
        try:
            # 尝试解析JSON
            if '[' in response and ']' in response:
                start = response.find('[')
                end = response.rfind(']') + 1
                json_str = response[start:end]
                return json.loads(json_str)
        except:
            pass
        
        # 返回默认建议
        return [
            {
                "type": "plan_optimization",
                "priority": "high",
                "suggestion": "优化任务执行流程，提高成功率",
                "expected_effect": "减少执行错误"
            }
        ]
    
    def _extract_plan(self, response: str) -> List[Dict[str, Any]]:
        """从响应中提取补充计划"""
        try:
            # 尝试解析JSON
            if '[' in response and ']' in response:
                start = response.find('[')
                end = response.rfind(']') + 1
                json_str = response[start:end]
                return json.loads(json_str)
        except:
            pass
        
        # 返回默认计划
        return [
            {
                "step": 1,
                "tool": "integrate_content",
                "arguments": {
                    "content": "任务执行复盘",
                    "requirement": "总结任务执行情况"
                },
                "description": "生成任务执行总结"
            }
        ] 