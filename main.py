#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from destination_onedrive import DestinationOnedrive

if __name__ == "__main__":
    DestinationOnedrive().run(sys.argv[1:])
