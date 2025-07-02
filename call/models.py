from django.db import models
from django.utils import timezone

class Attendance(models.Model):
    student_name = models.CharField(max_length=100, verbose_name="学生姓名")
    class_name = models.CharField(max_length=100, verbose_name="班级名称")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="点名时间")

    def __str__(self):
        return f"{self.class_name} - {self.student_name} ({self.timestamp})"

    class Meta:
        indexes = [
            models.Index(fields=["student_name"]),
            models.Index(fields=["class_name", "student_name"]),
        ]


class Class(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="班级名称")
    
    def __str__(self):
        return self.name

class Student(models.Model):
    name = models.CharField(max_length=100, verbose_name="学生姓名")
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE, verbose_name="所属班级")
    
    def __str__(self):
        return f"{self.name} ({self.class_name})"