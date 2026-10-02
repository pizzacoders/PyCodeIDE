import random
import configparser
import os
import sys

class InterfaceGenerator:
    CONFIG_DIR_NAME = "Configs"
    CONFIG_FILE_NAME = "interface.cfg"

    def __init__(self, app_instance):
        self.app = app_instance
        if getattr(sys, 'frozen', False):
            self.base_path = os.path.dirname(sys.executable)
        else:
            self.base_path = os.path.dirname(os.path.abspath(__file__))

        self.config_dir = os.path.join(self.base_path, self.CONFIG_DIR_NAME)
        self.config_path = os.path.join(self.config_dir, self.CONFIG_FILE_NAME)
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        try:
            if not os.path.exists(self.config_dir):
                os.makedirs(self.config_dir)
        except Exception as e:
            print(f"Error creating config dir: {e}")

    def generate_random_theme(self):
        palettes = [
            {"bg": "#1e1e2e", "sidebar": "#181825", "accent": "#cba6f7", "text": "#cdd6f4", "btn": "#313244"},
            {"bg": "#282c34", "sidebar": "#21252b", "accent": "#61afef", "text": "#abb2bf", "btn": "#3e4451"},
            {"bg": "#1a1b26", "sidebar": "#16161e", "accent": "#7aa2f7", "text": "#a9b1d6", "btn": "#24283b"},
            {"bg": "#2d3436", "sidebar": "#212529", "accent": "#00cec9", "text": "#dfe6e9", "btn": "#636e72"}
        ]
        p = random.choice(palettes)
        fonts = ["Menlo", "Monaco", "Courier New", "SF Mono"]

        theme = {
            "bg": p["bg"],
            "sidebar": p["sidebar"],
            "accent": p["accent"],
            "text": p["text"],
            "btn": p["btn"],
            "font_family": random.choice(fonts),
            "font_size": "13"
        }
        self._save_theme(theme)
        return theme

    def _save_theme(self, theme_data):
        try:
            config = configparser.ConfigParser()
            config['Theme'] = theme_data
            with open(self.config_path, 'w') as f:
                config.write(f)
        except Exception as e:
            print(f"Error saving theme: {e}")

    def load_theme(self):
        if not os.path.exists(self.config_path):
            return self.generate_random_theme()

        try:
            config = configparser.ConfigParser()
            config.read(self.config_path)
            if 'Theme' not in config:
                return self.generate_random_theme()
            theme = dict(config['Theme'])
            required_keys = ["bg", "sidebar", "accent", "text", "btn", "font_family", "font_size"]
            if not all(key in theme for key in required_keys):
                return self.generate_random_theme()
            return theme
        except:
            return self.generate_random_theme()

    def get_stylesheet(self, t):
        return f"""
        QMainWindow, QDialog {{
            background-color: {t['bg']};
            color: {t['text']};
        }}
        QWidget {{
            background-color: {t['bg']};
            color: {t['text']};
            font-family: {t['font_family']};
        }}
        QListWidget {{
            background-color: {t['sidebar']};
            border: none;
            border-right: 1px solid {t['btn']};
            padding: 5px;
            outline: none;
        }}
        QListWidget::item {{
            padding: 8px;
            border-radius: 4px;
            margin-bottom: 2px;
        }}
        QListWidget::item:selected {{
            background-color: {t['accent']};
            color: {t['bg']};
        }}
        QTabWidget::pane {{
            border: none;
        }}
        QTabBar::tab {{
            background: {t['sidebar']};
            padding: 10px 20px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            margin-right: 2px;
            color: {t['text']};
        }}
        QTabBar::tab:selected {{
            background: {t['bg']};
            border-bottom: 2px solid {t['accent']};
        }}
        QTextEdit {{
            background-color: {t['bg']};
            color: {t['text']};
            border: none;
            font-family: 'Menlo', 'Monaco', 'monospace';
            font-size: {t['font_size']}pt;
            padding: 15px;
        }}
        QPushButton {{
            background-color: {t['btn']};
            color: {t['text']};
            border: 1px solid {t['accent']};
            padding: 8px 15px;
            border-radius: 6px;
        }}
        QPushButton:hover {{
            background-color: {t['accent']};
            color: {t['bg']};
        }}
        QStatusBar {{
            background-color: {t['sidebar']};
            color: {t['text']};
            border-top: 1px solid {t['btn']};
        }}
        """
