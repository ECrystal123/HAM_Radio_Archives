import tkinter as tk
from tkinter import filedialog
import zlib
import struct

class PNGViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("PNG 查看器")
        
        # 创建菜单
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="打开", command=self.open_file)
        filemenu.add_separator()
        filemenu.add_command(label="退出", command=root.quit)
        menubar.add_cascade(label="文件", menu=filemenu)
        root.config(menu=menubar)
        
        # 创建画布
        self.canvas = tk.Canvas(root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 状态栏
        self.status = tk.Label(root, text="就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(fill=tk.X)
        
        # 图像数据
        self.image_data = None
        self.width = 0
        self.height = 0
        self.bit_depth = 0
        self.color_type = 0
        self.compression = 0
        self.filter_method = 0
        self.interlace_method = 0
    
    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PNG 图片", "*.png")])
        if not file_path:
            return
            
        try:
            with open(file_path, "rb") as f:
                self.parse_png(f)
                self.display_image()
            self.status.config(text=f"已加载: {file_path} - {self.width}x{self.height}")
        except Exception as e:
            self.status.config(text=f"错误: {str(e)}")
    
    def parse_png(self, file):
        # 检查PNG签名
        signature = file.read(8)
        if signature != b'\x89PNG\r\n\x1a\n':
            raise ValueError("不是有效的PNG文件")
        
        # 解析IHDR块
        chunk = self.read_chunk(file)
        if chunk[0] != b'IHDR':
            raise ValueError("第一个块不是IHDR")
        
        # 解析IHDR数据
        self.width, self.height = struct.unpack(">II", chunk[1][:8])
        self.bit_depth = chunk[1][8]
        self.color_type = chunk[1][9]
        self.compression = chunk[1][10]
        self.filter_method = chunk[1][11]
        self.interlace_method = chunk[1][12]
        
        # 查找IDAT块
        idat_data = bytearray()
        while True:
            chunk = self.read_chunk(file)
            if chunk[0] == b'IEND':
                break
            if chunk[0] == b'IDAT':
                idat_data.extend(chunk[1])
        
        # 解压IDAT数据
        decompressed = zlib.decompress(idat_data)
        
        # 处理扫描线
        bytes_per_pixel = self.get_bytes_per_pixel()
        stride = self.width * bytes_per_pixel
        self.image_data = bytearray()
        
        for i in range(self.height):
            filter_type = decompressed[i * (stride + 1)]
            scanline = decompressed[i * (stride + 1) + 1 : (i + 1) * (stride + 1)]
            
            # 应用过滤器 (这里只处理无过滤的情况)
            if filter_type != 0:
                raise ValueError("只支持无过滤的PNG")
            
            self.image_data.extend(scanline)
    
    def read_chunk(self, file):
        length = struct.unpack(">I", file.read(4))[0]
        chunk_type = file.read(4)
        chunk_data = file.read(length)
        crc = file.read(4)
        return (chunk_type, chunk_data, crc)
    
    def get_bytes_per_pixel(self):
        if self.color_type == 0:  # 灰度
            return 1
        elif self.color_type == 2:  # RGB
            return 3
        elif self.color_type == 3:  # 调色板
            return 1
        elif self.color_type == 4:  # 灰度+alpha
            return 2
        elif self.color_type == 6:  # RGBA
            return 4
        else:
            raise ValueError(f"不支持的颜色类型: {self.color_type}")
    
    def display_image(self):
        # 清除画布
        self.canvas.delete("all")
        
        # 创建PhotoImage对象
        if self.color_type == 2:  # RGB
            image = tk.PhotoImage(width=self.width, height=self.height)
            for y in range(self.height):
                for x in range(self.width):
                    idx = (y * self.width + x) * 3
                    r = self.image_data[idx]
                    g = self.image_data[idx + 1]
                    b = self.image_data[idx + 2]
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    image.put(color, (x, y))
        elif self.color_type == 6:  # RGBA
            image = tk.PhotoImage(width=self.width, height=self.height)
            for y in range(self.height):
                for x in range(self.width):
                    idx = (y * self.width + x) * 4
                    r = self.image_data[idx]
                    g = self.image_data[idx + 1]
                    b = self.image_data[idx + 2]
                    a = self.image_data[idx + 3]
                    # 简单处理alpha - 混合到白色背景
                    if a < 255:
                        r = int(r * (a/255) + 255 * (1 - a/255))
                        g = int(g * (a/255) + 255 * (1 - a/255))
                        b = int(b * (a/255) + 255 * (1 - a/255))
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    image.put(color, (x, y))
        else:
            raise ValueError(f"不支持显示颜色类型: {self.color_type}")
        
        # 显示图像
        self.canvas.create_image(0, 0, anchor=tk.NW, image=image)
        self.canvas.image = image  # 保持引用
        
        # 调整窗口大小
        self.root.geometry(f"{self.width}x{self.height}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PNGViewer(root)
    root.mainloop()
