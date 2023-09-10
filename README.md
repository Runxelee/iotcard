# 专为处理无良物联网卡商家
[密码字典来源](https://github.com/TheKingOfDuck/fuzzDicts/tree/master/passwordDict)

已实现功能：
- [x] 字典循环POST
- [x] 及时从页面更新csrf_token和cookie
- [x] 固定并记录文件读取顺序
- [x] 每5小时自动停止并记录密码编号，第6个小时继续运行以应对Github Action限制