import logging
import sys
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name: str) -> logging.Logger:
    """
    Khởi tạo và cấu hình Logger chuẩn.
    Ghi log ra cả Console (màn hình) và File (để debug sau này).
    """
    logger = logging.getLogger(name)
    
    # Nếu logger đã được cấu hình rồi thì không cấu hình lại tránh duplicate log
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    # Định dạng Log: [Thời gian] -[Tên module] - [Cấp độ] - Nội dung
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 1. Handler in ra Console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. Handler ghi ra File (Tạo file log tự động xoay vòng nếu dung lượng quá lớn)
    os.makedirs("logs", exist_ok=True)
    file_handler = RotatingFileHandler(
        "logs/app.log", maxBytes=5*1024*1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Khởi tạo một logger mặc định cho ứng dụng
app_logger = setup_logger("uit_chatbot")