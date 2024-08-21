from PySide6 import QtWidgets, QtCore
from .plot_canvas import PlotCanvas
from .connection_info_widget import ConnectionInfoWidget
from .waveform_save_panel import WaveformSavePanel
from config import X_AXIS_RANGE, Y_AXIS_RANGE
from waveform_saver import WaveformSaver

class AppWindow(QtWidgets.QMainWindow):
    """
    应用程序主窗口类，用于显示实时 USB 数据绘图及其频谱。

    :param reader: 一个数据读取器对象，必须实现 `get_data()` 和 `get_speed()` 方法。
    :param use_simulated_signal: 布尔值，指示是否使用模拟信号。
    :param show_connection_info: 布尔值，指示是否显示设备连接信息面板。
    """
    
    def __init__(self, reader, use_simulated_signal, show_connection_info):
        """
        初始化 AppWindow 类。

        :param reader: 一个数据读取器对象，必须实现 `get_data()` 和 `get_speed()` 方法。
        :param use_simulated_signal: 布尔值，指示是否使用模拟信号。
        :param show_connection_info: 布尔值，指示是否显示设备连接信息面板。
        """
        super().__init__()
        self.reader = reader  # 数据读取器对象
        self.use_simulated_signal = use_simulated_signal  # 是否使用模拟信号
        self.show_connection_info = show_connection_info  # 是否显示设备连接信息面板
        self.waveform_saver = WaveformSaver(self.reader)  # 波形保存器对象
        self.init_ui()  # 初始化用户界面

    def init_ui(self):
        """
        初始化用户界面，包括连接信息面板、控制面板、绘图画布等。
        """
        self.setWindowTitle("USB Data Real-Time Plot with Spectrum")
        self.setGeometry(100, 100, 1200, 900)
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QtWidgets.QHBoxLayout(self.central_widget)

        # 左侧信息面板
        if self.show_connection_info:
            self.connection_info_widget = ConnectionInfoWidget(self.reader.get_device_info())
            self.connection_info_widget.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
            self.main_layout.addWidget(self.connection_info_widget)

        # 右侧图表和控制面板
        self.right_widget = QtWidgets.QWidget()
        self.right_layout = QtWidgets.QVBoxLayout(self.right_widget)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(0)

        # 控制面板
        self.controls_widget = QtWidgets.QWidget()
        self.controls_widget.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.controls_layout = QtWidgets.QHBoxLayout(self.controls_widget)
        self.controls_layout.setContentsMargins(5, 5, 5, 5)
        self.controls_layout.setSpacing(5)

        # 添加控制项
        self.x_range_input = QtWidgets.QLineEdit(str(X_AXIS_RANGE))
        self.y_min_input = QtWidgets.QLineEdit(str(Y_AXIS_RANGE[0]))
        self.y_max_input = QtWidgets.QLineEdit(str(Y_AXIS_RANGE[1]))
        self.update_button = QtWidgets.QPushButton('Update Ranges')
        self.update_button.clicked.connect(self.update_ranges)

        self.controls_layout.addWidget(QtWidgets.QLabel('X Range:'))
        self.controls_layout.addWidget(self.x_range_input)
        self.controls_layout.addWidget(QtWidgets.QLabel('Y Min:'))
        self.controls_layout.addWidget(self.y_min_input)
        self.controls_layout.addWidget(QtWidgets.QLabel('Y Max:'))
        self.controls_layout.addWidget(self.y_max_input)
        self.controls_layout.addWidget(self.update_button)

        self.simulated_signal_checkbox = QtWidgets.QCheckBox('Use Simulated Signal')
        self.simulated_signal_checkbox.setChecked(self.use_simulated_signal)
        self.simulated_signal_checkbox.stateChanged.connect(self.toggle_simulated_signal)
        self.controls_layout.addWidget(self.simulated_signal_checkbox)

        self.right_layout.addWidget(self.controls_widget)

        # 绘图画布
        self.canvas = PlotCanvas(self)
        self.right_layout.addWidget(self.canvas, 1)  # 添加拉伸因子

        self.main_layout.addWidget(self.right_widget)

        # 启动定时器定期更新图表
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(50)

        # 保存面板
        self.save_panel = WaveformSavePanel()
        self.save_panel.save_signal.connect(self.save_waveform_data)
        self.save_panel.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.main_layout.addWidget(self.save_panel)

    def update_ranges(self):
        """
        更新绘图的 X 和 Y 轴范围，根据用户输入的值进行设置。
        """
        x_range = int(self.x_range_input.text())
        y_min = float(self.y_min_input.text())
        y_max = float(self.y_max_input.text())

        self.canvas.set_x_axis_range(x_range)
        self.canvas.set_y_axis_range(y_min, y_max)

    def toggle_simulated_signal(self, state):
        print(f"Simulated signal {'enabled' if state == QtCore.Qt.Checked else 'disabled'}")


    def update_plot(self):
        """
        定时更新绘图，获取新数据并刷新图表显示。
        """
        data = self.reader.get_data()
        speed = self.reader.get_speed()
        self.canvas.update_plot(data, speed)

    def save_waveform_data(self, path, filename, record_time):
        """
        保存波形数据到指定路径和文件名。

        :param path: 保存路径。
        :param filename: 保存的文件名。
        :param record_time: 记录时间长度，单位为秒。
        """
        if self.waveform_saver.is_saving():
            QtWidgets.QMessageBox.warning(self, "警告", "已有保存任务正在进行")
            return

        success = self.waveform_saver.start_saving(path, filename, record_time)
        if success:
            QtWidgets.QMessageBox.information(self, "信息", f"开始保存波形，时长：{record_time}秒")
        else:
            QtWidgets.QMessageBox.warning(self, "警告", "无法开始保存任务")

    def closeEvent(self, event):
        """
        处理窗口关闭事件，停止波形保存和数据读取。

        :param event: 窗口关闭事件。
        """
        self.waveform_saver.stop_saving()
        self.reader.stop()
        event.accept()
