# -*- coding: utf-8 -*-
"""
===================================
时段分析模块 - 早盘/午盘/复盘
===================================

职责：
1. 早盘分析（8:30）：盘前早报、交易策略
2. 午盘总结（12:00）：早盘情况总结
3. 晚间复盘（16:30）：完整复盘、次日预测
"""

import logging
from datetime import datetime
from typing import Optional, List
from src.config import get_config
from src.notification import NotificationService
from src.analyzer import GeminiAnalyzer
from src.search_service import SearchService

logger = logging.getLogger(__name__)


class PeriodAnalysis:
    """时段分析基类"""
    
    def __init__(
        self,
        notifier: Optional[NotificationService] = None,
        analyzer: Optional[GeminiAnalyzer] = None,
        search_service: Optional[SearchService] = None
    ):
        self.config = get_config()
        self.notifier = notifier or NotificationService()
        self.analyzer = analyzer
        self.search_service = search_service
    
    def _init_services(self):
        """初始化服务（如果未提供）"""
        if not self.analyzer and (self.config.gemini_api_key or self.config.openai_api_key):
            from src.analyzer import GeminiAnalyzer
            self.analyzer = GeminiAnalyzer(api_key=self.config.gemini_api_key)
        
        if not self.search_service and (
            self.config.bocha_api_keys or 
            self.config.tavily_api_keys or 
            self.config.brave_api_keys or 
            self.config.serpapi_keys
        ):
            from src.search_service import SearchService
            self.search_service = SearchService(
                bocha_keys=self.config.bocha_api_keys,
                tavily_keys=self.config.tavily_api_keys,
                brave_keys=self.config.brave_api_keys,
                serpapi_keys=self.config.serpapi_keys,
                news_max_age_days=self.config.news_max_age_days,
            )
    
    def send_report(self, report: str, title: str):
        """发送报告"""
        if report and self.notifier.is_available():
            full_report = f"# {title}\n\n{report}"
            if self.notifier.send(full_report):
                logger.info(f"报告已推送: {title}")
            
            # 保存到文件
            date_str = datetime.now().strftime('%Y%m%d')
            report_filename = f"{title.replace(' ', '_')}_{date_str}.md"
            filepath = self.notifier.save_report_to_file(full_report, report_filename)
            logger.info(f"报告已保存: {filepath}")


class MorningAnalysis(PeriodAnalysis):
    """早盘分析（8:30）"""
    
    def run(self):
        """执行早盘分析"""
        logger.info("=" * 60)
        logger.info("开始早盘分析 - 盘前早报与交易策略")
        logger.info("=" * 60)
        
        self._init_services()
        
        try:
            # 步骤1：获取盘前新闻
            news_summary = self._get_morning_news()
            
            # 步骤2：生成交易策略
            trading_strategy = self._generate_trading_strategy(news_summary)
            
            # 步骤3：合并报告
            full_report = self._combine_morning_report(news_summary, trading_strategy)
            
            # 发送报告
            self.send_report(full_report, "🚀 早盘分析 - 盘前早报与交易策略")
            
            return full_report
            
        except Exception as e:
            logger.exception(f"早盘分析失败: {e}")
            return None
    
    def _get_morning_news(self) -> str:
        """获取盘前新闻"""
        today = datetime.now().strftime('%Y年%m月%d日')
        prompt = f"""
你是一位优秀的证券从业者。请提供{today}的市场早盘消息简报，包括：

1. 宏观新闻（政策、经济数据、国际形势）
2. 行业新闻（各行业动态、政策影响）
3. 企业微观新闻（重要公司公告、业绩预告等）

请从财联社、东方财富、巨潮资讯网、同花顺等权威来源整理信息，
确保数据真实可靠，并突出对投资有重要影响的内容。

格式要求：
- 使用清晰的标题和分段
- 每条新闻注明简要的影响分析
- 控制在1000字以内
"""
        
        if self.analyzer:
            try:
                return self.analyzer.analyze(prompt)
            except Exception as e:
                logger.warning(f"AI分析新闻失败: {e}")
        
        return self._get_default_news()
    
    def _generate_trading_strategy(self, news_summary: str) -> str:
        """生成交易策略"""
        prompt = f"""
基于以下盘前新闻，请生成今日的交易策略：

{news_summary}

请按照以下结构分析：

### 一、市场整体判断
- 今日大盘走势预判
- 市场情绪分析

### 二、短线操作策略
- 今日可关注的热点板块
- 推荐的短线标的和理由
- 风险提示

### 三、长线投资建议
- 近期值得布局的方向
- 看好的长期赛道

### 四、操作建议
- 仓位管理建议
- 具体的买卖点提示

请给出真实、可靠、可操作的建议。
"""
        
        if self.analyzer:
            try:
                return self.analyzer.analyze(prompt)
            except Exception as e:
                logger.warning(f"AI生成策略失败: {e}")
        
        return self._get_default_strategy()
    
    def _combine_morning_report(self, news_summary: str, trading_strategy: str) -> str:
        """合并早盘报告"""
        return f"""
## 📰 盘前早报

{news_summary}

---

## 🎯 今日交易策略

{trading_strategy}

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    def _get_default_news(self) -> str:
        """默认新闻（当AI不可用时）"""
        today = datetime.now().strftime('%Y-%m-%d')
        return f"""
### 宏观新闻
1. 关注今日央行公开市场操作
2. 隔夜美股走势将影响A股开盘情绪

### 行业新闻
1. 持续关注新能源、人工智能等赛道动向
2. 消费板块复苏态势值得观察

### 企业新闻
请关注自选股的最新公告和业绩预告。
"""
    
    def _get_default_strategy(self) -> str:
        """默认策略（当AI不可用时）"""
        return """
### 一、市场整体判断
建议谨慎观望，等待明确信号。

### 二、短线操作策略
关注盘面热点，快进快出为主。

### 三、长线投资建议
可分批布局业绩确定性强的优质标的。

### 四、操作建议
控制仓位在50%以下，设置好止损止盈。
"""


class NoonAnalysis(PeriodAnalysis):
    """午盘总结（12:00）"""
    
    def run(self):
        """执行午盘总结"""
        logger.info("=" * 60)
        logger.info("开始午盘总结 - 早盘情况回顾")
        logger.info("=" * 60)
        
        self._init_services()
        
        try:
            # 生成午盘总结
            noon_summary = self._generate_noon_summary()
            
            # 发送报告
            self.send_report(noon_summary, "📊 午盘总结 - 早盘情况回顾")
            
            return noon_summary
            
        except Exception as e:
            logger.exception(f"午盘总结失败: {e}")
            return None
    
    def _generate_noon_summary(self) -> str:
        """生成午盘总结"""
        today = datetime.now().strftime('%Y年%m月%d日')
        prompt = f"""
你是一位优秀的证券分析师。请总结{today}上午A股市场的情况：

### 一、市场总体表现
- 主要指数涨跌幅
- 成交量变化
- 市场涨跌分布

### 二、热点板块分析
- 涨幅居前的板块及原因
- 跌幅较大的板块分析
- 资金流向情况

### 三、重要个股表现
- 市场龙头股走势
- 异动个股分析

### 四、午后展望
- 下午走势预判
- 操作建议

请结合财联社、巨潮资讯网、东方财富等信息，给出专业分析。
"""
        
        if self.analyzer:
            try:
                return self.analyzer.analyze(prompt)
            except Exception as e:
                logger.warning(f"AI生成午盘总结失败: {e}")
        
        return self._get_default_noon_summary()
    
    def _get_default_noon_summary(self) -> str:
        """默认午盘总结（当AI不可用时）"""
        return f"""
### 一、市场总体表现
请关注实盘走势，结合技术指标判断。

### 二、热点板块分析
观察盘面资金流向，紧跟市场热点。

### 三、重要个股表现
关注自选股和龙头股的走势变化。

### 四、午后展望
建议结合上午走势，灵活调整策略。

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""


class EveningAnalysis(PeriodAnalysis):
    """晚间复盘（16:30）"""
    
    def run(self):
        """执行晚间复盘"""
        logger.info("=" * 60)
        logger.info("开始晚间复盘 - 完整复盘与次日预测")
        logger.info("=" * 60)
        
        self._init_services()
        
        try:
            # 步骤1：大盘复盘
            market_review = self._review_market()
            
            # 步骤2：板块表现分析
            sector_analysis = self._analyze_sectors()
            
            # 步骤3：涨停个股分析
            stock_analysis = self._analyze_stocks()
            
            # 步骤4：次日预测
            next_day_forecast = self._forecast_next_day()
            
            # 步骤5：合并报告
            full_report = self._combine_evening_report(
                market_review,
                sector_analysis,
                stock_analysis,
                next_day_forecast
            )
            
            # 发送报告
            self.send_report(full_report, "📈 晚间复盘 - 完整复盘与次日预测")
            
            return full_report
            
        except Exception as e:
            logger.exception(f"晚间复盘失败: {e}")
            return None
    
    def _review_market(self) -> str:
        """大盘复盘"""
        today = datetime.now().strftime('%Y年%m月%d日')
        prompt = f"""
请对{today}的A股市场进行复盘分析：

### 一、市场总体情况
- 主要指数表现（上证指数、深证成指、创业板指等）
- 成交量与量能分析
- 涨跌停数据统计（涨跌停家数、连板情况）
- 市场涨跌原因分析

### 二、资金流向
- 北向资金动向
- 主力资金流向
- 行业板块资金流入流出情况

### 三、市场最强主线
- 当前市场主线方向
- 主线逻辑分析

请用普通人能看懂的语言进行分析。
"""
        
        if self.analyzer:
            try:
                return self.analyzer.analyze(prompt)
            except Exception as e:
                logger.warning(f"AI大盘复盘失败: {e}")
        
        return self._get_default_market_review()
    
    def _analyze_sectors(self) -> str:
        """板块表现分析"""
        prompt = """
请分析今日板块表现：

### 一、涨幅居前板块
- 涨幅前5的板块
- 上涨原因分析
- 相关个股表现

### 二、跌幅较大板块
- 跌幅前5的板块
- 下跌原因分析

### 三、板块轮动分析
- 今日板块轮动特点
- 持续性判断
"""
        
        if self.analyzer:
            try:
                return self.analyzer.analyze(prompt)
            except Exception as e:
                logger.warning(f"AI板块分析失败: {e}")
        
        return self._get_default_sector_analysis()
    
    def _analyze_stocks(self) -> str:
        """涨停个股分析"""
        prompt = """
请分析今日涨停个股：

### 一、涨停个股梳理
- 连板个股（2连板及以上，非一字板）
- 首板涨停个股
- 热门概念龙头股

### 二、热门股分析
- 市场关注度最高的股票
- 涨停逻辑分析
- 后续走势预判

### 三、机会与风险
- 值得关注的标的
- 需要警惕的风险
"""
        
        if self.analyzer:
            try:
                return self.analyzer.analyze(prompt)
            except Exception as e:
                logger.warning(f"AI个股分析失败: {e}")
        
        return self._get_default_stock_analysis()
    
    def _forecast_next_day(self) -> str:
        """次日预测"""
        prompt = """
请对次日市场进行预测：

### 一、次日大盘走势预判
- 整体走势判断
- 关键点位分析

### 二、热点方向预测
- 可能的热点板块
- 关注逻辑

### 三、股票池更新
- 新增关注标的
- 移除观察标的
- 持仓建议

### 四、操作策略
- 具体的买卖建议
- 仓位管理
- 风险控制
"""
        
        if self.analyzer:
            try:
                return self.analyzer.analyze(prompt)
            except Exception as e:
                logger.warning(f"AI次日预测失败: {e}")
        
        return self._get_default_forecast()
    
    def _combine_evening_report(
        self,
        market_review: str,
        sector_analysis: str,
        stock_analysis: str,
        next_day_forecast: str
    ) -> str:
        """合并晚间复盘报告"""
        return f"""
## 📊 一、大盘复盘

{market_review}

---

## 🧩 二、板块表现分析

{sector_analysis}

---

## 🏆 三、涨停个股分析

{stock_analysis}

---

## 🔮 四、次日预测与股票池

{next_day_forecast}

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    def _get_default_market_review(self) -> str:
        """默认大盘复盘"""
        return """
### 一、市场总体情况
请查看实际行情数据进行分析。

### 二、资金流向
关注北向资金和主力资金动向。

### 三、市场最强主线
观察市场持续性热点。
"""
    
    def _get_default_sector_analysis(self) -> str:
        """默认板块分析"""
        return """
### 一、涨幅居前板块
请关注盘面领涨板块。

### 二、跌幅较大板块
注意风险规避。

### 三、板块轮动分析
观察板块轮动规律。
"""
    
    def _get_default_stock_analysis(self) -> str:
        """默认个股分析"""
        return """
### 一、涨停个股梳理
关注连板个股和热门概念。

### 二、热门股分析
分析龙头股走势。

### 三、机会与风险
把握机会，控制风险。
"""
    
    def _get_default_forecast(self) -> str:
        """默认预测"""
        return """
### 一、次日大盘走势预判
结合今日走势和消息面判断。

### 二、热点方向预测
关注今日强势板块的持续性。

### 三、股票池更新
更新自选股观察名单。

### 四、操作策略
制定明日操作计划。
"""


def run_morning_analysis():
    """运行早盘分析"""
    analysis = MorningAnalysis()
    return analysis.run()


def run_noon_analysis():
    """运行午盘总结"""
    analysis = NoonAnalysis()
    return analysis.run()


def run_evening_analysis():
    """运行晚间复盘"""
    analysis = EveningAnalysis()
    return analysis.run()
