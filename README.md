# auto-bookkeeping
A fully automated financial analysis tool that uses machine learning to automatically clean and categorize data and output visual charts

## 用户设置

```json
{
  // 用户设定关键词过滤
  "keywords": {
    "超市": "餐饮",
    "生鲜": "餐饮",
    "便利店": "餐饮",

    "公交": "交通",
    "地铁": "交通",
    "打车": "交通"
  },
  // 特征词频最小阈值
  "minKeyWordsFrequency": 2,
  // 支付宝原始账单路径
  "aliPayOriginPath": "data-source/origin-data/alipay_record.csv",
  // 微信原始账单路径
  "wechatPayOriginPath": "data-source/origin-data/wechat_record.csv",
  // 数据集路径
  "datasetPath": "data-source/dataset/dataset.csv",
  // 生成的csv文件路径
  "destinationPath": "out/processed-data.csv",
  // excel 模板文件路径
  "templatePath": "data-source/template/template.xlsx",
  // excel 目标文件路径
  "xlsxDestinationPath": "out/processed-data.xlsx"
}
```
