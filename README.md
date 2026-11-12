# victoriametrics for TOS 7

x86_64 Docker 整改版本 1.156.0.2。本地静态及容器回归通过，真实TOS应用中心安装仍待官方验收；Release发布不代表已通过审核。

首次启动自动生成独立随机凭据，无需 .env；TOS平台须按官方规范创建数据目录并设置配置user的所有权。初始化服务与主服务均使用 1000:1000，私有数据位于应用专用绑定目录的 private 目录。管理员从 Container Manager 中查看该应用数据目录的 private/password，用户名为 metrics。请勿将凭据放入日志或反馈。保留数据目录重装可保留数据和密码；删除该数据目录会永久清除数据。

旧版绑定目录迁移必须停服、备份，将原 data 和凭据移入绑定目录 private 下并保持 1000:1000 所有权，验证后再切换。本地回归验证将分别记录，不将重建等同于跨版本升级。

[隐私政策](PRIVACY.md) · [第三方许可](licenses/) · [反馈](https://github.com/metal643958961-a11y/victoriametrics-tos/issues)

公开源码、隐私政策和许可随此固定版本提供。上游镜像全部来自 Docker Hub，以摘要固定。





## 构建与本地回归

`python3 build.py` 在本应用目录确定性重建四文件安装包及SHA256。依赖系统Python3、Ruby YAML，不安装额外包。
隔离Linux回归命令与适用范围见[TESTING.md](TESTING.md)。

## 卸载和迁移

Compose使用 `/data:/tmp`（初始化服务）及 `/data:/state`（主服务）。这不是固定Volume1路径：TOS按官方规范将源路径映射到所选卷的DockerAppData/victoriametrics/data，并在拉取阶段设置配置user的所有权。不要在普通Linux宿主直接运行本Compose并假设TOS会替你创建目录；本地验收脚本将这两步明确模拟在隔离临时目录。

默认卸载保留业务数据；选择删除数据时，按平台规范清理该应用映射目录。本地模拟分别验证保留/删除和不触碰其他应用；实际TOS行为仍待验收。

首次密码在上述data/private/password，数据在data/private/data；非root初始化将私有目录设为700、凭据600。管理员通过TOS应用数据目录或Container Manager查看，勿公开凭据。

旧版真实目录布局须备份后确认。停服，把原数据复制到新映射目录的private/data，把原config/http-password复制到private/password，保持1000:1000和700/600权限；再启动核对。原版到候选的合成数据迁移通过，不声称平台自动迁移。TOS Docker按现行文档采用卸载保留数据后重装，不支持原地更新。
