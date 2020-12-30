import os
import shutil
import zlib


def file_compress(origin_filepath, zipped_filepath, level=6):
    """文件压缩
    :param origin_filepath: 待压缩文件的路径
    :param zipped_filepath: 压缩后的文件的路径
    :param level: 压缩等级 0-9。0是仅打包，9是压缩效果最好但时间长。默认为6.
    """
    infile_io = open(origin_filepath, "rb")  # 待压缩的文件对象
    outfile_io = open(zipped_filepath, "wb")
    compress_obj = zlib.compressobj()
    data = infile_io.read(1024)  # 1024为读取的size参数
    while data:
        outfile_io.write(compress_obj.compress(data))  # 写入压缩数据
        data = infile_io.read(1024)  # 继续读取文件中的下一个size的内容
    outfile_io.write(compress_obj.flush())  # compress_obj.flush()包含剩余压缩输出的字节对象，将剩余的字节内容写入到目标文件中


def file_decompress(zipped_file_path, unzipped_file_path):
    """文件解压
    :param zipped_file_path:压缩文件的路径
    :param unzipped_file_path: 解压后文件释放的路径
    """

    infile = open(zipped_file_path, "rb")  # 待解压文件对象
    outfile = open(unzipped_file_path, "wb")  # 用于输出的文件对象
    decompress_obj = zlib.decompressobj()
    data = infile.read(1024)
    while data:
        outfile.write(decompress_obj.decompress(data))
        data = infile.read(1024)
    outfile.write(decompress_obj.flush())


if __name__ == '__main__':
    name = './hello'

    # fc.zip(name)
    # fc.unzip('tmp/' + name + '.zip')
    # fc.clean()
    z = fc.file_compress(name)
    d = fc.file_decompress(z)
    print(z)
    print(d)
