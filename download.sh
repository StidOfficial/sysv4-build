#!/bin/sh
archive_url="https://winworldpc.com/download/4061c39c-c39b-18c3-9a11-c3a4e284a2ef/from/c3ae6ee2-8099-713d-3411-c3a6e280947e"
archive_filename="AT&T UNIX System V Release 4 Version 2.1 (3.5).7z"

intel_archive_url="https://archive.org/download/intel-unix-sv-r4-v2/Intel%20Unix%20SVR4V2%20%285.25%20Floppy%29.zip"
intel_archive_name="Intel Unix SVR4V2 (5.25 Floppy)"

source_code_url="https://archive.org/download/ATTUNIXSystemVRelease4Version2/sysvr4.tar.bz2"
source_code_filename="sysvr4.tar.bz2"

if [ ! -f "$archive_filename" ]; then
        curl -L $archive_url -o "$archive_filename"
        7z x "$archive_filename"
fi

if [ ! -f "$intel_archive_name.zip" ]; then
        curl -L $intel_archive_url -o "$intel_archive_name.zip"
        unzip "$intel_archive_name.zip" -d "$intel_archive_name"
fi

if [ ! -f "$source_code_filename" ]; then
        curl -L $source_code_url -o "$source_code_filename"
        bzip2 -d $source_code_filename
        compress sysvr4.tar
        split -b 1474560 sysvr4.tar.Z src/x
fi