# astrbot_plugin_idgen

_✨ [astrbot](https://github.com/AstrBotDevs/AstrBot) 身份证生成/校验插件 ✨_  
[![License](https://img.shields.io/badge/License-AGPLv3-purple.svg)](https://opensource.org/license/agpl-v3)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![AstrBot](https://img.shields.io/badge/AstrBot-3.4%2B-orange.svg)](https://github.com/Soulter/AstrBot)
[![GitHub](https://img.shields.io/badge/作者-ZvZPvz-blue)](https://github.com/ZvZPvz)

</div>

## 🤝 介绍

生成香港和大陆身份证号码/计算校验码

## 📦 安装

- 直接在Astrbot插件市场安装即可

## ⌨️ 使用说明

### 命令

```plaintext
- `gen_cn <YYYYMMDD> [M|F]`: 
  隨機生成中國大陸ID。需提供8位生日。
  可選 [M](男) 或 [F](女) 指定性別。
- `gen_hk <YYYY>` 或 `gen_hk <Letter>`:
  隨機生成香港ID。
  可輸入年份 (如 1985) 自動匹配字母，或直接指定字母 (如 K)。

- `sum_cn <17位本體>`: 計算CNID的第18位校驗碼。
- `sum_hk <本體>`: 計算HKID的校驗碼 (如 G123456)。

- `validate_cn <18位ID>`: 驗證CNID。
- `validate_hk <ID(C)>`: 驗證HKID (如 C123456(9))。

```

## 👥 贡献指南

- 🌟 Star 这个项目！（点右上角的星星，感谢支持！）
- 🐛 提交 Issue 报告问题
- 💡 提出新功能建议
- 🔧 提交 Pull Request 改进代码

# 支持

验证身份证功能仅为验证计算所得校验码是否合法，並不能验证身份证真伪！
请勿输入个人私隐信息
