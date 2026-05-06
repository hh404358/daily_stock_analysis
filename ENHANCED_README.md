# A股自选股智能分析系统 - 增强版

## 新增功能

### 增强版定时任务系统

新增了三个时段的分析功能，配合定时任务系统可以实现全天自动化分析：

1. **早盘分析 (8:30)** - 盘前早报 + 交易策略
2. **午盘总结 (12:00)** - 早盘市场情况总结
3. **晚间复盘 (16:30)** - 完整复盘 + 次日预测

## 使用方法

### 单独运行各时段分析

```bash
# 早盘分析
python main.py --morning

# 午盘总结
python main.py --noon

# 晚间复盘
python main.py --evening
```

### 运行增强版定时任务（推荐）

```bash
# 启动增强版定时任务，会自动在 8:30、12:00、16:30 执行
python main.py --enhanced-schedule
```

### 原始功能（保持不变）

```bash
# 原始定时任务
python main.py --schedule

# 仅运行大盘复盘
python main.py --market-review

# 正常分析
python main.py
```

## 配置说明

### .env 文件配置

确保在 `.env` 文件中正确配置了以下内容：

```env
# 商汤日日新平台 API 配置（已配置）
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.sensenova.cn/v1
OPENAI_MODEL=deepseek-v4-flash
LITELLM_FALLBACK_MODELS=sensenova-6.7-flash-lite

# 飞书通知（已配置）
FEISHU_WEBHOOK_URL=your_webhook_url

# 邮件通知（已配置）
EMAIL_SENDER=your_email@qq.com
EMAIL_PASSWORD=your_password
EMAIL_RECEIVERS=receiver@qq.com
```

### 定时任务时间配置

三个时段的时间已固定：
- 早盘分析：08:30
- 午盘总结：12:00
- 晚间复盘：16:30

如果需要修改，可以编辑 `src/enhanced_scheduler.py` 文件。

## 项目结构

```
/workspace/
├── src/
│   ├── enhanced_scheduler.py    # 新增：增强版定时任务调度器
│   ├── period_analysis.py       # 新增：时段分析模块（早/午/晚）
│   ├── scheduler.py             # 原始定时任务调度器
│   ├── config.py                # 配置管理
│   ├── notification.py          # 通知服务
│   └── ...
├── main.py                      # 主程序（已更新）
├── test_enhanced.py             # 新增：测试脚本
└── ENHANCED_README.md           # 本文档
```

## 测试

运行测试脚本验证系统功能：

```bash
python test_enhanced.py
```

## 注意事项

1. **网络连接**：系统需要网络连接获取股票数据和调用 AI API
2. **API 配置**：确保 API Key 配置正确，否则 AI 分析功能会降级到模板模式
3. **推送通知**：确保飞书 Webhook 和邮件配置正确，否则推送会失败
4. **交易日检查**：系统会自动检查交易日，非交易日可能会跳过分析
