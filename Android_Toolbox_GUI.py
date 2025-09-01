import sys
import os
import subprocess
import re
import tarfile
import tempfile
import shutil
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QComboBox, QLineEdit, QPushButton, QTextEdit, QLabel, QCheckBox,
    QFileDialog, QGroupBox, QTabWidget, QMessageBox, QDialog, QDialogButtonBox,
    QListWidget, QSplitter, QListWidgetItem, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PyQt6.QtCore import Qt, QProcess, QSettings
from PyQt6.QtGui import QFont, QIcon, QMovie, QAction, QActionGroup, QColor, QTextCursor

class DropLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and len(event.mimeData().urls()) == 1:
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.setText(file_path)

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.settings = QSettings("MySoft", "FastAdbGui")
        
        layout = QGridLayout(self)
        
        self.adb_label = QLabel()
        layout.addWidget(self.adb_label, 0, 0)
        self.adb_path_edit = QLineEdit(self.settings.value("adb_path", "adb"))
        layout.addWidget(self.adb_path_edit, 0, 1)
        self.adb_browse_btn = QPushButton()
        self.adb_browse_btn.clicked.connect(lambda: self.browse_for_executable(self.adb_path_edit))
        layout.addWidget(self.adb_browse_btn, 0, 2)

        self.fastboot_label = QLabel()
        layout.addWidget(self.fastboot_label, 1, 0)
        self.fastboot_path_edit = QLineEdit(self.settings.value("fastboot_path", "fastboot"))
        layout.addWidget(self.fastboot_path_edit, 1, 1)
        self.fastboot_browse_btn = QPushButton()
        self.fastboot_browse_btn.clicked.connect(lambda: self.browse_for_executable(self.fastboot_path_edit))
        layout.addWidget(self.fastboot_browse_btn, 1, 2)
        
        self.scrcpy_label = QLabel()
        layout.addWidget(self.scrcpy_label, 2, 0)
        self.scrcpy_path_edit = QLineEdit(self.settings.value("scrcpy_path", "scrcpy"))
        layout.addWidget(self.scrcpy_path_edit, 2, 1)
        self.scrcpy_browse_btn = QPushButton()
        self.scrcpy_browse_btn.clicked.connect(lambda: self.browse_for_executable(self.scrcpy_path_edit))
        layout.addWidget(self.scrcpy_browse_btn, 2, 2)

        self.odin_label = QLabel()
        layout.addWidget(self.odin_label, 3, 0)
        self.odin_path_edit = QLineEdit(self.settings.value("odin_path", "odin4"))
        layout.addWidget(self.odin_path_edit, 3, 1)
        self.odin_browse_btn = QPushButton()
        self.odin_browse_btn.clicked.connect(lambda: self.browse_for_executable(self.odin_path_edit))
        layout.addWidget(self.odin_browse_btn, 3, 2)

        self.heimdall_label = QLabel()
        layout.addWidget(self.heimdall_label, 4, 0)
        self.heimdall_path_edit = QLineEdit(self.settings.value("heimdall_path", "heimdall"))
        layout.addWidget(self.heimdall_path_edit, 4, 1)
        self.heimdall_browse_btn = QPushButton()
        self.heimdall_browse_btn.clicked.connect(lambda: self.browse_for_executable(self.heimdall_path_edit))
        layout.addWidget(self.heimdall_browse_btn, 4, 2)

        self.spft_label = QLabel()
        layout.addWidget(self.spft_label, 5, 0)
        self.spft_path_edit = QLineEdit(self.settings.value("spft_path", "flash_tool"))
        layout.addWidget(self.spft_path_edit, 5, 1)
        self.spft_browse_btn = QPushButton()
        self.spft_browse_btn.clicked.connect(lambda: self.browse_for_executable(self.spft_path_edit))
        layout.addWidget(self.spft_browse_btn, 5, 2)

        self.edl_label = QLabel()
        layout.addWidget(self.edl_label, 6, 0)
        self.edl_path_edit = QLineEdit(self.settings.value("edl_path", "edl"))
        layout.addWidget(self.edl_path_edit, 6, 1)
        self.edl_browse_btn = QPushButton()
        self.edl_browse_btn.clicked.connect(lambda: self.browse_for_executable(self.edl_path_edit))
        layout.addWidget(self.edl_browse_btn, 6, 2)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons, 7, 0, 1, 3)
        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(self.parent.get_string("settings_title"))
        self.adb_label.setText(self.parent.get_string("settings_adb_path"))
        self.fastboot_label.setText(self.parent.get_string("settings_fastboot_path"))
        self.scrcpy_label.setText(self.parent.get_string("settings_scrcpy_path"))
        self.odin_label.setText(self.parent.get_string("settings_odin_path"))
        self.heimdall_label.setText(self.parent.get_string("settings_heimdall_path"))
        self.spft_label.setText(self.parent.get_string("settings_spft_path"))
        self.edl_label.setText(self.parent.get_string("settings_edl_path"))
        self.adb_browse_btn.setText(self.parent.get_string("browse"))
        self.fastboot_browse_btn.setText(self.parent.get_string("browse"))
        self.scrcpy_browse_btn.setText(self.parent.get_string("browse"))
        self.odin_browse_btn.setText(self.parent.get_string("browse"))
        self.heimdall_browse_btn.setText(self.parent.get_string("browse"))
        self.spft_browse_btn.setText(self.parent.get_string("browse"))
        self.edl_browse_btn.setText(self.parent.get_string("browse"))

    def browse_for_executable(self, line_edit):
        filter = "Executables (*.exe)" if sys.platform == "win32" else "All files (*)"
        path, _ = QFileDialog.getOpenFileName(self, self.parent.get_string("select_executable"), "", filter)
        if path:
            line_edit.setText(path)

    def accept(self):
        self.settings.setValue("adb_path", self.adb_path_edit.text())
        self.settings.setValue("fastboot_path", self.fastboot_path_edit.text())
        self.settings.setValue("scrcpy_path", self.scrcpy_path_edit.text())
        self.settings.setValue("odin_path", self.odin_path_edit.text())
        self.settings.setValue("heimdall_path", self.heimdall_path_edit.text())
        self.settings.setValue("spft_path", self.spft_path_edit.text())
        self.settings.setValue("edl_path", self.edl_path_edit.text())
        super().accept()

class FastbootAdbGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("MySoft", "FastAdbGui")
        
        self.current_lang = self.settings.value("language", "sv")
        self.init_translations()
        self.init_themes()

        self.adb_path = self.settings.value("adb_path", "adb")
        self.fastboot_path = self.settings.value("fastboot_path", "fastboot")
        self.scrcpy_path = self.settings.value("scrcpy_path", "scrcpy")
        self.odin_path = self.settings.value("odin_path", "odin4")
        self.heimdall_path = self.settings.value("heimdall_path", "heimdall")
        self.spft_path = self.settings.value("spft_path", "flash_tool")
        self.edl_path = self.settings.value("edl_path", "edl")
        
        self.is_recording = False
        self.temp_dir = None

        self.common_partitions = [
            "BOOT", "RECOVERY", "SYSTEM", "USERDATA", "CACHE", "RADIO", "EFS", "APNHLOS", "MODEM", "PIT"
        ]
        
        self.process = QProcess(self)
        self.logcat_process = QProcess(self)
        self.screenrecord_process = QProcess(self)

        self.init_ui()
        self.load_settings()
        self.check_executables()
        
        self.apply_theme(self.settings.value("theme", "Light"))

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.create_menu()
        
        self.device_group = QGroupBox()
        device_layout = QGridLayout(self.device_group)
        self.device_select_label = QLabel()
        self.serial_input = QLineEdit()
        self.device_combo = QComboBox()
        self.device_combo.currentTextChanged.connect(self.update_serial_from_combo)
        self.serial_label = QLabel()
        self.refresh_devices_btn = QPushButton()
        self.refresh_devices_btn.setIcon(QIcon.fromTheme("view-refresh"))
        self.refresh_devices_btn.clicked.connect(self.update_device_list)
        device_layout.addWidget(self.device_select_label, 0, 0)
        device_layout.addWidget(self.device_combo, 0, 1, 1, 2)
        device_layout.addWidget(self.serial_label, 1, 0)
        device_layout.addWidget(self.serial_input, 1, 1, 1, 2)
        device_layout.addWidget(self.refresh_devices_btn, 2, 1, 1, 2)
        main_layout.addWidget(self.device_group)

        self.main_tabs = QTabWidget()
        self.main_tabs.addTab(self.create_adb_tab_widget(), QIcon.fromTheme("smartphone"), "ADB")
        self.main_tabs.addTab(self.create_fastboot_tab_widget(), QIcon.fromTheme("system-run"), "Fastboot")
        self.main_tabs.addTab(self.create_xiaomi_tab(), QIcon.fromTheme("folder-zip"), "Xiaomi")
        self.main_tabs.addTab(self.create_edl_tab(), QIcon.fromTheme("usb-port"), "Qualcomm EDL")
        self.main_tabs.addTab(self.create_heimdall_tab(), QIcon.fromTheme("drive-removable-media"), "Heimdall")
        self.main_tabs.addTab(self.create_spft_tab(), QIcon.fromTheme("cpu"), "SP Flash Tool")
        self.main_tabs.addTab(self.create_odin_tab(), QIcon.fromTheme("drive-harddisk"), "Odin")
        self.main_tabs.addTab(self.create_scrcpy_tab(), QIcon.fromTheme("video-display"), "scrcpy")
        self.main_tabs.addTab(self.create_logcat_tab(), QIcon.fromTheme("text-x-generic"), "Logcat")
        main_layout.addWidget(self.main_tabs)
        
        self.execution_group = QGroupBox()
        execution_layout = QVBoxLayout(self.execution_group)
        self.command_preview = QLineEdit()
        self.command_preview.setReadOnly(True)
        self.command_preview.setFont(QFont("Courier New", 9))
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Courier New", 9))
        self.output_text.textChanged.connect(lambda: self.output_text.verticalScrollBar().setValue(self.output_text.verticalScrollBar().maximum()))
        output_buttons_layout = QHBoxLayout()
        self.clear_button = QPushButton()
        self.clear_button.setIcon(QIcon.fromTheme("edit-clear"))
        self.clear_button.clicked.connect(self.output_text.clear)
        self.save_log_button = QPushButton()
        self.save_log_button.setIcon(QIcon.fromTheme("document-save"))
        self.save_log_button.clicked.connect(self.save_log_to_file)
        output_buttons_layout.addWidget(self.clear_button)
        output_buttons_layout.addWidget(self.save_log_button)
        execution_layout.addWidget(self.command_preview)
        execution_layout.addWidget(self.output_text)
        execution_layout.addLayout(output_buttons_layout)
        main_layout.addWidget(self.execution_group)

        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)
        self.current_running_button = None
        
        self.status_bar = self.statusBar()
        self.status_label = QLabel()
        self.status_bar.addWidget(self.status_label)
        self.loading_label = QLabel()
        self.loading_movie = QMovie(":/qt-project.org/styles/commonstyle/images/standardbutton-busy-16.gif")
        self.loading_label.setMovie(self.loading_movie)
        self.status_bar.addPermanentWidget(self.loading_label)
        self.loading_label.hide()
        
        self.retranslate_ui()

    # --- Metoder för att skapa huvudflikarna ---
    def create_fastboot_tab_widget(self):
        fastboot_tabs = QTabWidget()
        self.flashing_tab = self.create_flashing_tab()
        self.basic_actions_tab = self.create_basic_actions_tab()
        self.partitions_tab = self.create_partitions_tab()
        self.advanced_tab = self.create_advanced_tab()
        fastboot_tabs.addTab(self.flashing_tab, "")
        fastboot_tabs.addTab(self.basic_actions_tab, "")
        fastboot_tabs.addTab(self.partitions_tab, "")
        fastboot_tabs.addTab(self.advanced_tab, "")
        return fastboot_tabs

    def create_adb_tab_widget(self):
        adb_tabs = QTabWidget()
        self.adb_file_transfer_tab = self.create_adb_file_transfer_tab()
        self.adb_app_management_tab = self.create_adb_app_management_tab()
        self.adb_device_control_tab = self.create_adb_device_control_tab()
        self.adb_device_info_tab = self.create_adb_device_info_tab()
        self.adb_networking_tab = self.create_adb_networking_tab()
        self.adb_debloat_tab = self.create_adb_debloat_tab()
        self.adb_diagnostics_tab = self.create_adb_diagnostics_tab()
        adb_tabs.addTab(self.adb_file_transfer_tab, "")
        adb_tabs.addTab(self.adb_app_management_tab, "")
        adb_tabs.addTab(self.adb_device_control_tab, "")
        adb_tabs.addTab(self.adb_device_info_tab, "")
        adb_tabs.addTab(self.adb_networking_tab, "")
        adb_tabs.addTab(self.adb_debloat_tab, "")
        adb_tabs.addTab(self.adb_diagnostics_tab, "")
        return adb_tabs

    # --- Nya flikar ---
    def create_xiaomi_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        self.xiaomi_group = QGroupBox(); grid = QGridLayout(self.xiaomi_group)

        self.xiaomi_file_label = QLabel(); self.xiaomi_file_input = DropLineEdit()
        self.xiaomi_file_browse = QPushButton(); self.xiaomi_file_browse.clicked.connect(lambda: self.browse_file(self.xiaomi_file_input))
        grid.addWidget(self.xiaomi_file_label, 0, 0); grid.addWidget(self.xiaomi_file_input, 0, 1); grid.addWidget(self.xiaomi_file_browse, 0, 2)
        
        self.xiaomi_flash_all_btn = self.create_run_button("xiaomi_flash_all")
        self.xiaomi_flash_except_storage_btn = self.create_run_button("xiaomi_flash_except_storage")
        self.xiaomi_flash_lock_btn = self.create_run_button("xiaomi_flash_lock")
        self.xiaomi_flash_lock_btn.setStyleSheet("background-color: #f44336;")

        grid.addWidget(self.xiaomi_flash_all_btn, 1, 0, 1, 3)
        grid.addWidget(self.xiaomi_flash_except_storage_btn, 2, 0, 1, 3)
        grid.addWidget(self.xiaomi_flash_lock_btn, 3, 0, 1, 3)

        layout.addWidget(self.xiaomi_group)
        layout.addStretch()
        return tab

    def create_edl_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        
        # Actions
        self.edl_actions_group = QGroupBox(); actions_layout = QHBoxLayout(self.edl_actions_group)
        self.edl_reboot_btn = self.create_run_button("edl_reboot_edl")
        self.edl_printgpt_btn = self.create_run_button("edl_printgpt")
        self.edl_reset_btn = self.create_run_button("edl_reset")
        actions_layout.addWidget(self.edl_reboot_btn); actions_layout.addWidget(self.edl_printgpt_btn); actions_layout.addWidget(self.edl_reset_btn)
        layout.addWidget(self.edl_actions_group)

        # QFIL Flash
        self.edl_qfil_group = QGroupBox(); grid = QGridLayout(self.edl_qfil_group)
        self.edl_loader_label = QLabel(); self.edl_loader_input = DropLineEdit(); self.edl_loader_browse = QPushButton(); self.edl_loader_browse.clicked.connect(lambda: self.browse_file(self.edl_loader_input))
        self.edl_rawprogram_label = QLabel(); self.edl_rawprogram_input = DropLineEdit(); self.edl_rawprogram_browse = QPushButton(); self.edl_rawprogram_browse.clicked.connect(lambda: self.browse_file(self.edl_rawprogram_input))
        self.edl_patch_label = QLabel(); self.edl_patch_input = DropLineEdit(); self.edl_patch_browse = QPushButton(); self.edl_patch_browse.clicked.connect(lambda: self.browse_file(self.edl_patch_input))
        self.edl_imagedir_label = QLabel(); self.edl_imagedir_input = DropLineEdit(); self.edl_imagedir_browse = QPushButton(); self.edl_imagedir_browse.clicked.connect(self.browse_folder_for_edl)
        
        grid.addWidget(self.edl_loader_label, 0, 0); grid.addWidget(self.edl_loader_input, 0, 1); grid.addWidget(self.edl_loader_browse, 0, 2)
        grid.addWidget(self.edl_rawprogram_label, 1, 0); grid.addWidget(self.edl_rawprogram_input, 1, 1); grid.addWidget(self.edl_rawprogram_browse, 1, 2)
        grid.addWidget(self.edl_patch_label, 2, 0); grid.addWidget(self.edl_patch_input, 2, 1); grid.addWidget(self.edl_patch_browse, 2, 2)
        grid.addWidget(self.edl_imagedir_label, 3, 0); grid.addWidget(self.edl_imagedir_input, 3, 1); grid.addWidget(self.edl_imagedir_browse, 3, 2)
        
        self.edl_qfil_flash_btn = self.create_run_button("edl_qfil_flash")
        self.edl_qfil_flash_btn.setStyleSheet("background-color: #f44336;")
        grid.addWidget(self.edl_qfil_flash_btn, 4, 0, 1, 3)
        layout.addWidget(self.edl_qfil_group)

        layout.addStretch()
        return tab

    def create_heimdall_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        
        # Actions
        actions_group = QGroupBox(); actions_layout = QHBoxLayout(actions_group)
        self.heimdall_detect_btn = self.create_run_button("heimdall_detect")
        self.heimdall_pit_btn = self.create_run_button("heimdall_print_pit")
        self.heimdall_download_pit_btn = self.create_run_button("heimdall_download_pit")
        actions_layout.addWidget(self.heimdall_detect_btn)
        actions_layout.addWidget(self.heimdall_pit_btn)
        actions_layout.addWidget(self.heimdall_download_pit_btn)
        layout.addWidget(actions_group)

        # Partitions
        self.heimdall_parts_group = QGroupBox(); parts_layout = QVBoxLayout(self.heimdall_parts_group)
        self.heimdall_parts_table = QTableWidget(0, 3)
        self.heimdall_parts_table.setHorizontalHeaderLabels(["Partition", "File Path", ""])
        self.heimdall_parts_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        parts_layout.addWidget(self.heimdall_parts_table)
        
        parts_buttons_layout = QHBoxLayout()
        self.heimdall_add_part_btn = QPushButton(); self.heimdall_add_part_btn.setIcon(QIcon.fromTheme("list-add"))
        self.heimdall_add_part_btn.clicked.connect(self.add_heimdall_partition)
        self.heimdall_rem_part_btn = QPushButton(); self.heimdall_rem_part_btn.setIcon(QIcon.fromTheme("list-remove"))
        self.heimdall_rem_part_btn.clicked.connect(self.remove_heimdall_partition)
        parts_buttons_layout.addWidget(self.heimdall_add_part_btn); parts_buttons_layout.addWidget(self.heimdall_rem_part_btn)
        parts_layout.addLayout(parts_buttons_layout)
        layout.addWidget(self.heimdall_parts_group)

        # Options
        self.heimdall_options_group = QGroupBox(); options_layout = QHBoxLayout(self.heimdall_options_group)
        self.heimdall_repartition_check = QCheckBox()
        self.heimdall_no_reboot_check = QCheckBox()
        self.heimdall_tflash_check = QCheckBox()
        self.heimdall_skip_size_check = QCheckBox()
        options_layout.addWidget(self.heimdall_repartition_check); options_layout.addWidget(self.heimdall_no_reboot_check)
        options_layout.addWidget(self.heimdall_tflash_check); options_layout.addWidget(self.heimdall_skip_size_check)
        layout.addWidget(self.heimdall_options_group)

        # Flash
        self.heimdall_flash_btn = self.create_run_button("heimdall_flash")
        self.heimdall_flash_btn.setStyleSheet("background-color: #f44336;")
        layout.addWidget(self.heimdall_flash_btn)
        
        layout.addStretch()
        return tab

    def create_spft_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)

        # Files
        self.spft_files_group = QGroupBox(); grid = QGridLayout(self.spft_files_group)
        self.spft_scatter_label = QLabel(); self.spft_scatter_input = DropLineEdit()
        self.spft_scatter_browse_btn = QPushButton(); self.spft_scatter_browse_btn.clicked.connect(self.load_spft_scatter_file)
        self.spft_da_label = QLabel(); self.spft_da_input = DropLineEdit()
        self.spft_da_browse_btn = QPushButton(); self.spft_da_browse_btn.clicked.connect(lambda: self.browse_file(self.spft_da_input))
        grid.addWidget(self.spft_scatter_label, 0, 0); grid.addWidget(self.spft_scatter_input, 0, 1); grid.addWidget(self.spft_scatter_browse_btn, 0, 2)
        grid.addWidget(self.spft_da_label, 1, 0); grid.addWidget(self.spft_da_input, 1, 1); grid.addWidget(self.spft_da_browse_btn, 1, 2)
        layout.addWidget(self.spft_files_group)

        # Partitions
        self.spft_parts_table = QTableWidget(0, 2)
        self.spft_parts_table.setHorizontalHeaderLabels(["Flash", "Partition"])
        self.spft_parts_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.spft_parts_table)

        # Options
        self.spft_options_group = QGroupBox(); grid = QGridLayout(self.spft_options_group)
        self.spft_battery_label = QLabel(); self.spft_battery_combo = QComboBox(); self.spft_battery_combo.addItems(["Auto", "With Battery", "Without Battery"])
        self.spft_com_label = QLabel(); self.spft_com_input = QLineEdit()
        self.spft_reboot_check = QCheckBox()
        grid.addWidget(self.spft_battery_label, 0, 0); grid.addWidget(self.spft_battery_combo, 0, 1)
        grid.addWidget(self.spft_com_label, 1, 0); grid.addWidget(self.spft_com_input, 1, 1)
        grid.addWidget(self.spft_reboot_check, 2, 0, 1, 2)
        layout.addWidget(self.spft_options_group)

        # Actions
        self.spft_actions_group = QGroupBox(); actions_layout = QHBoxLayout(self.spft_actions_group)
        self.spft_dl_btn = self.create_run_button("spft_download")
        self.spft_fu_btn = self.create_run_button("spft_upgrade")
        self.spft_fa_btn = self.create_run_button("spft_format")
        self.spft_fa_btn.setStyleSheet("background-color: #f44336;")
        actions_layout.addWidget(self.spft_dl_btn); actions_layout.addWidget(self.spft_fu_btn); actions_layout.addWidget(self.spft_fa_btn)
        layout.addWidget(self.spft_actions_group)

        layout.addStretch()
        return tab

    def create_odin_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        
        # Files Group
        self.odin_files_group = QGroupBox(); grid = QGridLayout(self.odin_files_group)
        self.odin_bl_label = QLabel("BL:"); self.odin_bl_input = DropLineEdit(); self.odin_bl_browse = QPushButton(); self.odin_bl_browse.clicked.connect(lambda: self.browse_file(self.odin_bl_input))
        self.odin_ap_label = QLabel("AP:"); self.odin_ap_input = DropLineEdit(); self.odin_ap_browse = QPushButton(); self.odin_ap_browse.clicked.connect(lambda: self.browse_file(self.odin_ap_input))
        self.odin_cp_label = QLabel("CP:"); self.odin_cp_input = DropLineEdit(); self.odin_cp_browse = QPushButton(); self.odin_cp_browse.clicked.connect(lambda: self.browse_file(self.odin_cp_input))
        self.odin_csc_label = QLabel("CSC:"); self.odin_csc_input = DropLineEdit(); self.odin_csc_browse = QPushButton(); self.odin_csc_browse.clicked.connect(lambda: self.browse_file(self.odin_csc_input))
        self.odin_ums_label = QLabel("UMS:"); self.odin_ums_input = DropLineEdit(); self.odin_ums_browse = QPushButton(); self.odin_ums_browse.clicked.connect(lambda: self.browse_file(self.odin_ums_input))
        grid.addWidget(self.odin_bl_label, 0, 0); grid.addWidget(self.odin_bl_input, 0, 1); grid.addWidget(self.odin_bl_browse, 0, 2)
        grid.addWidget(self.odin_ap_label, 1, 0); grid.addWidget(self.odin_ap_input, 1, 1); grid.addWidget(self.odin_ap_browse, 1, 2)
        grid.addWidget(self.odin_cp_label, 2, 0); grid.addWidget(self.odin_cp_input, 2, 1); grid.addWidget(self.odin_cp_browse, 2, 2)
        grid.addWidget(self.odin_csc_label, 3, 0); grid.addWidget(self.odin_csc_input, 3, 1); grid.addWidget(self.odin_csc_browse, 3, 2)
        grid.addWidget(self.odin_ums_label, 4, 0); grid.addWidget(self.odin_ums_input, 4, 1); grid.addWidget(self.odin_ums_browse, 4, 2)
        layout.addWidget(self.odin_files_group)

        # Options Group
        self.odin_options_group = QGroupBox(); grid = QGridLayout(self.odin_options_group)
        self.odin_erase_check = QCheckBox()
        self.odin_reboot_check = QCheckBox()
        self.odin_redownload_check = QCheckBox()
        grid.addWidget(self.odin_erase_check, 0, 0)
        grid.addWidget(self.odin_reboot_check, 0, 1)
        grid.addWidget(self.odin_redownload_check, 0, 2)
        layout.addWidget(self.odin_options_group)
        
        # Device Group
        self.odin_device_group = QGroupBox(); grid = QGridLayout(self.odin_device_group)
        self.odin_device_label = QLabel(); self.odin_device_combo = QComboBox()
        self.odin_refresh_devices_btn = QPushButton(); self.odin_refresh_devices_btn.clicked.connect(self.update_odin_device_list)
        grid.addWidget(self.odin_device_label, 0, 0); grid.addWidget(self.odin_device_combo, 0, 1)
        grid.addWidget(self.odin_refresh_devices_btn, 0, 2)
        layout.addWidget(self.odin_device_group)

        # Flash Button
        self.odin_flash_btn = self.create_run_button("odin_flash")
        self.odin_flash_btn.setStyleSheet("background-color: #f44336;")
        layout.addWidget(self.odin_flash_btn)

        layout.addStretch()
        return tab

    def create_scrcpy_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        self.scrcpy_group = QGroupBox(); grid = QGridLayout(self.scrcpy_group)
        
        self.scrcpy_start_btn = self.create_run_button("scrcpy_start")
        grid.addWidget(self.scrcpy_start_btn, 0, 0, 1, 2)

        self.scrcpy_bitrate_label = QLabel(); self.scrcpy_bitrate_combo = QComboBox()
        self.scrcpy_bitrate_combo.addItems(["Default", "8M", "4M", "2M", "1M"])
        self.scrcpy_bitrate_combo.setEditable(True)
        grid.addWidget(self.scrcpy_bitrate_label, 1, 0); grid.addWidget(self.scrcpy_bitrate_combo, 1, 1)

        self.scrcpy_resolution_label = QLabel(); self.scrcpy_resolution_combo = QComboBox()
        self.scrcpy_resolution_combo.addItems(["Default", "1920", "1280", "1024", "800"])
        self.scrcpy_resolution_combo.setEditable(True)
        grid.addWidget(self.scrcpy_resolution_label, 2, 0); grid.addWidget(self.scrcpy_resolution_combo, 2, 1)

        self.scrcpy_show_touches_check = QCheckBox()
        self.scrcpy_stay_awake_check = QCheckBox()
        grid.addWidget(self.scrcpy_show_touches_check, 3, 0)
        grid.addWidget(self.scrcpy_stay_awake_check, 3, 1)
        
        layout.addWidget(self.scrcpy_group)
        layout.addStretch()
        return tab

    def create_logcat_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        hbox = QHBoxLayout()
        self.logcat_start_btn = QPushButton(); self.logcat_start_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        self.logcat_start_btn.clicked.connect(self.start_logcat)
        self.logcat_stop_btn = QPushButton(); self.logcat_stop_btn.setIcon(QIcon.fromTheme("media-playback-stop"))
        self.logcat_stop_btn.clicked.connect(self.stop_logcat); self.logcat_stop_btn.setEnabled(False)
        self.logcat_filter_label = QLabel()
        self.logcat_filter_input = QLineEdit()
        hbox.addWidget(self.logcat_start_btn); hbox.addWidget(self.logcat_stop_btn)
        hbox.addWidget(self.logcat_filter_label); hbox.addWidget(self.logcat_filter_input)
        layout.addLayout(hbox)
        
        self.logcat_output = QTextEdit(); self.logcat_output.setReadOnly(True)
        self.logcat_output.setFont(QFont("monospace", 9))
        layout.addWidget(self.logcat_output)
        
        self.logcat_process.readyReadStandardOutput.connect(self.handle_logcat_output)
        return tab

    def create_adb_debloat_tab(self):
        tab = QWidget(); layout = QHBoxLayout(tab)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_widget = QWidget(); left_layout = QVBoxLayout(left_widget)
        self.debloat_list_btn = QPushButton(); self.debloat_list_btn.clicked.connect(self.list_packages_for_debloat)
        self.debloat_pkg_list = QListWidget(); self.debloat_pkg_list.itemSelectionChanged.connect(self.debloat_package_selected)
        left_layout.addWidget(self.debloat_list_btn); left_layout.addWidget(self.debloat_pkg_list)
        
        right_widget = QWidget(); right_layout = QVBoxLayout(right_widget)
        self.debloat_selected_pkg_label = QLabel("<i>...</i>")
        self.debloat_disable_btn = self.create_run_button("debloat_disable"); self.debloat_disable_btn.setEnabled(False)
        self.debloat_enable_btn = self.create_run_button("debloat_enable"); self.debloat_enable_btn.setEnabled(False)
        right_layout.addWidget(self.debloat_selected_pkg_label); right_layout.addWidget(self.debloat_disable_btn); right_layout.addWidget(self.debloat_enable_btn)
        right_layout.addStretch()

        splitter.addWidget(left_widget); splitter.addWidget(right_widget)
        splitter.setSizes([400, 200])
        layout.addWidget(splitter)
        return tab

    def create_adb_diagnostics_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        # Bug Report
        self.bugreport_group = QGroupBox(); hbox = QHBoxLayout(self.bugreport_group)
        self.bugreport_btn = self.create_run_button("bugreport")
        hbox.addWidget(self.bugreport_btn); layout.addWidget(self.bugreport_group)
        # Battery
        self.battery_group = QGroupBox(); grid = QGridLayout(self.battery_group)
        self.battery_fetch_btn = QPushButton(); self.battery_fetch_btn.clicked.connect(self.fetch_battery_stats)
        self.battery_info_label = QLabel("<i>...</i>")
        self.battery_info_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        grid.addWidget(self.battery_fetch_btn, 0, 0); grid.addWidget(self.battery_info_label, 0, 1, 5, 1)
        layout.addWidget(self.battery_group)
        # WM
        self.wm_group = QGroupBox(); grid = QGridLayout(self.wm_group)
        self.wm_size_label = QLabel(); self.wm_size_input = QLineEdit()
        self.wm_density_label = QLabel(); self.wm_density_input = QLineEdit()
        self.wm_set_btn = self.create_run_button("wm_set")
        self.wm_reset_btn = self.create_run_button("wm_reset")
        grid.addWidget(self.wm_size_label, 0, 0); grid.addWidget(self.wm_size_input, 0, 1)
        grid.addWidget(self.wm_density_label, 1, 0); grid.addWidget(self.wm_density_input, 1, 1)
        grid.addWidget(self.wm_set_btn, 2, 0); grid.addWidget(self.wm_reset_btn, 2, 1)
        layout.addWidget(self.wm_group)
        layout.addStretch()
        return tab
        
    # --- Metoder för att skapa varje ADB-flik ---
    def create_adb_file_transfer_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        self.push_group = QGroupBox(); grid = QGridLayout(self.push_group)
        self.push_local_label = QLabel(); self.push_local_input = DropLineEdit()
        self.push_browse_btn = QPushButton(); self.push_browse_btn.clicked.connect(lambda: self.browse_file(self.push_local_input))
        self.push_remote_label = QLabel(); self.push_remote_input = QLineEdit("/sdcard/Download/")
        self.push_run_btn = self.create_run_button("push")
        grid.addWidget(self.push_local_label, 0, 0); grid.addWidget(self.push_local_input, 0, 1)
        grid.addWidget(self.push_browse_btn, 0, 2); grid.addWidget(self.push_remote_label, 1, 0)
        grid.addWidget(self.push_remote_input, 1, 1); grid.addWidget(self.push_run_btn, 2, 1, 1, 2)
        layout.addWidget(self.push_group)
        
        self.pull_group = QGroupBox(); grid = QGridLayout(self.pull_group)
        self.pull_remote_label = QLabel(); self.pull_remote_input = QLineEdit()
        self.pull_local_label = QLabel(); self.pull_local_input = DropLineEdit()
        self.pull_browse_btn = QPushButton(); self.pull_browse_btn.clicked.connect(lambda: self.browse_save_location(self.pull_local_input))
        self.pull_run_btn = self.create_run_button("pull")
        grid.addWidget(self.pull_remote_label, 0, 0); grid.addWidget(self.pull_remote_input, 0, 1)
        grid.addWidget(self.pull_local_label, 1, 0); grid.addWidget(self.pull_local_input, 1, 1)
        grid.addWidget(self.pull_browse_btn, 1, 2); grid.addWidget(self.pull_run_btn, 2, 1, 1, 2)
        layout.addWidget(self.pull_group)
        
        self.sideload_group = QGroupBox(); grid = QGridLayout(self.sideload_group)
        self.sideload_label = QLabel(); self.sideload_input = DropLineEdit()
        self.sideload_browse_btn = QPushButton(); self.sideload_browse_btn.clicked.connect(lambda: self.browse_file(self.sideload_input))
        self.sideload_run_btn = self.create_run_button("sideload")
        grid.addWidget(self.sideload_label, 0, 0); grid.addWidget(self.sideload_input, 0, 1)
        grid.addWidget(self.sideload_browse_btn, 0, 2); grid.addWidget(self.sideload_run_btn, 1, 1, 1, 2)
        layout.addWidget(self.sideload_group)
        layout.addStretch()
        return tab

    def create_adb_app_management_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        self.install_group = QGroupBox(); grid = QGridLayout(self.install_group)
        self.install_apk_label = QLabel(); self.install_apk_input = DropLineEdit()
        self.install_browse_btn = QPushButton(); self.install_browse_btn.clicked.connect(lambda: self.browse_file(self.install_apk_input))
        self.install_run_btn = self.create_run_button("install")
        self.install_reinstall_check = QCheckBox(); self.install_grant_perms_check = QCheckBox()
        grid.addWidget(self.install_apk_label, 0, 0); grid.addWidget(self.install_apk_input, 0, 1)
        grid.addWidget(self.install_browse_btn, 0, 2); grid.addWidget(self.install_reinstall_check, 1, 1)
        grid.addWidget(self.install_grant_perms_check, 2, 1); grid.addWidget(self.install_run_btn, 3, 1, 1, 2)
        layout.addWidget(self.install_group)
        
        self.uninstall_group = QGroupBox(); grid = QGridLayout(self.uninstall_group)
        self.uninstall_pkg_label = QLabel(); self.uninstall_pkg_input = QLineEdit()
        self.uninstall_run_btn = self.create_run_button("uninstall")
        self.uninstall_keep_data_check = QCheckBox()
        grid.addWidget(self.uninstall_pkg_label, 0, 0); grid.addWidget(self.uninstall_pkg_input, 0, 1)
        grid.addWidget(self.uninstall_keep_data_check, 1, 1); grid.addWidget(self.uninstall_run_btn, 2, 1)
        layout.addWidget(self.uninstall_group)

        self.list_packages_group = QGroupBox(); list_layout = QVBoxLayout(self.list_packages_group)
        self.list_pkgs_btn = QPushButton(); self.list_pkgs_btn.clicked.connect(self.list_installed_packages)
        list_layout.addWidget(self.list_pkgs_btn)
        layout.addWidget(self.list_packages_group)
        layout.addStretch()
        return tab

    def create_adb_device_control_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        self.adb_reboot_group = QGroupBox(); grid = QGridLayout(self.adb_reboot_group)
        self.adb_reboot_label = QLabel(); self.adb_reboot_combo = QComboBox()
        self.adb_reboot_combo.addItems(["System", "Bootloader", "Recovery", "Sideload"])
        self.adb_reboot_run_btn = self.create_run_button("reboot")
        grid.addWidget(self.adb_reboot_label, 0, 0); grid.addWidget(self.adb_reboot_combo, 0, 1)
        grid.addWidget(self.adb_reboot_run_btn, 0, 2)
        layout.addWidget(self.adb_reboot_group)
        
        self.root_access_group = QGroupBox(); hbox = QHBoxLayout(self.root_access_group)
        self.root_btn = self.create_run_button("root"); self.unroot_btn = self.create_run_button("unroot")
        hbox.addWidget(self.root_btn); hbox.addWidget(self.unroot_btn)
        layout.addWidget(self.root_access_group)
        
        self.screenshot_group = QGroupBox(); hbox = QHBoxLayout(self.screenshot_group)
        self.screenshot_btn = QPushButton(); self.screenshot_btn.setIcon(QIcon.fromTheme("applets-screenshooter"))
        self.screenshot_btn.clicked.connect(self.take_screenshot)
        hbox.addWidget(self.screenshot_btn)
        layout.addWidget(self.screenshot_group)

        self.screenrecord_group = QGroupBox(); hbox = QHBoxLayout(self.screenrecord_group)
        self.screenrecord_btn = QPushButton(); self.screenrecord_btn.setIcon(QIcon.fromTheme("media-record"))
        self.screenrecord_btn.clicked.connect(self.toggle_screen_recording)
        hbox.addWidget(self.screenrecord_btn)
        layout.addWidget(self.screenrecord_group)
        
        self.shell_group = QGroupBox(); grid = QGridLayout(self.shell_group)
        self.shell_label = QLabel(); self.shell_command_input = QLineEdit()
        self.shell_run_btn = self.create_run_button("shell")
        grid.addWidget(self.shell_label, 0, 0); grid.addWidget(self.shell_command_input, 0, 1)
        grid.addWidget(self.shell_run_btn, 0, 2)
        layout.addWidget(self.shell_group)
        layout.addStretch()
        return tab

    def create_adb_device_info_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        self.get_info_btn = QPushButton(); self.get_info_btn.clicked.connect(self.fetch_device_info)
        layout.addWidget(self.get_info_btn)
        self.info_layout = QGridLayout(); layout.addLayout(self.info_layout)
        self.info_labels_map = {
            "model": "ro.product.model", "manufacturer": "ro.product.manufacturer",
            "android_version": "ro.build.version.release", "sdk_version": "ro.build.version.sdk",
            "build_id": "ro.build.display.id"
        }
        self.info_widgets = {}
        for i, (key, _) in enumerate(self.info_labels_map.items()):
            name_label = QLabel(); name_label.setObjectName(f"info_name_{key}")
            value_label = QLabel(); value_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            self.info_layout.addWidget(name_label, i, 0)
            self.info_layout.addWidget(value_label, i, 1)
            self.info_widgets[key] = (name_label, value_label)
        layout.addStretch()
        return tab

    def create_adb_networking_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        self.tcpip_group = QGroupBox(); grid = QGridLayout(self.tcpip_group)
        self.tcpip_port_label = QLabel(); self.tcpip_port_input = QLineEdit("5555")
        self.tcpip_run_btn = self.create_run_button("tcpip")
        grid.addWidget(self.tcpip_port_label, 0, 0); grid.addWidget(self.tcpip_port_input, 0, 1)
        grid.addWidget(self.tcpip_run_btn, 0, 2)
        layout.addWidget(self.tcpip_group)
        
        self.connect_group = QGroupBox(); grid = QGridLayout(self.connect_group)
        self.connect_ip_label = QLabel(); self.connect_ip_input = QLineEdit()
        self.connect_run_btn = self.create_run_button("connect")
        grid.addWidget(self.connect_ip_label, 0, 0); grid.addWidget(self.connect_ip_input, 0, 1)
        grid.addWidget(self.connect_run_btn, 0, 2)
        layout.addWidget(self.connect_group)
        
        self.disconnect_group = QGroupBox(); grid = QGridLayout(self.disconnect_group)
        self.disconnect_ip_label = QLabel(); self.disconnect_ip_input = QLineEdit()
        self.disconnect_run_btn = self.create_run_button("disconnect")
        grid.addWidget(self.disconnect_ip_label, 0, 0); grid.addWidget(self.disconnect_ip_input, 0, 1)
        grid.addWidget(self.disconnect_run_btn, 0, 2)
        layout.addWidget(self.disconnect_group)
        layout.addStretch()
        return tab

    # --- Metoder för att skapa Fastboot-flikar ---
    def create_flashing_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        self.flash_group = QGroupBox(); grid = QGridLayout(self.flash_group)
        self.flash_partition_label = QLabel(); self.flash_partition_combo = self.create_partition_combo()
        self.flash_file_label = QLabel(); self.flash_file_input = DropLineEdit()
        self.flash_browse_btn = QPushButton(); self.flash_browse_btn.clicked.connect(lambda: self.browse_file(self.flash_file_input))
        self.flash_run_btn = self.create_run_button("flash")
        grid.addWidget(self.flash_partition_label, 0, 0); grid.addWidget(self.flash_partition_combo, 0, 1)
        grid.addWidget(self.flash_file_label, 1, 0); grid.addWidget(self.flash_file_input, 1, 1)
        grid.addWidget(self.flash_browse_btn, 1, 2); grid.addWidget(self.flash_run_btn, 2, 1, 1, 2)
        layout.addWidget(self.flash_group)

        self.update_zip_group = QGroupBox(); grid = QGridLayout(self.update_zip_group)
        self.update_zip_label = QLabel(); self.update_zip_input = DropLineEdit()
        self.update_browse_btn = QPushButton(); self.update_browse_btn.clicked.connect(lambda: self.browse_file(self.update_zip_input))
        self.update_run_btn = self.create_run_button("update")
        grid.addWidget(self.update_zip_label, 0, 0); grid.addWidget(self.update_zip_input, 0, 1)
        grid.addWidget(self.update_browse_btn, 0, 2); grid.addWidget(self.update_run_btn, 1, 1, 1, 2)
        layout.addWidget(self.update_zip_group)

        self.flash_options_group = QGroupBox(); hbox = QHBoxLayout(self.flash_options_group)
        self.wipe_check = QCheckBox(); self.skip_reboot_check = QCheckBox()
        hbox.addWidget(self.wipe_check); hbox.addWidget(self.skip_reboot_check)
        layout.addWidget(self.flash_options_group)
        layout.addStretch()
        return tab

    def create_basic_actions_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        self.fb_reboot_group = QGroupBox(); grid = QGridLayout(self.fb_reboot_group)
        self.fb_reboot_label = QLabel(); self.reboot_combo = QComboBox()
        self.reboot_run_btn = self.create_run_button("reboot_fb")
        grid.addWidget(self.fb_reboot_label, 0, 0); grid.addWidget(self.reboot_combo, 0, 1)
        grid.addWidget(self.reboot_run_btn, 0, 2)
        layout.addWidget(self.fb_reboot_group)

        self.locking_group = QGroupBox(); grid = QGridLayout(self.locking_group)
        self.unlock_btn = self.create_run_button("unlock"); self.lock_btn = self.create_run_button("lock")
        self.unlock_crit_btn = self.create_run_button("unlock_critical"); self.lock_crit_btn = self.create_run_button("lock_critical")
        grid.addWidget(self.unlock_btn, 0, 0); grid.addWidget(self.lock_btn, 0, 1)
        grid.addWidget(self.unlock_crit_btn, 1, 0); grid.addWidget(self.lock_crit_btn, 1, 1)
        layout.addWidget(self.locking_group)

        self.slot_group = QGroupBox(); grid = QGridLayout(self.slot_group)
        self.slot_label = QLabel(); self.set_active_combo = QComboBox(); self.set_active_combo.addItems(["a", "b"])
        self.set_active_btn = self.create_run_button("set_active")
        grid.addWidget(self.slot_label, 0, 0); grid.addWidget(self.set_active_combo, 0, 1)
        grid.addWidget(self.set_active_btn, 0, 2)
        layout.addWidget(self.slot_group)
        layout.addStretch()
        return tab

    def create_partitions_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        self.erase_group = QGroupBox(); grid = QGridLayout(self.erase_group)
        self.erase_label = QLabel(); self.erase_partition_combo = self.create_partition_combo()
        self.erase_btn = self.create_run_button("erase")
        grid.addWidget(self.erase_label, 0, 0); grid.addWidget(self.erase_partition_combo, 0, 1)
        grid.addWidget(self.erase_btn, 0, 2)
        layout.addWidget(self.erase_group)

        self.wipe_super_group = QGroupBox(); hbox = QHBoxLayout(self.wipe_super_group)
        self.wipe_super_btn = self.create_run_button("wipe-super")
        hbox.addWidget(self.wipe_super_btn)
        layout.addWidget(self.wipe_super_group)
        layout.addStretch()
        return tab

    def create_advanced_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        self.boot_group = QGroupBox(); grid = QGridLayout(self.boot_group)
        self.boot_file_label = QLabel(); self.boot_file_input = DropLineEdit()
        self.boot_browse_btn = QPushButton(); self.boot_browse_btn.clicked.connect(lambda: self.browse_file(self.boot_file_input))
        self.boot_run_btn = self.create_run_button("boot")
        grid.addWidget(self.boot_file_label, 0, 0); grid.addWidget(self.boot_file_input, 0, 1)
        grid.addWidget(self.boot_browse_btn, 0, 2); grid.addWidget(self.boot_run_btn, 1, 1, 1, 2)
        layout.addWidget(self.boot_group)

        self.getvar_group = QGroupBox(); grid = QGridLayout(self.getvar_group)
        self.getvar_label = QLabel(); self.getvar_combo = QComboBox()
        self.getvar_combo.addItems(["all", "product", "version", "serialno", "version-bootloader", "partition-size:boot"])
        self.getvar_combo.setEditable(True)
        self.getvar_btn = self.create_run_button("getvar")
        grid.addWidget(self.getvar_label, 0, 0); grid.addWidget(self.getvar_combo, 0, 1)
        grid.addWidget(self.getvar_btn, 0, 2)
        layout.addWidget(self.getvar_group)
        layout.addStretch()
        return tab
    
    # --- Nya funktioner (Definitioner) ---
    def start_logcat(self):
        self.logcat_output.clear()
        self.logcat_start_btn.setEnabled(False); self.logcat_stop_btn.setEnabled(True)
        command = self.build_command(self.adb_path, ["logcat"])
        self.logcat_process.start(command[0], command[1:])

    def stop_logcat(self):
        self.logcat_process.kill()
        self.logcat_start_btn.setEnabled(True); self.logcat_stop_btn.setEnabled(False)

    def handle_logcat_output(self):
        data = self.logcat_process.readAllStandardOutput().data().decode(errors='ignore')
        filter_text = self.logcat_filter_input.text().lower()
        cursor = self.logcat_output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        for line in data.splitlines():
            if filter_text and filter_text not in line.lower():
                continue
            
            color = "#f0f0f0"
            if re.search(r'\sE\s', line): color = "#ff7f7f"
            elif re.search(r'\sW\s', line): color = "#ffff7f"
            elif re.search(r'\sI\s', line): color = "#7fff7f"
            elif re.search(r'\sD\s', line): color = "#7fbfff"
            
            cursor.insertHtml(f"<span style='color: {color}; white-space: pre;'>{line}</span><br>")
        self.logcat_output.ensureCursorVisible()

    def list_packages_for_debloat(self):
        self.debloat_pkg_list.clear()
        try:
            command = self.build_command(self.adb_path, ["shell", "pm", "list", "packages", "-f"])
            result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
            for line in result.stdout.splitlines():
                path, package = line.replace("package:", "").split("=")
                item = QListWidgetItem(package)
                item.setData(Qt.ItemDataRole.UserRole, path)
                self.debloat_pkg_list.addItem(item)
        except Exception as e:
            self.show_error(f"Failed to list packages: {e}")

    def debloat_package_selected(self):
        items = self.debloat_pkg_list.selectedItems()
        if items:
            self.debloat_selected_pkg_label.setText(items[0].text())
            self.debloat_disable_btn.setEnabled(True)
            self.debloat_enable_btn.setEnabled(True)
        else:
            self.debloat_selected_pkg_label.setText("<i>...</i>")
            self.debloat_disable_btn.setEnabled(False)
            self.debloat_enable_btn.setEnabled(False)
            
    def fetch_battery_stats(self):
        try:
            command = self.build_command(self.adb_path, ["shell", "dumpsys", "battery"])
            result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
            
            level = re.search(r'level: (\d+)', result.stdout)
            temp = re.search(r'temperature: (\d+)', result.stdout)
            health = re.search(r'health: (\d+)', result.stdout)
            
            level_str = f"Level: {level.group(1)}%" if level else "N/A"
            temp_str = f"Temp: {int(temp.group(1))/10.0}°C" if temp else "N/A"
            health_map = {"2": "Good", "3": "Overheat", "4": "Dead", "7": "Cold"}
            health_str = f"Health: {health_map.get(health.group(1), 'Unknown')}" if health else "N/A"
            
            self.battery_info_label.setText(f"{level_str}\n{temp_str}\n{health_str}")

        except Exception as e:
            self.battery_info_label.setText("<i>Failed to fetch</i>")
            self.show_error(f"Failed to get battery stats: {e}")

    def add_heimdall_partition(self):
        row = self.heimdall_parts_table.rowCount()
        self.heimdall_parts_table.insertRow(row)

        combo = QComboBox()
        combo.addItems(self.common_partitions)
        combo.setEditable(True)
        self.heimdall_parts_table.setCellWidget(row, 0, combo)

        line_edit = DropLineEdit()
        self.heimdall_parts_table.setCellWidget(row, 1, line_edit)

        browse_btn = QPushButton(self.get_string("browse"))
        browse_btn.clicked.connect(lambda _, le=line_edit: self.browse_file(le))
        self.heimdall_parts_table.setCellWidget(row, 2, browse_btn)

    def remove_heimdall_partition(self):
        current_row = self.heimdall_parts_table.currentRow()
        if current_row >= 0:
            self.heimdall_parts_table.removeRow(current_row)

    def load_spft_scatter_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, self.get_string("spft_scatter_browse_btn"), "", "Scatter Files (*.txt);;All Files (*)")
        if not file_path: return
        
        self.spft_scatter_input.setText(file_path)
        self.spft_parts_table.setRowCount(0)
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    match = re.search(r'partition_name:\s*(\w+)', line)
                    if match:
                        partition_name = match.group(1)
                        row = self.spft_parts_table.rowCount()
                        self.spft_parts_table.insertRow(row)
                        
                        check_item = QTableWidgetItem()
                        check_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                        check_item.setCheckState(Qt.CheckState.Unchecked)
                        self.spft_parts_table.setItem(row, 0, check_item)

                        name_item = QTableWidgetItem(partition_name)
                        name_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                        self.spft_parts_table.setItem(row, 1, name_item)
        except Exception as e:
            self.show_error(f"Could not parse scatter file: {e}")

    # --- Språk och Tema ---
    def init_translations(self):
        self.translations = {
            # Keys must be unique
            "main_title": {"sv": "Android Verktygslåda", "en": "Android Toolbox"},
            # Menus
            "file_menu": {"sv": "&Arkiv", "en": "&File"},
            "settings": {"sv": "Inställningar...", "en": "Settings..."},
            "exit": {"sv": "Avsluta", "en": "Exit"},
            "view_menu": {"sv": "&Utseende", "en": "&View"},
            "themes": {"sv": "Teman", "en": "Themes"},
            "lang_menu": {"sv": "&Språk", "en": "&Language"},
            "help_menu": {"sv": "&Hjälp", "en": "&Help"},
            "about": {"sv": "Om...", "en": "About..."},
            # Global
            "device_group": {"sv": "Globala Enhetsinställningar", "en": "Global Device Settings"},
            "device_select_label": {"sv": "Välj enhet:", "en": "Select Device:"},
            "serial_label": {"sv": "Serienummer (-s):", "en": "Serial Number (-s):"},
            "serial_placeholder": {"sv": "Valfritt, fylls i automatiskt", "en": "Optional, filled automatically"},
            "refresh_devices_btn": {"sv": "Uppdatera Enhetslista", "en": "Refresh Device List"},
            "execution_group": {"sv": "Exekvering & Output", "en": "Execution & Output"},
            "command_preview_placeholder": {"sv": "Kommando som kommer köras visas här...", "en": "Command to be executed will be shown here..."},
            "clear_button": {"sv": "Rensa output", "en": "Clear Output"},
            "save_log_button": {"sv": "Spara Logg...", "en": "Save Log..."},
            # Statusbar
            "status_ready": {"sv": "Redo", "en": "Ready"},
            "status_running": {"sv": "Kör: {exe}...", "en": "Running: {exe}..."},
            "status_error": {"sv": "Fel inträffade", "en": "An error occurred"},
            "status_log_saved": {"sv": "Loggen sparades!", "en": "Log saved!"},
            "status_settings_saved": {"sv": "Inställningar sparade.", "en": "Settings saved."},
            "status_recording": {"sv": "Spelar in skärmen...", "en": "Recording screen..."},
            "status_pulling_video": {"sv": "Hämtar video...", "en": "Pulling video..."},
            "status_video_saved": {"sv": "Video sparad!", "en": "Video saved!"},
            # Generic
            "browse": {"sv": "Bläddra...", "en": "Browse..."},
            "run": {"sv": "Kör", "en": "Run"},
            # Main Tabs
            "xiaomi_tab": {"sv": "Xiaomi", "en": "Xiaomi"},
            "edl_tab": {"sv": "Qualcomm EDL", "en": "Qualcomm EDL"},
            "heimdall_tab": {"sv": "Heimdall", "en": "Heimdall"},
            "spft_tab": {"sv": "SP Flash Tool", "en": "SP Flash Tool"},
            "odin_tab": {"sv": "Odin", "en": "Odin"},
            "scrcpy_tab": {"sv": "Skärmspegling", "en": "Screen Mirror"},
            "logcat_tab": {"sv": "Logcat", "en": "Logcat"},
            # ADB Tabs
            "adb_tab_file": {"sv": "Filöverföring", "en": "File Transfer"},
            "adb_tab_app": {"sv": "Apphantering", "en": "App Management"},
            "adb_tab_control": {"sv": "Enhetskontroll", "en": "Device Control"},
            "adb_tab_info": {"sv": "Enhetsinformation", "en": "Device Information"},
            "adb_tab_net": {"sv": "Nätverk", "en": "Networking"},
            "adb_tab_debloat": {"sv": "Debloat", "en": "Debloat"},
            "adb_tab_diagnostics": {"sv": "Diagnostik", "en": "Diagnostics"},
            # Fastboot Tabs
            "fb_tab_flash": {"sv": "Flashning", "en": "Flashing"},
            "fb_tab_basic": {"sv": "Grundläggande", "en": "Basic Actions"},
            "fb_tab_part": {"sv": "Partitioner", "en": "Partitions"},
            "fb_tab_adv": {"sv": "Avancerat", "en": "Advanced"},
            # Xiaomi Tab
            "xiaomi_group": {"sv": "Xiaomi Fastboot ROM Flash", "en": "Xiaomi Fastboot ROM Flash"},
            "xiaomi_file_label": {"sv": "Firmware (.tgz):", "en": "Firmware (.tgz):"},
            "xiaomi_flash_all_btn": {"sv": "Flash All (Rensar data)", "en": "Flash All (Wipes data)"},
            "xiaomi_flash_except_storage_btn": {"sv": "Flash All Except Storage (Behåller data)", "en": "Flash All Except Storage (Keeps data)"},
            "xiaomi_flash_lock_btn": {"sv": "Flash All and Lock (Rensar data & låser)", "en": "Flash All and Lock (Wipes data & locks)"},
            # EDL Tab
            "edl_actions_group": {"sv": "Grundläggande kommandon", "en": "Basic Commands"},
            "edl_reboot_btn": {"sv": "Starta om till EDL", "en": "Reboot to EDL"},
            "edl_printgpt_btn": {"sv": "Visa partitionstabell", "en": "Print Partition Table"},
            "edl_reset_btn": {"sv": "Starta om enhet", "en": "Reset Device"},
            "edl_qfil_group": {"sv": "QFIL Flash (Unbrick)", "en": "QFIL Flash (Unbrick)"},
            "edl_loader_label": {"sv": "Loader/Firehose:", "en": "Loader/Firehose:"},
            "edl_rawprogram_label": {"sv": "Rawprogram XML:", "en": "Rawprogram XML:"},
            "edl_patch_label": {"sv": "Patch XML:", "en": "Patch XML:"},
            "edl_imagedir_label": {"sv": "Mapp med images:", "en": "Image Directory:"},
            "edl_qfil_flash_btn": {"sv": "Starta QFIL Flash", "en": "Start QFIL Flash"},
            # Heimdall Tab
            "heimdall_actions_group": {"sv": "Åtgärder", "en": "Actions"},
            "heimdall_detect_btn": {"sv": "Hitta enhet", "en": "Detect Device"},
            "heimdall_pit_btn": {"sv": "Hämta & visa PIT", "en": "Print PIT"},
            "heimdall_download_pit_btn": {"sv": "Spara PIT till fil...", "en": "Save PIT to File..."},
            "heimdall_parts_group": {"sv": "Partitioner att flasha", "en": "Partitions to Flash"},
            "heimdall_options_group": {"sv": "Alternativ", "en": "Options"},
            "heimdall_repartition_check": {"sv": "Repartition", "en": "Repartition"},
            "heimdall_no_reboot_check": {"sv": "Starta inte om", "en": "No Reboot"},
            "heimdall_tflash_check": {"sv": "Flash till SD-kort", "en": "Flash to SD-Card"},
            "heimdall_skip_size_check": {"sv": "Hoppa över storlekskoll", "en": "Skip Size Check"},
            "heimdall_flash_btn": {"sv": "Starta Heimdall Flash", "en": "Start Heimdall Flash"},
            # SPFT Tab
            "spft_files_group": {"sv": "Filer", "en": "Files"},
            "spft_scatter_label": {"sv": "Scatter-fil:", "en": "Scatter File:"},
            "spft_da_label": {"sv": "Download Agent:", "en": "Download Agent:"},
            "spft_scatter_browse_btn": {"sv": "Ladda Scatter-fil...", "en": "Load Scatter File..."},
            "spft_options_group": {"sv": "Alternativ", "en": "Options"},
            "spft_battery_label": {"sv": "Batteriläge:", "en": "Battery Mode:"},
            "spft_com_label": {"sv": "COM Port (valfritt):", "en": "COM Port (optional):"},
            "spft_reboot_check": {"sv": "Starta om enhet", "en": "Reboot device"},
            "spft_actions_group": {"sv": "Flash-läge", "en": "Flash Mode"},
            "spft_dl_btn": {"sv": "Download Only", "en": "Download Only"},
            "spft_fu_btn": {"sv": "Firmware Upgrade", "en": "Firmware Upgrade"},
            "spft_fa_btn": {"sv": "Format All + Download", "en": "Format All + Download"},
            # Odin Tab
            "odin_files_group": {"sv": "Firmware-filer", "en": "Firmware Files"},
            "odin_options_group": {"sv": "Alternativ", "en": "Options"},
            "odin_erase_check": {"sv": "Nand Erase", "en": "Nand Erase"},
            "odin_reboot_check": {"sv": "Starta om efteråt", "en": "Reboot when finished"},
            "odin_redownload_check": {"sv": "Starta om till Download Mode", "en": "Reboot to Download Mode"},
            "odin_device_group": {"sv": "Odin-enhet", "en": "Odin Device"},
            "odin_device_label": {"sv": "Målenhet:", "en": "Target Device:"},
            "odin_refresh_devices_btn": {"sv": "Hitta Odin-enheter", "en": "Find Odin Devices"},
            "odin_flash_btn": {"sv": "Starta Flashning (Riskfyllt!)", "en": "Start Flashing (Risky!)"},
            # scrcpy
            "scrcpy_group": {"sv": "scrcpy Inställningar", "en": "scrcpy Settings"},
            "scrcpy_start_btn": {"sv": "Starta Skärmspegling", "en": "Start Screen Mirroring"},
            "scrcpy_bitrate_label": {"sv": "Bitrate:", "en": "Bitrate:"},
            "scrcpy_resolution_label": {"sv": "Max upplösning:", "en": "Max Resolution:"},
            "scrcpy_show_touches_check": {"sv": "Visa tryckpunkter", "en": "Show touches"},
            "scrcpy_stay_awake_check": {"sv": "Håll skärmen vaken", "en": "Stay awake"},
            # Logcat
            "logcat_filter_label": {"sv": "Filter:", "en": "Filter:"},
            # Debloat
            "debloat_list_btn": {"sv": "Läs in paketlista", "en": "Load Package List"},
            "debloat_disable_btn": {"sv": "Inaktivera vald app", "en": "Disable Selected App"},
            "debloat_enable_btn": {"sv": "Aktivera vald app", "en": "Enable Selected App"},
            # Diagnostics
            "bugreport_group": {"sv": "Buggrapport", "en": "Bug Report"},
            "bugreport_btn": {"sv": "Hämta buggrapport till datorn", "en": "Fetch bug report to computer"},
            "battery_group": {"sv": "Batteristatus", "en": "Battery Status"},
            "battery_fetch_btn": {"sv": "Hämta status", "en": "Fetch Status"},
            "wm_group": {"sv": "Skärmhanterare (WM)", "en": "Window Manager (WM)"},
            "wm_size_label": {"sv": "Storlek (t.ex. 1080x1920):", "en": "Size (e.g. 1080x1920):"},
            "wm_density_label": {"sv": "Densitet (t.ex. 420):", "en": "Density (e.g. 420):"},
            "wm_set_btn": {"sv": "Använd", "en": "Apply"},
            "wm_reset_btn": {"sv": "Återställ", "en": "Reset"},
            # ADB File Transfer
            "push_group": {"sv": "Skicka fil (adb push)", "en": "Send File (adb push)"},
            "push_local_label": {"sv": "Lokal fil:", "en": "Local File:"},
            "push_remote_label": {"sv": "Mål på enhet:", "en": "Device Destination:"},
            "push_run_btn": {"sv": "Skicka (Push)", "en": "Send (Push)"},
            "pull_group": {"sv": "Hämta fil (adb pull)", "en": "Get File (adb pull)"},
            "pull_remote_label": {"sv": "Fil på enhet:", "en": "File on Device:"},
            "pull_local_label": {"sv": "Spara lokalt som:", "en": "Save Locally As:"},
            "pull_run_btn": {"sv": "Hämta (Pull)", "en": "Get (Pull)"},
            "sideload_group": {"sv": "OTA Sideload (adb sideload)", "en": "OTA Sideload (adb sideload)"},
            "sideload_label": {"sv": "OTA-paket (.zip):", "en": "OTA Package (.zip):"},
            "sideload_run_btn": {"sv": "Starta Sideload", "en": "Start Sideload"},
            # ADB App Management
            "install_group": {"sv": "Installera App (adb install)", "en": "Install App (adb install)"},
            "install_apk_label": {"sv": "APK-fil:", "en": "APK File:"},
            "install_reinstall_check": {"sv": "Ominstallera (-r)", "en": "Reinstall (-r)"},
            "install_grant_perms_check": {"sv": "Ge alla rättigheter (-g)", "en": "Grant all permissions (-g)"},
            "install_run_btn": {"sv": "Installera App", "en": "Install App"},
            "uninstall_group": {"sv": "Avinstallera App (adb uninstall)", "en": "Uninstall App (adb uninstall)"},
            "uninstall_pkg_label": {"sv": "Paketnamn:", "en": "Package Name:"},
            "uninstall_keep_data_check": {"sv": "Behåll data/cache (-k)", "en": "Keep data/cache (-k)"},
            "uninstall_run_btn": {"sv": "Avinstallera App", "en": "Uninstall App"},
            "list_packages_group": {"sv": "Lista Appar", "en": "List Apps"},
            "list_pkgs_btn": {"sv": "Lista alla installerade paket", "en": "List all installed packages"},
            # ADB Device Control
            "adb_reboot_group": {"sv": "Omstart (adb reboot)", "en": "Reboot (adb reboot)"},
            "adb_reboot_label": {"sv": "Starta om till:", "en": "Reboot to:"},
            "adb_reboot_run_btn": {"sv": "Starta om", "en": "Reboot"},
            "root_access_group": {"sv": "Root-åtkomst", "en": "Root Access"},
            "root_btn": {"sv": "Aktivera Root (adb root)", "en": "Enable Root (adb root)"},
            "unroot_btn": {"sv": "Avaktivera Root (adb unroot)", "en": "Disable Root (adb unroot)"},
            "screenshot_group": {"sv": "Skärmdump", "en": "Screenshot"},
            "screenshot_btn": {"sv": "Ta skärmdump och spara...", "en": "Take screenshot and save..."},
            "screenrecord_group": {"sv": "Skärminspelning", "en": "Screen Recording"},
            "screenrecord_start_btn": {"sv": "Starta inspelning", "en": "Start Recording"},
            "screenrecord_stop_btn": {"sv": "Stoppa & spara inspelning...", "en": "Stop & Save Recording..."},
            "shell_group": {"sv": "Kör Shell-kommando", "en": "Run Shell Command"},
            "shell_label": {"sv": "Kommando:", "en": "Command:"},
            "shell_run_btn": {"sv": "Kör Shell", "en": "Run Shell"},
            # ADB Device Info
            "get_info_btn": {"sv": "Hämta enhetsinformation", "en": "Fetch Device Information"},
            "info_name_model": {"sv": "<b>Modell:</b>", "en": "<b>Model:</b>"},
            "info_name_manufacturer": {"sv": "<b>Tillverkare:</b>", "en": "<b>Manufacturer:</b>"},
            "info_name_android_version": {"sv": "<b>Android-version:</b>", "en": "<b>Android Version:</b>"},
            "info_name_sdk_version": {"sv": "<b>SDK-version:</b>", "en": "<b>SDK Version:</b>"},
            "info_name_build_id": {"sv": "<b>Build-ID:</b>", "en": "<b>Build ID:</b>"},
            "info_waiting": {"sv": "<i>Väntar på data...</i>", "en": "<i>Waiting for data...</i>"},
            "info_failed": {"sv": "<i>Kunde inte hämta</i>", "en": "<i>Failed to fetch</i>"},
            # ADB Networking
            "tcpip_group": {"sv": "Nätverks-debug (adb tcpip)", "en": "Network Debugging (adb tcpip)"},
            "tcpip_port_label": {"sv": "Port:", "en": "Port:"},
            "tcpip_run_btn": {"sv": "Starta TCP/IP-läge", "en": "Start TCP/IP Mode"},
            "connect_group": {"sv": "Anslut till enhet (adb connect)", "en": "Connect to Device (adb connect)"},
            "connect_ip_label": {"sv": "IP-adress:", "en": "IP Address:"},
            "connect_run_btn": {"sv": "Anslut", "en": "Connect"},
            "disconnect_group": {"sv": "Koppla från enhet (adb disconnect)", "en": "Disconnect Device (adb disconnect)"},
            "disconnect_ip_label": {"sv": "IP-adress:", "en": "IP Address:"},
            "disconnect_run_btn": {"sv": "Koppla från", "en": "Disconnect"},
            # Fastboot Flashing
            "flash_group": {"sv": "Flash Partition (fastboot flash)", "en": "Flash Partition (fastboot flash)"},
            "flash_partition_label": {"sv": "Partition:", "en": "Partition:"},
            "flash_file_label": {"sv": "Image-fil:", "en": "Image File:"},
            "flash_run_btn": {"sv": "Flash Partition", "en": "Flash Partition"},
            "update_zip_group": {"sv": "Installera ZIP (fastboot update)", "en": "Install ZIP (fastboot update)"},
            "update_zip_label": {"sv": "ZIP-fil:", "en": "ZIP File:"},
            "update_run_btn": {"sv": "Installera ZIP", "en": "Install ZIP"},
            "flash_options_group": {"sv": "Flash-alternativ", "en": "Flash Options"},
            "wipe_check": {"sv": "Rensa användardata (-w)", "en": "Wipe user data (-w)"},
            "skip_reboot_check": {"sv": "Starta inte om efteråt", "en": "Don't reboot after"},
            # Fastboot Basic
            "fb_reboot_group": {"sv": "Omstart (reboot)", "en": "Reboot"},
            "fb_reboot_label": {"sv": "Starta om enhet:", "en": "Reboot device:"},
            "fb_reboot_run_btn": {"sv": "Starta om", "en": "Reboot"},
            "reboot_normal": {"sv": "Normalt", "en": "Normal"},
            "reboot_bootloader": {"sv": "Till Bootloader", "en": "To Bootloader"},
            "locking_group": {"sv": "Bootloader Lås/Upplåsning", "en": "Bootloader Lock/Unlock"},
            "unlock_btn": {"sv": "Lås upp", "en": "Unlock"},
            "lock_btn": {"sv": "Lås", "en": "Lock"},
            "unlock_crit_btn": {"sv": "Lås upp Kritiska", "en": "Unlock Critical"},
            "lock_crit_btn": {"sv": "Lås Kritiska", "en": "Lock Critical"},
            "slot_group": {"sv": "Hantera aktiv slot", "en": "Manage Active Slot"},
            "slot_label": {"sv": "Välj slot:", "en": "Select slot:"},
            "set_active_btn": {"sv": "Sätt aktiv slot", "en": "Set Active Slot"},
            # Fastboot Partitions
            "erase_group": {"sv": "Radera Partition (erase)", "en": "Erase Partition (erase)"},
            "erase_label": {"sv": "Partition att radera:", "en": "Partition to erase:"},
            "erase_btn": {"sv": "Radera Partition", "en": "Erase Partition"},
            "wipe_super_group": {"sv": "Återställ Super-partition", "en": "Wipe Super Partition"},
            "wipe_super_btn": {"sv": "Återställ Super", "en": "Wipe Super"},
            # Fastboot Advanced
            "boot_group": {"sv": "Temporär Boot (boot)", "en": "Temporary Boot (boot)"},
            "boot_file_label": {"sv": "Image-fil:", "en": "Image File:"},
            "boot_run_btn": {"sv": "Boota Image", "en": "Boot Image"},
            "getvar_group": {"sv": "Hämta variabel (getvar)", "en": "Get Variable (getvar)"},
            "getvar_label": {"sv": "Variabelnamn:", "en": "Variable Name:"},
            "getvar_btn": {"sv": "Hämta Variabel", "en": "Get Variable"},
            # Dialogs
            "settings_title": {"sv": "Inställningar", "en": "Settings"},
            "settings_adb_path": {"sv": "Sökväg till ADB:", "en": "Path to ADB:"},
            "settings_fastboot_path": {"sv": "Sökväg till Fastboot:", "en": "Path to Fastboot:"},
            "settings_scrcpy_path": {"sv": "Sökväg till scrcpy:", "en": "Path to scrcpy:"},
            "settings_odin_path": {"sv": "Sökväg till odin4:", "en": "Path to odin4:"},
            "settings_heimdall_path": {"sv": "Sökväg till Heimdall:", "en": "Path to Heimdall:"},
            "settings_spft_path": {"sv": "Sökväg till SP Flash Tool:", "en": "Path to SP Flash Tool:"},
            "settings_edl_path": {"sv": "Sökväg till edl:", "en": "Path to edl:"},
            "select_executable": {"sv": "Välj körbar fil", "en": "Select Executable"},
            "about_title": {"sv": "Om Android Verktygslåda", "en": "About Android Toolbox"},
            "about_text": {"sv": "<b>Android Verktygslåda v8.0</b><br>Ett komplett grafiskt verktyg för Android.<br><br>Utvecklad med PyQt6.", "en": "<b>Android Toolbox v8.0</b><br>A complete graphical tool for Android.<br><br>Developed with PyQt6."},
            "confirm_title": {"sv": "Bekräfta åtgärd", "en": "Confirm Action"},
            "confirm_text": {"sv": "Du är på väg att utföra en farlig åtgärd: <b>{action}</b>.", "en": "You are about to perform a dangerous action: <b>{action}</b>."},
            "confirm_info": {"sv": "Detta kan leda till dataförlust. Är du säker?", "en": "This can lead to data loss. Are you sure?"},
            "error_all_fields": {"sv": "Alla obligatoriska fält måste fyllas i!", "en": "All required fields must be filled!"},
            "error_file_not_found": {"sv": "Filen hittades inte: {path}", "en": "File not found: {path}"},
            "error_no_odin_files": {"sv": "Minst en firmware-fil (BL, AP, CP, eller CSC) måste anges!", "en": "At least one firmware file (BL, AP, CP, or CSC) must be specified!"},
        }

    def get_string(self, key, **kwargs):
        s = self.translations.get(key, {}).get(self.current_lang, f"MISSING_STR_{key}")
        return s.format(**kwargs)
        
    def retranslate_ui(self):
        self.setWindowTitle(self.get_string("main_title"))
        self.file_menu.setTitle(self.get_string("file_menu")); self.settings_action.setText(self.get_string("settings")); self.exit_action.setText(self.get_string("exit"))
        self.view_menu.setTitle(self.get_string("view_menu")); self.themes_menu.setTitle(self.get_string("themes"))
        self.lang_menu.setTitle(self.get_string("lang_menu"))
        self.help_menu.setTitle(self.get_string("help_menu")); self.about_action.setText(self.get_string("about"))
        self.device_group.setTitle(self.get_string("device_group")); self.device_select_label.setText(self.get_string("device_select_label")); self.serial_label.setText(self.get_string("serial_label")); self.serial_input.setPlaceholderText(self.get_string("serial_placeholder")); self.refresh_devices_btn.setText(self.get_string("refresh_devices_btn"))
        self.execution_group.setTitle(self.get_string("execution_group")); self.command_preview.setPlaceholderText(self.get_string("command_preview_placeholder")); self.clear_button.setText(self.get_string("clear_button")); self.save_log_button.setText(self.get_string("save_log_button"))
        self.status_label.setText(self.get_string("status_ready"))
        
        # Main Tabs
        self.main_tabs.setTabText(0, "ADB"); self.main_tabs.setTabText(1, "Fastboot"); self.main_tabs.setTabText(2, self.get_string("xiaomi_tab")); self.main_tabs.setTabText(3, self.get_string("edl_tab")); self.main_tabs.setTabText(4, self.get_string("heimdall_tab")); self.main_tabs.setTabText(5, self.get_string("spft_tab")); self.main_tabs.setTabText(6, self.get_string("odin_tab")); self.main_tabs.setTabText(7, self.get_string("scrcpy_tab")); self.main_tabs.setTabText(8, self.get_string("logcat_tab"))
        # ADB Sub-tabs
        adb_tabs = self.main_tabs.widget(0)
        adb_tabs.setTabText(0, self.get_string("adb_tab_file")); adb_tabs.setTabText(1, self.get_string("adb_tab_app")); adb_tabs.setTabText(2, self.get_string("adb_tab_control")); adb_tabs.setTabText(3, self.get_string("adb_tab_info")); adb_tabs.setTabText(4, self.get_string("adb_tab_net")); adb_tabs.setTabText(5, self.get_string("adb_tab_debloat")); adb_tabs.setTabText(6, self.get_string("adb_tab_diagnostics"))
        # Fastboot Sub-tabs
        fb_tabs = self.main_tabs.widget(1)
        fb_tabs.setTabText(0, self.get_string("fb_tab_flash")); fb_tabs.setTabText(1, self.get_string("fb_tab_basic")); fb_tabs.setTabText(2, self.get_string("fb_tab_part")); fb_tabs.setTabText(3, self.get_string("fb_tab_adv"))

        # Xiaomi Tab
        self.xiaomi_group.setTitle(self.get_string("xiaomi_group")); self.xiaomi_file_label.setText(self.get_string("xiaomi_file_label")); self.xiaomi_file_browse.setText(self.get_string("browse")); self.xiaomi_flash_all_btn.setText(self.get_string("xiaomi_flash_all_btn")); self.xiaomi_flash_except_storage_btn.setText(self.get_string("xiaomi_flash_except_storage_btn")); self.xiaomi_flash_lock_btn.setText(self.get_string("xiaomi_flash_lock_btn"))
        # EDL Tab
        self.edl_actions_group.setTitle(self.get_string("edl_actions_group")); self.edl_reboot_btn.setText(self.get_string("edl_reboot_btn")); self.edl_printgpt_btn.setText(self.get_string("edl_printgpt_btn")); self.edl_reset_btn.setText(self.get_string("edl_reset_btn")); self.edl_qfil_group.setTitle(self.get_string("edl_qfil_group")); self.edl_loader_label.setText(self.get_string("edl_loader_label")); self.edl_loader_browse.setText(self.get_string("browse")); self.edl_rawprogram_label.setText(self.get_string("edl_rawprogram_label")); self.edl_rawprogram_browse.setText(self.get_string("browse")); self.edl_patch_label.setText(self.get_string("edl_patch_label")); self.edl_patch_browse.setText(self.get_string("browse")); self.edl_imagedir_label.setText(self.get_string("edl_imagedir_label")); self.edl_imagedir_browse.setText(self.get_string("browse")); self.edl_qfil_flash_btn.setText(self.get_string("edl_qfil_flash_btn"))
        # Heimdall Tab
        self.heimdall_pit_btn.setText(self.get_string("heimdall_pit_btn")); self.heimdall_detect_btn.setText(self.get_string("heimdall_detect_btn")); self.heimdall_download_pit_btn.setText(self.get_string("heimdall_download_pit_btn")); self.heimdall_parts_group.setTitle(self.get_string("heimdall_parts_group")); self.heimdall_options_group.setTitle(self.get_string("heimdall_options_group")); self.heimdall_repartition_check.setText(self.get_string("heimdall_repartition_check")); self.heimdall_no_reboot_check.setText(self.get_string("heimdall_no_reboot_check")); self.heimdall_tflash_check.setText(self.get_string("heimdall_tflash_check")); self.heimdall_skip_size_check.setText(self.get_string("heimdall_skip_size_check")); self.heimdall_flash_btn.setText(self.get_string("heimdall_flash_btn"))
        # SPFT Tab
        self.spft_files_group.setTitle(self.get_string("spft_files_group")); self.spft_scatter_label.setText(self.get_string("spft_scatter_label")); self.spft_da_label.setText(self.get_string("spft_da_label")); self.spft_scatter_browse_btn.setText(self.get_string("spft_scatter_browse_btn")); self.spft_da_browse_btn.setText(self.get_string("browse")); self.spft_options_group.setTitle(self.get_string("spft_options_group")); self.spft_battery_label.setText(self.get_string("spft_battery_label")); self.spft_com_label.setText(self.get_string("spft_com_label")); self.spft_reboot_check.setText(self.get_string("spft_reboot_check")); self.spft_actions_group.setTitle(self.get_string("spft_actions_group")); self.spft_dl_btn.setText(self.get_string("spft_dl_btn")); self.spft_fu_btn.setText(self.get_string("spft_fu_btn")); self.spft_fa_btn.setText(self.get_string("spft_fa_btn"))
        # Odin Tab
        self.odin_files_group.setTitle(self.get_string("odin_files_group")); self.odin_options_group.setTitle(self.get_string("odin_options_group")); self.odin_device_group.setTitle(self.get_string("odin_device_group")); self.odin_bl_browse.setText(self.get_string("browse")); self.odin_ap_browse.setText(self.get_string("browse")); self.odin_cp_browse.setText(self.get_string("browse")); self.odin_csc_browse.setText(self.get_string("browse")); self.odin_ums_browse.setText(self.get_string("browse")); self.odin_erase_check.setText(self.get_string("odin_erase_check")); self.odin_reboot_check.setText(self.get_string("odin_reboot_check")); self.odin_redownload_check.setText(self.get_string("odin_redownload_check")); self.odin_device_label.setText(self.get_string("odin_device_label")); self.odin_refresh_devices_btn.setText(self.get_string("odin_refresh_devices_btn")); self.odin_flash_btn.setText(self.get_string("odin_flash_btn"))
        # scrcpy Tab
        self.scrcpy_group.setTitle(self.get_string("scrcpy_group")); self.scrcpy_start_btn.setText(self.get_string("scrcpy_start_btn")); self.scrcpy_bitrate_label.setText(self.get_string("scrcpy_bitrate_label")); self.scrcpy_resolution_label.setText(self.get_string("scrcpy_resolution_label")); self.scrcpy_show_touches_check.setText(self.get_string("scrcpy_show_touches_check")); self.scrcpy_stay_awake_check.setText(self.get_string("scrcpy_stay_awake_check"))
        # Logcat Tab
        self.logcat_filter_label.setText(self.get_string("logcat_filter_label"))
        # Debloat Tab
        self.debloat_list_btn.setText(self.get_string("debloat_list_btn")); self.debloat_disable_btn.setText(self.get_string("debloat_disable_btn")); self.debloat_enable_btn.setText(self.get_string("debloat_enable_btn"))
        # Diagnostics Tab
        self.bugreport_group.setTitle(self.get_string("bugreport_group")); self.bugreport_btn.setText(self.get_string("bugreport_btn")); self.battery_group.setTitle(self.get_string("battery_group")); self.battery_fetch_btn.setText(self.get_string("battery_fetch_btn")); self.wm_group.setTitle(self.get_string("wm_group")); self.wm_size_label.setText(self.get_string("wm_size_label")); self.wm_density_label.setText(self.get_string("wm_density_label")); self.wm_set_btn.setText(self.get_string("wm_set_btn")); self.wm_reset_btn.setText(self.get_string("wm_reset_btn"))
        # ADB File Transfer
        self.push_group.setTitle(self.get_string("push_group")); self.push_local_label.setText(self.get_string("push_local_label")); self.push_remote_label.setText(self.get_string("push_remote_label")); self.push_browse_btn.setText(self.get_string("browse")); self.push_run_btn.setText(self.get_string("push_run_btn"))
        self.pull_group.setTitle(self.get_string("pull_group")); self.pull_remote_label.setText(self.get_string("pull_remote_label")); self.pull_local_label.setText(self.get_string("pull_local_label")); self.pull_browse_btn.setText(self.get_string("browse")); self.pull_run_btn.setText(self.get_string("pull_run_btn"))
        self.sideload_group.setTitle(self.get_string("sideload_group")); self.sideload_label.setText(self.get_string("sideload_label")); self.sideload_browse_btn.setText(self.get_string("browse")); self.sideload_run_btn.setText(self.get_string("sideload_run_btn"))
        # ADB App Management
        self.install_group.setTitle(self.get_string("install_group")); self.install_apk_label.setText(self.get_string("install_apk_label")); self.install_browse_btn.setText(self.get_string("browse")); self.install_reinstall_check.setText(self.get_string("install_reinstall_check")); self.install_grant_perms_check.setText(self.get_string("install_grant_perms_check")); self.install_run_btn.setText(self.get_string("install_run_btn"))
        self.uninstall_group.setTitle(self.get_string("uninstall_group")); self.uninstall_pkg_label.setText(self.get_string("uninstall_pkg_label")); self.uninstall_keep_data_check.setText(self.get_string("uninstall_keep_data_check")); self.uninstall_run_btn.setText(self.get_string("uninstall_run_btn"))
        self.list_packages_group.setTitle(self.get_string("list_packages_group")); self.list_pkgs_btn.setText(self.get_string("list_pkgs_btn"))
        # ADB Device Control
        self.adb_reboot_group.setTitle(self.get_string("adb_reboot_group")); self.adb_reboot_label.setText(self.get_string("adb_reboot_label")); self.adb_reboot_run_btn.setText(self.get_string("adb_reboot_run_btn"))
        self.root_access_group.setTitle(self.get_string("root_access_group")); self.root_btn.setText(self.get_string("root_btn")); self.unroot_btn.setText(self.get_string("unroot_btn"))
        self.screenshot_group.setTitle(self.get_string("screenshot_group")); self.screenshot_btn.setText(self.get_string("screenshot_btn"))
        self.screenrecord_group.setTitle(self.get_string("screenrecord_group"))
        self.screenrecord_btn.setText(self.get_string("screenrecord_stop_btn") if self.is_recording else self.get_string("screenrecord_start_btn"))
        self.shell_group.setTitle(self.get_string("shell_group")); self.shell_label.setText(self.get_string("shell_label")); self.shell_run_btn.setText(self.get_string("shell_run_btn"))
        # ADB Device Info
        self.get_info_btn.setText(self.get_string("get_info_btn"))
        for key, (name_label, value_label) in self.info_widgets.items():
            name_label.setText(self.get_string(f"info_name_{key}"))
            if "<i>" in value_label.text(): value_label.setText(self.get_string("info_waiting"))
        # ADB Networking
        self.tcpip_group.setTitle(self.get_string("tcpip_group")); self.tcpip_port_label.setText(self.get_string("tcpip_port_label")); self.tcpip_run_btn.setText(self.get_string("tcpip_run_btn"))
        self.connect_group.setTitle(self.get_string("connect_group")); self.connect_ip_label.setText(self.get_string("connect_ip_label")); self.connect_run_btn.setText(self.get_string("connect_run_btn"))
        self.disconnect_group.setTitle(self.get_string("disconnect_group")); self.disconnect_ip_label.setText(self.get_string("disconnect_ip_label")); self.disconnect_run_btn.setText(self.get_string("disconnect_run_btn"))
        # Fastboot Flashing
        self.flash_group.setTitle(self.get_string("flash_group")); self.flash_partition_label.setText(self.get_string("flash_partition_label")); self.flash_file_label.setText(self.get_string("flash_file_label")); self.flash_browse_btn.setText(self.get_string("browse")); self.flash_run_btn.setText(self.get_string("flash_run_btn"))
        self.update_zip_group.setTitle(self.get_string("update_zip_group")); self.update_zip_label.setText(self.get_string("update_zip_label")); self.update_browse_btn.setText(self.get_string("browse")); self.update_run_btn.setText(self.get_string("update_run_btn"))
        self.flash_options_group.setTitle(self.get_string("flash_options_group")); self.wipe_check.setText(self.get_string("wipe_check")); self.skip_reboot_check.setText(self.get_string("skip_reboot_check"))
        # Fastboot Basic
        self.reboot_combo.clear(); self.reboot_combo.addItems([self.get_string("reboot_normal"), self.get_string("reboot_bootloader")])
        self.fb_reboot_group.setTitle(self.get_string("fb_reboot_group")); self.fb_reboot_label.setText(self.get_string("fb_reboot_label")); self.reboot_run_btn.setText(self.get_string("fb_reboot_run_btn"))
        self.locking_group.setTitle(self.get_string("locking_group")); self.unlock_btn.setText(self.get_string("unlock_btn")); self.lock_btn.setText(self.get_string("lock_btn")); self.unlock_crit_btn.setText(self.get_string("unlock_crit_btn")); self.lock_crit_btn.setText(self.get_string("lock_crit_btn"))
        self.slot_group.setTitle(self.get_string("slot_group")); self.slot_label.setText(self.get_string("slot_label")); self.set_active_btn.setText(self.get_string("set_active_btn"))
        # Fastboot Partitions
        self.erase_group.setTitle(self.get_string("erase_group")); self.erase_label.setText(self.get_string("erase_label")); self.erase_btn.setText(self.get_string("erase_btn"))
        self.wipe_super_group.setTitle(self.get_string("wipe_super_group")); self.wipe_super_btn.setText(self.get_string("wipe_super_btn"))
        # Fastboot Advanced
        self.boot_group.setTitle(self.get_string("boot_group")); self.boot_file_label.setText(self.get_string("boot_file_label")); self.boot_browse_btn.setText(self.get_string("browse")); self.boot_run_btn.setText(self.get_string("boot_run_btn"))
        self.getvar_group.setTitle(self.get_string("getvar_group")); self.getvar_label.setText(self.get_string("getvar_label")); self.getvar_btn.setText(self.get_string("getvar_btn"))

    def change_language(self, lang):
        self.current_lang = lang
        self.settings.setValue("language", lang)
        self.retranslate_ui()

    def init_themes(self):
        self.themes = {
            "Light": "",
            "Dark": """QWidget{background-color:#2b2b2b;color:#f0f0f0}QGroupBox{border:1px solid #444;margin-top:10px}QGroupBox::title{subcontrol-origin:margin;left:10px;padding:0 5px}QLineEdit,QTextEdit,QComboBox,QListWidget,QTableWidget{background-color:#3c3f41;color:#f0f0f0;border:1px solid #555}QPushButton{background-color:#005A9C;color:white;border:none;padding:8px;border-radius:4px}QPushButton:hover{background-color:#0078D4}QPushButton:disabled{background-color:#555}QTabWidget::pane{border-top:2px solid #444}QTabBar::tab{background:#3c3f41;padding:8px;border:1px solid #444;border-bottom:none;border-top-left-radius:4px;border-top-right-radius:4px}QTabBar::tab:selected{background:#2b2b2b}QMenuBar{background-color:#3c3f41}QMenuBar::item:selected{background-color:#555}QMenu{background-color:#3c3f41;border:1px solid #555}QMenu::item:selected{background-color:#555}""",
            "Matrix": """QWidget{background-color:#000;color:#0F0;font-family:monospace}QGroupBox{border:1px solid #0F0}QLineEdit,QTextEdit,QComboBox,QListWidget,QTableWidget{background-color:#0a0a0a;border:1px solid #0F0}QPushButton{background-color:#003300;color:#0F0;border:1px solid #0F0;padding:8px}QPushButton:hover{background-color:#005500}QTextEdit{background-color:#050505}""",
            "Synthwave": """QWidget{background-color:#2a2139;color:#f0d8ff;font-family:Verdana}QGroupBox{border:1px solid #ff00ff}QLineEdit,QTextEdit,QComboBox,QTableWidget{background-color:#1e152a;border:1px solid #ff00ff}QPushButton{background-color:#ff00ff;color:#fff;border:none;padding:8px;font-weight:bold}QPushButton:hover{background-color:#e600e6}QTextEdit{color:#00ffff}QLabel{color:#ff8d00}""",
            "Dracula": """QWidget{background-color:#282a36;color:#f8f8f2}QGroupBox{border:1px solid #44475a}QLineEdit,QTextEdit,QComboBox,QTableWidget{background-color:#44475a;border:1px solid #6272a4}QPushButton{background-color:#bd93f9;color:#282a36;border:none;padding:8px;font-weight:bold}QPushButton:hover{background-color:#caa9fa}QTextEdit{color:#50fa7b}QLabel{color:#8be9fd}""",
        }

    def apply_theme(self, theme_name):
        self.settings.setValue("theme", theme_name)
        self.current_theme_name = theme_name
        self.setStyleSheet(self.themes.get(theme_name, ""))
        for action in self.themes_group.actions():
            if action.text() == theme_name: action.setChecked(True)

    def create_menu(self):
        menu_bar = self.menuBar()
        self.file_menu = menu_bar.addMenu(""); self.settings_action = QAction(QIcon.fromTheme("preferences-system"), "", self); self.settings_action.triggered.connect(self.open_settings_dialog); self.file_menu.addAction(self.settings_action); self.exit_action = QAction(QIcon.fromTheme("application-exit"), "", self); self.exit_action.triggered.connect(self.close); self.file_menu.addAction(self.exit_action)
        self.view_menu = menu_bar.addMenu(""); self.themes_menu = self.view_menu.addMenu(""); self.themes_group = QActionGroup(self); self.themes_group.setExclusive(True)
        for theme_name in self.themes.keys():
            action = QAction(theme_name, self, checkable=True); action.triggered.connect(lambda checked, name=theme_name: self.apply_theme(name)); self.themes_menu.addAction(action); self.themes_group.addAction(action)
        self.lang_menu = menu_bar.addMenu(""); lang_group = QActionGroup(self); lang_group.setExclusive(True)
        sv_action = QAction("Svenska", self, checkable=True); sv_action.triggered.connect(lambda: self.change_language("sv")); self.lang_menu.addAction(sv_action); lang_group.addAction(sv_action)
        en_action = QAction("English", self, checkable=True); en_action.triggered.connect(lambda: self.change_language("en")); self.lang_menu.addAction(en_action); lang_group.addAction(en_action)
        
        if self.current_lang == "sv":
            sv_action.setChecked(True)
        else:
            en_action.setChecked(True)

        self.help_menu = menu_bar.addMenu(""); self.about_action = QAction(QIcon.fromTheme("help-about"), "", self); self.about_action.triggered.connect(self.show_about_dialog); self.help_menu.addAction(self.about_action)

    # --- Hjälpmetoder ---
    def create_partition_combo(self):
        combo = QComboBox(); combo.addItems(self.common_partitions); combo.setEditable(True)
        combo.completer().setCompletionMode(combo.completer().CompletionMode.PopupCompletion)
        return combo

    def create_run_button(self, command_key):
        btn = QPushButton()
        btn.clicked.connect(lambda: self.route_command(command_key, btn))
        return btn

    def route_command(self, key, button):
        if key == "scrcpy_start":
            args = []
            if self.scrcpy_bitrate_combo.currentText() != "Default":
                args.extend(["-b", self.scrcpy_bitrate_combo.currentText()])
            if self.scrcpy_resolution_combo.currentText() != "Default":
                args.extend(["-m", self.scrcpy_resolution_combo.currentText()])
            if self.scrcpy_show_touches_check.isChecked(): args.append("--show-touches")
            if self.scrcpy_stay_awake_check.isChecked(): args.append("--stay-awake")
            self.start_process(self.scrcpy_path, args, button)
            return
            
        current_main_tab_index = self.main_tabs.currentIndex()
        if current_main_tab_index == 1: # Fastboot
             self.run_fastboot_command(key, button)
        elif current_main_tab_index == 2: # Xiaomi
             self.run_xiaomi_command(key, button)
        elif current_main_tab_index == 3: # EDL
             self.run_edl_command(key, button)
        elif current_main_tab_index == 4: # Heimdall
             self.run_heimdall_command(key, button)
        elif current_main_tab_index == 5: # SPFT
             self.run_spft_command(key, button)
        elif current_main_tab_index == 6: # Odin
             self.run_odin_command(key, button)
        else: # ADB (covers index 0, 7, 8)
            self.run_adb_command(key, button)

    def browse_file(self, line_edit):
        file_path, _ = QFileDialog.getOpenFileName(self, self.get_string("browse"))
        if file_path: line_edit.setText(file_path)
            
    def browse_save_location(self, line_edit):
        file_path, _ = QFileDialog.getSaveFileName(self, self.get_string("browse"))
        if file_path: line_edit.setText(file_path)
    
    def browse_folder_for_edl(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Image Directory")
        if folder_path:
            self.edl_imagedir_input.setText(folder_path)

    def build_command(self, executable, extra_args=[]):
        parts = [executable]
        # Odin does not use -s for serial, it uses -d for device path
        if executable not in [self.odin_path, self.heimdall_path, self.spft_path, self.edl_path] and self.serial_input.text():
            parts.extend(["-s", self.serial_input.text().strip()])
        parts.extend(extra_args)
        return parts

    def update_command_preview(self, parts):
        try: self.command_preview.setText(subprocess.list2cmdline(parts))
        except AttributeError: self.command_preview.setText(' '.join(f'"{p}"' if ' ' in p else p for p in parts))

    def update_serial_from_combo(self, text):
        data = self.device_combo.currentData()
        if data: self.serial_input.setText(data)

    def save_log_to_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, self.get_string("save_log_button"), "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.output_text.toPlainText())
                self.status_bar.showMessage(self.get_string("status_log_saved"), 3000)
            except Exception as e:
                self.show_error(f"Could not save log: {e}")

    def list_installed_packages(self):
        try:
            command = self.build_command(self.adb_path, ["shell", "pm", "list", "packages"])
            result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
            packages = [line.replace("package:", "").strip() for line in result.stdout.splitlines()]
            dialog = QDialog(self); dialog.setWindowTitle("Installed Packages"); layout = QVBoxLayout(dialog)
            list_widget = QListWidget(); list_widget.addItems(packages)
            list_widget.itemDoubleClicked.connect(lambda item: self.uninstall_pkg_input.setText(item.text()))
            list_widget.itemDoubleClicked.connect(dialog.accept)
            layout.addWidget(QLabel("Double-click a package to populate the uninstall field."))
            layout.addWidget(list_widget); dialog.exec()
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            self.show_error(f"Could not list packages: {e}")

    def take_screenshot(self):
        save_path, _ = QFileDialog.getSaveFileName(self, self.get_string("screenshot_btn"), "screenshot.png", "PNG Image (*.png)")
        if not save_path: return
        self.status_bar.showMessage("Taking screenshot on device..."); QApplication.processEvents()
        remote_path = "/sdcard/screenshot_temp.png"
        try:
            subprocess.run(self.build_command(self.adb_path, ["shell", "screencap", "-p", remote_path]), check=True)
            self.status_bar.showMessage("Downloading screenshot..."); QApplication.processEvents()
            subprocess.run(self.build_command(self.adb_path, ["pull", remote_path, save_path]), check=True)
            subprocess.run(self.build_command(self.adb_path, ["shell", "rm", remote_path]), check=True)
            self.output_text.append(f"Screenshot saved to: {save_path}")
            self.status_bar.showMessage("Screenshot saved!", 3000)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            self.show_error(f"Screenshot failed: {e}")
            self.status_bar.showMessage("Screenshot failed!", 3000)

    def toggle_screen_recording(self):
        if not self.is_recording:
            # Start recording
            self.is_recording = True
            self.retranslate_ui()
            self.status_bar.showMessage(self.get_string("status_recording"))
            command = self.build_command(self.adb_path, ["shell", "screenrecord", "/sdcard/screenrecord_temp.mp4"])
            self.screenrecord_process.start(command[0], command[1:])
        else:
            # Stop recording
            self.screenrecord_process.kill()
            self.is_recording = False
            self.retranslate_ui()
            self.status_bar.showMessage(self.get_string("status_pulling_video"))
            QApplication.processEvents()

            save_path, _ = QFileDialog.getSaveFileName(self, self.get_string("screenrecord_stop_btn"), "screenrecord.mp4", "MP4 Video (*.mp4)")
            if save_path:
                try:
                    subprocess.run(self.build_command(self.adb_path, ["pull", "/sdcard/screenrecord_temp.mp4", save_path]), check=True)
                    subprocess.run(self.build_command(self.adb_path, ["shell", "rm", "/sdcard/screenrecord_temp.mp4"]), check=True)
                    self.status_bar.showMessage(self.get_string("status_video_saved"), 4000)
                    self.output_text.append(f"Screen recording saved to: {save_path}")
                except Exception as e:
                    self.show_error(f"Could not pull video: {e}")
            else:
                 subprocess.run(self.build_command(self.adb_path, ["shell", "rm", "/sdcard/screenrecord_temp.mp4"]), check=True)
                 self.status_bar.showMessage(self.get_string("status_ready"))

    def fetch_device_info(self):
        for key, prop in self.info_labels_map.items():
            _, value_widget = self.info_widgets[key]
            try:
                command = self.build_command(self.adb_path, ["shell", "getprop", prop])
                result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
                value_widget.setText(result.stdout.strip())
            except Exception:
                value_widget.setText(self.get_string("info_failed"))

    def confirm_dangerous_action(self, action_name):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(self.get_string("confirm_title"))
        msg_box.setText(self.get_string("confirm_text", action=action_name))
        msg_box.setInformativeText(self.get_string("confirm_info"))
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        return msg_box.exec() == QMessageBox.StandardButton.Yes

    def update_device_list(self):
        self.device_combo.clear()
        self.output_text.append("<font color='cyan'>> Searching for devices...</font>\n")
        try:
            adb_res = subprocess.run([self.adb_path, "devices"], capture_output=True, text=True, encoding='utf-8')
            for line in adb_res.stdout.splitlines()[1:]:
                if "\tdevice" in line:
                    serial = line.split("\t")[0]; self.device_combo.addItem(f"ADB: {serial}", serial)
            fb_res = subprocess.run([self.fastboot_path, "devices"], capture_output=True, text=True, encoding='utf-8')
            for line in fb_res.stdout.splitlines():
                if "\tfastboot" in line:
                    serial = line.split("\t")[0]; self.device_combo.addItem(f"Fastboot: {serial}", serial)
            self.output_text.append(f"Found {self.device_combo.count()} device(s).")
        except Exception as e:
            self.show_error(f"Could not search for devices: {e}")
    
    def update_odin_device_list(self):
        self.odin_device_combo.clear()
        self.output_text.append("<font color='cyan'>> Searching for Odin devices...</font>\n")
        try:
            command = [self.odin_path, "-l"]
            result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
            devices = [line.strip() for line in result.stdout.splitlines() if line.strip()]
            self.odin_device_combo.addItems(devices)
            self.output_text.append(f"Found {len(devices)} Odin device(s).")
        except Exception as e:
            self.show_error(f"Could not search for Odin devices: {e}")

    def run_fastboot_command(self, command_type, button):
        args = []
        if command_type == "flash":
            partition = self.flash_partition_combo.currentText(); filepath = self.flash_file_input.text()
            if not all([partition, filepath]): return self.show_error(self.get_string("error_all_fields"))
            if not os.path.exists(filepath): return self.show_error(self.get_string("error_file_not_found", path=filepath))
            args = ["flash", partition, filepath]
            if self.wipe_check.isChecked(): args.insert(0, "-w")
            if self.skip_reboot_check.isChecked(): args.append("--skip-reboot")
        elif command_type in ["unlock", "lock", "unlock_critical", "lock_critical"]:
            if not self.confirm_dangerous_action(command_type): return
            args = ["flashing", command_type]
        elif command_type == "erase":
            partition = self.erase_partition_combo.currentText()
            if not partition: return self.show_error(self.get_string("error_all_fields"))
            if not self.confirm_dangerous_action(f"erase '{partition}'"): return
            args = ["erase", partition]
        elif command_type == "wipe-super":
            if not self.confirm_dangerous_action("wipe-super"): return
            args = ["wipe-super"]
        elif command_type == "getvar":
            variable = self.getvar_combo.currentText()
            if not variable: return self.show_error(self.get_string("error_all_fields"))
            args = ["getvar", variable]
        elif command_type == "update":
            filepath = self.update_zip_input.text()
            if not filepath or not os.path.exists(filepath): return self.show_error(self.get_string("error_file_not_found", path=filepath))
            args = ["update", filepath]
        elif command_type == "reboot_fb":
            reboot_target = self.reboot_combo.currentText()
            args.append("reboot")
            if reboot_target == self.get_string("reboot_bootloader"): args.append("bootloader")
        elif command_type == "set_active":
            args = ["set_active", self.set_active_combo.currentText()]
        elif command_type == "boot":
            filepath = self.boot_file_input.text()
            if not filepath or not os.path.exists(filepath): return self.show_error(self.get_string("error_file_not_found", path=filepath))
            args = ["boot", filepath]
        
        if args: self.start_process(self.fastboot_path, args, button)

    def run_adb_command(self, command_type, button):
        args = []; dispatch = {
            "push": lambda: ["push", self.push_local_input.text(), self.push_remote_input.text()],
            "pull": lambda: ["pull", self.pull_remote_input.text(), self.pull_local_input.text()],
            "sideload": lambda: ["sideload", self.sideload_input.text()],
            "install": lambda: ["install"] + (["-r"] if self.install_reinstall_check.isChecked() else []) + (["-g"] if self.install_grant_perms_check.isChecked() else []) + [self.install_apk_input.text()],
            "uninstall": lambda: ["uninstall"] + (["-k"] if self.uninstall_keep_data_check.isChecked() else []) + [self.uninstall_pkg_input.text()],
            "reboot": lambda: ["reboot", self.adb_reboot_combo.currentText().lower()] if self.adb_reboot_combo.currentText() != "System" else ["reboot"],
            "root": lambda: ["root"], "unroot": lambda: ["unroot"],
            "shell": lambda: ["shell", self.shell_command_input.text()] if self.shell_command_input.text() else ["shell"],
            "tcpip": lambda: ["tcpip", self.tcpip_port_input.text()],
            "connect": lambda: ["connect", self.connect_ip_input.text()],
            "disconnect": lambda: ["disconnect", self.disconnect_ip_input.text()] if self.disconnect_ip_input.text() else ["disconnect"]
        }
        if command_type in dispatch:
            args = dispatch[command_type]()
            if any(not part for part in args if isinstance(part, str) and not part.startswith("-")):
                return self.show_error(self.get_string("error_all_fields"))
        elif command_type == "debloat_disable":
            items = self.debloat_pkg_list.selectedItems()
            if items and self.confirm_dangerous_action(f"disable {items[0].text()}"):
                args = ["shell", "pm", "disable-user", "--user", "0", items[0].text()]
        elif command_type == "debloat_enable":
            items = self.debloat_pkg_list.selectedItems()
            if items: args = ["shell", "pm", "enable", "--user", "0", items[0].text()]
        elif command_type == "bugreport":
            save_path, _ = QFileDialog.getSaveFileName(self, self.get_string("bugreport_btn"), "bugreport.zip", "ZIP Files (*.zip)")
            if save_path: args = ["bugreport", save_path]
        elif command_type == "wm_set":
            size = self.wm_size_input.text(); density = self.wm_density_input.text()
            if size: self.start_process(self.adb_path, ["shell", "wm", "size", size], button)
            if density: self.start_process(self.adb_path, ["shell", "wm", "density", density], button)
            return
        elif command_type == "wm_reset":
            self.start_process(self.adb_path, ["shell", "wm", "size", "reset"], button)
            self.start_process(self.adb_path, ["shell", "wm", "density", "reset"], button)
            return
            
        if args: self.start_process(self.adb_path, args, button)

    def run_odin_command(self, command_type, button):
        if command_type != "odin_flash": return
        
        args = []
        files = {
            "-b": self.odin_bl_input.text(),
            "-a": self.odin_ap_input.text(),
            "-c": self.odin_cp_input.text(),
            "-s": self.odin_csc_input.text(),
            "-u": self.odin_ums_input.text(),
        }

        has_files = False
        for flag, path in files.items():
            if path:
                if not os.path.exists(path): return self.show_error(self.get_string("error_file_not_found", path=path))
                args.extend([flag, path])
                if flag != "-u": has_files = True
        
        if not has_files:
            return self.show_error(self.get_string("error_no_odin_files"))

        if self.odin_erase_check.isChecked(): args.append("-e")
        if self.odin_reboot_check.isChecked(): args.append("--reboot")
        if self.odin_redownload_check.isChecked(): args.append("--redownload")
        
        if self.odin_device_combo.currentText():
            args.extend(["-d", self.odin_device_combo.currentText()])

        if self.confirm_dangerous_action("Odin Flash"):
            self.start_process(self.odin_path, args, button)

    def run_heimdall_command(self, command_type, button):
        args = []
        if command_type == "heimdall_detect":
            args = ["detect"]
        elif command_type == "heimdall_print_pit":
            args = ["print-pit"]
        elif command_type == "heimdall_download_pit":
            save_path, _ = QFileDialog.getSaveFileName(self, self.get_string("heimdall_download_pit_btn"), "device.pit", "PIT Files (*.pit)")
            if save_path:
                args = ["download-pit", "--output", save_path]
        elif command_type == "heimdall_flash":
            args = ["flash"]
            has_pit = False
            for row in range(self.heimdall_parts_table.rowCount()):
                part_name = self.heimdall_parts_table.cellWidget(row, 0).currentText()
                file_path = self.heimdall_parts_table.cellWidget(row, 1).text()
                if part_name and file_path:
                    if not os.path.exists(file_path): return self.show_error(self.get_string("error_file_not_found", path=file_path))
                    args.extend([f"--{part_name}", file_path])
                    if part_name.upper() == "PIT":
                        has_pit = True

            if self.heimdall_repartition_check.isChecked():
                if not has_pit: return self.show_error("Repartition requires a PIT file to be specified in the table.")
                args.insert(1, "--repartition")

            if self.heimdall_no_reboot_check.isChecked(): args.append("--no-reboot")
            if self.heimdall_tflash_check.isChecked(): args.append("--tflash")
            if self.heimdall_skip_size_check.isChecked(): args.append("--skip-size-check")
            
            if len(args) == 1: return self.show_error("No partitions added to flash.")
            if not self.confirm_dangerous_action("Heimdall Flash"): return

        if args: self.start_process(self.heimdall_path, args, button)

    def run_spft_command(self, command_type, button):
        scatter_file = self.spft_scatter_input.text()
        if not scatter_file or not os.path.exists(scatter_file):
            return self.show_error(self.get_string("error_file_not_found", path=scatter_file))
        
        args = ["-s", scatter_file]

        da_file = self.spft_da_input.text()
        if da_file:
            if not os.path.exists(da_file): return self.show_error(self.get_string("error_file_not_found", path=da_file))
            args.extend(["-d", da_file])

        if command_type == "spft_download":
            args.extend(["-c", "download"])
        elif command_type == "spft_upgrade":
            args.extend(["-c", "firmware-upgrade"])
        elif command_type == "spft_format":
            if not self.confirm_dangerous_action("Format All + Download"): return
            args.extend(["-c", "format-download"])
        
        if self.spft_com_input.text():
            args.extend(["-p", self.spft_com_input.text()])
        
        battery_mode = self.spft_battery_combo.currentText()
        if battery_mode != "Auto":
            mode = "with" if "With" in battery_mode else "without"
            args.extend(["-t", mode])

        if self.spft_reboot_check.isChecked():
            args.append("-b")

        self.start_process(self.spft_path, args, button)

    def run_edl_command(self, command_type, button):
        args = []
        if command_type == "edl_reboot_edl":
            self.start_process(self.adb_path, ["reboot", "edl"], button)
            return
        elif command_type == "edl_printgpt":
            args = ["printgpt"]
            if self.edl_loader_input.text(): args.extend(["--loader", self.edl_loader_input.text()])
        elif command_type == "edl_reset":
            args = ["reset"]
            if self.edl_loader_input.text(): args.extend(["--loader", self.edl_loader_input.text()])
        elif command_type == "edl_qfil_flash":
            rawprogram = self.edl_rawprogram_input.text()
            patch = self.edl_patch_input.text()
            imagedir = self.edl_imagedir_input.text()
            if not all([rawprogram, patch, imagedir]): return self.show_error(self.get_string("error_all_fields"))
            if not os.path.exists(rawprogram): return self.show_error(self.get_string("error_file_not_found", path=rawprogram))
            if not os.path.exists(patch): return self.show_error(self.get_string("error_file_not_found", path=patch))
            if not os.path.isdir(imagedir): return self.show_error(f"Image path is not a valid directory: {imagedir}")
            
            args = ["qfil", rawprogram, patch, imagedir]
            if self.edl_loader_input.text(): args.extend(["--loader", self.edl_loader_input.text()])
            if not self.confirm_dangerous_action("EDL QFIL Flash"): return
        
        if args: self.start_process(self.edl_path, args, button)

    def run_xiaomi_command(self, command_type, button):
        tgz_file = self.xiaomi_file_input.text()
        if not tgz_file or not os.path.exists(tgz_file):
            return self.show_error(self.get_string("error_file_not_found", path=tgz_file))

        script_map = {
            "xiaomi_flash_all": "flash_all.sh",
            "xiaomi_flash_except_storage": "flash_all_except_storage.sh",
            "xiaomi_flash_lock": "flash_all_lock.sh"
        }
        script_to_run = script_map.get(command_type)
        if not script_to_run: return

        if not self.confirm_dangerous_action(f"Xiaomi Flash ({script_to_run})"): return

        try:
            self.temp_dir = tempfile.mkdtemp()
            self.output_text.append(f"Unpacking firmware to {self.temp_dir}...")
            QApplication.processEvents()
            with tarfile.open(tgz_file, "r:gz") as tar:
                # Find the root directory inside the tarball
                root_folder = tar.getmembers()[0].name.split('/')[0]
                tar.extractall(path=self.temp_dir)
            
            script_path = os.path.join(self.temp_dir, root_folder, script_to_run)
            if not os.path.exists(script_path):
                self.show_error(f"Script not found: {script_path}")
                shutil.rmtree(self.temp_dir)
                return

            # Make script executable
            os.chmod(script_path, 0o755)

            # The script needs to be run from its directory
            working_directory = os.path.join(self.temp_dir, root_folder)
            
            # We can't use the normal start_process because this is a shell script, not an executable
            # and it needs a specific working directory.
            self.output_text.append(f"<font color='cyan'>> Executing: {script_path}</font>\n")
            self.process.setWorkingDirectory(working_directory)
            self.process.start(script_path, [])
            self.process.finished.connect(self.cleanup_temp_dir)

        except Exception as e:
            self.show_error(f"Failed to extract or run Xiaomi script: {e}")
            if self.temp_dir: shutil.rmtree(self.temp_dir)

    def cleanup_temp_dir(self):
        if self.temp_dir:
            try:
                shutil.rmtree(self.temp_dir)
                self.output_text.append(f"Cleaned up temporary directory: {self.temp_dir}")
                self.temp_dir = None
            except Exception as e:
                self.show_error(f"Could not clean up temp directory: {e}")
        self.process.setWorkingDirectory("") # Reset working directory
        self.process.finished.disconnect(self.cleanup_temp_dir) # Disconnect to avoid re-triggering

    def start_process(self, executable, command_parts, button):
        if self.process.state() == QProcess.ProcessState.Running:
            return self.show_error("Wait, a command is already running...")
        
        # Special handling for tools that don't use build_command structure
        if executable in [self.odin_path, self.heimdall_path, self.spft_path, self.edl_path]:
            full_command = [executable] + command_parts
        else:
            full_command = self.build_command(executable, command_parts)

        self.update_command_preview(full_command)
        self.output_text.append(f"<font color='cyan'>> {self.command_preview.text()}</font>\n")
        
        self.current_running_button = button
        if button: button.setEnabled(False)
        self.status_label.setText(self.get_string("status_running", exe=os.path.basename(executable)))
        self.loading_label.show(); self.loading_movie.start()
        
        self.process.start(full_command[0], full_command[1:])

    def handle_stdout(self): self.output_text.insertPlainText(self.process.readAllStandardOutput().data().decode(errors='ignore'))
    def handle_stderr(self): self.output_text.append(f"<font color='red'>{self.process.readAllStandardError().data().decode(errors='ignore').strip()}</font>")

    def process_finished(self, exit_code, exit_status):
        if self.current_running_button: self.current_running_button.setEnabled(True)
        self.current_running_button = None
        self.loading_movie.stop(); self.loading_label.hide()
        
        if exit_code == 0:
            self.output_text.append(f"\n<font color='lime'>--- Command finished (Success, code {exit_code}) ---</font>\n")
            self.status_label.setText(self.get_string("status_ready"))
        else:
            self.output_text.append(f"\n<font color='red'>--- Command failed (Exit Code: {exit_code}) ---</font>\n")
            self.status_label.setText(self.get_string("status_error"))
        
    def show_error(self, message):
        self.output_text.append(f"<font color='yellow'>ERROR: {message}</font>")
        self.status_bar.showMessage(message, 5000)

    def load_settings(self):
        self.restoreGeometry(self.settings.value("windowGeometry", self.saveGeometry()))
        self.serial_input.setText(self.settings.value("lastSerial", ""))

    def save_settings(self):
        self.settings.setValue("windowGeometry", self.saveGeometry())
        self.settings.setValue("lastSerial", self.serial_input.text())
        self.settings.setValue("language", self.current_lang)
        self.settings.setValue("theme", self.current_theme_name)

    def open_settings_dialog(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            self.adb_path = self.settings.value("adb_path", "adb")
            self.fastboot_path = self.settings.value("fastboot_path", "fastboot")
            self.scrcpy_path = self.settings.value("scrcpy_path", "scrcpy")
            self.odin_path = self.settings.value("odin_path", "odin4")
            self.heimdall_path = self.settings.value("heimdall_path", "heimdall")
            self.spft_path = self.settings.value("spft_path", "flash_tool")
            self.edl_path = self.settings.value("edl_path", "edl")
            self.status_bar.showMessage(self.get_string("status_settings_saved"), 3000)
            self.check_executables()

    def show_about_dialog(self):
        QMessageBox.about(self, self.get_string("about_title"), self.get_string("about_text"))

    def check_executables(self):
        for name, path in [("ADB", self.adb_path), ("Fastboot", self.fastboot_path), ("scrcpy", self.scrcpy_path), ("Odin", self.odin_path), ("Heimdall", self.heimdall_path), ("SPFT", self.spft_path), ("EDL", self.edl_path)]:
            try:
                startupinfo = None
                if sys.platform == "win32":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                version_flag = "--version"
                if name == "Odin": version_flag = "-v"
                if name == "Heimdall": version_flag = "version"
                if name in ["SPFT", "EDL"]: version_flag = "-h" 
                
                command = [path, version_flag] if name not in ["Heimdall"] else [path, "version"]

                subprocess.run(command, capture_output=True, check=True, startupinfo=startupinfo, timeout=2)
            except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
                if name not in ["scrcpy", "Odin", "Heimdall", "SPFT", "EDL"]: # Core tools
                    self.show_error(f"{name} not found at '{path}'. Please set the correct path in File -> Settings.")

    def closeEvent(self, event):
        self.logcat_process.kill()
        self.screenrecord_process.kill()
        self.process.kill()
        self.save_settings()
        if self.temp_dir:
            try:
                shutil.rmtree(self.temp_dir)
            except Exception:
                pass
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = FastbootAdbGUI()
    ex.show()
    sys.exit(app.exec())
