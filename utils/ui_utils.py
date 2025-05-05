from PyQt5.QtWidgets import QMessageBox


def show_warning(parent, title, message):
    """Uyarı mesajı gösterir"""
    QMessageBox.warning(parent, title, message)


def show_info(parent, title, message):
    """Bilgi mesajı gösterir"""
    QMessageBox.information(parent, title, message)


def show_error(parent, title, message):
    """Hata mesajı gösterir"""
    QMessageBox.critical(parent, title, message)


def show_question(parent, title, message):
    """Soru mesajı gösterir ve kullanıcının cevabını döndürür"""
    reply = QMessageBox.question(
        parent,
        title,
        message,
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    return reply == QMessageBox.Yes 