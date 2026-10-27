# Optical Data Analyzer

一个基于 Python 的光学实验数据分析桌面软件，用于读取 CSV 实验数据、计算光学参数、绘制光强分布图，并导出分析结果。

## 项目功能

- 读取 CSV 格式的实验数据
- 计算最大光强、峰值位置和平均光强
- 搜索主峰左右两侧的半峰值交点
- 使用线性插值计算半峰值交点位置
- 计算半峰全宽（FWHM）
- 绘制光强分布图并标注关键参数
- 导出分析结果 CSV 文件和 PNG 图片
- 提供 Windows 桌面图形界面

## 技术栈

- Python
- Tkinter
- Matplotlib
- CSV 数据处理
- PyInstaller

## 运行环境

- Windows
- Python 3

## 安装依赖

在项目目录的终端中执行：

```bash
python -m pip install -r requirements.txt
```

## 运行软件

执行以下命令：

```bash
python "光学实验数据自动分析优化.py"
```

启动后，选择需要分析的 CSV 文件，再点击“开始分析”。

## 输入数据格式

CSV 文件应包含位置和光强两列，表头格式需要与程序中的数据读取函数保持一致。

## 输出文件

- `analysis_result.csv`：保存分析参数
- `intensity_distribution.png`：保存光强分布图

默认保存到输入 CSV 文件所在的文件夹。

## 项目状态

当前版本已实现基础的数据读取、光学参数计算、图像绘制、结果保存和 Windows 桌面界面。

后续计划包括界面优化、异常处理完善、测试覆盖和 AI Agent 功能探索。

## License

暂未选择开源许可证。
