#-----Dependency installation -----
#|pip install pillow              |
#----------------------------------
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class PNGViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("PNG 查看器 ©2025 HRA")
        
        # 创建菜单
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="打开", command=self.open_file)
        filemenu.add_command(label="适应窗口", command=self.fit_to_window)
        filemenu.add_command(label="原始大小", command=self.original_size)
        filemenu.add_separator()
        filemenu.add_command(label="退出", command=root.quit)
        menubar.add_cascade(label="文件", menu=filemenu)
        
        # 添加视图菜单
        viewmenu = tk.Menu(menubar, tearoff=0)
        viewmenu.add_command(label="放大", command=self.zoom_in)
        viewmenu.add_command(label="缩小", command=self.zoom_out)
        menubar.add_cascade(label="视图", menu=viewmenu)
        
        root.config(menu=menubar)
        
        # 创建画布和滚动条
        self.canvas = tk.Canvas(root, bg="white")
        self.hscroll = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.vscroll = tk.Scrollbar(root, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.hscroll.set, yscrollcommand=self.vscroll.set)
        
        # 布局
        self.hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 状态栏
        self.status = tk.Label(root, text="就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(fill=tk.X)
        
        # 图像相关变量
        self.image = None
        self.tk_image = None
        self.zoom_level = 1.0
        self.original_size_flag = False
        
        # 绑定鼠标滚轮缩放
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)  # Windows
        self.canvas.bind("<Button-4>", self.on_mousewheel)    # Linux (向上滚动)
        self.canvas.bind("<Button-5>", self.on_mousewheel)    # Linux (向下滚动)
        
    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("PNG 图片", "*.png"), ("所有文件", "*.*")]
        )
        if not file_path:
            return
            
        try:
            # 使用Pillow打开图像
            self.image = Image.open(file_path)
            self.original_size_flag = False
            self.zoom_level = 1.0
            self.display_image()
            self.status.config(text=f"已加载: {file_path} - {self.image.width}x{self.image.height} - {self.image.mode}")
        except Exception as e:
            self.status.config(text=f"错误: {str(e)}")
    
    def display_image(self):
        if self.image is None:
            return
            
        # 清除画布
        self.canvas.delete("all")
        
        # 计算缩放后的尺寸
        if self.original_size_flag:
            new_width, new_height = self.image.width, self.image.height
        else:
            new_width = int(self.image.width * self.zoom_level)
            new_height = int(self.image.height * self.zoom_level)
        
        # 调整图像大小
        resized_image = self.image.resize((new_width, new_height), Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(resized_image)
        
        # 在画布上显示图像
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        self.canvas.config(scrollregion=(0, 0, new_width, new_height))
        
        # 更新状态栏
        self.status.config(text=f"尺寸: {self.image.width}x{self.image.height} | 显示: {new_width}x{new_height} | 缩放: {self.zoom_level*100:.0f}%")
    
    def fit_to_window(self):
        if self.image is None:
            return
            
        # 获取窗口尺寸
        window_width = self.canvas.winfo_width()
        window_height = self.canvas.winfo_height()
        
        # 计算适合窗口的缩放比例
        width_ratio = window_width / self.image.width
        height_ratio = window_height / self.image.height
        self.zoom_level = min(width_ratio, height_ratio)
        self.original_size_flag = False
        self.display_image()
    
    def original_size(self):
        self.original_size_flag = True
        self.zoom_level = 1.0
        self.display_image()
    
    def zoom_in(self):
        if self.image is None:
            return
        self.original_size_flag = False
        self.zoom_level *= 1.25
        self.display_image()
    
    def zoom_out(self):
        if self.image is None:
            return
        self.original_size_flag = False
        self.zoom_level *= 0.8
        if self.zoom_level < 0.1:
            self.zoom_level = 0.1
        self.display_image()
    
    def on_mousewheel(self, event):
        if self.image is None:
            return
            
        # Windows使用event.delta，Linux使用event.num
        delta = 0
        if event.num == 4 or (hasattr(event, 'delta') and event.delta > 0):
            delta = 1  # 向上滚动，放大
        elif event.num == 5 or (hasattr(event, 'delta') and event.delta < 0):
            delta = -1  # 向下滚动，缩小
        
        if delta > 0:
            self.zoom_in()
        elif delta < 0:
            self.zoom_out()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    app = PNGViewer(root)
    root.mainloop()
