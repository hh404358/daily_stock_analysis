#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from datetime import datetime
from pathlib import Path

# Set up environment
sys.path.insert(0, '/workspace')
os.environ['RUN_IMMEDIATELY'] = 'false'  # Prevent main.py from running automatically

from src.config import setup_env, get_config
setup_env()

from src.core.market_review import MarketAnalyzer
from src.core.pipeline import StockAnalysisPipeline
from src.search_service import SearchService
from src.notification import NotificationService
from src.analyzer import GeminiAnalyzer
from data_provider.base import canonical_stock_code

def main():
    # User's stock list
    stock_list = [
        "600519", "300750", "002594", "000601", "600666",
        "601857", "601015", "600815", "002490", "600095",
        "002840", "000735", "300059", "600313",
        "600900", "601868", "002015"
    ]
    
    # Canonicalize stock codes
    stock_codes = [canonical_stock_code(code) for code in stock_list]

    config = get_config()

    # 1. Run market review
    print("Running market review...")
    notifier = NotificationService()
    search_service = None
    analyzer = None

    if config.bocha_api_keys or config.tavily_api_keys or config.brave_api_keys or config.serpapi_keys:
        search_service = SearchService(
            bocha_keys=config.bocha_api_keys,
            tavily_keys=config.tavily_api_keys,
            brave_keys=config.brave_api_keys,
            serpapi_keys=config.serpapi_keys,
            news_max_age_days=config.news_max_age_days,
        )

    if config.gemini_api_key or config.openai_api_key or config.litellm_model:
        analyzer = GeminiAnalyzer()
        if not analyzer.is_available():
            print("AI analyzer not available")
            analyzer = None

    market_analyzer = MarketAnalyzer(
        search_service=search_service,
        analyzer=analyzer,
        region="cn"
    )
    market_report = market_analyzer.run_daily_review()

    # 2. Run stock analysis
    print("Running stock analysis...")
    pipeline = StockAnalysisPipeline(
        config=config,
        max_workers=4,
        query_id="evening_review",
        query_source="cli",
        save_context_snapshot=False
    )
    results = pipeline.run(
        stock_codes=stock_codes,
        dry_run=False,
        send_notification=False
    )

    # 3. Generate full report
    print("Generating report...")
    stock_report = notifier.generate_dashboard_report(results)

    date_str = datetime.now().strftime('%Y%m%d')
    report_path = Path("/workspace/logs") / f"晚间复盘_{date_str}.md"

    full_report = f"""\
# 晚间复盘 - {datetime.now().strftime('%Y年%m月%d日')}

---

## 第一步：复盘主要指数
{market_report}

---

## 第四步：个人持仓分析
{stock_report}

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(full_report)

    print(f"Report saved to {report_path}")

if __name__ == "__main__":
    main()
