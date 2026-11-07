# VictoriaMetrics 单机版 · TOS 7 x86_64

本包提供时间序列写入、MetricsQL 查询与 VMUI。上游 Docker Hub 镜像使用开源 scratch 版本 v1.156.0-rc0，固定 linux/amd64 摘要。适配包版本 1.156.0.1，标记 Beta。依赖 DockerEngine 和可用 TCP 18428。

安装后，在所选卷的 DockerAppData/victoriametrics/config 目录中创建名为 http-password 的纯文本文件，写入自己生成的非空强口令。仅允许管理员和服务 UID 1000 读取该文件；Linux 文件所有者应为 1000，模式 0600。不要把口令放进仓库或日志。启动服务，用浏览器访问 NAS 的 18428 端口，打开 /vmui/，以 metrics 和该口令登录。HTTP Basic Auth 需要可信网络，外部访问应经 HTTPS 反向代理。应用只挂载自身的 config 和 data。备份或迁移时一并保留两者。

用 Python 3 和 Ruby/Psych 运行 `python3 build.py`，然后运行 `(cd dist && shasum -a 256 -c SHA256SUMS)`。在专用空闲 Linux Docker 测试机上用 `sudo python3 test.py dist/victoriametrics.tar.gz` 测试。测试仅使用临时账户口令、临时目录和合成指标。TOS 7.0.1422 已通过同摘要镜像导入后的 Compose 运行、读写及数据保留验证。平台冷拉取、应用中心桌面入口和卸载选项仍需在投放流程核验。

上游源码与许可证见 [固定提交](https://github.com/VictoriaMetrics/VictoriaMetrics/tree/0c1bf87a0c9843c30566df0c0aa6593466425ac5) 和 [Apache-2.0 全文](licenses/Apache-2.0.txt)。发行附件仅含适配配置、语言和自绘图标；DockerEngine 从上游获取镜像，附件不包含第三方二进制、镜像层或前端代码。公开后由独立适配仓库的 Issues 接收安装与安全反馈。

发布说明：首个单机版 Beta，提供权限受限的单服务容器，使用按实例设置的口令，无预设通用密码。默认端口 18428。替换版本前先备份，卸载时选择保留数据。
