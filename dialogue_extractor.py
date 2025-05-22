import sys
import re
import csv

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QTextEdit, QLabel, QLineEdit, QHBoxLayout, QMessageBox, QInputDialog
)
from PyQt5.QtWidgets import QRadioButton, QButtonGroup


class DialogueApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("小说对话提取与人工校对工具")
        self.resize(800, 700)

        self.dialogues = []
        self.index = 0
        self.chapter_pattern = None

        layout = QVBoxLayout()

        self.info_label = QLabel("未加载文本")
        layout.addWidget(self.info_label)

        # 章节编号与标题
        self.chapter_num_input = QLineEdit()
        layout.addWidget(QLabel("章节编号："))
        layout.addWidget(self.chapter_num_input)

        self.chapter_title_input = QLineEdit()
        layout.addWidget(QLabel("章节标题："))
        layout.addWidget(self.chapter_title_input)

        # 上下文显示
        self.context_display = QTextEdit()
        self.context_display.setReadOnly(True)
        layout.addWidget(QLabel("上下文（自动提取）"))
        layout.addWidget(self.context_display)

        # 可修改字段
        self.speaker_input = QLineEdit()
        layout.addWidget(QLabel("文中说话人："))
        layout.addWidget(self.speaker_input)

        self.dialogue_input = QTextEdit()
        layout.addWidget(QLabel("对话内容："))
        layout.addWidget(self.dialogue_input)

        # 是否为对话（按钮组）
        layout.addWidget(QLabel("是否为对话："))
        self.dialogue_yes = QRadioButton("是")
        self.dialogue_no = QRadioButton("否")
        self.dialogue_group = QButtonGroup()
        self.dialogue_group.addButton(self.dialogue_yes)
        self.dialogue_group.addButton(self.dialogue_no)
        btn_row = QHBoxLayout()
        btn_row.addWidget(self.dialogue_yes)
        btn_row.addWidget(self.dialogue_no)
        layout.addLayout(btn_row)

        self.standard_name_input = QLineEdit()
        layout.addWidget(QLabel("标准姓名（用于映射）："))
        layout.addWidget(self.standard_name_input)

        btn_layout = QHBoxLayout()
        self.prev_btn = QPushButton("上一条")
        self.prev_btn.clicked.connect(self.prev_dialogue)
        btn_layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton("下一条")
        self.next_btn.clicked.connect(self.next_dialogue)
        btn_layout.addWidget(self.next_btn)

        layout.addLayout(btn_layout)

        self.save_btn = QPushButton("保存为 CSV")
        self.save_btn.clicked.connect(self.save_csv)
        layout.addWidget(self.save_btn)

        self.load_btn = QPushButton("加载 TXT 文本")
        self.load_btn.clicked.connect(self.load_txt)
        layout.addWidget(self.load_btn)

        self.setLayout(layout)

    def load_txt(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择 TXT 文件", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            # 用户输入章节标题示例
            if not self.get_user_chapter_examples():
                return

            self.dialogues = self.extract_dialogues_with_user_pattern(text, self.chapter_pattern)
            if not self.dialogues:
                QMessageBox.warning(self, "提取失败", "未提取到任何对话")
            else:
                self.index = 0
                self.show_current()
                self.info_label.setText(f"已加载，共 {len(self.dialogues)} 条对话")

    def get_user_chapter_examples(self):
        examples, ok = QInputDialog.getMultiLineText(
            self, "输入章节示例", "请粘贴几行章节编号与标题（如：第五回 贾宝玉游太虚幻境）："
        )
        if ok and examples.strip():
            self.chapter_pattern = self.guess_chapter_pattern(examples)
            QMessageBox.information(self, "成功", "章节提取模式已生成！")
            return True
        return False

    def guess_chapter_pattern(self, example_text):
        #return re.compile(r"(第[一二三四五六七八九十百千]+回)\s+(.+)")
        return re.compile(r"(第[0123456789]+章)\s+(.+)")

    def extract_dialogues_with_user_pattern(self, text, chapter_regex):
        chapters = chapter_regex.split(text)
        dialogue_data = []
        for i in range(1, len(chapters) - 1, 3):
            chapter_num = chapters[i].strip()
            chapter_title = chapters[i + 1].strip()
            chapter_text = chapters[i + 2]

            dialogues = re.findall(r"([\u4e00-\u9fa5]{1,10})[道说曰问应答喊叫嚷骂笑哭叹云言告劝禀叱呵]：“(.*?)”", chapter_text)
            #dialogues = re.findall(r"([\u4e00-\u9fa5]{1,8})[道说曰问应答喊叫嚷骂笑哭叹云言告劝禀叱呵]:[“\"『「](.*?)[”\"』」]", chapter_text)

            for speaker, content in dialogues:
                index = chapter_text.find(content)
                context = chapter_text[max(0, index - 300): index + len(content) + 300]
                dialogue_data.append({
                    "章节编号": chapter_num,
                    "章节标题": chapter_title,
                    "文中说话人": speaker.strip(),
                    "对话内容": content.strip(),
                    "上下文": context.strip(),
                    "是否为对话": "是",
                    "标准姓名": ""
                })
        return dialogue_data

    # def show_current(self):
    #     if 0 <= self.index < len(self.dialogues):
    #         d = self.dialogues[self.index]
    #         self.chapter_num_input.setText(d["章节编号"])
    #         self.chapter_title_input.setText(d["章节标题"])
    #         self.context_display.setPlainText(d["上下文"])
    #         self.speaker_input.setText(d["文中说话人"])
    #         self.dialogue_input.setPlainText(d["对话内容"])
    #         if d["是否为对话"] == "是":
    #             self.dialogue_yes.setChecked(True)
    #         else:
    #             self.dialogue_no.setChecked(True)
    #
    #         self.standard_name_input.setText(d["标准姓名"])
    #         self.info_label.setText(f"第 {self.index + 1} / {len(self.dialogues)} 条")

    def show_current(self):
        if 0 <= self.index < len(self.dialogues):
            d = self.dialogues[self.index]
            self.chapter_num_input.setText(d["章节编号"])
            self.chapter_title_input.setText(d["章节标题"])
            self.speaker_input.setText(d["文中说话人"])
            self.dialogue_input.setPlainText(d["对话内容"])
            self.standard_name_input.setText(d["标准姓名"])
            if d["是否为对话"] == "是":
                self.dialogue_yes.setChecked(True)
            else:
                self.dialogue_no.setChecked(True)

            self.info_label.setText(f"第 {self.index + 1} / {len(self.dialogues)} 条")

            # 原始上下文、说话人、对话内容
            context = d["上下文"]
            speaker = d["文中说话人"]
            dialogue = d["对话内容"]

            # 优先替换对话内容为蓝色（避免标签嵌套冲突）
            if dialogue:
                context = re.sub(
                    re.escape(dialogue),
                    lambda m: f'<span style="color:blue;">{m.group(0)}</span>',
                    context
                )

            # 再高亮说话人（红色+加粗）
            if speaker:
                context = re.sub(
                    re.escape(speaker),
                    lambda m: f'<span style="color:red;"><b>{m.group(0)}</b></span>',
                    context
                )

            self.context_display.setHtml(context)

    def save_current(self):
        if 0 <= self.index < len(self.dialogues):
            d = self.dialogues[self.index]
            d["章节编号"] = self.chapter_num_input.text().strip()
            d["章节标题"] = self.chapter_title_input.text().strip()
            d["文中说话人"] = self.speaker_input.text().strip()
            d["对话内容"] = self.dialogue_input.toPlainText().strip()
            if self.dialogue_yes.isChecked():
                d["是否为对话"] = "是"
            elif self.dialogue_no.isChecked():
                d["是否为对话"] = "否"
            else:
                d["是否为对话"] = ""
            d["标准姓名"] = self.standard_name_input.text().strip()

    def next_dialogue(self):
        self.save_current()
        if self.index < len(self.dialogues) - 1:
            self.index += 1
            self.show_current()

    def prev_dialogue(self):
        self.save_current()
        if self.index > 0:
            self.index -= 1
            self.show_current()

    def save_csv(self):
        self.save_current()
        file_path, _ = QFileDialog.getSaveFileName(self, "保存对话 CSV", "", "CSV 文件 (*.csv)")
        if not file_path:
            return

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(self.dialogues[0].keys()))
            writer.writeheader()
            for row in self.dialogues:
                writer.writerow(row)

        # 保存姓名映射
        mapping = {}
        for d in self.dialogues:
            raw = d["文中说话人"]
            std = d["标准姓名"]
            if raw and std:
                mapping[raw] = std
        map_file = file_path.replace(".csv", "_姓名映射.csv")
        with open(map_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["文中说话人", "标准姓名"])
            for raw, std in mapping.items():
                writer.writerow([raw, std])

        QMessageBox.information(self, "保存成功", f"已保存为：\n{file_path}\n{map_file}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont()
    font.setPointSize(12)  # 设置字体大小为12，可根据需要调整
    app.setFont(font)
    window = DialogueApp()
    window.show()
    sys.exit(app.exec_())
