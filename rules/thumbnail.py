#!/usr/bin/env python

import re, os, sys, time

ImgExtensions = ['dpx','exr','jpg','jpeg','png','tif']
MovExtensions = ['mov','avi','mp4','mpg','mpeg']

from optparse import OptionParser

Parser = OptionParser( usage="%prog [options]\ntype \"%prog -h\" for help", version="%prog 1.0")

Parser.add_option('-x', '--xres',    dest='xres',       type  ='int',        default=160,
	help='X Resolution')
Parser.add_option('-y', '--yres',    dest='yres',       type  ='int',        default=90,
	help='Y Resolution')
Parser.add_option('-n', '--number',  dest='number',     type  ='int',        default=3,
	help='Number of images')
Parser.add_option('-i', '--input',   dest='input',      type  ='string',     default='',
	help='Input image')
Parser.add_option('-o', '--output',  dest='output',     type  ='string',     default='thumbnail.jpg',
	help='Output image')
Parser.add_option('-t', '--time',    dest='time',       type  ='int',        default=0,
	help='Midification test time')
Parser.add_option('-f', '--force',   dest='force',      action='store_true', default=False,
	help='Force creation, no modification time check.')
Parser.add_option('-V', '--verbose', dest='verbose',    action='store_true', default=False,
	help='Verbose mode.')
Parser.add_option('-D', '--debug',   dest='debug',      action='store_true', default=False,
	help='Debug mode.')

(Options, Args) = Parser.parse_args()

if Options.input == '':
	print('ERROR: :Input not specified.')
	sys.exit(1)

Images = []
Movie = None
MTime = 0
if os.path.isfile( Options.output):
	MTime = os.path.getmtime( Options.output)
	if Options.verbose:
		print('Thumbnail "%s" already exists.' % Options.output)
	if Options.time > 0:
		if time.time() - MTime < Options.time:
			print('thumbnail is up to date:'+Options.output)
			sys.exit(0)

if Options.input.find(',') != -1 or os.path.isdir( Options.input):
	folders = [Options.input]
	if folders[0].find(',') != -1:
		folders = folders[0].split(',')
	cur_mtime = 0
	for folder in folders:
		if Options.verbose: print('Scanning folder "%s"...' % folder)
		if not os.path.isdir( folder):
			print('ERROR: folder "%s" does not exist.' % folder)
			continue
		for root, dirs, files in os.walk( folder):
			if len( files) == 0: continue
			images = []
			for afile in files:
				split = re.split( r'\d\.', afile)
				if len(split) > 1 and split[-1] in ImgExtensions:
					images.append( afile)
				else:
					split = afile.split('.')
					if len(split) > 1 and split[-1] in MovExtensions:
						new_movie = os.path.join( root, afile)
						new_mtime = int( os.path.getmtime( new_movie))
						if new_movie > cur_mtime:
							Movie = new_movie
							cur_mtime = new_mtime
			if len( images) == 0: continue
			new_mtime = int( os.path.getmtime(os.path.join( root, images[0])))
			if new_mtime > cur_mtime:
				Images = []
				Movie = None
				images.sort()
				for i in range( Options.number):
					num = int( len(images) * (i+1.0) / (Options.number+1.0) )
					Images.append( os.path.join( root, images[num]))
				cur_mtime = new_mtime
else:
	if not os.path.isfile( Options.input):
		print('ERROR: Input does not exist:\n' + str( Options.input))
		sys.exit(1)

if len( Images ) == 0 and Movie is None:
	print('ERROR: Can`t find images in "%s"' % Options.input)
	sys.exit(1)

if Options.verbose:
	if Movie is not None:
		print('Movie: '+Movie)
	else:
		print('Images:')
		for img in Images:
			print( img)

if MTime >= cur_mtime:
	if Options.force:
		if Options.verbose:
			print('Forcing thumbnail creation')
	else:
		os.utime( Options.output, None)
		print('thumbnail time updated:'+Options.output)
		sys.exit(0)

OutDir = os.path.dirname( Options.output )
if OutDir != '':
	if not os.path.isdir( OutDir):
		os.makedirs( OutDir)
		if not os.path.isdir( OutDir):
			print('ERROR: Can`t create output folder "%s"' % OutDir)
			sys.exit(1)

Cmds = []
Thumbnails = []

if Movie is not None:
	frame = os.path.join( OutDir, 'frame.%07d.jpg')
	cmd = 'avconv -y'
	cmd += ' -i "%s"' % Movie
	cmd += ' -f image2 -vframes %d' % Options.number
	cmd += ' "%s"' % frame
	for i in range( 0, Options.number):
		Images.append( frame % (i+1) )
	Cmds.append( cmd)

cmd = 'convert'
cmd += ' "%s"'
if Movie is None:
	imgtype = Images[0].rfind('.');
	if imgtype > 0:
		imgtype = Images[0][imgtype+1:].lower()
		if   imgtype == 'exr': cmd += ' -set colorspace sRGB'
		elif imgtype == 'dpx': cmd += ' -set colorspace Log'
		elif imgtype == 'cin': cmd += ' -set colorspace Log'
cmd += ' -resize %dx%d' % (Options.xres, Options.yres)
cmd += ' "%s"'
for i in range( len( Images)):
	thumbnail = os.path.join( OutDir, 'thumbnail_%d.jpg' % i)
	Cmds.append( cmd % ( Images[i], thumbnail))
	Thumbnails.append( thumbnail)

cmd = 'montage'
cmd += ' -geometry +0+0'
for img in Thumbnails:
	cmd += ' "%s"' % img
cmd += ' -alpha Off -strip'
cmd += ' "%s"' % Options.output
Cmds.append( cmd)

if Options.verbose or Options.debug:
	for cmd in Cmds:
		print( cmd)

if Options.debug:
	print('Debug mode. Exiting...')
	sys.exit( 0)

for cmd in Cmds:
	os.system( cmd)

print('thumbnail generated:'+Options.output)
