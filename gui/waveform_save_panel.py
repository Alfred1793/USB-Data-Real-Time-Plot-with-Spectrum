from PySide6 import QtWidgets, QtCore, QtGui
import os

class WaveformSavePanel(QtWidgets.QWidget):
    """
    波形保存面板类，用于选择保存路径、输入文件名并设置记录时间，发出保存信号。

    该面板包括一个目录树视图用于选择保存路径，文件名输入框，以及一个记录时间选择器。
    当用户点击保存按钮时，会发出保存信号，包含路径、文件名和记录时间。

    信号:
        save_signal(str, str, int): 发出保存信号，参数分别为路径、文件名和记录时间长度（秒）。
    """

    save_signal = QtCore.Signal(str, str, int)  # 发送保存信号：路径、文件名、记录时间

    def __init__(self):
        """
        初始化 WaveformSavePanel 类。
        """
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """
        初始化用户界面，设置目录树、文件名输入框、记录时间选择器和保存按钮。
        """
        layout = QtWidgets.QVBoxLayout(self)

        # 目录树视图
        self.directory_tree = QtWidgets.QTreeView()
        self.directory_model = QtWidgets.QFileSystemModel()
        self.directory_model.setRootPath(QtCore.QDir.rootPath())

        # 获取当前脚本所在的路径，并设置为目录树的根路径
        script_path = os.path.abspath(__file__)
        drive = os.path.splitdrive(script_path)[0] + os.path.sep
        # 固定的后半段内容
        fixed_suffix = r"gui\waveform_save_panel.py"
        # 找到固定后半段的起始位置
        suffix_index = script_path.find(fixed_suffix)
        # 截取目标子字符串
        if suffix_index != -1:
            extracted_path = script_path[:suffix_index]
        else:
            extracted_path = drive
        self.directory_tree.setModel(self.directory_model)
        self.directory_tree.setRootIndex(self.directory_model.index(extracted_path))

        self.directory_tree.setAnimated(False)
        self.directory_tree.setIndentation(20)
        self.directory_tree.setSortingEnabled(True)
        self.directory_tree.setColumnWidth(0, 250)
        self.directory_tree.setHeaderHidden(True)
        self.directory_tree.hideColumn(1)
        self.directory_tree.hideColumn(2)
        self.directory_tree.hideColumn(3)
        layout.addWidget(self.directory_tree)

        # 文件名输入框
        self.filename_input = QtWidgets.QLineEdit()
        self.filename_input.setPlaceholderText("输入文件名")
        layout.addWidget(self.filename_input)

        # 记录时间长度选择
        time_layout = QtWidgets.QHBoxLayout()
        time_layout.addWidget(QtWidgets.QLabel("记录时间 (秒):"))
        self.time_spinbox = QtWidgets.QSpinBox()
        self.time_spinbox.setRange(1, 3600)  # 1秒到1小时
        self.time_spinbox.setValue(60)  # 默认60秒
        time_layout.addWidget(self.time_spinbox)
        layout.addLayout(time_layout)

        # 保存按钮
        self.save_button = QtWidgets.QPushButton("保存波形")
        self.save_button.clicked.connect(self.save_waveform)
        layout.addWidget(self.save_button)

        # 设置大小策略
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)

    def save_waveform(self):
        """
        处理保存波形的逻辑，获取路径、文件名和记录时间，并发出保存信号。

        如果未选择路径，则默认保存到用户的主目录。
        如果文件名为空，则弹出警告提示用户输入文件名。
        """
        selected_indexes = self.directory_tree.selectedIndexes()
        if selected_indexes:
            path = self.directory_model.filePath(selected_indexes[0])
        else:
            path = QtCore.QDir.homePath()

        filename = self.filename_input.text()
        if not filename:
            QtWidgets.QMessageBox.warning(self, "警告", "请输入文件名")
            return

        record_time = self.time_spinbox.value()

        # 发送保存信号
        self.save_signal.emit(path, filename, record_time)

    def get_selected_path(self):
        """
        获取用户在目录树中选择的路径。

        :return: 选择的路径，如果未选择则返回用户的主目录路径。
        """
        selected_indexes = self.directory_tree.selectedIndexes()
        if selected_indexes:
            return self.directory_model.filePath(selected_indexes[0])
        return QtCore.QDir.homePath()

# 测试代码
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    panel = WaveformSavePanel()
    panel.show()
    app.exec()
