# -*- coding: utf-8 -*-
"""
===================================
增强版定时调度模块 - 支持多时段分析
===================================

职责：
1. 支持早（8:30）、中（12:00）、晚（16:30）三个时段的定时任务
2. 支持早盘分析、午盘总结、复盘三个不同类型的分析
3. 优雅处理信号，确保可靠退出
"""

import logging
import signal
import sys
import time
import threading
from datetime import datetime
from typing import Callable, Optional, Dict, List

logger = logging.getLogger(__name__)


class GracefulShutdown:
    """
    优雅退出处理器
    
    捕获 SIGTERM/SIGINT 信号，确保任务完成后再退出
    """
    
    def __init__(self):
        self.shutdown_requested = False
        self._lock = threading.Lock()
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理函数"""
        with self._lock:
            if not self.shutdown_requested:
                logger.info(f"收到退出信号 ({signum})，等待当前任务完成...")
                self.shutdown_requested = True
    
    @property
    def should_shutdown(self) -> bool:
        """检查是否应该退出"""
        with self._lock:
            return self.shutdown_requested


class EnhancedScheduler:
    """
    增强版定时任务调度器
    
    基于 schedule 库实现，支持：
    - 多个定时任务同时运行
    - 早中晚三个时段的分析任务
    - 优雅退出
    """
    
    def __init__(self):
        """
        初始化调度器
        """
        try:
            import schedule
            self.schedule = schedule
        except ImportError:
            logger.error("schedule 库未安装，请执行: pip install schedule")
            raise ImportError("请安装 schedule 库: pip install schedule")
        
        self.shutdown_handler = GracefulShutdown()
        self._task_callbacks: Dict[str, Callable] = {}
        self._running = False
        
        # 预设分析时段
        self.MORNING_TIME = "08:30"
        self.NOON_TIME = "12:00"
        self.EVENING_TIME = "16:30"
    
    def add_morning_task(self, task: Callable, run_immediately: bool = True):
        """
        添加早盘分析任务（8:30）
        
        Args:
            task: 要执行的任务函数
            run_immediately: 是否在设置后立即执行一次
        """
        self._add_task("morning", self.MORNING_TIME, task, run_immediately)
    
    def add_noon_task(self, task: Callable, run_immediately: bool = False):
        """
        添加午盘总结任务（12:00）
        
        Args:
            task: 要执行的任务函数
            run_immediately: 是否在设置后立即执行一次
        """
        self._add_task("noon", self.NOON_TIME, task, run_immediately)
    
    def add_evening_task(self, task: Callable, run_immediately: bool = False):
        """
        添加复盘任务（16:30）
        
        Args:
            task: 要执行的任务函数
            run_immediately: 是否在设置后立即执行一次
        """
        self._add_task("evening", self.EVENING_TIME, task, run_immediately)
    
    def add_custom_task(self, task_name: str, schedule_time: str, task: Callable, run_immediately: bool = False):
        """
        添加自定义定时任务
        
        Args:
            task_name: 任务名称
            schedule_time: 执行时间 "HH:MM"
            task: 要执行的任务函数
            run_immediately: 是否立即执行一次
        """
        self._add_task(task_name, schedule_time, task, run_immediately)
    
    def _add_task(self, task_name: str, schedule_time: str, task: Callable, run_immediately: bool):
        """内部方法：添加任务"""
        self._task_callbacks[task_name] = task
        
        # 设置每日定时任务
        self.schedule.every().day.at(schedule_time).do(
            self._safe_run_task, 
            task_name=task_name,
            task=task
        )
        logger.info(f"已设置任务 [{task_name}]，执行时间: {schedule_time}")
        
        if run_immediately:
            logger.info(f"立即执行任务 [{task_name}]...")
            self._safe_run_task(task_name, task)
    
    def _safe_run_task(self, task_name: str, task: Callable):
        """安全执行任务（带异常捕获）"""
        try:
            logger.info("=" * 60)
            logger.info(f"定时任务开始执行 - {task_name} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 60)
            
            task()
            
            logger.info(f"定时任务执行完成 - {task_name} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            logger.exception(f"定时任务 [{task_name}] 执行失败: {e}")
    
    def run(self):
        """
        运行调度器主循环
        
        阻塞运行，直到收到退出信号
        """
        self._running = True
        logger.info("增强版调度器开始运行...")
        logger.info(f"已设置任务: {list(self._task_callbacks.keys())}")
        logger.info(f"下次执行时间: {self._get_next_run_time()}")
        
        while self._running and not self.shutdown_handler.should_shutdown:
            self.schedule.run_pending()
            time.sleep(30)  # 每30秒检查一次
            
            # 每小时打印一次心跳
            if datetime.now().minute == 0 and datetime.now().second < 30:
                logger.info(f"调度器运行中... 下次执行: {self._get_next_run_time()}")
        
        logger.info("调度器已停止")
    
    def _get_next_run_time(self) -> str:
        """获取下次执行时间"""
        jobs = self.schedule.get_jobs()
        if jobs:
            next_run = min(job.next_run for job in jobs)
            return next_run.strftime('%Y-%m-%d %H:%M:%S')
        return "未设置"
    
    def stop(self):
        """停止调度器"""
        self._running = False


def run_enhanced_schedule(
    morning_task: Optional[Callable] = None,
    noon_task: Optional[Callable] = None,
    evening_task: Optional[Callable] = None,
    custom_tasks: Optional[List[Dict]] = None,
    run_immediately: bool = True
):
    """
    便捷函数：使用增强版定时调度运行任务
    
    Args:
        morning_task: 早盘分析任务（8:30）
        noon_task: 午盘总结任务（12:00）
        evening_task: 复盘任务（16:30）
        custom_tasks: 自定义任务列表，每项为 {'name': '', 'time': '', 'task': func}
        run_immediately: 是否立即执行一次
    """
    scheduler = EnhancedScheduler()
    
    if morning_task:
        scheduler.add_morning_task(morning_task, run_immediately=run_immediately)
    
    if noon_task:
        scheduler.add_noon_task(noon_task, run_immediately=False)
    
    if evening_task:
        scheduler.add_evening_task(evening_task, run_immediately=False)
    
    if custom_tasks:
        for task_config in custom_tasks:
            scheduler.add_custom_task(
                task_name=task_config['name'],
                schedule_time=task_config['time'],
                task=task_config['task'],
                run_immediately=task_config.get('run_immediately', False)
            )
    
    scheduler.run()


if __name__ == "__main__":
    # 测试增强版调度器
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
    )
    
    def test_morning():
        print(f"⏰ 早盘分析任务执行中... {datetime.now()}")
        time.sleep(2)
        print("✅ 早盘分析任务完成!")
    
    def test_noon():
        print(f"⏰ 午盘总结任务执行中... {datetime.now()}")
        time.sleep(2)
        print("✅ 午盘总结任务完成!")
    
    def test_evening():
        print(f"⏰ 复盘任务执行中... {datetime.now()}")
        time.sleep(2)
        print("✅ 复盘任务完成!")
    
    print("启动测试增强版调度器（按 Ctrl+C 退出）")
    run_enhanced_schedule(
        morning_task=test_morning,
        noon_task=test_noon,
        evening_task=test_evening,
        run_immediately=True
    )
