# auto-bookkeeping

一个全自动财务分析工具，使用机器学习自动清洗和分类数据，并输出可视化图表。

## 项目简介

Auto-Bookkeeping 是一个智能账单管理系统，能够自动处理来自微信和支付宝的账单数据，通过机器学习算法对交易进行分类，并生成直观的财务报表和可视化图表，帮助用户更好地了解自己的消费习惯和财务状况。

## 主要功能

- **多源账单导入**：支持微信和支付宝账单CSV文件的导入和解析
- **数据清洗与标准化**：自动处理和标准化不同来源的账单数据
- **智能分类**：使用机器学习和向量数据库对交易进行自动分类
- **财务分析**：生成月度、季度和年度财务报表
- **可视化图表**：直观展示消费趋势、类别分布等信息
- **持续学习**：系统会不断学习用户的消费模式，提高分类准确率

## 技术栈

- **Python**：核心编程语言
- **Pandas**：数据处理和分析
- **Scikit-learn**：机器学习模型训练
- **Sentence-Transformers**：文本嵌入生成
- **ChromaDB**：向量数据库存储和检索
- **Matplotlib/Plotly**：数据可视化
- **Jupyter Notebook**：交互式开发和分析

## 使用方法

### 环境准备

1. 确保已安装Python 3.8+
2. 安装依赖包：

```bash
pip install pandas numpy scikit-learn matplotlib plotly sentence-transformers chromadb jupyter
```

### 数据准备

1. 从微信和支付宝导出账单CSV文件
2. 将文件分别命名为 wechat_record.csv 和 alipay_record.csv
3. 将文件放入 data-source 目录

### 运行流程

1. 运行 1.bill_formatter.ipynb 进行账单格式化和合并
2. 运行 0.vector_db_initializer.ipynb 初始化向量数据库
3. 运行 2.ml_train_by_vector_db.ipynb 训练分类模型
4. 运行 3.statistics.ipynb 生成统计报表和可视化图表

## 未来计划

- 开发Web界面，提供更友好的用户交互
- 支持更多账单来源（如银行账单、信用卡账单等）
- 添加预算管理和财务预测功能
- 实现自动化定期处理流程
- 增强数据安全性和隐私保护

## 贡献指南

欢迎贡献代码或提出建议！请遵循以下步骤：

1. Fork本仓库
2. 创建您的特性分支 ( git checkout -b feature/amazing-feature )
3. 提交您的更改 ( git commit -m 'Add some amazing feature' )
4. 推送到分支 ( git push origin feature/amazing-feature )
5. 开启一个Pull Request

## 许可证

本项目采用MIT许可证 - 详情请参见 LICENSE 文件
