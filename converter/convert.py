from argparse import ArgumentParser
from dataclasses import dataclass, astuple
import zlib
from typing import Literal

type ConvertType = Literal['decode', 'encode']

@dataclass
class Arguments(object):
  convert_type: ConvertType
  i_path: str
  o_path: str

  @classmethod
  def from_cli(cls):
    parser = ArgumentParser(description="Convert Packet Tracer files between '.pkt' and '.xml' extensions")
    convert_type = parser.add_mutually_exclusive_group()
    convert_type.add_argument("-d", "--decode", help="Converts '.pkt' to '.xml'", action="store_true")
    convert_type.add_argument("-e", "--encode", help="Converts '.xml' to '.pkt'", action="store_true")
    parser.add_argument("i_path", help="Input file path", action="store", type=str)
    parser.add_argument("o_path", help="Output file path", action="store", type=str)

    arguments = parser.parse_args()

    return cls(
      convert_type='decode' if arguments.decode else 'encode',
      i_path=arguments.i_path,
      o_path=arguments.o_path
    )

def readfile(path: str) -> bytearray:
  with open(path, 'rb') as file:
    return bytearray(file.read())

def writefile(path: str, data: bytes):
  with open(path, 'wb') as file:
    file.write(data)

def decode(i_path: str, o_path: str):
  print('Decoding...')
  i_data = readfile(i_path)
  i_size = len(i_data)

  print(f"  - Opening Packet Tracer file '{i_path}' ")
  print(f"  - File size compressed = {i_size:d} bytes")

  o_data = bytearray()
  for byte in i_data:
    o_data.append((byte ^ i_size).to_bytes(4, "little")[0])
    i_size = i_size - 1

  header, content = o_data[:4], o_data[4:]
  o_size = int.from_bytes(header, byteorder='big')
  print(f"  - File size uncompressed = {o_size:d} bytes")
  print(f"  - Writing XML to '{o_path}'")

  deco = zlib.decompress(content)
  writefile(o_path, deco)

def encode(i_path: str, o_path: str):
  print('Encoding...')
  i_data = readfile(i_path)
  i_size = len(i_data)

  print(f"  - Opening XML file '{i_path}' ")
  print(f"  - IFile size = {i_size:d} bytes")

  i_size = i_size.to_bytes(4, 'big')

  d_data = zlib.compress(i_data)
  d_data = i_size + d_data
  d_size = len(d_data)
  print(f"  - OFile size = {d_size:d} bytes")

  o_data = bytearray()
  for byte in d_data:
    o_data.append((byte ^ d_size).to_bytes(4, "little")[0])
    d_size = d_size - 1

  print(f"  - Writing '.pkt' as '{o_path}'")
  writefile(o_path, o_data)

def main():
  arguments = Arguments(
    convert_type='decode',
    i_path='./input.pkt',
    o_path='./output.xml'
  )

  (convert_type, i_path, o_path) = astuple(arguments)
  match convert_type:
    case 'decode':
      decode(i_path, o_path)
    case 'encode':
      encode(i_path, o_path)

if __name__ == "__main__":
  main()
