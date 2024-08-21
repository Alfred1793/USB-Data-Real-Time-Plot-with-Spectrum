import os
import time
import numpy as np
import csv
from threading import Thread, Event
from collections import deque

# 假设采样率为1000样本/秒
SAMPLE_RATE = 1000

class WaveformSaver:
    def __init__(self, usb_reader):
        """
        初始化WaveformSaver类。
        
        :param usb_reader: 一个能够获取波形数据的对象，需实现get_data()方法。
        """
        self.usb_reader = usb_reader  # 用于获取数据的USB读取器对象
        self.save_thread = None  # 保存数据的线程对象
        self.stop_event = Event()  # 用于停止保存线程的事件
        # 使用双端队列存储数据，最多存储1小时的数据（以SAMPLE_RATE计算）
        self.data_buffer = deque(maxlen=SAMPLE_RATE * 3600)

    def start_saving(self, path, filename, record_time):
        """
        开始异步保存波形数据。
        
        :param path: 保存文件的路径
        :param filename: 保存的文件名
        :param record_time: 录制时间（秒）
        :return: 如果已有保存任务在进行，返回False；否则返回True。
        """
        # 检查是否已有保存任务在进行
        if self.save_thread and self.save_thread.is_alive():
            print("已有保存任务正在进行")
            return False

        # 清除停止事件并启动保存线程
        self.stop_event.clear()
        self.save_thread = Thread(target=self._save_process, args=(path, filename, record_time))
        self.save_thread.start()
        return True

    def stop_saving(self):
        """
        停止正在进行的数据保存任务。
        """
        # 检查是否有正在进行的保存任务
        if self.save_thread and self.save_thread.is_alive():
            self.stop_event.set()  # 设置停止事件
            self.save_thread.join()  # 等待保存线程结束
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
        start_time = time.time()  # 记录开始时间
        full_path = os.path.join(path, filename)  # 组合完整文件路径

        # 在指定时间内循环采集数据
        while time.time() - start_time < record_time and not self.stop_event.is_set():
            new_data = self.usb_reader.get_data()  # 获取新数据
            self.data_buffer.extend(new_data)  # 将新数据添加到缓冲区
            time.sleep(0.1)  # 短暂休眠以减少CPU使用

        # 将采集的数据保存到CSV文件
        data_to_save = list(self.data_buffer)  # 将缓冲区数据转换为列表
        self._save_to_csv(full_path, data_to_save)  # 保存数据到文件
        print(f"波形已保存至 {full_path}")

        # 清空缓冲区
        self.data_buffer.clear()

    def _save_to_csv(self, full_path, data):
        """
        将数据保存到CSV文件，每行包含时间戳和对应的信号值。
        
        :param full_path: 保存文件的完整路径
        :param data: 要保存的信号数据列表
        """
        with open(full_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            # 写入表头，包括时间列和信号列
            csv_writer.writerow(['Time (s)', 'Signal'])
            
            # 根据采样率计算时间戳
            time_stamps = np.arange(len(data)) / SAMPLE_RATE
            
            # 写入每个时间戳和对应的信号值
            for time_stamp, data_point in zip(time_stamps, data):
                csv_writer.writerow([time_stamp, data_point])

    def is_saving(self):
        """
        检查是否有保存任务正在进行。
        
        :return: 如果保存任务正在进行，返回True；否则返回False。
        """
        return self.save_thread and self.save_thread.is_alive()


# 假设 usb_reader 是一个有 get_data() 方法的对象
class MockUSBReader:
    def get_data(self):
        """
        模拟从USB读取数据，返回100个随机数据点。
        
        :return: 包含100个随机浮点数的列表
        """
        return np.random.rand(100).tolist()  # 返回 100 个随机数据点

# 测试代码
if __name__ == "__main__":
    usb_reader = MockUSBReader()  # 创建模拟USB读取器对象
    saver = WaveformSaver(usb_reader)  # 创建WaveformSaver实例

    # 开始保存波形数据
    saver.start_saving(".", "waveform.csv", 10)

    # 等待一段时间后停止保存
    time.sleep(5)
    saver.stop_saving()
