#-----Dependency installation-----
#|       pip install pillow       |
#---------------------------------
import os
import argparse
from PIL import Image

def convert_jpeg_to_png(input_path, output_path=None, quality=95):
    """
    将 JPEG 图像转换为 PNG 格式
    
    参数:
        input_path (str): 输入的 JPEG 文件路径
        output_path (str): 输出的 PNG 文件路径（可选）
        quality (int): 输出质量（1-100），默认 95
    """
    try:
        # 打开 JPEG 图像
        with Image.open(input_path) as img:
            # 如果未指定输出路径，则修改扩展名
            if output_path is None:
                base_name = os.path.splitext(input_path)[0]
                output_path = f"{base_name}.png"
            
            # 保存为 PNG
            img.save(output_path, "PNG", quality=quality)
            print(f"转换成功: {input_path} -> {output_path}")
    
    except Exception as e:
        print(f"转换失败: {input_path} - {str(e)}")

def main():
    # 设置命令行参数
    parser = argparse.ArgumentParser(description="将 JPEG 图像转换为 PNG 格式")
    parser.add_argument("input", help="输入的 JPEG 文件或目录路径")
    parser.add_argument("-o", "--output", help="输出的 PNG 文件或目录路径（可选）")
    parser.add_argument("-q", "--quality", type=int, default=95, 
                        help="输出质量 (1-100)，默认 95")
    
    args = parser.parse_args()
    
    # 检查输入是文件还是目录
    if os.path.isfile(args.input):
        # 单个文件转换
        convert_jpeg_to_png(args.input, args.output, args.quality)
    elif os.path.isdir(args.input):
        # 目录批量转换
        input_dir = args.input
        output_dir = args.output if args.output else input_dir
        
        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 遍历目录中的 JPEG 文件
        for filename in os.listdir(input_dir):
            if filename.lower().endswith((".jpeg", ".jpg")):
                input_path = os.path.join(input_dir, filename)
                base_name = os.path.splitext(filename)[0]
                output_path = os.path.join(output_dir, f"{base_name}.png")
                convert_jpeg_to_png(input_path, output_path, args.quality)
    else:
        print(f"错误: 输入路径 '{args.input}' 不存在")

if __name__ == "__main__":
    main()
