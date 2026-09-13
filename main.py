import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit,
    QPushButton, QHBoxLayout, QDialog, QFileDialog, QMenuBar,
    QAction, QMessageBox, QListWidget, QLabel, QTabWidget, QInputDialog, QStatusBar
)
from PyQt5.QtCore import Qt
from interface import InterfaceGenerator

class WelcomeWindow(QDialog):
    def __init__(self, interface_manager):
        super().__init__()
        self.interface_manager = interface_manager
        self.setWindowTitle("PyCode IDE Launcher")
        self.setFixedSize(500, 350)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Welcome to PyCode")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title, 0, Qt.AlignCenter)

        self.btn_create = QPushButton("➕ Create New Project")
        self.btn_open = QPushButton("📂 Open Existing Project")

        self.btn_create.setFixedWidth(250)
        self.btn_open.setFixedWidth(250)

        self.btn_create.clicked.connect(self.handle_create)
        self.btn_open.clicked.connect(self.handle_open)

        layout.addWidget(self.btn_create, 0, Qt.AlignCenter)
        layout.addWidget(self.btn_open, 0, Qt.AlignCenter)

    def handle_create(self):
        parent_dir = QFileDialog.getExistingDirectory(self, "Select Location for Project")
        if parent_dir:
            name, ok = QInputDialog.getText(self, "Project Name", "Enter folder name:")
            if ok and name:
                project_path = os.path.join(parent_dir, name)
                try:
                    os.makedirs(project_path, exist_ok=True)
                    self.accept_with_path(project_path)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to create: {e}")

    def handle_open(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if path:
            self.accept_with_path(path)

    def accept_with_path(self, path):
        self.selected_path = path
        self.accept()

class CodeEditorApp(QMainWindow):
    def __init__(self, project_path, interface_manager):
        super().__init__()
        self.project_path = project_path
        self.interface_manager = interface_manager
        self.open_files = {}

        self.setWindowTitle(f"PyCode IDE - {project_path}")
        self.setGeometry(100, 100, 1300, 850)

        self._init_ui()
        self._init_menu()
        self.refresh_file_list()
        self.apply_theme_from_config()

    def _init_ui(self):
        central_widget = QWidget()
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(280)
        sidebar_layout = QVBoxLayout(self.sidebar)

        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self.open_file)

        self.btn_new_file = QPushButton("📄 New File")
        self.btn_new_file.clicked.connect(self.create_new_file)

        self.btn_delete_file = QPushButton("🗑️ Delete File")
        self.btn_delete_file.clicked.connect(self.delete_selected_file)

        sidebar_layout.addWidget(QLabel("EXPLORER"))
        sidebar_layout.addWidget(self.file_list)
        sidebar_layout.addWidget(self.btn_new_file)
        sidebar_layout.addWidget(self.btn_delete_file)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        bottom_layout = QHBoxLayout()
        self.settings_button = QPushButton("🎨 Randomize Theme")
        self.settings_button.clicked.connect(self.regenerate_theme)
        bottom_layout.addWidget(self.settings_button)
        bottom_layout.addStretch(1)

        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.addWidget(self.tabs)
        editor_layout.addLayout(bottom_layout)

        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(editor_container)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        self.setCentralWidget(central_widget)

    def _init_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        self.save_action = QAction("Save Current", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_current_file)

        self.save_all_action = QAction("Save All", self)
        self.save_all_action.setShortcut("Ctrl+Shift+S")
        self.save_all_action.triggered.connect(self.save_all_files)

        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_all_action)

    def refresh_file_list(self):
        self.file_list.clear()
        try:
            for file in os.listdir(self.project_path):
                if file.endswith((".py", ".txt", ".md")):
                    self.file_list.addItem(file)
        except Exception as e:
            self.status_bar.showMessage(f"Error loading files: {e}")

    def create_new_file(self):
        name, ok = QInputDialog.getText(self, "New File", "Enter filename (e.g. main.py):")
        if ok and name:
            if not name.endswith(".py"): name += ".py"
            full_path = os.path.join(self.project_path, name)
            try:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write("")
                self.refresh_file_list()
                self.open_file_by_path(full_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not create file: {e}")

    def delete_selected_file(self):
        selected_item = self.file_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Warning", "Please select a file to delete!")
            return

        filename = selected_item.text()
        full_path = os.path.join(self.project_path, filename)

        reply = QMessageBox.question(self, "Confirm Delete",
                                     f"Are you sure you want to delete {filename}?\nThis cannot be undone!",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                if full_path in self.open_files:
                    editor_widget = self.open_files[full_path]
                    index = self.tabs.indexOf(editor_widget)
                    if index != -1:
                        self.tabs.removeTab(index)
                    del self.open_files[full_path]

                os.remove(full_path)
                self.refresh_file_list()
                self.status_bar.showMessage(f"Deleted: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete file: {e}")

    def open_file(self, item):
        full_path = os.path.join(self.project_path, item.text())
        self.open_file_by_path(full_path)

    def open_file_by_path(self, path):
        if path in self.open_files:
            self.tabs.setCurrentWidget(self.open_files[path])
            return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            editor = QTextEdit()
            editor.setPlainText(content)

            filename = os.path.basename(path)
            index = self.tabs.addTab(editor, filename)
            self.tabs.setCurrentIndex(index)
            self.open_files[path] = editor
            self.status_bar.showMessage(f"Opened: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open: {e}")

    def close_tab(self, index):
        widget = self.tabs.widget(index)
        for path, editor in list(self.open_files.items()):
            if editor == widget:
                del self.open_files[path]
                break
        self.tabs.removeTab(index)

    def save_current_file(self):
        current_widget = self.tabs.currentWidget()
        if not current_widget: return

        for path, editor in self.open_files.items():
            if editor == current_widget:
                try:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(editor.toPlainText())
                    self.status_bar.showMessage(f"Saved: {path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Save failed: {e}")
                break

    def save_all_files(self):
        try:
            for path, editor in self.open_files.items():
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(editor.toPlainText())
            self.status_bar.showMessage("All files saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Save all failed: {e}")

    def apply_theme_from_config(self):
        t = self.interface_manager.load_theme()
        self.interface_manager.app.setStyleSheet(self.interface_manager.get_stylesheet(t))

    def regenerate_theme(self):
        t = self.interface_manager.generate_random_theme()
        self.interface_manager.app.setStyleSheet(self.interface_manager.get_stylesheet(t))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gen = InterfaceGenerator(app)

    welcome = WelcomeWindow(gen)
    if welcome.exec_() == QDialog.Accepted:
        editor = CodeEditorApp(welcome.selected_path, gen)
        editor.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)
