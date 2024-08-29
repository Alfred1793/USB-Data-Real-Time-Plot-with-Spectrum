import os
import time
import numpy as np
import csv
from threading import Thread, Event
from collections import deque
from config import SAMPLE_RATE

class WaveformSaver:
    """
    用于保存波形数据的类。
    
    这个类可以从USB读取器获取数据，并将其保存到CSV文件中。
    它支持异步保存和可配置的记录时间。
    """

    def __init__(self, usb_reader):
        """
        初始化WaveformSaver实例。

        :param usb_reader: 一个能够获取波形数据的对象，需实现get_data()方法。
        """
        self.usb_reader = usb_reader
        self.save_thread = None  # 保存数据的线程
        self.stop_event = Event()  # 用于停止保存线程的事件
        # 使用双端队列存储数据，最多存储1小时的数据
        self.data_buffer = deque(maxlen=int(SAMPLE_RATE) * 3600)

    def start_saving(self, path, filename, record_time):
        """
        开始异步保存波形数据。

        :param path: 保存文件的路径
        :param filename: 保存的文件名
        :param record_time: 录制时间（秒）
        :return: 如果成功启动保存任务，返回True；否则返回False。
        """
        if self.save_thread and self.save_thread.is_alive():
            print("已有保存任务正在进行")
            return False

        self.stop_event.clear()
        self.save_thread = Thread(target=self._save_process, args=(path, filename, record_time))
        self.save_thread.start()
        return True

    def stop_saving(self):
        """
        停止正在进行的数据保存任务。
        """
        if self.save_thread and self.save_thread.is_alive():
            self.stop_event.set()
            self.save_thread.join()
            print("保存已停止")
        else:
            print("没有正在进行的保存任务")

    def _save_process(self, path, filename, record_time):
        """
        保存数据的后台线程，按指定时间段进行数据采集并保存至文件。

        :param path: 保存文件的路径
        :param filename: 保存的文件名
        :param record_time: 录制时间（秒）
        """
        start_time = time.time()
        full_path = os.path.join(path, filename)

        while time.time() - start_time < record_time and not self.stop_event.is_set():
            new_data = self.usb_reader.get_data()
            self.data_buffer.extend(new_data)
            time.sleep(0.1)  # 短暂休眠以减少CPU使用

        data_to_save = list(self.data_buffer)
        actual_duration = time.time() - start_time
        self._save_to_csv(full_path, data_to_save, actual_duration)
        print(f"波形已保存至 {full_path}")

        self.data_buffer.clear()

    def _save_to_csv(self, full_path, data, actual_duration):
        """
        将数据保存到CSV文件，每行包含时间戳和对应的信号值。

        :param full_path: 保存文件的完整路径
        :param data: 要保存的信号数据列表
        :param actual_duration: 实际的数据采集持续时间（秒）
        """
        with open(full_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Time (s)', 'Signal'])
            
            # 根据实际持续时间和数据点数量计算时间戳
            num_samples = len(data)
            time_stamps = np.linspace(0, actual_duration, num_samples)
            
            # 写入每个时间戳和对应的信号值
            for time_stamp, data_point in zip(time_stamps, data):
                csv_writer.writerow([f"{time_stamp:.6f}", data_point])

    def is_saving(self):
        """
        检查是否有保存任务正在进行。

        :return: 如果保存任务正在进行，返回True；否则返回False。
        """
        return self.save_thread and self.save_thread.is_alive()

# 测试代码
if __name__ == "__main__":
    class MockUSBReader:
        def get_data(self):
            """模拟从USB读取数据，返回100个随机数据点。"""
            return np.random.rand(100).tolist()

    usb_reader = MockUSBReader()
    saver = WaveformSaver(usb_reader)

    # 开始保存波形数据
    saver.start_saving(".", "waveform.csv", 10)

    # 等待5秒后停止保存
    time.sleep(5)
    saver.stop_saving()