from PySide6 import QtWidgets, QtCore, QtGui
import os
import sys

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
        self.directory_tree.setModel(self.directory_model)
        
        # 获取主函数所在的路径，并设置为目录树的根路径
        main_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.directory_tree.setRootIndex(self.directory_model.index(main_path))
        
        # 隐藏类型、大小和创建时间列
        self.directory_tree.setColumnHidden(1, True)  # 隐藏类型列
        self.directory_tree.setColumnHidden(2, True)  # 隐藏大小列
        self.directory_tree.setColumnHidden(3, True)  # 隐藏创建时间列
        self.directory_tree.setHeaderHidden(True)  # 隐藏表头
        layout.addWidget(self.directory_tree)

        # 文件名输入框
        self.filename_input = QtWidgets.QLineEdit()
        self.filename_input.setPlaceholderText("输入文件名")
        self.filename_input.setText("default_filename")  # 默认文件名
        self.filename_input.mousePressEvent = self.clear_default_filename
        layout.addWidget(self.filename_input)

        # 记录时间长度选择（使用 QSlider 和 QLineEdit）
        time_layout = QtWidgets.QHBoxLayout()
        time_layout.addWidget(QtWidgets.QLabel("记录时间 (秒):"))
        self.time_input = QtWidgets.QLineEdit()
        self.time_input.setText("60")  # 默认值为60秒
        self.time_input.setFixedWidth(70)
        # 设置验证器，只允许输入1-3600之间的整数
        validator = QtGui.QIntValidator(1, 3600)
        self.time_input.setValidator(validator)
        time_layout.addWidget(self.time_input)

        self.time_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.time_slider.setRange(1, 3600)
        self.time_slider.setValue(60)  # 默认值为60秒
        self.time_slider.setFixedWidth(100)
        self.time_slider.valueChanged.connect(self.update_time_input)
        time_layout.addWidget(self.time_slider)

        layout.addLayout(time_layout)

        # 批量保存选项
        batch_layout = QtWidgets.QHBoxLayout()
        batch_layout.addWidget(QtWidgets.QLabel("文件数量:        "))
        self.file_count_input = QtWidgets.QLineEdit()
        self.file_count_input.setText("1")  # 默认值为1
        self.file_count_input.setFixedWidth(70)
        # 设置验证器，只允许输入1-100之间的整数
        file_count_validator = QtGui.QIntValidator(1, 100)
        self.file_count_input.setValidator(file_count_validator)
        batch_layout.addWidget(self.file_count_input)

        self.file_count_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.file_count_slider.setRange(1, 100)
        self.file_count_slider.setValue(1)  # 默认值为1
        self.file_count_slider.setFixedWidth(100)
        self.file_count_slider.valueChanged.connect(self.update_file_count_input)
        batch_layout.addWidget(self.file_count_slider)

        batch_layout.addStretch()
        layout.addLayout(batch_layout)

        # 保存按钮
        self.save_button = QtWidgets.QPushButton("保存波形")
        self.save_button.clicked.connect(self.save_waveform)
        layout.addWidget(self.save_button)

    def clear_default_filename(self, event):
        """
        清空默认文件名，一旦用户编辑过，清空功能将关闭。
        """
        if self.filename_input.text() == "default_filename":
            self.filename_input.clear()
            self.filename_input.mousePressEvent = None

    def update_time_input(self):
        """
        更新时间输入框的值为滑块的值。
        """
        self.time_input.setText(str(self.time_slider.value()))

    def update_file_count_input(self):
        """
        更新文件数量输入框的值为滑块的值。
        """
        self.file_count_input.setText(str(self.file_count_slider.value()))

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
            path = os.path.dirname(os.path.abspath(sys.argv[0]))

        filename = self.filename_input.text()
        if not filename:
            QtWidgets.QMessageBox.warning(self, "警告", "请输入文件名")
            return

        try:
            record_time = int(self.time_input.text())
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "警告", "请输入有效的记录时间")
            return

        try:
            file_count = int(self.file_count_input.text())
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "警告", "请输入有效的文件数量")
            return

        for i in range(file_count):
            file_name = f"{filename}_{str(i+1).zfill(5)}.csv"
            self.save_signal.emit(path, file_name, record_time)
