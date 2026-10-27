#读取文件
def read_data(filename):
    positions = []
    intensities = []
    try:
        with open(filename,"r",encoding="utf-8-sig") as f:
            #encoding="utf-8-sig"：除了读取普通 UTF-8 文件，也能处理部分带有 UTF-8 BOM 文件头的 CSV。
            header = f.readline()
            if not header:
                raise ValueError("CSV 文件为空，缺少表头")
                #raise ValueError(...)：主动抛出错误，停止处理有问题的数据，而不是打印提示后继续进行可能不可靠的计算。
            header_columns = [
                column.strip() for column in header.split(",")
            ]
            # 检查表头是否合法
            if header_columns != ["position_mm","intensity"]:
                raise ValueError("CSV 表头格式错误，正确格式应为：position_mm,intensity")

            for line_number,line in enumerate(f,start=2):
            #enumerate() 可以让我们在遍历数据时，同时获得当前数据和它对应的编号。start=2 从第二行开始
                if not line.strip():
                    continue
                # 跳过空白行
                data = line.strip().split(",")

                if len(data) != 2:
                    raise ValueError(f"第{line_number}行必须包含位置和光强两列")
                try:
                    position = float(data[0])
                    intensity = float(data[1])
                except ValueError:
                    raise ValueError(f"第{line_number}行存在非数字数据")
                positions.append(position)
                intensities.append(intensity)
    except FileNotFoundError:
        raise FileNotFoundError(f"找不到文件：{filename}")
    if len(positions) == 0 or len(intensities) == 0:
        raise ValueError("没有读取到有效的实验数据")
    #它检查的是：整个文件处理完后，是否成功获得了有效的位置数据。
    return positions, intensities
# # positions,intensities = read_data("./optical_data.csv")
# print("位置数据：",positions)
# print("光强数据：",intensities)

#文件读取检查顺序
#文件能否打开？
#表头和数据结构是否正确？
#字段能否转换为正确的数据类型？
#数据是否缺失、异常或不合理？
#返回有效数据，交给后续程序分析

#处理数据

import  math
def analyze_data(positions,intensities):
    left_positions = []
    left_intensities = []
    right_positions = []
    right_intensities = []
    ## 记录是否已经找到左右交点
    left_found = False
    right_found = False
    #检测长度是否一致
    if len(positions) != len(intensities):
        raise ValueError("位置数据与光强数据的数量不一致")

    #检测数据点够不够
    if len(positions) < 3:
        raise ValueError("至少需要3个采样点才能分析FWHM")

    #检查位置数据是否严格递增
    for i in range(len(positions) - 1):
        if positions[i] >= positions[i + 1]:
            raise ValueError(
                f"位置数据顺序错误：第 {i + 1} 个位置必须小于第 {i + 2} 个位置"
            )

    #检查数据是否为有效值
    for i in range(len(positions)):
        if not math.isfinite(positions[i]):
            raise ValueError(f"第{1+i}个位置数据无效")
        if not math.isfinite(intensities[i]):
            raise ValueError(f"第{i+1}个光强数据无效")
    #math.isfinite()判断一个数值是否为有限数。

    #计算最大光强数据
    max_intensity = max(intensities)
    max_index = intensities.index(max_intensity)
    max_position = positions[max_index]

    #检测是否存在最大光强
    if max_intensity <= 0 :
        raise ValueError("最大光强必须大于0，无法计算FWHM")

    #计算平均光强
    average_intensity = sum(intensities)/len(positions)

    #计算半峰值
    half_max_intensity = max_intensity/2

    # 左侧：低于半峰值 -> 半峰值及以上
    for i in range(max_index -1,-1,-1):
        current_intensity = intensities[i]
        next_intensity = intensities[i+1]

        current_position = positions[i]
        next_position = positions [i+1]
        if (current_intensity < half_max_intensity <= next_intensity and not left_found) :
            #左侧交点
            left_intensities.extend([current_intensity,next_intensity])
            left_positions.extend([current_position,next_position])
            left_found = True
            break
    # 右侧：半峰值及以上 -> 低于半峰值
    for i in range(max_index,len(intensities)-1):
        current_intensity = intensities[i]
        next_intensity = intensities[i + 1]

        current_position = positions[i]
        next_position = positions[i + 1]
        if (current_intensity >= half_max_intensity > next_intensity and not right_found) :
            right_positions.extend([current_position,next_position])
            right_intensities.extend([current_intensity,next_intensity])
            right_found = True
            break
    if not left_found:
        raise ValueError("没有找到左侧半峰值交点")
    if not right_found:
        raise ValueError("没有找到右侧半峰值交点")

    #线性插值
    def linear_interpolation(x1,y1,x2,y2,target_y):
        if y2 == y1:
            raise ValueError("无法进行线性插值：两个光强相同")
        x = x1 + (target_y - y1) / (y2 - y1) * (x2 - x1)
        return x
    x_left = linear_interpolation(
        left_positions[0],
        left_intensities[0],
        left_positions[1],
        left_intensities[1],
        half_max_intensity)
    x_right = linear_interpolation(
        right_positions[0],
        right_intensities[0],
        right_positions[1],
        right_intensities[1],
        half_max_intensity)

    #计算FWHM
    fwhm = x_right - x_left
    return{
        "max_intensity":max_intensity,
        "max_position":max_position,
        "average_intensity":average_intensity,
        "half_max_intensity":half_max_intensity,
        "left_intensities":left_intensities,
        "left_positions":left_positions,
        "right_intensities":right_intensities,
        "right_positions":right_positions,
        "x_left":x_left,
        "x_right":x_right,
        "fwhm":fwhm,
        "左边fwhm点坐标":(x_left,half_max_intensity),
        "右边fwhm点坐标":(x_right,half_max_intensity)
    }
#result = analyze_data(positions,intensities)


#测试恰好等于半峰值的情况
test_positions = [0, 1, 2, 3, 4, 5, 6]
test_intensities = [20, 50, 80, 100, 80, 50, 20]

try:
    test_result = analyze_data(test_positions, test_intensities)

    # print("\n测试2：半峰值恰好命中采样点")
    # print("左侧交点：", result["x_left"])
    # print("右侧交点：", result["x_right"])
    # print("FWHM：", result["fwhm"])

except ValueError as e:
    print("测试2失败：", e)

#测试找不到交点的情况
test_positions = [0, 1, 2, 3]
test_intensities = [60, 70, 80, 100]

try:
    test_result = analyze_data(test_positions, test_intensities)
    print("测试3失败：本应报告缺少左侧交点")

except ValueError as e:
    print("测试3通过：", e)

#再测试位置和光强数量不一致
test_positions = [0, 1, 2, 3]
test_intensities = [20, 50, 100]

try:
    test_result = analyze_data(test_positions, test_intensities)
    print("测试4失败：本应报告数据数量不一致")

except ValueError as e:
    print("测试4通过：", e)


# 测试5：位置数据顺序错误
test_positions = [0, 1, 1, 2, 4]
test_intensities = [10, 30, 80, 60, 20]

try:
    test_result = analyze_data(test_positions, test_intensities)
    print("测试5失败：本应报告位置顺序错误")

except ValueError as e:
    print("测试5通过：", e)

#测试数据是否有效
test_positions = [0, 1, 2, 3, 4]
test_intensities = [20, 50, float("nan"), 100, 30]

try:
    test_result = analyze_data(test_positions, test_intensities)
    print("测试失败：没有识别无效光强")

except ValueError as e:
    print("测试通过：", e)

#测试采样点数据不足

test_positions = [0, 1]
test_intensities = [20, 100]

try:
    test_result = analyze_data(test_positions, test_intensities)
    print("测试失败：未识别采样点不足")
except ValueError as e:
    print("测试通过：", e)

#测试最大光强为0

test_positions = [0, 1, 2, 3, 4]
test_intensities = [0, 0, 0, 0, 0]

try:
    test_result = analyze_data(test_positions, test_intensities)
    print("测试失败：未识别无效峰值")
except ValueError as e:
    print("测试通过：", e)

#检查数据是否有效：防止错误数据进入计算。
#完成光学参数计算：最大光强、峰值位置、平均光强、半峰值、FWHM。
#保证结果可靠：正确处理特殊情况，并将结果返回给后续绘图和保存函数。
    #检测顺序：
    # 1. 检查空数据
    # 2. 检查两个列表长度是否一致
    # 3. 检查数据点是否至少为3个
    # 4. 检查数据是否为有效数值
    # 5. 检查位置是否严格递增
    # 6. 计算最大光强
    # 7. 检查最大光强是否大于0

#画图

import matplotlib.pyplot as plt

def plot_data(positions,intensities,result):
    plt.plot(positions,intensities,marker = "o")
    plt.title("Optical Intensity Distribution")  # 表头
    plt.grid(True)  # plt.grid()	显示网格线，方便读取数值
    plt.xlabel("Position (mm)")  # 横坐标
    plt.ylabel("Intensity (a.u.)")  # 纵坐标
    max_intensity = result["max_intensity"]
    max_position = result["max_position"]
    half_max_intensity  = result["half_max_intensity"]
    x_left = result["x_left"]
    x_right = result["x_right"]
    fwhm = result["fwhm"]

    plt.scatter(max_position,max_intensity,color = "red" ,s=100)
    plt.annotate(
        f"Max Intensity:{max_intensity}\nMax Position:{max_position}",
        (max_position,max_intensity),
        xytext = (10,-10),
        textcoords="offset points",
        arrowprops=dict(arrowstyle="->")
    )

    plt.axhline(
        y=half_max_intensity,
        color = "green",
        linestyle="--",
        label="Half Maximum"
    )

    plt.scatter(
        [x_left,x_right],
        [half_max_intensity,half_max_intensity],
        color = "red",
        s=80
    )

    plt.hlines(
        y=half_max_intensity-8,
        xmin=x_left,
        xmax=x_right,
        color="purple"
    )
    plt.vlines(
        [x_left,x_right],
        ymin=half_max_intensity-8,
        ymax=half_max_intensity,
        color="purple",
        linestyle = "--"
    )
    plt.text(
        (x_left + x_right) / 2,
        half_max_intensity - 10,
        f"FWHM = {fwhm:.2f} mm",
        ha="center",
        va="top",
        bbox=dict(
            boxstyle = "round,pad=0.4",
            facecolor = "white",
            edgecolor = "purple"
        )
    )
    plt.legend()
    #plt.legend()：显示图例
    plt.tight_layout()
    #plt.tight_layout()：自动调整布局
    fig = plt.gcf()
    return fig
    #返回图形对象，方便后续保存

#fig = plot_data(positions,intensities,result)

import csv

def save_result(result,filename):
    rows = [
        ["max_intensity", result["max_intensity"], "a.u."],
        ["max_position", result["max_position"], "mm"],
        ["average_intensity", result["average_intensity"], "a.u."],
        ["half_max_intensity", result["half_max_intensity"], "a.u."],
        ["left_half_position", result["x_left"], "mm"],
        ["right_half_position", result["x_right"], "mm"],
        ["fwhm", result["fwhm"], "mm"]
    ]
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        #newline=""	配合 csv 模块正确处理换行，可以让 Python 的 csv 模块自行处理 CSV 所需的换行方式，避免这种问题。
        writer = csv.writer(f)
        #这行代码创建一个 CSV 写入器，并让它负责向文件对象 f 写入数据。
        writer.writerow(["parameter", "value", "unit"])
        #写入表头
        writer.writerows(rows)

    print(f"分析结果已保存：{filename}")
#save_result(result, "./analysis_result.csv")

def save_plot(fig, filename):
    fig.savefig(filename, dpi=300, bbox_inches="tight")
    #bbox_inches="tight"：尽量裁掉图像周围多余的空白，避免部分内容被边界裁切
    print(f"光强分布图已保存：{filename}")
#save_plot(fig, "./intensity_distribution.png")

plt.show()

import tkinter as tk
from tkinter import filedialog

#创建窗口
root = tk.Tk()
#它创建了软件的主窗口。你可以把 root 理解为整个软件界面的容器，后续的按钮、文字和输入框都可以放进这个窗口。
root.title("光学实验数据分析软件")
root.geometry("600x300")
#geometry()：设置窗口初始宽度和高度，单位是像素。

#创建一个变量，用来保存文件路径
file_path = tk.StringVar()#tk.StringVar()：保存界面中的字符串
#file_path.set(filename)	把文件路径存进去
#file_path.get()	把文件路径取出来

#创建提示文字
#tk.Label()：显示文字
label = tk.Label(
    root,
    text="请选择需要分析的 CSV 实验数据",
    font=("Microsoft YaHei", 12)
)
#root：标签放在哪个窗口中。
#text：要显示的文字。
#font：字体设置。
label.pack(pady=20)
#pack() 表示把这个控件放进窗口布局中。pady=20 表示在控件周围增加垂直方向的外部间距。
# pack()：将控件放进布局。
# pady：控制垂直方向的间距。
# padx：控制水平方向的间距。

#显示当前选择的文件路径
path_label = tk.Label(
    root,
    textvariable=file_path,
    #textvariable 让标签与变量建立联系，因此不需要每次选择文件后都重新创建一个标签。textvariable	显示某个变量当前的值	file_path
    wraplength=550
    #表示文字超过大约 550 个像素的宽度时，可以自动换行，避免文件路径过长而挤出窗口。
)
path_label.pack(pady=10)

#定义选择文件的函数
def choose_file():
    filename = filedialog.askopenfilename(
        #filedialog.askopenfilename()：这个函数会打开系统的文件选择对话框。
        title="选择实验数据 CSV 文件",
        filetypes=[
            ("CSV 文件","*.csv"),
            ("所有文件","*.*")
            #filetypes：限制或筛选显示的文件类型。
        ]
    )
    # 如果用户确实选择了文件
    if filename:
        file_path.set(filename)

# 创建选择文件按钮
select_button = tk.Button(#Button 是按钮控件。
    root,
    text="选择 CSV 文件",
    command=choose_file,#command	点击按钮时执行什么函数
    font=("Microsoft YaHei", 11)
)
select_button.pack(pady=20)


from tkinter import messagebox
import os

def analyze_file():
    # 获取用户选择的文件路径
    filename = file_path.get()

    # 检查用户是否选择了文件
    if not filename:
        messagebox.showwarning(
            "提示",
            "请先选择一个 CSV 文件！"
        )
        return#这行代码会立即结束当前的 analyze_file() 函数。

    try:
        # 1. 读取数据
        positions, intensities = read_data(filename)

        # 2. 分析数据
        result = analyze_data(positions, intensities)

        # 3. 绘制图像
        fig = plot_data(positions, intensities, result)

        # 4. 获取输入文件所在目录
        output_folder = os.path.dirname(filename)#这意味着，你的程序不必把输出文件固定保存在 PyCharm 项目目录，而是可以将结果保存到用户所选 CSV 文件所在的文件夹。

        # 5. 保存分析结果和图片
        result_path = os.path.join(#os.path.join() 用于把文件夹路径与文件名组合成完整路径。
            output_folder, "analysis_result.csv"
        )
        image_path = os.path.join(
            output_folder, "intensity_distribution.png"
        )

        save_result(result, result_path)
        save_plot(fig, image_path)

        # 先显示图片，但不阻塞后续代码
        plt.show(block=False)#会尝试非阻塞地显示图像，让程序继续执行后面的代码。

        # 稍微等待一下，让图片窗口完成显示
        plt.pause(0.1)

        # 再弹出分析结果窗口
        messagebox.showinfo(
            "分析完成",
            f"最大光强：{result['max_intensity']:.2f} a.u.\n"
            f"峰值位置：{result['max_position']:.2f} mm\n"
            f"平均光强：{result['average_intensity']:.2f} a.u.\n"
            f"半峰值：{result['half_max_intensity']:.2f} a.u.\n"
            f"FWHM：{result['fwhm']:.2f} mm\n\n"
            f"结果保存位置：\n{output_folder}"
        )


    except (ValueError, FileNotFoundError) as e:
        messagebox.showerror("分析失败", str(e))

analyze_button = tk.Button(
    root,
    text="开始分析",
    command=analyze_file,
    font=("Microsoft YaHei", 11)
)
analyze_button.pack(pady=10)

# 启动窗口
root.mainloop()
# 告诉程序，窗口已经准备好了，现在开始等待用户操作。
