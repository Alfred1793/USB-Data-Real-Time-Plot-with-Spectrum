from PySide6 import QtWidgets

class ConnectionInfoWidget(QtWidgets.QWidget):
    """
    设备连接信息显示部件，用于显示和更新 USB 设备的连接信息。

    :param device_info: 包含设备信息的字典。
    """

    def __init__(self, device_info):
        """
        初始化 ConnectionInfoWidget 类。

        :param device_info: 包含设备信息的字典。
        """
        super().__init__()
        self.device_info = device_info  # 存储设备信息
        self.init_ui()  # 初始化用户界面

    def init_ui(self):
        """
        初始化用户界面，显示设备连接信息。
        """
        layout = QtWidgets.QVBoxLayout(self)  # 创建垂直布局

        layout.addWidget(QtWidgets.QLabel("<b>Connection Information:</b>"))  # 添加标题标签

        # 遍历设备信息字典，创建并添加对应的标签
        for key, value in self.device_info.items():
            label = QtWidgets.QLabel(f"{key.replace('_', ' ').title()}: {value}")
            layout.addWidget(label)

        layout.addStretch()  # 添加弹性空间，将信息顶置

    def update_info(self, new_info):
        """
        更新设备信息并刷新显示。

        :param new_info: 包含新设备信息的字典。
        """
        self.device_info.update(new_info)  # 更新设备信息
        self.clear_layout()  # 清空当前布局内容
        self.init_ui()  # 重新初始化用户界面，显示新的设备信息

    def clear_layout(self):
        """
        清空布局中的所有部件。
        """
        while self.layout().count():  # 遍历布局中的所有子项
            child = self.layout().takeAt(0)  # 移除子项
            if child.widget():
                child.widget().deleteLater()  # 删除子项部件
