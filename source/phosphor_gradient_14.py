import gc9a01
import struct
## https://colordesigner.io/gradient-generator

_gradient_rgb = [ (10, 15, 10),(10, 15, 10),  (15, 22, 15), (19, 31, 20), (24, 47, 26), (28, 64, 32), (31, 82, 39), 
                 (34, 100, 45), (37, 118, 51), (38, 138, 57), (40, 157, 63), (41, 177, 68), 
                 (41, 198, 74), (41, 219, 80), (41, 240, 85), (150, 255, 200) ]

phosphor_gradient = [gc9a01.color565(r,g,b) for r,g,b in _gradient_rgb]

