#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-

#  Undo the temporal transformation (Temporal inverse transform).

import os
import sys
from shell import Shell as shell
from GOP import GOP
from arguments_parser import arguments_parser
from colorlog import ColorLog
import logging

log = ColorLog(logging.getLogger("synthesize"))
log.setLevel('ERROR')
shell.setLogger(log)

MAX_SEARCH_RANGE = 128

parser = arguments_parser(description="Performs the temporal synthesis of a picture sequence.")
parser.GOPs()
parser.TRLs()
parser.block_size()
parser.pixels_in_x()
parser.pixels_in_y()
parser.subpixel_accuracy()
parser.border_size()
parser.block_overlaping()
parser.search_range()
parser.update_factor()

args = parser.parse_known_args()[0]
TRLs = int(args.TRLs)
GOPs = int(args.GOPs)
block_size = int(args.block_size)
pixels_in_x = int(args.pixels_in_x)
pixels_in_y = int(args.pixels_in_y)
subpixel_accuracy = int(args.subpixel_accuracy)
border_size = int(args.border_size)
block_overlaping = int(args.block_overlaping)
search_range = int(args.search_range)
update_factor = float(args.update_factor)

gop = GOP()
GOP_size = gop.get_size(TRLs)
pictures = (GOPs - 1) * GOP_size + 1
_search_range = search_range
_pictures = pictures

# Controls the increment of the search area between temporal levels
search_factor = 1

if TRLs > 1 :

    temporal_subband = 1
    while temporal_subband < (TRLs - 1) :

        search_range = search_range * search_factor
        if search_range > MAX_SEARCH_RANGE:
            search_range = MAX_SEARCH_RANGE

        pictures = (pictures + 1) // 2
        temporal_subband += 1


    while temporal_subband > 0 :
        shell.run("mctf synthesize_step"
                  + " --block_overlaping="  + str(block_overlaping)
                  + " --block_size="        + str(block_size)
                  + " --pictures="          + str(pictures)
                  + " --pixels_in_x="       + str(pixels_in_x)
                  + " --pixels_in_y="       + str(pixels_in_y)
                  + " --search_range="      + str(search_range)
                  + " --subpixel_accuracy=" + str(subpixel_accuracy)
                  + " --temporal_subband="  + str(temporal_subband)
                  + " --update_factor="     + str(update_factor))

        pictures = _pictures
        search_range = _search_range
        temporal_subband -= 1

        ## Initializes the variable, temporal subband a '1'.
        j = 1
        while j < temporal_subband :

            search_range = search_range * search_factor
            if search_range > MAX_SEARCH_RANGE:
                search_range = MAX_SEARCH_RANGE

            pictures = ( pictures + 1 ) // 2
            j += 1
