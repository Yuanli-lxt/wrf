# WRF 50x50 长窗口验证实施计划

**目标：** 在不破坏现有 24h、72h 和 domain-size sweep 结果的前提下，新增 `50x50` 的 7 天验证通道，并为后续半月分段验证打基础。

**原则：**

- 先做 7 天，不直接跳到半月。
- 所有输出目录使用 `168h` 标识，避免覆盖已有 `24h/72h` 结果。
- 自动测试只检查脚本、路径、namelist 和导出契约，不在 pytest 中运行 WRF。
- WRF 长运行作为独立验证步骤执行。

## 任务 1：测试契约

**文件：**

- 修改：`tests/test_data_preparation_scripts.py`
- 修改：`tests/test_deployment_files.py`
- 修改：`tests/test_export_script.py`

步骤：

- [x] 为 GFS 准备脚本增加测试，要求支持可配置最大 forecast hour，例如 `MaxForecastHour = 168`。
- [x] 为 Ubuntu GFS 准备脚本增加测试，要求支持 `MAX_FORECAST_HOUR=168`。
- [x] 为 168h WPS runner 增加测试，要求读取 57 个 GFS 文件，输出到 `data/wps/domain_50_168h_validation_20241001_00`。
- [x] 为 168h WRF namelist 增加测试，要求窗口为 `2024-10-01_00:00:00` 到 `2024-10-08_00:00:00`。
- [x] 为 168h WRF runner 增加测试，要求读取 57 个 `met_em` 文件，最终检查 `wrfout_d01_2024-10-08_00-00-00`。
- [x] 为 168h APSIM 导出脚本增加测试，要求输出 `domain_50_168h_validation_wrf_20241001.met`。

## 任务 2：扩展 GFS 边界数据准备

**文件：**

- 修改：`scripts/prepare_gfs_boundary.ps1`
- 新增：`scripts/prepare_gfs_boundary.sh`

步骤：

- [x] PowerShell 脚本增加参数 `MaxForecastHour`，默认保持 `72`，避免改变现有行为。
- [x] 让 `$ForecastHours` 从 `0..$MaxForecastHour` 中每 3 小时取一个。
- [x] 新增 Ubuntu Bash 版本，支持 `MAX_FORECAST_HOUR=168`。
- [x] 保持远端 `HEAD` 校验和本地文件大小校验。
- [x] 7 天验证时使用 `-MaxForecastHour 168` 或 `MAX_FORECAST_HOUR=168`，应得到 57 个 GFS 文件。

## 任务 3：新增 168h WPS runner

**文件：**

- 新增：`scripts/run_wps_domain_50_168h.sh`

步骤：

- [x] 基于 `scripts/run_wps_domain_size.sh` 创建 50x50 专用 168h WPS runner。
- [x] 固定 `DOMAIN_SIZE=50`。
- [x] 生成 `namelist.wps` 时设置：
  - `e_we = 50`
  - `e_sn = 50`
  - `end_date = '2024-10-08_00:00:00'`
- [x] 要求 GFS 文件数量为 57。
- [x] 输出到 `data/wps/domain_50_168h_validation_20241001_00`。
- [x] 检查最终 `met_em.d01.2024-10-08_00-00-00.nc`。

## 任务 4：新增 168h WRF namelist 和 runner

**文件：**

- 新增：`wrf/namelists/namelist.input.168h.template`
- 新增：`scripts/run_wrf_domain_50_168h.sh`

步骤：

- [x] 基于 `namelist.input.72h.template` 创建 168h namelist。
- [x] 设置：
  - `run_days = 7`
  - `run_hours = 0`
  - `end_day = 08`
  - `end_hour = 00`
  - `e_we = 50`
  - `e_sn = 50`
- [x] runner 读取 `data/wps/domain_50_168h_validation_20241001_00`。
- [x] runner 要求 57 个 `met_em` 文件。
- [x] runner 输出到 `data/wrfout/domain_50_168h_validation_20241001_00`。
- [x] runner 检查最终 `wrfout_d01_2024-10-08_00-00-00`。

## 任务 5：新增 168h APSIM 导出

**文件：**

- 新增：`scripts/export_domain_50_168h_met.py`

步骤：

- [x] 读取 `data/wrfout/domain_50_168h_validation_20241001_00`。
- [x] 使用独立 staging 目录 `data/generated/wrfout_domain_50_168h_ascii`。
- [x] 输出 `data/generated/apsim/domain_50_168h_validation_wrf_20241001.met`。
- [x] 复用 `aggregate_wrf_dataset` 和 `write_met_file`。
- [x] 导出后检查 `.met` 记录数为 7，日期为 `2024-10-01` 到 `2024-10-07`。

## 任务 6：自动验证

步骤：

- [x] 运行定向 pytest。
- [x] 运行完整 pytest。
- [x] 运行 shell 语法检查：
  - `bash -n scripts/run_wps_domain_50_168h.sh`
  - `bash -n scripts/run_wrf_domain_50_168h.sh`
- [x] 运行 Python 编译检查：
  - `uv run python -m py_compile scripts/export_domain_50_168h_met.py`
- [x] 运行 Docker Compose 配置检查：
  - `docker compose -f docker/docker-compose.yml config --quiet`
- [x] 运行 `git diff --check`。

## 任务 7：重型 7 天验证

步骤：

- [x] 准备 GFS 边界：
  - `.\scripts\prepare_gfs_boundary.ps1 -MaxForecastHour 168`
- [x] 确认 GFS 文件数量为 57。
- [x] 运行 WPS：
  - `docker compose -f docker/docker-compose.yml run --rm wrf bash /work/scripts/run_wps_domain_50_168h.sh`
- [x] 运行 WRF：
  - `NPROC=4 docker compose -f docker/docker-compose.yml run --rm wrf bash /work/scripts/run_wrf_domain_50_168h.sh`
- [x] 记录 WPS 和 WRF 耗时。
- [x] 导出 APSIM `.met`：
  - `uv run python scripts/export_domain_50_168h_met.py`
- [x] 解析 `.met`，确认 7 条记录。
- [x] 检查 WRF 日志 `SUCCESS COMPLETE WRF`。

## 任务 8：review

步骤：

- [x] 检查 7 天通道是否没有覆盖已有 24h、72h、domain-size sweep 结果。
- [x] 检查测试是否没有下载数据、没有运行 WRF。
- [x] 检查脚本失败时是否能清楚指出缺失 GFS/WPS 输入。
- [x] 检查 7 天结果是否支持继续推进半月分段验证。

## 半月扩展计划

7 天通过后，再新建单独 spec/plan 处理半月。半月不建议直接作为单个 15 天 WRF 任务处理，优先方案是分段：

- 方案 A：5 个 3 天窗口。
- 方案 B：2 个 7 天窗口加 1 个 1 天窗口。

半月计划需要额外设计：

- 分段边界数据准备。
- 分段 WPS/WRF 输出目录命名。
- APSIM `.met` 拼接和日期去重。
- 失败重跑策略。
- 是否启用 WRF restart。
