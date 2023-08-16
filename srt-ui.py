import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QComboBox, QDoubleSpinBox
from PySide6.QtCore import QSettings
from PySide6.QtGui import QIntValidator

import SRTInsertImage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SRT Insert Image")
        self.setGeometry(100, 100, 450, 300)

        # 图片路径
        self.image_label = QLabel("输入图片路径:", self)
        self.image_label.move(20, 20)
        self.image_input = QLineEdit(self)
        self.image_input.setGeometry(150, 20, 200, 20)
        self.image_button = QPushButton("选择图片", self)
        self.image_button.setGeometry(360, 20, 60, 20)
        self.image_button.clicked.connect(self.browse_image)

        # 位置高度
        self.position_label = QLabel("位置高度:", self)
        self.position_label.move(20, 50)
        self.position_input = QLineEdit(self)
        self.position_input.setGeometry(150, 50, 200, 20)
        self.position_input.setValidator(QIntValidator(-999999, 999999, self))  # 只允许输入非负整数
        self.position_input.setText('0')

        # SRT文件路径
        self.srt_label = QLabel("SRT 路径:", self)
        self.srt_label.move(20, 80)
        self.srt_input = QLineEdit(self)
        self.srt_input.setGeometry(150, 80, 200, 20)
        self.srt_button = QPushButton("选择SRT", self)
        self.srt_button.setGeometry(360, 80, 60, 20)
        self.srt_button.clicked.connect(self.browse_srt)

        # 输出路径
        self.output_label = QLabel("输出路径:", self)
        self.output_label.move(20, 110)
        self.output_input = QLineEdit(self)
        self.output_input.setGeometry(150, 110, 200, 20)
        self.output_button = QPushButton("选择输出", self)
        self.output_button.setGeometry(360, 110, 60, 20)
        self.output_button.clicked.connect(self.browse_output)

        # 缩放因子
        self.scale_label = QLabel("缩放系数:", self)
        self.scale_label.move(20, 140)
        self.scale_input = QDoubleSpinBox(self)
        self.scale_input.setGeometry(150, 140, 200, 20)
        self.scale_input.setRange(0.001, 1000.0)
        self.scale_input.setSingleStep(0.25)
        self.scale_input.setValue(1.0)

        # 背景图片大小
        self.background_label = QLabel("背景大小:", self)
        self.background_label.move(20, 170)
        self.background_input_width = QLineEdit(self)
        self.background_input_width.setGeometry(150, 170, 90, 20)
        self.background_input_width.setValidator(QIntValidator(0, 999999, self))  # 只允许输入非负整数
        self.background_input_width.setText("1920")  # 设置默认值为1920

        self.background_input_height = QLineEdit(self)
        self.background_input_height.setGeometry(260, 170, 90, 20)
        self.background_input_height.setValidator(QIntValidator(0, 999999, self))  # 只允许输入非负整数
        self.background_input_height.setText("1080")  # 设置默认值为1080

        # 时间码策略
        self.timecode_label = QLabel("时间点策略:", self)
        self.timecode_label.move(20, 200)
        self.timecode_combobox = QComboBox(self)
        self.timecode_combobox.setGeometry(150, 200, 100, 20)
        self.timecode_combobox.addItems(["start", "end", "middle"])
        self.timecode_combobox.setCurrentText("end")  # 设置默认选项为'end'

        # 开始按钮
        self.start_button = QPushButton("开始", self)
        self.start_button.setGeometry(150, 240, 80, 30)
        self.start_button.clicked.connect(self.start_processing)

        # 恢复用户输入的历史记录
        settings = QSettings("licc", "srt-insert-image-ui")
        image_path = settings.value("image_path", "")
        srt_path = settings.value("srt_path", "")
        output_path = settings.value("output_path", "")

        self.image_input.setText(image_path)
        self.srt_input.setText(srt_path)
        self.output_input.setText(output_path)

    def browse_image(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("PNG Images (*.png)")
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self.image_input.setText(file_path)

    def browse_srt(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("SRT Files (*.srt)")
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self.srt_input.setText(file_path)

    def browse_output(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Images (*.png)")
        if len(filename) > 0:
            self.output_input.setText(filename)

    def start_processing(self):
        # 从 UI 获取相应参数值
        image_path = self.image_input.text()
        position_height = int(self.position_input.text())
        srt_path = self.srt_input.text()
        output_path = self.output_input.text()
        scale_factor = float(self.scale_input.value())
        background_width = int(self.background_input_width.text())
        background_height = int(self.background_input_height.text())
        background_size = (background_width, background_height)
        timecode_strategy = self.timecode_combobox.currentText()

        # 检查参数的有效性
        if not image_path:
            self.show_error_message("Please select an image.")
            return

        if not srt_path:
            self.show_error_message("Please select an SRT file.")
            return

        if not output_path:
            self.show_error_message("Please select an output directory.")
            return

        print("Image Path:", image_path)
        print("Position Height:", position_height)
        print("SRT Path:", srt_path)
        print("Output Path:", output_path)
        print("Scale Factor:", scale_factor)
        print("Background Size:", background_size)
        print("Timecode Strategy:", timecode_strategy)

        SRTInsertImage.srt_insert_image(image_path, srt_path, position_height, output_path, scale_factor, background_size, timecode_strategy)
        # 保存用户输入的路径到应用程序设置
        settings = QSettings("licc", "srt-insert-image-ui")
        settings.setValue("image_path", image_path)
        settings.setValue("srt_path", srt_path)
        settings.setValue("output_path", output_path)
        QMessageBox.information(self, "通知", "完成.")

    def show_error_message(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())