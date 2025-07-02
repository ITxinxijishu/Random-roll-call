import os
import random
import datetime
from django.shortcuts import render
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone  # 用于时区处理
from .models import Attendance  # 导入模型
from django.db import models  # 添加这一行
from django.shortcuts import render, redirect, get_object_or_404
from .models import Student, Class
from django.shortcuts import render, redirect
from .file_utils import *
from django.db.models import Count, Q, Max

def manage_banji(request):
    # 班级管理
    if request.method == 'POST':
        # 添加班级
        if 'add_banji' in request.POST:
            new_id = request.POST.get('new_id')
            if new_id:
                banji_list = read_all_banji()
                if new_id not in banji_list:
                    banji_list.append(new_id)
                    save_all_banji(banji_list)
                    # 创建空班级文件
                    open(get_class_path(new_id), 'w').close()
        
        # 删除班级
        elif 'delete_banji' in request.POST:
            del_id = request.POST.get('delete_banji')
            banji_list = read_all_banji()
            if del_id in banji_list:
                banji_list.remove(del_id)
                save_all_banji(banji_list)
                # 删除班级文件
                if class_exists(del_id):
                    os.remove(get_class_path(del_id))
        
        return redirect('manage_banji')
    
    banji_list = sorted(read_all_banji(), key=lambda x: int(x))
    return render(request, 'banji.html', {'banji_list': banji_list})

def manage_students(request, class_id):
    # 学生管理
    if not class_exists(class_id):
        return redirect('manage_banji')
    
    students = read_class_students(class_id)
    
    if request.method == 'POST':
        # 添加学生
        if 'add_student' in request.POST:
            new_name = request.POST.get('new_name')
            if new_name and new_name not in students:
                students.append(new_name)
                save_class_students(class_id, students)
        
        # 删除学生
        elif 'delete_student' in request.POST:
            del_name = request.POST.get('delete_student')
            if del_name in students:
                students.remove(del_name)
                save_class_students(class_id, students)
        
        # 修改学生
        elif 'edit_student' in request.POST:
            old_name = request.POST.get('old_name')
            new_name = request.POST.get('new_name')
            if old_name in students and new_name:
                index = students.index(old_name)
                students[index] = new_name
                save_class_students(class_id, students)
        
        return redirect('manage_students', class_id=class_id)
    
    return render(request, 'students.html', {
        'class_id': class_id,
        'students': students
    })

def get_current_reset_time():
    time_path = os.path.join(settings.BASE_DIR, 'time.txt')
    try:
        with open(time_path, 'r', encoding='utf-8') as f:
            times = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return None

    reset_times = []
    for t in times:
        try:
            hour, minute = map(int, t.split(':'))
            reset_times.append(datetime.time(hour, minute))
        except ValueError:
            continue

    if not reset_times:
        return None

    reset_times.sort()
    now = datetime.datetime.now().time()
    current_reset_time = None

    for rt in reset_times:
        if rt <= now:
            current_reset_time = rt
        else:
            break

    if current_reset_time is None:
        current_reset_time = reset_times[-1]

    return current_reset_time


def index(request):
    # 读取班级列表
    banji_path = os.path.join(settings.BASE_DIR, 'banji.txt')
    with open(banji_path, 'r', encoding='utf-8') as f:
        classes = [line.strip() for line in f if line.strip()]

    selected_student = None
    selected_class = None
    current_reset_time = get_current_reset_time()

    # 从会话中获取上次选择的班级和学生
    last_selected_class = request.session.get('last_selected_class')
    last_selected_student = request.session.get('last_selected_student')

    if request.method == 'POST':
        selected_class = request.POST.get('class_num')
        if selected_class:
            # 更新会话中保存的班级
            request.session['last_selected_class'] = selected_class

            # 处理班级状态初始化（保持原有逻辑不变）
            last_reset = cache.get(f'{selected_class}_last_reset')
            need_initialize = last_reset != current_reset_time

            try:
                if need_initialize:
                    file_path = os.path.join(settings.BASE_DIR, f'{selected_class}.txt')
                    with open(file_path, 'r', encoding='utf-8') as f:
                        students = [line.strip() for line in f if line.strip()]
                    random.shuffle(students)
                    cache.set(f'{selected_class}_remaining', students.copy(), None)
                    cache.set(f'{selected_class}_called', [], None)
                    cache.set(f'{selected_class}_last_reset', current_reset_time, None)
                else:
                    remaining = cache.get(f'{selected_class}_remaining')
                    if not remaining:
                        file_path = os.path.join(settings.BASE_DIR, f'{selected_class}.txt')
                        with open(file_path, 'r', encoding='utf-8') as f:
                            students = [line.strip() for line in f if line.strip()]
                        random.shuffle(students)
                        cache.set(f'{selected_class}_remaining', students.copy(), None)
                        cache.set(f'{selected_class}_called', [], None)

                # 进行点名操作
                remaining = cache.get(f'{selected_class}_remaining')
                called = cache.get(f'{selected_class}_called')

                if remaining:
                    selected_student = remaining.pop(0)
                    called.append(selected_student)
                    cache.set(f'{selected_class}_remaining', remaining, None)
                    cache.set(f'{selected_class}_called', called, None)
                    
                    # 保存点名记录到数据库，精确到秒
                    Attendance.objects.create(
                        student_name=selected_student,
                        class_name=selected_class,
                        timestamp=timezone.now()  # 记录精确到秒的时间
                    )
                else:
                    selected_student = "所有学生都已点名"
                    # 即使没有点名成功，也要记录尝试
                    Attendance.objects.create(
                        student_name="点名完成",
                        class_name=selected_class,
                        timestamp=timezone.now()
                    )

                # 更新会话中保存的学生
                request.session['last_selected_student'] = selected_student

            except FileNotFoundError:
                selected_student = "班级文件不存在"
                # 记录错误信息
                Attendance.objects.create(
                    student_name="错误：班级文件不存在",
                    class_name=selected_class,
                    timestamp=timezone.now()
                )

    else:
        # GET 请求：使用上次保存的班级和学生
        selected_class = last_selected_class
        selected_student = last_selected_student

    # 获取最近7天的点名统计数据（用于页面展示）
    from django.db.models import Count
    recent_attendance = Attendance.objects.values('timestamp__date')\
        .annotate(date_count=Count('id'))\
        .order_by('-timestamp__date')[:7]
    
    # 获取各班级的总点名次数
    class_totals = Attendance.objects.values('class_name')\
        .annotate(total=Count('id'))\
        .order_by('-total')
    
    return render(request, 'index.html', {
        'classes': classes,
        'selected_student': selected_student,
        'selected_class': selected_class,
        'current_reset_time': current_reset_time,
        'recent_attendance': recent_attendance,
        'class_totals': class_totals
    })


def attendance_statistics(request):
    # 从文件获取班级列表
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    banji_path = os.path.join(BASE_DIR, 'banji.txt')
    
    classes = []
    if os.path.exists(banji_path):
        with open(banji_path, 'r', encoding='utf-8') as f:
            classes = [line.strip() for line in f if line.strip()]
    
    # 获取统计数据
    stats = {}
    
    # 按班级分组统计
    class_stats = Attendance.objects.values('class_name').annotate(
        total_attendances=Count('id'),
        last_time=Max('timestamp')
    ).order_by('-total_attendances')
    
    # 按日期分组统计
    date_stats = Attendance.objects.values('timestamp__date').annotate(
        total_attendances=Count('id'),
        last_time=Max('timestamp')
    ).order_by('-timestamp__date')
    
    # 按学生分组统计
    student_stats = Attendance.objects.values('student_name').annotate(
        total_attendances=Count('id'),
        last_time=Max('timestamp')
    ).order_by('-total_attendances')
    
    # 按班级和学生分组统计
    class_student_stats = Attendance.objects.values(
        'class_name', 'student_name'
    ).annotate(
        total_attendances=Count('id'),
        last_time=Max('timestamp')
    ).order_by('-total_attendances')
    
    # 按日期和学生分组统计
    date_student_stats = Attendance.objects.values(
        'timestamp__date', 'student_name'
    ).annotate(
        total_attendances=Count('id'),
        last_time=Max('timestamp')
    ).order_by('-total_attendances')
    
    # 按班级和日期分组统计
    class_date_stats = Attendance.objects.values(
        'class_name', 'timestamp__date'
    ).annotate(
        total_attendances=Count('id'),
        last_time=Max('timestamp')
    ).order_by('-total_attendances')
    
    return render(request, "attendance/statistics.html", {
        'classes': classes,
        'class_stats': class_stats,
        'date_stats': date_stats,
        'student_stats': student_stats,
        'class_student_stats': class_student_stats,
        'date_student_stats': date_student_stats,
        'class_date_stats': class_date_stats
    })