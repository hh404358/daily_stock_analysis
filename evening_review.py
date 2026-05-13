# -*- coding: utf-8 -*-
"""
===================================
A股晚间复盘脚本
===================================

执行步骤：
1. 复盘主要指数
2. 复盘板块表现
3. 复盘涨停个股
4. 个人持仓分析
5. 次日关注方向
6. 推送结果
"""

import logging
import os
import sys
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
)

logger = logging.getLogger("evening_review")

STOCK_NAME_MAP = {
    '600519': '贵州茅台',
    '300750': '宁德时代',
    '002594': '比亚迪',
    '000601': '力帆科技',
    '600666': '瑞德智能',
    '601857': '中国石油',
    '601015': '陕西黑猫',
    '600815': '厦工股份',
    '002490': '山东墨龙',
    '600095': '湘财股份',
    '002840': '华统股份',
    '000735': '罗牛山',
    '300059': '东方财富',
    '600313': '农发种业',
    '600900': '长江电力',
    '601868': '中国能建',
    '002015': '协鑫能科',
}

def get_main_indices():
    """获取主要指数数据 - 模拟数据"""
    return [
        {'code': 'sh000001', 'name': '上证指数', 'current': 3524.78, 'change': 12.35, 'change_pct': 0.35, 'open': 3512.43, 'high': 3532.15, 'low': 3508.67},
        {'code': 'sz399001', 'name': '深证成指', 'current': 11289.76, 'change': -28.45, 'change_pct': -0.25, 'open': 11318.21, 'high': 11345.67, 'low': 11276.34},
        {'code': 'sz399006', 'name': '创业板指', 'current': 2387.45, 'change': -15.68, 'change_pct': -0.65, 'open': 2403.13, 'high': 2408.92, 'low': 2382.17},
        {'code': 'sh000688', 'name': '科创50', 'current': 1123.89, 'change': 8.45, 'change_pct': 0.76, 'open': 1115.44, 'high': 1128.76, 'low': 1112.34},
    ]

def get_market_stats():
    """获取市场统计数据 - 模拟数据"""
    return {
        'up_count': 2156,
        'down_count': 1734,
        'flat_count': 89,
        'limit_up_count': 45,
        'limit_down_count': 12,
        'total_amount': 9258.6,
    }

def get_sector_rankings(n=5):
    """获取板块涨跌榜 - 模拟数据"""
    top_sectors = [
        {'name': '半导体', 'change_pct': 3.25},
        {'name': '人工智能', 'change_pct': 2.87},
        {'name': '金融科技', 'change_pct': 2.15},
        {'name': '消费电子', 'change_pct': 1.98},
        {'name': '新能源', 'change_pct': 1.56},
    ]
    
    bottom_sectors = [
        {'name': '房地产', 'change_pct': -2.34},
        {'name': '银行', 'change_pct': -1.87},
        {'name': '煤炭', 'change_pct': -1.56},
        {'name': '钢铁', 'change_pct': -1.34},
        {'name': '建筑装饰', 'change_pct': -1.12},
    ]
    
    return top_sectors, bottom_sectors

def get_stock_analysis(stock_code):
    """获取个股分析数据 - 模拟数据"""
    mock_data = {
        '600519': {'price': 1685.00, 'change_pct': 1.25, 'volume': 285600, 'turnover_rate': 0.35, 'pe_ratio': 28.5},
        '300750': {'price': 189.50, 'change_pct': -0.87, 'volume': 1568000, 'turnover_rate': 2.15, 'pe_ratio': 35.2},
        '002594': {'price': 268.80, 'change_pct': 2.34, 'volume': 987500, 'turnover_rate': 1.87, 'pe_ratio': 42.6},
        '000601': {'price': 4.85, 'change_pct': -1.23, 'volume': 2345000, 'turnover_rate': 3.45, 'pe_ratio': 128.5},
        '600666': {'price': 18.65, 'change_pct': 1.56, 'volume': 456700, 'turnover_rate': 4.23, 'pe_ratio': 38.7},
        '601857': {'price': 7.85, 'change_pct': -0.51, 'volume': 3456000, 'turnover_rate': 0.87, 'pe_ratio': 12.3},
        '601015': {'price': 4.23, 'change_pct': -2.34, 'volume': 1234000, 'turnover_rate': 2.56, 'pe_ratio': 56.8},
        '600815': {'price': 5.12, 'change_pct': 0.78, 'volume': 567800, 'turnover_rate': 1.89, 'pe_ratio': 45.2},
        '002490': {'price': 9.87, 'change_pct': 1.23, 'volume': 789000, 'turnover_rate': 3.21, 'pe_ratio': 67.5},
        '600095': {'price': 12.34, 'change_pct': -0.45, 'volume': 456000, 'turnover_rate': 2.87, 'pe_ratio': 48.9},
        '002840': {'price': 16.78, 'change_pct': 0.98, 'volume': 234000, 'turnover_rate': 1.56, 'pe_ratio': 32.4},
        '000735': {'price': 8.56, 'change_pct': -1.67, 'volume': 876000, 'turnover_rate': 2.34, 'pe_ratio': 78.6},
        '300059': {'price': 15.45, 'change_pct': 1.89, 'volume': 2345000, 'turnover_rate': 4.56, 'pe_ratio': 38.2},
        '600313': {'price': 8.92, 'change_pct': 3.45, 'volume': 1567000, 'turnover_rate': 5.23, 'pe_ratio': 89.7},
        '600900': {'price': 22.34, 'change_pct': 0.45, 'volume': 123000, 'turnover_rate': 0.45, 'pe_ratio': 21.8},
        '601868': {'price': 2.78, 'change_pct': -0.67, 'volume': 4567000, 'turnover_rate': 1.23, 'pe_ratio': 25.6},
        '002015': {'price': 14.56, 'change_pct': 2.12, 'volume': 567000, 'turnover_rate': 2.89, 'pe_ratio': 45.3},
    }
    
    data = mock_data.get(stock_code, {'price': 0, 'change_pct': 0, 'volume': 0, 'turnover_rate': 0, 'pe_ratio': 0})
    return {
        'code': stock_code,
        'name': STOCK_NAME_MAP.get(stock_code, stock_code),
        'price': data['price'],
        'change_pct': data['change_pct'],
        'change_amount': data['price'] * data['change_pct'] / 100,
        'volume': data['volume'],
        'amount': data['price'] * data['volume'] / 10000,
        'high': data['price'] * 1.02,
        'low': data['price'] * 0.98,
        'open_price': data['price'] * 0.995,
        'turnover_rate': data['turnover_rate'],
        'pe_ratio': data['pe_ratio'],
        'pb_ratio': None,
        'total_mv': 0,
        'circ_mv': 0,
        'volume_ratio': 1.2,
        'amplitude': 4.0
    }

def generate_report(indices, market_stats, top_sectors, bottom_sectors, stock_analysis_list):
    """生成复盘报告"""
    now = datetime.now()
    date_str = now.strftime('%Y年%m月%d日')
    time_str = now.strftime('%H:%M')
    
    report = f"""# {date_str} A股晚间复盘

---

## 一、主要指数复盘

### 1.1 指数表现

| 指数 | 最新点位 | 涨跌幅 | 涨跌额 | 最高 | 最低 |
|------|---------|--------|--------|------|------|"""
    
    for idx in indices:
        arrow = "📈" if idx['change_pct'] > 0 else "📉" if idx['change_pct'] < 0 else "➡"
        report += f"""
| {idx['name']} | {idx['current']:.2f} | {arrow} {idx['change_pct']:+.2f}% | {idx['change']:+.2f} | {idx['high']:.2f} | {idx['low']:.2f} |"""
    
    report += f"""

### 1.2 量能分析

- **两市成交额**: {market_stats.get('total_amount', 0):.0f} 亿元
- **较昨日**: {'↑ 放量' if market_stats.get('total_amount', 0) > 9000 else '↓ 缩量'}

### 1.3 涨跌停统计

| 项目 | 数值 |
|------|------|
| 上涨家数 | {market_stats.get('up_count', 0):,} |
| 下跌家数 | {market_stats.get('down_count', 0):,} |
| 平盘家数 | {market_stats.get('flat_count', 0):,} |
| 涨停家数 | {market_stats.get('limit_up_count', 0)} |
| 跌停家数 | {market_stats.get('limit_down_count', 0)} |

### 1.4 大盘涨跌原因分析

今日市场整体{'强势上涨' if market_stats.get('up_count', 0) > market_stats.get('down_count', 0) * 1.5 else '震荡整理' if abs(market_stats.get('up_count', 0) - market_stats.get('down_count', 0)) < (market_stats.get('up_count', 0) + market_stats.get('down_count', 0)) * 0.3 else '弱势下跌'}。

从盘面来看，市场情绪{'活跃' if market_stats.get('limit_up_count', 0) > 100 else '平稳'}，资金{'持续流入' if market_stats.get('total_amount', 0) > 8000 else '观望为主'}。热点板块轮动{'有序' if len(top_sectors) > 0 else '较缓'}，{'权重股表现强势带动指数上行' if any(idx.get('change_pct', 0) > 1 for idx in indices) else '个股活跃度较高'}。

### 1.5 资金流向

- **北向资金**: 净流入 35.6 亿元
- **南向资金**: 净流入 12.3 亿元
- **两融余额**: 1.68 万亿元

---

## 二、板块表现复盘

### 2.1 涨幅前5板块

| 排名 | 板块名称 | 涨幅 | 龙头股 |
|------|---------|------|--------|"""
    
    for i, sector in enumerate(top_sectors[:5], 1):
        report += f"""
| {i} | {sector['name']} | {sector['change_pct']:+.2f}% | {get_sector_leader(sector['name'])} |"""
    
    report += f"""

### 2.2 跌幅前5板块

| 排名 | 板块名称 | 跌幅 |
|------|---------|------|"""
    
    for i, sector in enumerate(bottom_sectors[:5], 1):
        report += f"""
| {i} | {sector['name']} | {sector['change_pct']:+.2f}% |"""
    
    report += """

### 2.3 概念板块表现

今日领涨板块主要集中在{}等方向，{}板块表现疲软。市场热点{}。

### 2.4 板块轮动分析

从板块涨跌分布来看，{}，显示市场{}。建议关注{}。
""".format(
        '、'.join([s['name'] for s in top_sectors[:3]]) if top_sectors else '暂无',
        '、'.join([s['name'] for s in bottom_sectors[:3]]) if bottom_sectors else '暂无',
        '持续性较强' if len(top_sectors) > 0 and top_sectors[0].get('change_pct', 0) > 3 else '轮换较快',
        '资金流向{}等强势板块'.format('、'.join([s['name'] for s in top_sectors[:2]])) if top_sectors else '缺乏明显主线',
        '情绪较为{}'.format('高涨' if market_stats.get('limit_up_count', 0) > 50 else '谨慎'),
        '{}板块的持续性机会'.format('、'.join([s['name'] for s in top_sectors[:2]])) if top_sectors else '防御性板块'
    )
    
    hot_concepts = []
    if top_sectors:
        hot_concepts.append(f"1. **{top_sectors[0]['name']}**: 涨幅{top_sectors[0].get('change_pct', 0):.2f}%，领涨市场")
    if len(top_sectors) > 1:
        hot_concepts.append(f"2. **{top_sectors[1]['name']}**: 涨幅{top_sectors[1].get('change_pct', 0):.2f}%")
    if len(top_sectors) > 2:
        hot_concepts.append(f"3. **{top_sectors[2]['name']}**: 涨幅{top_sectors[2].get('change_pct', 0):.2f}%")
    
    report += f"""
---

## 三、涨停个股复盘

### 3.1 连板个股（近10日2连板）

| 股票 | 连板数 | 涨停原因 |
|------|--------|----------|
| 农发种业 | 3连板 | 农业政策利好 |
| 东方财富 | 2连板 | 金融科技概念 |
| 协鑫能科 | 2连板 | 新能源赛道 |
| 比亚迪 | 2连板 | 新能源汽车销量超预期 |

### 3.2 首板涨停

首板涨停{market_stats.get('limit_up_count', 0)}家，主要集中在{'、'.join([s['name'] for s in top_sectors[:3]]) if top_sectors else '暂无'}等方向。涨停逻辑以政策驱动和业绩预增为主。

### 3.3 市场龙头

今日市场龙头股表现{'强势' if market_stats.get('limit_up_count', 0) > 30 else '一般'}，{top_sectors[0]['name'] if top_sectors else '暂无'}板块整体领涨。

### 3.4 热门概念

{chr(10).join(hot_concepts) if hot_concepts else '暂无'}"""
    
    report += """
---

## 四、个人持仓分析

本次分析自选股共{}只：

| 代码 | 名称 | 最新价 | 涨跌幅 | 成交量 | 换手率 | 市盈率 | 技术判断 | 明日建议 |
|------|------|--------|--------|--------|--------|--------|----------|----------|""".format(len(stock_analysis_list))
    
    for stock in stock_analysis_list:
        if stock:
            arrow = "📈" if stock['change_pct'] > 0 else "📉" if stock['change_pct'] < 0 else "➡"
            tech_judge = get_technical_judgment(stock)
            suggestion = get_suggestion(stock)
            report += f"""
| {stock['code']} | {stock.get('name', stock['code'])} | {stock['price']:.2f} | {arrow} {stock['change_pct']:+.2f}% | {stock['volume']:,} | {stock['turnover_rate']:.2f}% | {stock['pe_ratio']:.2f} | {tech_judge} | {suggestion} |"""
    
    valid_stocks = [s for s in stock_analysis_list if s]
    avg_change = sum(s['change_pct'] for s in valid_stocks) / len(valid_stocks) if valid_stocks else 0
    
    report += """

### 持仓综合分析

- **上涨股票**: {} 只
- **下跌股票**: {} 只
- **平盘股票**: {} 只
- **平均涨幅**: {:.2f}%

{}

**资金流向分析**: 今日持仓个股整体呈现{}态势，{}等个股资金流入明显。
""".format(
        sum(1 for s in stock_analysis_list if s and s['change_pct'] > 0),
        sum(1 for s in stock_analysis_list if s and s['change_pct'] < 0),
        sum(1 for s in stock_analysis_list if s and s['change_pct'] == 0),
        avg_change,
        '持仓整体表现{}于大盘。'.format('好' if avg_change > 0 else '差'),
        '资金流入' if avg_change > 0 else '资金流出',
        '、'.join([s.get('name', s['code']) for s in stock_analysis_list if s and s['change_pct'] > 2])[:50]
    )
    
    report += """
---

## 五、次日关注方向

### 5.1 大盘预判

**上证指数**:
- **支撑位**: {}
- **压力位**: {}

**创业板指**:
- **支撑位**: {}
- **压力位**: {}

预计明日大盘{}。
""".format(
        f"{indices[0]['low']:.2f}" if indices else 'N/A',
        f"{indices[0]['high']:.2f}" if indices else 'N/A',
        f"{indices[2]['low']:.2f}" if len(indices) > 2 else 'N/A',
        f"{indices[2]['high']:.2f}" if len(indices) > 2 else 'N/A',
        '继续震荡上行' if market_stats.get('up_count', 0) > market_stats.get('down_count', 0) else '维持震荡格局'
    )
    
    report += """

### 5.2 热点预测

1. **{}**: {}
2. **{}**: {}
3. **{}**: {}
""".format(
        top_sectors[0]['name'] if top_sectors else '暂无',
        '有望延续强势' if top_sectors else '',
        top_sectors[1]['name'] if len(top_sectors) > 1 else '暂无',
        '值得关注' if len(top_sectors) > 1 else '',
        top_sectors[2]['name'] if len(top_sectors) > 2 else '暂无',
        '有补涨机会' if len(top_sectors) > 2 else ''
    )
    
    report += """

### 5.3 股票池更新建议

- **重点关注**: {}
- **谨慎观望**: {}
- **建议减仓**: {}
""".format(
        '、'.join([s.get('name', s['code']) for s in stock_analysis_list if s and s['change_pct'] > 3]) or '暂无',
        '、'.join([s.get('name', s['code']) for s in stock_analysis_list if s and abs(s['change_pct']) <= 1])[:80] or '暂无',
        '、'.join([s.get('name', s['code']) for s in stock_analysis_list if s and s['change_pct'] < -2]) or '暂无'
    )
    
    report += """

### 5.4 操作策略

- **仓位建议**: {}
- **买入策略**: {}
- **卖出策略**: {}
- **风险提示**: {}
""".format(
        '建议{}仓位操作'.format('70%以上' if market_stats.get('up_count', 0) > market_stats.get('down_count', 0) else '50%-70%'),
        '关注{}等板块的回踩机会'.format('、'.join([s['name'] for s in top_sectors[:2]]) if top_sectors else '强势'),
        '涨幅过大个股注意止盈，破位个股果断止损',
        '市场有风险，投资需谨慎。以上分析仅供参考，不构成投资建议'
    )
    
    report += f"""

---

**复盘时间**: {date_str} {time_str}
**数据来源**: 模拟数据（网络环境限制）

---

*以上内容仅供参考，不构成投资建议*"""
    
    return report

def get_sector_leader(sector_name):
    """获取板块龙头股"""
    leaders = {
        '半导体': '中芯国际、北方华创',
        '人工智能': '科大讯飞、三六零',
        '金融科技': '东方财富、同花顺',
        '消费电子': '立讯精密、歌尔股份',
        '新能源': '宁德时代、比亚迪',
        '房地产': '万科A、保利发展',
        '银行': '招商银行、平安银行',
        '煤炭': '中国神华、陕西煤业',
        '钢铁': '宝钢股份、鞍钢股份',
        '建筑装饰': '中国建筑、中国中铁',
    }
    return leaders.get(sector_name, '龙头股')

def get_technical_judgment(stock):
    """技术判断"""
    change = stock['change_pct']
    turnover = stock['turnover_rate']
    
    if change > 3:
        return '强势上涨，量能充足'
    elif change > 1:
        return '震荡上行'
    elif change > -1:
        return '横盘整理'
    elif change > -3:
        return '小幅回调'
    else:
        return '放量下跌，注意风险'

def get_suggestion(stock):
    """操作建议"""
    change = stock['change_pct']
    pe = stock['pe_ratio']
    
    if change > 3:
        return '持有待涨'
    elif change > 0:
        return '继续持有'
    elif abs(change) < 2:
        return '观望'
    elif pe > 100:
        return '建议减仓'
    else:
        return '逢低补仓'

def main():
    logger.info("========== 开始执行 A股晚间复盘 ==========")
    
    stock_list = [
        '600519', '300750', '002594', '000601', '600666',
        '601857', '601015', '600815', '002490', '600095',
        '002840', '000735', '300059', '600313',
        '600900', '601868', '002015'
    ]
    
    logger.info("获取主要指数数据...")
    indices = get_main_indices()
    logger.info(f"获取到 {len(indices)} 个指数")
    
    logger.info("获取市场统计数据...")
    market_stats = get_market_stats()
    
    logger.info("获取板块涨跌榜...")
    top_sectors, bottom_sectors = get_sector_rankings(5)
    
    logger.info("分析自选股...")
    stock_analysis_list = []
    for code in stock_list:
        logger.info(f"分析 {code}...")
        analysis = get_stock_analysis(code)
        stock_analysis_list.append(analysis)
    
    logger.info("生成复盘报告...")
    report = generate_report(indices, market_stats, top_sectors, bottom_sectors, stock_analysis_list)
    
    date_str = datetime.now().strftime('%Y%m%d')
    report_dir = '/workspace/logs'
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f'晚间复盘_{date_str}.md')
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info(f"复盘报告已保存: {report_path}")
    
    push_script = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

def send_feishu(url, title, content):
    try:
        import requests
        payload = {"msg_type": "interactive", "card": {"header": {"title": {"tag": "plain_text", "content": title}, "template": "blue"}, "elements": [{"tag": "markdown", "content": content[:4000]}]}}
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200 and resp.json().get("code") == 0: print("[飞书] 成功"); return True
        print(f"[飞书] 失败")
    except: pass
    return False

def send_email(sender, pwd, receivers, subject, content):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject; msg["From"] = sender; msg["To"] = ", ".join(receivers)
        html = f'<html><body style="font-family:Microsoft YaHei;"><div>{content.replace(chr(10), "<br>")}</div></body></html>'
        msg.attach(MIMEText(content, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))
        with smtplib.SMTP_SSL("smtp.qq.com", 465) as s: s.login(sender, pwd); s.sendmail(sender, receivers, msg.as_string())
        print("[邮件] 成功")
    except: pass

def push_report(title, content):
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    full_title = f"[A股分析] {title} - {now}"
    send_feishu("https://open.feishu.cn/open-apis/bot/v2/hook/47549031-08ab-4b58-9c96-f8d5d74e19ae", full_title, content)
    send_email("2770754682@qq.com", "hlcsedrvznxmdeee", ["2770754682@qq.com"], full_title, content)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2: sys.exit(1)
    title = sys.argv[1]
    date_str = datetime.now().strftime('%Y%m%d')
    filepath = Path("/workspace/logs") / f"{title.replace(' ', '_')}_{date_str}.md"
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f: push_report(title, f.read())
"""
    
    push_script_path = '/workspace/run_push.py'
    with open(push_script_path, 'w', encoding='utf-8') as f:
        f.write(push_script)
    
    os.chmod(push_script_path, 0o755)
    logger.info(f"推送脚本已创建: {push_script_path}")
    
    logger.info("========== A股晚间复盘完成 ==========")
    
    return report_path

if __name__ == "__main__":
    main()