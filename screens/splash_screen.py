from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect
from PyQt6.QtCore import QTimer, QPropertyAnimation, QEasingCurve
from PyQt6 import uic

from utils.window_manager import switch_window


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/splash_screen.ui", self)

        # Hiệu ứng fade-out sau 3 giây
        self.effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.effect)
        self.effect.setOpacity(1.0)

        QTimer.singleShot(3000, self.bat_dau_fade_out)

    def bat_dau_fade_out(self):
        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.finished.connect(self.chuyen_sang_login)
        self.animation.start()

    def chuyen_sang_login(self):
        from screens.login_screen import LoginScreen
        switch_window(LoginScreen())
