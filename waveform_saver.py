import os
import time
import numpy as np
import csv
from threading import Thread, Event
from collections import deque
from config import SAMPLE_RATE

class WaveformSaver:
    def __init__(self, usb_reader):
        self.usb_reader = usb_reader
        self.save_thread = None
        self.stop_event = Event()
        self.data_buffer = deque(maxlen=int(SAMPLE_RATE) * 3600)

    def start_saving(self, path, filename, record_time):
        if self.save_thread and self.save_thread.is_alive():
            print("已有保存任务正在进行")
            return False

        self.stop_event.clear()
        self.save_thread = Thread(target=self._save_process, args=(path, filename, record_time))
        self.save_thread.start()
        return True

    def stop_saving(self):
        if self.save_thread and self.save_thread.is_alive():
            self.stop_event.set()
            self.save_thread.join()
            print("保存已停止")
        else:
            print("没有正在进行的保存任务")

    def _save_process(self, path, filename, record_time):
        start_time = time.time()
        full_path = os.path.join(path, filename)

        while time.time() - start_time < record_time and not self.stop_event.is_set():
            new_data = self.usb_reader.get_data()
            self.data_buffer.extend(new_data)
            time.sleep(0.1)

        data_to_save = list(self.data_buffer)
        actual_duration = time.time() - start_time
        self._save_to_csv(full_path, data_to_save, actual_duration)
        print(f"波形已保存至 {full_path}")

        self.data_buffer.clear()

    def _save_to_csv(self, full_path, data, actual_duration):
        with open(full_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Time (s)', 'Signal'])
            
            # Calculate time stamps based on actual duration and number of data points
            num_samples = len(data)
            time_stamps = np.linspace(0, actual_duration, num_samples)
            
            for time_stamp, data_point in zip(time_stamps, data):
                csv_writer.writerow([f"{time_stamp:.6f}", data_point])

    def is_saving(self):
        return self.save_thread and self.save_thread.is_alive()

# Test code remains the same
if __name__ == "__main__":
    class MockUSBReader:
        def get_data(self):
            return np.random.rand(100).tolist()

    usb_reader = MockUSBReader()
    saver = WaveformSaver(usb_reader)

    saver.start_saving(".", "waveform.csv", 10)

    time.sleep(5)
    saver.stop_saving()