from __future__ import annotations

import argparse
import os
import struct


def get_s3v0_header(file):
    header = {}
    magic = file.read(4)
    if magic != b'S3V0':
        raise ValueError('Invalid S3V0 magic')

    header['size'], header['original_size'], header['data_hash'] = struct.unpack(
        '<III', file.read(12),
    )
    file.read(16)  # skip 16 bytes
    return header


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', help='Input S3P file', required=True)
    args = parser.parse_args()

    with open(args.input, 'rb') as infile:
        magic = infile.read(4)
        if magic != b'S3P0':
            raise ValueError('Invalid S3P0 magic')

        num_files = struct.unpack('<I', infile.read(4))[0]
        index = []

        for i in range(num_files):
            offset, size = struct.unpack('<II', infile.read(8))
            index.append((offset, size))

        for i, (offset, size) in enumerate(index):
            infile.seek(offset, 0)
            header = get_s3v0_header(infile)
            data = infile.read(header['original_size'])
            output_file = os.path.join(f'{i}.wma')
            with open(output_file, 'wb') as outfile:
                outfile.write(data)
