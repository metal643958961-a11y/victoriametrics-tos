# VictoriaMetrics for TOS 7 · v1.156.0.1 Beta

适用于 x86_64 TNAS，依赖 DockerEngine。单机服务提供时间序列写入、MetricsQL 查询和 VMUI，端口 18428。固定上游 OSS 镜像 v1.156.0-rc0-scratch。设置实例口令后登录，具体目录、权限和 HTTPS 配置见 README.md。

拟用标签 v1.156.0.1。附件为 victoriametrics.tar.gz 及 SHA256SUMS。安装包 SHA256 为 2d3fa59e13b9edefca19379c786b690887326060d80728d04ba2a3e44672e6a4。公开后通过适配仓库 Issues 接收反馈。

已在官方 TOS 7.0.1422 x86_64 体验机上通过固定镜像启动、VMUI HTTP、指标读写以及重启和重建持久化验证。该体验机的镜像代理首次拉取返回 502，验证使用导入的同摘要镜像。Beta 在 TOS 仅对测试用户展示。
