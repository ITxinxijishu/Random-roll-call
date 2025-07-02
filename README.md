# 随机点名系统（Random Roll Call）

本项目为一个基于 Django 的随机点名与班级管理系统，适用于课堂教学、学生点名、考勤和数据统计等场景。支持通过网页进行班级、学生的管理，以及点名历史统计分析。

## 功能介绍

- **随机点名**：可在网页上选择班级并进行随机点名，自动记录点名时间与学生信息。
- **班级管理**：支持班级的添加、删除、列表显示。
- **学生管理**：支持向班级添加、编辑、删除学生。
- **点名统计**：按班级、日期、学生、班级-学生、日期-学生、班级-日期多维度统计点名历史，支持筛选与可视化展示。
- **数据批量导入**：可通过 `banji.txt` 和各班级对应的txt文件批量导入班级与学生信息。
- **友好的 UI 界面**：采用 Bootstrap 美化，支持 PC 和移动端浏览。

## 目录结构简介

```
.
├── call/               # 核心Django应用，包含models、views、migrations等
├── roll_call/          # 项目主配置目录
├── templates/          # 前端模板(html)
├── static/             # 静态资源目录（如有）
├── manage.py           # Django管理脚本
├── import_data.py      # 数据批量导入脚本
├── banji.txt           # 班级编号列表，每行为一个编号
├── [班级编号].txt      # 每个班级的学生名单（如“1.txt”）
├── time.txt            # 点名时间点设置
└── README.md           # 项目说明
```

## 快速开始

### 1. 环境准备

- Python 3.8+
- 安装依赖包

```bash
pip install django
```

### 2. 数据准备

- 在项目根目录下准备 `banji.txt`，每行一个班级编号（如：`1`）。
- 为每个班级新增同名txt文件（如：`1.txt`），每行一个学生姓名。

### 3. 初始化数据库

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. 启动开发服务器

```bash
python manage.py runserver
```

访问 [http://127.0.0.1:8000/](http://127.0.0.1:8000/) 即可使用。

### 5. 数据批量导入（可选）

如需将txt数据批量导入数据库中的班级与学生表：

```bash
python import_data.py
```

## 部分核心文件说明

- `call/file_utils.py`：封装了班级和学生名单的文件操作。
- `call/models.py`：数据库模型设计，包括出勤、班级、学生等。
- `call/views.py`：主要视图逻辑，包括点名、统计、数据管理等。
- `templates/`：前端页面模板，均为美化后的 Bootstrap 风格。

## 统计与分析

在“/jilu/”页面，可按照多种方式查看点名历史统计，包括：

- 按班级、日期、学生、班级-学生、日期-学生、班级-日期等。

## 常见问题

- **页面样式不美观？** 请保证网络畅通以加载 Bootstrap CDN。
- **无法添加/删除数据？** 请确保项目目录有写权限，相关txt文件未被占用或损坏。
- **时区设置问题？** 默认采用 Asia/Shanghai（上海时区），可在 settings.py 调整。

## 参与贡献

欢迎 PR、Issue 交流建议与改进！

## License

MIT License

---

如需定制或问题反馈，请联系作者。"# -" 
