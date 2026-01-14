import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import psutil
import os
import time
import threading
import sys

class ServiceManager:
    def __init__(self, root):
        self.root = root
        self.root.title("服务管理器")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        # 设置主题
        self.setup_theme()
        
        # 设置项目路径
        if getattr(sys, 'frozen', False):
            # 当程序被打包成exe时，使用当前工作目录
            self.project_path = os.getcwd()
        else:
            # 当程序作为脚本运行时，使用文件所在目录
            self.project_path = os.path.dirname(os.path.abspath(__file__))
        
        self.backend_path = os.path.join(self.project_path, "backend")
        self.frontend_path = os.path.join(self.project_path, "frontend")
        
        # 服务进程
        self.backend_process = None
        self.frontend_process = None
        
        # 初始化UI
        self.setup_ui()
        
        # 启动状态监控线程
        self.status_thread = threading.Thread(target=self.check_service_status, daemon=True)
        self.status_thread.start()
        
    def setup_theme(self):
        """设置现代化主题"""
        # 创建自定义样式
        style = ttk.Style()
        
        # 确保使用经典主题，避免Windows主题冲突
        style.theme_use("clam")
        
        # 设置全局字体和样式 - 统一黑色文字
        style.configure(".", 
                       font=("Segoe UI", 11),
                       background="#f0f4f8",
                       foreground="#000000")
        
        # 主窗口背景色
        self.root.configure(bg="#f0f4f8")
        
        # 标题样式 - 黑色文字
        style.configure("Title.TLabel", 
                       font=("Segoe UI", 22, "bold"), 
                       foreground="#000000",
                       background="#f0f4f8")
        
        # 状态标签样式 - 黑色文字，仅状态值保持彩色
        style.configure("Status.TLabel", 
                       font=("Segoe UI", 14, "bold"),
                       foreground="#000000",
                       background="#ffffff")
        style.configure("Running.TLabel", 
                       foreground="#27ae60",
                       background="#ffffff")
        style.configure("Stopped.TLabel", 
                       foreground="#e74c3c",
                       background="#ffffff")
        
        # 文本样式 - 统一黑色文字
        style.configure("Text.TLabel", 
                       font=("Segoe UI", 11), 
                       foreground="#000000",
                       background="#ffffff")
        style.configure("Value.TLabel", 
                       font=("Segoe UI", 11, "bold"), 
                       foreground="#000000",
                       background="#ffffff")
        
        # 框架样式
        style.configure("Card.TFrame", 
                       background="#ffffff",
                       borderwidth=0,
                       relief="flat")
        
        # 标签框架样式 - 卡片样式
        style.configure("Card.TLabelframe", 
                       background="#ffffff",
                       borderwidth=1,
                       relief="solid",
                       bordercolor="#e0e0e0")
        style.configure("Card.TLabelframe.Label", 
                       font=("Segoe UI", 13, "bold"), 
                       foreground="#000000",
                       background="#ffffff")
        
        # 日志标签框架样式
        style.configure("Log.TLabelframe", 
                       background="#ffffff",
                       borderwidth=1,
                       relief="solid",
                       bordercolor="#e0e0e0")
        style.configure("Log.TLabelframe.Label", 
                       font=("Segoe UI", 13, "bold"), 
                       foreground="#000000",
                       background="#ffffff")
        
        # 重置按钮样式，使用更简单可靠的设置
        # 主按钮 - 使用标准ttk样式，确保文字清晰
        style.configure("Primary.TButton", 
                       font=("Segoe UI", 11, "bold"),
                       foreground="#000000",  # 改为黑色文字，确保在任何背景下都可见
                       background="#3498db",   # 蓝色背景
                       padding=(15, 8),
                       borderwidth=1,
                       relief="raised")
        
        # 简化状态变化，只保留必要的效果
        style.map("Primary.TButton", 
                  background=[("active", "#2980b9"),
                             ("disabled", "#cccccc")],
                  relief=[("pressed", "sunken"),
                          ("!pressed", "raised")])
        
        # 危险按钮 - 使用标准ttk样式，确保文字清晰
        style.configure("Danger.TButton", 
                       font=("Segoe UI", 11, "bold"),
                       foreground="#000000",  # 改为黑色文字，确保在任何背景下都可见
                       background="#e74c3c",   # 红色背景
                       padding=(15, 8),
                       borderwidth=1,
                       relief="raised")
        
        # 简化状态变化，只保留必要的效果
        style.map("Danger.TButton", 
                  background=[("active", "#c0392b"),
                             ("disabled", "#cccccc")],
                  relief=[("pressed", "sunken"),
                          ("!pressed", "raised")])
        
        # 滚动条样式
        style.configure("Vertical.TScrollbar",
                       background="#f0f4f8",
                       troughcolor="#e0e0e0",
                       arrowcolor="#666666",
                       borderwidth=0)
        style.map("Vertical.TScrollbar",
                 background=[("active", "#bdc3c7")])
        
    def setup_ui(self):
        """设置UI界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="25")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.configure(style="Card.TFrame")
        
        # 添加标题和描述
        title = ttk.Label(main_frame, text="智能股票筛选系统", style="Title.TLabel")
        title.pack(pady=(0, 5))
        
        subtitle = ttk.Label(main_frame, text="服务管理器", font=("Segoe UI", 12), foreground="#7f8c8d")
        subtitle.pack(pady=(0, 30))
        
        # 创建卡片容器
        cards_frame = ttk.Frame(main_frame)
        cards_frame.pack(fill=tk.X, pady=(0, 25))
        
        # 后端服务状态卡片
        backend_card = ttk.LabelFrame(cards_frame, text="后端服务", padding="25", style="Card.TLabelframe")
        backend_card.pack(fill=tk.X, pady=(0, 20))
        backend_card.configure(relief="flat", borderwidth=0, padding=(25, 20))
        
        backend_card_frame = ttk.Frame(backend_card)
        backend_card_frame.pack(fill=tk.X)
        
        # 后端状态显示
        backend_status_container = ttk.Frame(backend_card_frame)
        backend_status_container.pack(fill=tk.X, pady=(0, 20))
        
        # 左侧状态和右侧指示灯布局
        status_row = ttk.Frame(backend_status_container)
        status_row.pack(fill=tk.X, anchor="center")
        
        status_label = ttk.Label(status_row, text="当前状态: ", style="Text.TLabel")
        status_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.backend_status = ttk.Label(status_row, text="未运行", style="Status.TLabel Stopped.TLabel")
        self.backend_status.pack(side=tk.LEFT, padx=(0, 15))
        
        # 状态指示灯
        self.backend_indicator = ttk.Frame(status_row, width=12, height=12, style="Indicator.TFrame")
        self.backend_indicator.pack(side=tk.LEFT, padx=(0, 10))
        self.update_indicator(self.backend_indicator, "stopped")
        
        # 后端端口显示
        port_row = ttk.Frame(backend_status_container)
        port_row.pack(fill=tk.X, anchor="center")
        
        port_label = ttk.Label(port_row, text="监听端口: ", style="Text.TLabel")
        port_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.backend_port = ttk.Label(port_row, text="8000", style="Value.TLabel")
        self.backend_port.pack(side=tk.LEFT)
        
        # 后端按钮组
        backend_buttons = ttk.Frame(backend_card_frame)
        backend_buttons.pack(fill=tk.X)
        
        self.backend_start_btn = ttk.Button(backend_buttons, text="启动后端", command=self.start_backend, style="Primary.TButton")
        self.backend_start_btn.pack(side=tk.LEFT, padx=(0, 15), pady=5, fill=tk.X, expand=True)
        
        self.backend_stop_btn = ttk.Button(backend_buttons, text="停止后端", command=self.stop_backend, state=tk.DISABLED, style="Danger.TButton")
        self.backend_stop_btn.pack(side=tk.LEFT, pady=5, fill=tk.X, expand=True)
        
        # 前端服务状态卡片
        frontend_card = ttk.LabelFrame(cards_frame, text="前端服务", padding="25", style="Card.TLabelframe")
        frontend_card.pack(fill=tk.X, pady=(0, 20))
        frontend_card.configure(relief="flat", borderwidth=0, padding=(25, 20))
        
        frontend_card_frame = ttk.Frame(frontend_card)
        frontend_card_frame.pack(fill=tk.X)
        
        # 前端状态显示
        frontend_status_container = ttk.Frame(frontend_card_frame)
        frontend_status_container.pack(fill=tk.X, pady=(0, 20))
        
        # 左侧状态和右侧指示灯布局
        status_row = ttk.Frame(frontend_status_container)
        status_row.pack(fill=tk.X, anchor="center")
        
        status_label = ttk.Label(status_row, text="当前状态: ", style="Text.TLabel")
        status_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.frontend_status = ttk.Label(status_row, text="未运行", style="Status.TLabel Stopped.TLabel")
        self.frontend_status.pack(side=tk.LEFT, padx=(0, 15))
        
        # 状态指示灯
        self.frontend_indicator = ttk.Frame(status_row, width=12, height=12, style="Indicator.TFrame")
        self.frontend_indicator.pack(side=tk.LEFT, padx=(0, 10))
        self.update_indicator(self.frontend_indicator, "stopped")
        
        # 前端端口显示
        port_row = ttk.Frame(frontend_status_container)
        port_row.pack(fill=tk.X, anchor="center")
        
        port_label = ttk.Label(port_row, text="监听端口: ", style="Text.TLabel")
        port_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.frontend_port = ttk.Label(port_row, text="3000", style="Value.TLabel")
        self.frontend_port.pack(side=tk.LEFT)
        
        # 前端按钮组
        frontend_buttons = ttk.Frame(frontend_card_frame)
        frontend_buttons.pack(fill=tk.X)
        
        self.frontend_start_btn = ttk.Button(frontend_buttons, text="启动前端", command=self.start_frontend, style="Primary.TButton")
        self.frontend_start_btn.pack(side=tk.LEFT, padx=(0, 15), pady=5, fill=tk.X, expand=True)
        
        self.frontend_stop_btn = ttk.Button(frontend_buttons, text="停止前端", command=self.stop_frontend, state=tk.DISABLED, style="Danger.TButton")
        self.frontend_stop_btn.pack(side=tk.LEFT, pady=5, fill=tk.X, expand=True)
        
        # 操作日志卡片
        log_card = ttk.LabelFrame(main_frame, text="操作日志", padding="25", style="Log.TLabelframe")
        log_card.pack(fill=tk.BOTH, expand=True)
        log_card.configure(relief="flat", borderwidth=0, padding=(25, 20))
        

        
        # 日志文本框容器
        log_container = ttk.Frame(log_card)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        # 日志文本框 - 现代化设计
        self.log_text = tk.Text(log_container, height=14, state=tk.DISABLED, 
                               font=("Consolas", 10), 
                               bg="#f8f9fa", 
                               fg="#495057", 
                               borderwidth=1, 
                               relief="solid",
                               highlightthickness=0,
                               insertbackground="#3498db",
                               selectbackground="#e3f2fd",
                               selectforeground="#1976d2")
        self.log_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 10))
        
        # 日志文本框样式
        self.log_text.tag_configure("time", foreground="#95a5a6")
        self.log_text.tag_configure("info", foreground="#3498db")
        self.log_text.tag_configure("success", foreground="#27ae60")
        self.log_text.tag_configure("error", foreground="#e74c3c")
        
        # 滚动条 - 现代化设计
        scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        # 应用窗口样式
        self.root.update_idletasks()
        
    def update_indicator(self, indicator_frame, status):
        """更新状态指示灯"""
        for widget in indicator_frame.winfo_children():
            widget.destroy()
        
        # 创建圆形指示灯
        canvas = tk.Canvas(indicator_frame, width=12, height=12, bg="#ffffff", highlightthickness=0)
        canvas.pack()
        
        if status == "running":
            canvas.create_oval(1, 1, 11, 11, fill="#27ae60", outline="")
        else:
            canvas.create_oval(1, 1, 11, 11, fill="#e74c3c", outline="")
        
    def log(self, message, level="info"):
        """添加日志信息，支持不同级别"""
        self.log_text.config(state=tk.NORMAL)
        
        # 获取当前时间
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # 插入日志信息，使用不同颜色标签
        self.log_text.insert(tk.END, f"{current_time} - ", "time")
        
        if level == "success":
            self.log_text.insert(tk.END, f"{message}\n", "success")
        elif level == "error":
            self.log_text.insert(tk.END, f"{message}\n", "error")
        else:
            self.log_text.insert(tk.END, f"{message}\n", "info")
        
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def is_port_in_use(self, port):
        """检查端口是否被占用"""
        for conn in psutil.net_connections():
            if conn.status == 'LISTEN' and conn.laddr.port == port:
                return True
        return False
    
    def check_service_status(self):
        """检查服务状态"""
        while True:
            # 检查后端服务状态
            if self.is_port_in_use(8000):
                self.backend_status.config(text="运行中", style="Status.TLabel Running.TLabel")
                self.backend_start_btn.config(state=tk.DISABLED)
                self.backend_stop_btn.config(state=tk.NORMAL)
                self.update_indicator(self.backend_indicator, "running")
            else:
                self.backend_status.config(text="未运行", style="Status.TLabel Stopped.TLabel")
                self.backend_start_btn.config(state=tk.NORMAL)
                self.backend_stop_btn.config(state=tk.DISABLED)
                self.backend_process = None
                self.update_indicator(self.backend_indicator, "stopped")
            
            # 检查前端服务状态
            if self.is_port_in_use(3000):
                self.frontend_status.config(text="运行中", style="Status.TLabel Running.TLabel")
                self.frontend_start_btn.config(state=tk.DISABLED)
                self.frontend_stop_btn.config(state=tk.NORMAL)
                self.update_indicator(self.frontend_indicator, "running")
            else:
                self.frontend_status.config(text="未运行", style="Status.TLabel Stopped.TLabel")
                self.frontend_start_btn.config(state=tk.NORMAL)
                self.frontend_stop_btn.config(state=tk.DISABLED)
                self.frontend_process = None
                self.update_indicator(self.frontend_indicator, "stopped")
            
            time.sleep(2)
        

    

    
    def start_backend(self):
        """启动后端服务"""
        try:
            self.log("正在启动后端服务...", level="info")
            self.backend_process = subprocess.Popen(
                ["python", "main.py"],
                cwd=self.backend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True
            )
            self.log("后端服务启动命令已执行，正在初始化...", level="success")
        except Exception as e:
            self.log(f"启动后端服务失败: {str(e)}", level="error")
            messagebox.showerror("错误", f"启动后端服务失败: {str(e)}")
    
    def stop_backend(self):
        """停止后端服务"""
        try:
            self.log("正在停止后端服务...", level="info")
            # 查找并杀死占用8000端口的进程
            process_found = False
            for conn in psutil.net_connections():
                if conn.status == 'LISTEN' and conn.laddr.port == 8000:
                    process = psutil.Process(conn.pid)
                    process.terminate()
                    process.wait(timeout=5)
                    self.log(f"已终止后端进程 {conn.pid}", level="success")
                    process_found = True
            if not process_found:
                self.log("未找到运行中的后端进程", level="info")
            self.log("后端服务已停止", level="success")
        except Exception as e:
            self.log(f"停止后端服务失败: {str(e)}", level="error")
            messagebox.showerror("错误", f"停止后端服务失败: {str(e)}")
    
    def start_frontend(self):
        """启动前端服务"""
        try:
            self.log("正在启动前端服务...", level="info")
            self.frontend_process = subprocess.Popen(
                ["npm", "run", "dev", "--", "--port", "3000"],
                cwd=self.frontend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True
            )
            self.log("前端服务启动命令已执行，正在初始化...", level="success")
        except Exception as e:
            self.log(f"启动前端服务失败: {str(e)}", level="error")
            messagebox.showerror("错误", f"启动前端服务失败: {str(e)}")
    
    def stop_frontend(self):
        """停止前端服务"""
        try:
            self.log("正在停止前端服务...", level="info")
            # 查找并杀死占用3000端口的进程
            process_found = False
            for conn in psutil.net_connections():
                if conn.status == 'LISTEN' and conn.laddr.port == 3000:
                    process = psutil.Process(conn.pid)
                    process.terminate()
                    process.wait(timeout=5)
                    self.log(f"已终止前端进程 {conn.pid}", level="success")
                    process_found = True
            if not process_found:
                self.log("未找到运行中的前端进程", level="info")
            self.log("前端服务已停止", level="success")
        except Exception as e:
            self.log(f"停止前端服务失败: {str(e)}", level="error")
            messagebox.showerror("错误", f"停止前端服务失败: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ServiceManager(root)
    root.mainloop()