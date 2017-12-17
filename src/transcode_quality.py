#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

# Quality transcoding.

# Extracts a codestream from a bigger one, discarding a number of
# quality subband-layers.

# Reducing the number of quality subband-layers basically means that
# the list:
#
# [L^{T-1}_{Q-1}, M^{T-1}_{q-1}, H^{T-1}_{Q-1}, M^{T-2}_{q-1}, H^{T-2}_{Q-1}, ..., M^1_{q-1}, H^1_{Q-1},
#  L^{T-1}_{Q-2}, M^{T-1}_{q-2}, H^{T-1}_{Q-2}, M^{T-2}_{q-2}, H^{T-2}_{Q-2}, ..., M^1_{q-2}, H^1_{Q-2},
#  :
#  L^{T-1}_0, -, H^{T-1}_0, H^{T-1}_0, H^{T-2}_0, ..., H^1_0]
#
# is going to be truncated at a subband-layer, starting at
# L^{T-1}_{Q-1}, where T=number of TRLs, Q=number of quality layers
# for texture, and q=number of quality layers for movement. A total
# number of TQ+q subband-layers are available. In the last set
# description, it has been supposed that q<Q.

# Examples:
#
#   mctf transcode_quality --QSLs=5

#import info_j2k
import sys
#import getopt
#import os
#import array
#import display
#import string
#import math
#import re
import subprocess as sub
from GOP              import GOP
from subprocess       import check_call
from subprocess       import CalledProcessError
from arguments_parser import arguments_parser

parser = arguments_parser(description="Transcodes a sequence transfering a number of quality subband-layers.")
parser.GOPs()
parser.motion_layers()
parser.pixels_in_x()
parser.add_argument("-QSLs",
parser.pixels_in_y()
                    help="Number of Quality Subband-Layers.",
                    default=1)
parser.SRLs()
parser.texture_layers()
parser.TRLs()

args = parser.parse_known_args()[0]
GOPs = int(args.GOPs)
motion_layers = int(args.motion_layers)
pixels_in_x = int(args.pixels_in_x)
pixels_in_y = int(args.pixels_in_y)
QSLs = int(args.QSLs)
SRLs = int(args.SRLs)
texture_layers = int(args.texture_layers)
TRLs = int(args.TRLs)

# We need to compute the number of quality layers of each temporal
# subband. For example, if QSLs=1, only the first quality layer of the
# subband L^{T-1} will be output. If QSLs=2, only the first quality
# layer of the subbands L^{T-1} and M^{T-1} will be output, if QSLs=3,
# the first quality layer of H^{T-1} will be output too, and so on.

def generate_list_of_subband_layers(T, Qt, Qm):
    l = []
    for q in range(Qt):
        l.append(('L', T-1, Qt-q-1))
        for t in range(T-1):
            if q < Qm:
                l.append(('M', T-t-1, Qm-q-1))
            l.append(('H', T-t-1, Qt-q-1))
    return l

all_subband_layers = generate_list_of_subband_layers(TRLs,
                                                     motion_layers,
                                                     texture_layers)

subband_layers_to_copy = all_subband_layers[:QSLs]
print("Subband layers to copy = {}".format(subband_layers_to_copy))

number_of_quality_layers_in_L = len([x for x in subband_layers_to_copy
                                    if x[0]=='L'])
print("Number of subband layers in L = {}".format(number_of_quality_layers_in_L))

number_of_quality_layers_in_H = [None]*TRLs
for i in range(TRLs):
    number_of_quality_layers_in_H[i] = len([x for x in subband_layers_to_copy
                                            if x[0]=='H' and x[1]==i])
    print("Number of quality layers in H[{}]={}".format(i, number_of_quality_layers_in_H[i]))
    
number_of_quality_layers_in_M = [None]*TRLs
for i in range(TRLs):
    number_of_quality_layers_in_M[i] = len([x for x in subband_layers_to_copy
                                            if x[0]=='M' and x[1]==i])
    print("Number of quality layers in M[{}]={}".format(i, number_of_quality_layers_in_M[i]))

def kdu_transcode(filename, layers):
    try:
        check_call("trace kdu_transcode Clayers=" + str(layers)
                   + " -i " + filename
                   + " -o " + "transcode_quality/" + filename,
                   shell=True)
    except CalledProcessError:
        sys.exit(-1)

pictures = GOPs * GOP_size + 1
        
# Transcoding of L subband
image_number = 0
while image_number < pictures:

    str_image_number = '%04d' % image_number

    filename = LOW + str(subband) + "_Y_" + str_image_number
    kdu_transcode(filename + ".j2c", number_of_quality_layers_in_L)

    filename = LOW + str(subband) + "_U_" + str_image_number
    kdu_transcode(filename + ".j2c", number_of_quality_layers_in_L)

    filename = LOW + str(subband) + "_V_" + str_image_number
    kdu_transcode(filename + ".j2c", number_of_quality_layers_in_L)

    image_number += 1
        
# Transcoding of H subbands
subband = TRLs - 1
while subband > 0:
    
    image_number = 0
    # pictures = 
    while image_number < pictures:

        str_image_number = '%04d' % image_number

        filename = HIGH + str(subband) + "_Y_" + str_image_number
        kdu_transcode(filename + ".j2c", number_of_quality_layers_in_H[subband])

        filename = HIGH + str(subband) + "_U_" + str_image_number
        kdu_transcode(filename + ".j2c", number_of_quality_layers_in_H[subband])

        filename = HIGH + str(subband) + "_V_" + str_image_number
        kdu_transcode(filename + ".j2c", number_of_quality_layers_in_H[subband])

        image_number += 1

    subband -= 1

# Transcoding of M "subbands"
subband = TRLs - 1
while subband > 0:

    field_number = 0
    fields = 4 
    while field_number < fields:

        str_field_number = '%04d' % field_number
        filename = MOTION + str(subband) + "_" + str(field_number) + ".j2c"
        kdu_transcode(filename, number_of_quality_layers_in_M[subband])