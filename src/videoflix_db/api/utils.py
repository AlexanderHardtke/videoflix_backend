def get_video_file(video, quality):
    file_map = {
        '1080p': 'file1080p',
        '720p': 'file720p',
        '360p': 'file360p',
        '240p': 'file240p',
    }
    field_name = file_map.get(quality)
    return getattr(video, field_name, None) if field_name else None


def get_range(range_header, file_size):
    try:
        byte_range = range_header.split('=')[1]
        start_str, end_str = byte_range.split('-')
        start = int(start_str)
        end = int(end_str) if end_str else file_size - 1
        if start > end or start >= file_size:
            raise ValueError
        length = end - start + 1
        return start, end, length
    except (ValueError, IndexError):
        return 0, file_size - 1, file_size


def read_range(path, start, end, block_size=8192):
    with open(path, 'rb') as file:
        file.seek(start)
        bytes_left = end - start + 1
        while bytes_left > 0:
            chunk_size = min(block_size, bytes_left)
            data = file.read(chunk_size)
            if not data:
                break
            yield data
            bytes_left -= len(data)
