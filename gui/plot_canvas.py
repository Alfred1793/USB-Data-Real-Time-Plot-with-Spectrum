import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from config import X_AXIS_RANGE, Y_AXIS_RANGE, SAMPLE_RATE

class PlotCanvas(FigureCanvas):
    """
    自定义绘图画布类，用于显示时域信号和频域频谱。

    :param parent: 父级窗口或控件，默认为 None。
    """

    def __init__(self, parent=None):
        """
        初始化 PlotCanvas 类。

        :param parent: 父级窗口或控件，默认为 None。
        """
        self.x_range = X_AXIS_RANGE  # X 轴范围（样本数）
        self.fig = Figure(figsize=(8, 10), dpi=100)  # 创建 Matplotlib 图形对象
        self.axes = self.fig.subplots(2, 1)  # 创建两个子图：时域和频域
        super(PlotCanvas, self).__init__(self.fig)
        self.setParent(parent)

        # 初始化时域和频域绘图
        self.init_time_domain_plot()
        self.init_frequency_domain_plot()

        # 调整布局以适应窗口
        self.fig.tight_layout()

    def init_time_domain_plot(self):
        """
        初始化时域信号的绘图。
        """
        self.axes[0].set_title('Time Domain Signal')  # 设置时域图的标题
        self.axes[0].set_xlim(0, self.x_range)  # 设置 X 轴范围
        self.axes[0].set_ylim(Y_AXIS_RANGE)  # 设置 Y 轴范围
        self.axes[0].set_xlabel('Sample')  # 设置 X 轴标签
        self.axes[0].set_ylabel('Amplitude')  # 设置 Y 轴标签
        self.xdata = np.linspace(0, self.x_range, self.x_range)  # 生成 X 轴数据
        self.time_line, = self.axes[0].plot(self.xdata, np.zeros(self.x_range), 'r-')  # 初始化时域图的曲线
        self.speed_text = self.axes[0].text(0.02, 0.95, '', transform=self.axes[0].transAxes)  # 显示接收速度的文本

    def init_frequency_domain_plot(self):
        """
        初始化频域频谱的绘图。
        """
        self.axes[1].set_title('Frequency Domain Spectrum')  # 设置频域图的标题
        self.freq_line, = self.axes[1].plot([], [])  # 初始化频域图的曲线
        self.axes[1].set_xlim(0, SAMPLE_RATE / 2)  # 设置 X 轴范围为采样率的一半
        self.axes[1].set_ylim(0, 100)  # 设置 Y 轴初始范围
        self.axes[1].set_xlabel('Frequency (Hz)')  # 设置 X 轴标签
        self.axes[1].set_ylabel('Magnitude')  # 设置 Y 轴标签
        self.max_freq_text = self.axes[1].text(0.02, 0.95, '', transform=self.axes[1].transAxes)  # 显示最大频率和幅度的文本

    def update_plot(self, data, speed):
        """
        更新时域和频域的绘图。

        :param data: 接收到的数据，用于更新时域和频域图。
        :param speed: 当前数据接收速度，用于显示在时域图上。
        """
        self.update_time_domain(data, speed)  # 更新时域图
        self.update_frequency_domain(data)  # 更新频域图
        self.draw()  # 重新绘制图表

    def update_time_domain(self, data, speed):
        """
        更新时域信号的绘图。

        :param data: 用于更新时域图的数据。
        :param speed: 当前数据接收速度。
        """
        ydata = np.zeros(self.x_range)  # 创建空的 Y 轴数据
        if len(data) >= self.x_range:
            ydata[:] = data[-self.x_range:]  # 如果数据足够多，取最后 x_range 个数据点
        else:
            ydata[-len(data):] = data  # 如果数据不足，填充到 Y 轴数据的末尾
        self.time_line.set_ydata(ydata)  # 更新时域曲线的 Y 数据
        self.speed_text.set_text(f'Receive speed: {speed:.2f} KB/s')  # 更新接收速度的显示文本

    def update_frequency_domain(self, data):
        """
        更新频域频谱的绘图。

        :param data: 用于计算频谱的时域数据。
        """
        if len(data) > 0:
            fft_result = np.fft.fft(data)  # 计算快速傅里叶变换（FFT）
            fft_freq = np.fft.fftfreq(len(data), 1 / SAMPLE_RATE)  # 计算频率分量
            fft_mag = np.abs(fft_result)  # 计算频率幅度

            positive_freq_idxs = fft_freq > 0  # 仅取正频率部分
            positive_fft_freq = fft_freq[positive_freq_idxs]
            positive_fft_mag = fft_mag[positive_freq_idxs]

            max_idx = np.argmax(positive_fft_mag)  # 找到最大频率分量的索引
            max_freq = positive_fft_freq[max_idx]  # 获取最大频率
            max_mag = positive_fft_mag[max_idx]  # 获取最大幅度

            self.max_freq_text.set_text(f'Max Frequency: {max_freq:.2f} Hz, Mag: {max_mag:.2f}')  # 显示最大频率和幅度

            self.freq_line.set_data(positive_fft_freq, positive_fft_mag)  # 更新频域图的曲线数据
            self.axes[1].set_ylim(0, max_mag * 1.1)  # 动态调整 Y 轴范围
            self.axes[1].relim()  # 重新计算范围
            self.axes[1].autoscale_view()  # 自动缩放视图

    def set_x_axis_range(self, x_range):
        """
        设置时域图的 X 轴范围。

        :param x_range: 新的 X 轴范围（样本数）。
        """
        self.x_range = x_range  # 更新 X 轴范围
        self.axes[0].set_xlim(0, x_range)  # 设置 X 轴范围
        self.xdata = np.linspace(0, x_range, x_range)  # 更新 X 轴数据
        self.time_line.set_xdata(self.xdata)  # 更新时域曲线的 X 数据
        self.time_line.set_ydata(np.zeros(x_range))  # 初始化 Y 数据为零

    def set_y_axis_range(self, y_min, y_max):
        """
        设置时域图的 Y 轴范围。

        :param y_min: Y 轴的最小值。
        :param y_max: Y 轴的最大值。
        """
        self.axes[0].set_ylim(y_min, y_max)  # 设置 Y 轴范围
