import argparse
import os
import cv2
import numpy as np
import pysrt

def timecode(time):
    return time.hour * 3600 + time.minute * 60 + time.second + time.microsecond / 1000000

# 将图片粘贴到背景图上
def paste_image(background, image, x, y):
    image_height, image_width, _ = image.shape
    bg_height, bg_width, _ = background.shape
    x_offset = int(x - (image_width / 2))
    print(f'x={x}, y={y}, image.shape={image.shape}')

    if x_offset < 0:
        image = image[:, abs(x_offset):]
        image_width -= abs(x_offset)
        x_offset = 0

    if x_offset + image_width > bg_width:
        image = image[:, :bg_width - x_offset]
        image_width = bg_width - x_offset

    if y < 0:
        image = image[abs(y):, :]
        image_height -= abs(y)
        y = 0

    if y + image_height > bg_height:
        image = image[:bg_height - y, :]
        image_height = bg_height - y

    if image_height <= 0 or image_width <= 0:
        return background
    
    # 用布尔索引选择需要更新的像素坐标
    inds = np.where(image[:,:,3]>0) 
    i,j = inds[0]+y, inds[1]+x_offset

    # 用数组直接更新
    background[i,j,0:3] = image[inds[0],inds[1],0:3] 
    background[i,j,3] = image[inds[0],inds[1],3]
    return background

def validate_image_path(path):
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(f"Invalid image path: {path} does not exist")
    if not path.endswith(".png"):
        raise argparse.ArgumentTypeError("Invalid image format: only PNG images are supported")
    return path

def validate_srt_path(path):
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(f"Invalid SRT file path: {path} does not exist")
    if not path.endswith(".srt"):
        raise argparse.ArgumentTypeError("Invalid SRT file format: only SRT files are supported")
    return path

def srt_insert_image(image_path: str, 
                     srt_path: str, 
                     position_height: int, 
                     output_path: str, 
                     scale_factor: float, 
                     background_size, 
                     timecode_strategy, 
                     auto_raised_height: int,
                     total_time = None
                     ):
    # 加载字幕文件
    subtitles = pysrt.open(srt_path)

    # 加载图片
    image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    image = cv2.resize(image, None, fx=scale_factor, fy=scale_factor)
    img_h, img_w, _ = image.shape

    print(f'image.shape = {image.shape}')

    # 创建空白背景图
    background = np.zeros((background_size[1], background_size[0], 4), dtype=np.uint8)
    bg_height, bg_width, _ = background.shape

    if total_time is None:
        total_time = timecode(subtitles[-1].end.to_time())
    last_locate = None

    # 解析字幕数据
    for subtitle in subtitles:
        start_time = timecode(subtitle.start.to_time())
        end_time = timecode(subtitle.end.to_time())
        duration = timecode((subtitle.end - subtitle.start).to_time())

        ratio = end_time / (total_time)
        if timecode_strategy == 'start':
            ratio = start_time / (total_time)
        elif timecode_strategy == 'middle':
            ratio = (start_time + duration/2) / (total_time)
        
        x = int(bg_width * ratio)
        y = int(bg_height - position_height - img_h)
        if last_locate is None:
            last_locate = (x, y)
        else:
            if x < last_locate[0] + img_w:
                if y == last_locate[1]:
                    y = y - auto_raised_height
                elif y < last_locate[1]:
                    pass
                elif y > last_locate[1]:
                    y = last_locate[1] - auto_raised_height

            last_locate = (x, y)

        # 粘贴图片到背景图上
        background = paste_image(background, image, x, y)

    # 保存透明图像为PNG格式
    cv2.imencode('.png', background)[1].tofile(output_path)

def main():
    parser = argparse.ArgumentParser(description="Image Processing Script")
    parser.add_argument("image_path", type=validate_image_path, help="path to the input PNG image")
    parser.add_argument("srt_path", type=validate_srt_path, help="path to the input SRT file")
    parser.add_argument("position_height", type=int, help="position height")
    parser.add_argument("-o", "--output", default="out.png", help="output image path (default: out.png)")
    parser.add_argument("-s", "--scale", type=float, default=1.0, help="image scaling factor")
    parser.add_argument("-a", "--auto_raised_height", type=int, default=30, help="auto raised height")
    parser.add_argument("-b", "--background-size", nargs=2, type=int, default=[1920, 1080],
                        metavar=("WIDTH", "HEIGHT"), help="background image size (default: 1920x1080)")
    parser.add_argument('-t', '--timecode_strategy', default='end', choices=['start', 'end', 'middle'], 
                    help='timecode strategy, must be "start", "end" or "middle", default is "end"')
    args = parser.parse_args()

    # 从命令行参数中获取值
    image_path = args.image_path
    position_height = args.position_height
    srt_path = args.srt_path
    output_path = args.output
    scale_factor = args.scale
    auto_raised_height = args.auto_raised_height
    background_size = tuple(args.background_size)
    timecode_strategy = args.timecode_strategy

    print("Image Path:", image_path)
    print("Position Height:", position_height)
    print("SRT Path:", srt_path)
    print("Output Path:", output_path)
    print("Scale Factor:", scale_factor)
    print("Auto Raised Height:", auto_raised_height)
    print("Background Size:", background_size)
    print("Timecode Strategy:", timecode_strategy)

    srt_insert_image(image_path, srt_path, position_height, output_path, scale_factor, background_size, timecode_strategy, auto_raised_height)

if __name__ == "__main__":
    main()
