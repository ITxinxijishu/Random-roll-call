import os
from django.conf import settings

def get_banji_path():
    return os.path.join(settings.BASE_DIR, 'banji.txt')

def get_class_path(class_id):
    return os.path.join(settings.BASE_DIR, f'{class_id}.txt')

def read_all_banji():
    """读取所有班级编号"""
    try:
        with open(get_banji_path(), 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def save_all_banji(banji_list):
    """保存班级列表"""
    with open(get_banji_path(), 'w', encoding='utf-8') as f:
        f.write('\n'.join(banji_list))

def read_class_students(class_id):
    """读取指定班级的学生"""
    try:
        with open(get_class_path(class_id), 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def save_class_students(class_id, students):
    """保存班级学生名单"""
    with open(get_class_path(class_id), 'w', encoding='utf-8') as f:
        f.write('\n'.join(students))

def class_exists(class_id):
    """检查班级是否存在"""
    return os.path.exists(get_class_path(class_id))