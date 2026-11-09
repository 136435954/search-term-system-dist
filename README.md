# 搜索词分析系统

基于积加开放平台 API 的亚马逊广告搜索词分析工具：本地运行、本地存储，自动同步广告报表并生成搜索词分析与优化建议。

## 下载

最新版本：**v1.2.9**

- Windows 免安装版：[下载 search-term-system-setup.exe](https://github.com/136435954/search-term-system-dist/releases/download/v1.2.9/search-term-system-setup.exe)
- [使用说明](使用说明.md)

## 本版更新（v1.2.9）

文案口径修正：卡片加 ACoS 线标注、p3/p4 标题区分、空状态引导、切店铺提示。

## 功能

- 全店广告总览：花费 / 订单 / 销售额 / 曝光 / 点击 / CVR / ACoS + 近 14 日趋势
- 搜索词两行制分析（历史累计 / 新增时段）与优化建议
- 重点优化清单、广告组合视图、ASIN 维度、投放证据
- 增量同步（断点续传）、Excel 导出
- 自动检查更新

## 系统要求

- Windows 10 / 11
- 可访问积加开放平台（open.gerpgo.com）
- 需要积加开放平台 AppId / AppKey（后台加白名单）

## 隐私与安全

- 凭证仅保存在本机 config.json，不随软件分发、不上传
- 数据全部存储在本机 data/ 目录
- 本地服务 127.0.0.1，不对外网开放

<!-- build/state: ok -->
