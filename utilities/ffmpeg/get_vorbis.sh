#!/bin/bash

ver="1.3.3"
arch="libogg-$ver.tar.gz"
[ -f "$arch" ] || wget "http://downloads.xiph.org/releases/ogg/$arch"
tar xfvz "$arch"

ver="1.3.5"
arch="libvorbis-$ver.tar.gz"
[ -f "$arch" ] || wget "http://downloads.xiph.org/releases/vorbis/$arch"
tar xfvz "$arch"

ver="1.1.1"
arch="libtheora-$ver.tar.gz"
[ -f "$arch" ] || wget "http://downloads.xiph.org/releases/theora/$arch"
tar xfvz "$arch"
