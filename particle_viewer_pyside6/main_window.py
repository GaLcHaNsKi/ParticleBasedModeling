from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from render_widget import FieldWidget
from vector_field import PRESET_FIELDS, VectorField


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Particle Field Viewer")
        self.resize(1280, 760)

        self.render_widget = FieldWidget(self)
        self._build_ui()
        self._sync_field_description()

    def _build_ui(self) -> None:
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(12)

        panel = QWidget(self)
        panel.setFixedWidth(320)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(12)

        field_box = QGroupBox("Поле скорости", self)
        field_layout = QFormLayout(field_box)
        self.field_combo = QComboBox(self)
        for item in PRESET_FIELDS:
            self.field_combo.addItem(item.title, item.key)
        self.field_combo.currentIndexChanged.connect(self._sync_field_description)
        field_layout.addRow("Тип поля", self.field_combo)

        self.description_label = QLabel(self)
        self.description_label.setWordWrap(True)
        self.description_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.description_label.setStyleSheet("color: #374151;")
        field_layout.addRow(self.description_label)

        self.ux_edit = QLineEdit("10", self)
        self.uy_edit = QLineEdit("5", self)
        field_layout.addRow("u_x(x, y)", self.ux_edit)
        field_layout.addRow("u_y(x, y)", self.uy_edit)

        apply_button = QPushButton("Применить поле", self)
        apply_button.clicked.connect(self._apply_field)
        field_layout.addRow(apply_button)

        display_box = QGroupBox("Отображение", self)
        display_layout = QVBoxLayout(display_box)

        self.arrows_checkbox = QCheckBox("Показывать стрелки", self)
        self.arrows_checkbox.setChecked(True)
        self.arrows_checkbox.toggled.connect(self.render_widget.set_show_arrows)

        self.streamlines_checkbox = QCheckBox("Показывать линии тока", self)
        self.streamlines_checkbox.setChecked(True)
        self.streamlines_checkbox.toggled.connect(self.render_widget.set_show_streamlines)

        self.trails_checkbox = QCheckBox("Показывать trail", self)
        self.trails_checkbox.setChecked(True)
        self.trails_checkbox.toggled.connect(self.render_widget.set_show_trails)

        self.pause_checkbox = QCheckBox("Пауза симуляции", self)
        self.pause_checkbox.toggled.connect(self.render_widget.set_paused)

        self.streamline_quality_label = QLabel("Гладкость линий: 55", self)
        self.streamline_quality_slider = QSlider(Qt.Horizontal, self)
        self.streamline_quality_slider.setRange(10, 100)
        self.streamline_quality_slider.setValue(55)
        self.streamline_quality_slider.valueChanged.connect(self._update_streamline_quality)

        display_layout.addWidget(self.arrows_checkbox)
        display_layout.addWidget(self.streamlines_checkbox)
        display_layout.addWidget(self.trails_checkbox)
        display_layout.addWidget(self.pause_checkbox)
        display_layout.addWidget(self.streamline_quality_label)
        display_layout.addWidget(self.streamline_quality_slider)

        actions_box = QGroupBox("Действия", self)
        actions_layout = QVBoxLayout(actions_box)
        clear_button = QPushButton("Очистить частицы", self)
        clear_button.clicked.connect(self.render_widget.clear_particles)
        actions_layout.addWidget(clear_button)

        particle_box = QGroupBox("Параметры частицы", self)
        particle_layout = QFormLayout(particle_box)

        self.radius_spin = QDoubleSpinBox(self)
        self.radius_spin.setRange(0.05, 5.0)
        self.radius_spin.setDecimals(3)
        self.radius_spin.setSingleStep(0.01)
        self.radius_spin.setSuffix(" мм")
        self.radius_spin.setValue(0.10)

        self.density_spin = QDoubleSpinBox(self)
        self.density_spin.setRange(10.0, 10000.0)
        self.density_spin.setDecimals(1)
        self.density_spin.setSingleStep(50.0)
        self.density_spin.setSuffix(" кг/м³")
        self.density_spin.setValue(2500.3)

        self.initial_vx_spin = QDoubleSpinBox(self)
        self.initial_vx_spin.setRange(-500.0, 500.0)
        self.initial_vx_spin.setDecimals(2)
        self.initial_vx_spin.setSingleStep(0.5)
        self.initial_vx_spin.setSuffix(" м/с")

        self.initial_vy_spin = QDoubleSpinBox(self)
        self.initial_vy_spin.setRange(-500.0, 500.0)
        self.initial_vy_spin.setDecimals(2)
        self.initial_vy_spin.setSingleStep(0.5)
        self.initial_vy_spin.setSuffix(" м/с")

        self.continuous_source_checkbox = QCheckBox("Непрерывный источник (удержание ЛКМ)", self)
        self.continuous_source_checkbox.toggled.connect(self.render_widget.set_continuous_source_enabled)

        particle_layout.addRow("Радиус", self.radius_spin)
        particle_layout.addRow("Плотность", self.density_spin)
        particle_layout.addRow("Начальная v_x", self.initial_vx_spin)
        particle_layout.addRow("Начальная v_y", self.initial_vy_spin)
        particle_layout.addRow(self.continuous_source_checkbox)

        for widget in (self.radius_spin, self.density_spin, self.initial_vx_spin, self.initial_vy_spin):
            widget.valueChanged.connect(self._update_particle_parameters)

        hint = QLabel("", self)
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #4b5563;")

        panel_layout.addWidget(field_box)
        panel_layout.addWidget(particle_box)
        panel_layout.addWidget(display_box)
        panel_layout.addWidget(actions_box)
        panel_layout.addWidget(hint)
        panel_layout.addStretch(1)

        root_layout.addWidget(panel)
        root_layout.addWidget(self.render_widget, 1)

        self._toggle_custom_inputs(False)
        self._update_particle_parameters()

    def _sync_field_description(self) -> None:
        key = self.field_combo.currentData()
        field = next(item for item in PRESET_FIELDS if item.key == key)
        self.description_label.setText(field.description)
        self._toggle_custom_inputs(key == "custom")

    def _toggle_custom_inputs(self, enabled: bool) -> None:
        self.ux_edit.setEnabled(enabled)
        self.uy_edit.setEnabled(enabled)

    def _apply_field(self) -> None:
        key = self.field_combo.currentData()
        try:
            field = VectorField(key, self.ux_edit.text(), self.uy_edit.text())
        except Exception as error:  # noqa: BLE001
            QMessageBox.critical(self, "Ошибка поля", f"Не удалось разобрать пользовательское поле.\n\n{error}")
            return

        self.render_widget.set_field(field)

    def _update_streamline_quality(self, value: int) -> None:
        self.streamline_quality_label.setText(f"Гладкость линий: {value}")
        self.render_widget.set_streamline_quality(value)

    def _update_particle_parameters(self) -> None:
        radius_meters = self.radius_spin.value() * 1e-3
        self.render_widget.set_particle_spawn_parameters(
            radius_meters,
            self.density_spin.value(),
            self.initial_vx_spin.value(),
            self.initial_vy_spin.value(),
        )