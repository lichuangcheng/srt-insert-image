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

    if x + image_width > bg_width or y + image_height > bg_height or y < 0:
        print('Error x + image_width > bg_width or y + image_height > bg_height')
        print(f'x={x}, y={y}, image_width={image_width}, image_height={image_height}, bg_height={bg_height}, bg_width={bg_width}')
        return background

    background[y:y+image_height, x:x+image_width] = image
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

def main():
    parser = argparse.ArgumentParser(description="Image Processing Script")
    parser.add_argument("image_path", type=validate_image_path, help="path to the input PNG image")
    parser.add_argument("srt_path", type=validate_srt_path, help="path to the input SRT file")
    parser.add_argument("position_height", type=int, help="position height")
    parser.add_argument("-o", "--output", default="out.png", help="output image path (default: out.png)")
    parser.add_argument("-s", "--scale", type=float, default=1.0, help="image scaling factor")
    parser.add_argument("-b", "--background-size", nargs=2, type=int, default=[1920, 1080],
                        metavar=("WIDTH", "HEIGHT"), help="background image size (default: 1920x1080)")

    args = parser.parse_args()

    # 从命令行参数中获取值
    image_path = args.image_path
    position_height = args.position_height
    srt_path = args.srt_path
    output_path = args.output
    scale_factor = args.scale
    background_size = tuple(args.background_size)

    # 在这里执行你的图像处理逻辑和 SRT 文件处理逻辑
    print("Image Path:", image_path)
    print("Position Height:", position_height)
    print("SRT Path:", srt_path)
    print("Output Path:", output_path)
    print("Scale Factor:", scale_factor)
    print("Background Size:", background_size)

    # 加载字幕文件
    subtitles = pysrt.open(srt_path)

    # 加载图片
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    print(f'image.shape = {image.shape}')

    # 创建空白背景图
    background = np.zeros((1080, 1920, 4), dtype=np.uint8)  # 1080P大小
    # background[:, :, 3] = 255  # 将透明度通道设置为不透明（255）

    total_time = subtitles[-1].end.to_time()

    # 解析字幕数据
    for subtitle in subtitles:
        start_time = timecode(subtitle.start.to_time())
        duration = timecode((subtitle.end - subtitle.start).to_time())
        ratio = (start_time + duration/2) / timecode(total_time)
        print(ratio)

        # 粘贴图片到背景图上
        bg_height, bg_width, _ = background.shape
        background = paste_image(background, image, int(bg_width * ratio), int(bg_height - image.shape[0]))

    # 缩小背景图
    background = cv2.resize(background, None, fx=0.5, fy=0.5)

    # 保存透明图像为PNG格式
    cv2.imwrite('background.png', background)

    # 显示结果图像
    cv2.imshow('Result', background)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
