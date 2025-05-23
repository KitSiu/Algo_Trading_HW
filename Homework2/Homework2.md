# 基于 Chinascope 与 DeepSeek 的新闻情绪选股策略

本项目基于 **Chinascope** 提供的新闻数据，结合 **DeepSeek** 大语言模型对新闻情绪的打分结果，构建了一个量化新闻情绪因子，并进行了回测分析。

## 数据与预处理

- **数据来源**：Chinascope 金融新闻
- **筛选标准**：仅保留与股票相关性大于等于 0.8 的新闻-股票对
- **时间戳处理**：为避免未来数据泄露，所有在收盘后发布的新闻，其时间戳统一顺延至 **次日（T+1）**

## 情绪打分方法

每条新闻通过 DeepSeek 模型进行情绪打分，输入包括：

- 新闻标题  
- 新闻概括  
- 关联股票代码  

模型输出分值范围为 **[-1, 1]**，含义如下：

- `1` → 强烈看多  
- `0` → 中性情绪  
- `-1` → 强烈看空  

## 因子构建逻辑

- 使用 **指数加权平均（EWA）函数**，对每支股票过去 **7 个自然日（含当日）** 的每日平均新闻情绪分数加权平均，生成当日因子值
- 每周最后一个交易日调仓，将股票按该因子值排序，分为 **10 组**
- 以第 1 组为空头组、第 10 组为多头组，分别构建多空组合和多头组合进行回测

## 回测设定

- **多空策略（0手续费）**：做多第 10 分组，做空第 1 分组
- **多头策略（0手续费）**：仅做多第 10 分组
- **多头策略（加手续费）**：假设每次交易收取 **0.0015 单边手续费**

## 回测表现（多头策略，考虑手续费）

| 指标               | 数值       |
|--------------------|------------|
| 年化收益率         | 35.43%     |
| 年化波动率         | 25.13%     |
| 夏普比率           | 1.33       |
| 最大回撤           | 41.92%     |
| Omega 比率         | -1.27      |
| Calmar 比率        | 0.80       |
| Sortino 比率       | 1.85       |

## 总结

本项目展示了如何基于大语言模型打分的高相关性金融新闻，构建新闻情绪因子并用于股票多头策略。实验证明，该因子具有一定的预期收益能力，并能在考虑手续费的情况下取得显著超额收益。
