#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import re
import subprocess
import time

from optparse import OptionParser

Parser = OptionParser(
    usage="%prog [options] input\ntype \"%prog -h\" for help",
    version="%prog 1.  0"
)

Parser.add_option('-a', '--avcmd',     dest='avcmd',     type  ='string', default='ffmpeg', help='AV convert command')
Parser.add_option(      '--ipar',      dest='ipar',      type  ='string', default=None,     help='Set input pixel aspect ratio')
Parser.add_option(      '--opar',      dest='opar',      type  ='string', default=None,     help='Set output pixel aspect ratio')
Parser.add_option('-r', '--resize',    dest='resize',    type  ='string', default=None,     help='Resize (1280x720)')
Parser.add_option('-c', '--codec',     dest='codec',     type  ='string', default=None,     help='Movie codec')
Parser.add_option('-f', '--fps'  ,     dest='fps',       type  ='string', default='24',     help='Movie FPS (24)')
Parser.add_option('-n', '--container', dest='container', type  ='string', default='mp4',    help='Movie Container')
Parser.add_option('-t', '--type',      dest='type',      type  ='string', default='png',    help='Images type (png)')
Parser.add_option('-o', '--output',    dest='output',    type  ='string', default=None,     help='Output movie or images folder (auto)')
Parser.add_option('-q', '--qscale',    dest='qscale',    type  ='int',    default=5,        help='JPEG compression rate (5)')
Parser.add_option('-s', '--timestart', dest='timestart', type  ='string', default=None,     help='Time start')
Parser.add_option('-d', '--duration',  dest='duration',  type  ='string', default=None,     help='Duration')
Parser.add_option('-p', '--padding',   dest='padding' ,  type  ='int',    default=7,        help='Padding')
Parser.add_option('-w', '--watermark', dest='watermark', type  ='string', default=None,     help='Add watermark')
Parser.add_option('-u', '--suffix',    dest='suffix',    type  ='string', default=None,     help='Add suffix to ouput file name')
Parser.add_option(      '--imgname',   dest='imgname',   type  ='string', default=None,     help='Images files name (frame)')
Parser.add_option(      '--audio',     dest='audio',     type  ='string', default=None,     help='Add sound from an audio file')
Parser.add_option(      '--acodec',    dest='acodec',    type  ='string', default='aac',    help='Audio codec')

Options, argv = Parser.parse_args()

if len(argv) < 1:
    print('ERROR: Movie file not specified.')
    sys.exit(0)

# Extract audio track(s) from file to flac if it is not flac already:
if Options.audio is not None:
    if not os.path.isfile(Options.audio):
        print('Audio file "%s" does not exist.' % Options.audio)
        Options.audio = None
    else:
        audio_name, audio_ext = os.path.splitext(Options.audio)
        if audio_ext != '.flac':
            audio_flac = '%s.%s' % (audio_name,'flac')
            print('Executing command to convert audio:')
            cmd_audio = 'ffmpeg -y -i "%s" -vn -acodec flac "%s"' % (Options.audio,audio_flac)
            print(cmd_audio)
            subprocess.call(cmd_audio,shell=True)
            Options.audio = audio_flac

Input = argv[0]
Output = Options.output
if Output is None:
    Output = Input

Sequence = []
StartNumber = None
if os.path.isdir(Input):
    InDir = Input
    allfiles = os.listdir(InDir)
    allfiles.sort()
    for afile in allfiles:
        if afile[0] == '.': continue
        afile = os.path.join( InDir, afile)
        if os.path.isdir( afile): continue

        Sequence.append( afile)

        if StartNumber is not None: continue

        afile = os.path.basename( afile)
        digits = re.findall(r'\d+', afile)
        if len(digits) == 0: continue
        digits = digits[-1]
        StartNumber = int(digits)
        Input = afile[:afile.rfind(digits)]
        Input += '%0' + str(len(digits)) + 'd'
        Input += afile[afile.rfind(digits) + len(digits):]
        Input = os.path.join(argv[0], Input)
        continue
else:
    if not os.path.isfile(Input):
        print('ERROR: Input does not exist: ' + Input)
        sys.exit(1)

MOVIEMAKER = os.path.dirname(sys.argv[0])
CODECSDIR = os.path.join(MOVIEMAKER, 'codecs')

Codec = Options.codec

cmd = ''

if Codec is None:
    cmd = Options.avcmd
    cmd += ' -y'
    if Options.timestart:
        cmd += ' -ss "%s"' % Options.timestart
    cmd += ' -i "%s"' % Input
    if Options.duration:
        cmd += ' -t "%s"' % Options.duration
    cmd += ' -an -f image2'
    if Options.type == 'jpg':
        cmd += ' -q:v ' + str(Options.qscale)
        Output += '.q' + str(Options.qscale)
    elif Options.type == 'dpx':
        cmd += ' -pix_fmt gbrp10be'
    elif Options.type == 'tif' or Options.type == 'tif8':
        cmd += ' -pix_fmt rgb24'
        Options.type = 'tif'
    elif Options.type == 'tif16':
        cmd += ' -pix_fmt rgb48le'
        Options.type = 'tif'

    if Options.resize is not None:
        resize = Options.resize.split('x')
        if len(resize) < 2:
            resize.append('-1')
        cmd += ' -vf "%s"' % ('scale=%s:%s' % (resize[0], resize[1]))
        Output += '.r%s' % Options.resize

    # Add images type (extension,format) to output:
    Output += '.' + Options.type

    # Add suffix to output:
    if Options.suffix is not None:
        Output += '.' + Options.suffix

    if not os.path.isdir(Output):
        os.makedirs(Output)
    if not os.path.isdir(Output):
        print('ERROR: Can`t create output folder: ' + Output)
        sys.exit(1)

    imgname = Options.imgname
    if imgname is None:
        imgname = os.path.basename( Input)
        imgname,ext = os.path.splitext( imgname)
    Output = os.path.join(Output, imgname + '.%0' + str(Options.padding) + 'd.' + Options.type)

    cmd += ' "%s"' % Output

else:
    if Codec.find('.') == -1:
        Codec += '.ffmpeg'
    if os.path.dirname(Codec) == '':
        Codec = os.path.join(CODECSDIR, Codec)
    if not os.path.isfile(Codec):
        print('ERROR: Can`t find codec "%s"' % Codec)
        sys.exit(1)

    with open(Codec) as f:
        lines = f.readlines()

    cmd = lines[len(lines) - 1].strip()
    if len(cmd) < 2:
        print('Invalid encode file "%s"' % Codec)
        sys.exit(1)

    # Remove same extesion from ouput (same container):
    name, ext = os.path.splitext( Output)
    if ext[1:] == Options.container:
        Output = name

    # Add codec name to output:
    Output += '.' + os.path.basename(Codec.split('.')[0])

    # Add suffix to output:
    if Options.suffix is not None:
        Output += '.' + Options.suffix

    auxargs = ''
    if Options.resize is not None or Options.watermark is not None:
        filter_complex = ''
        if Options.ipar is not None:
            if len(filter_complex): filter_complex += ','
            filter_complex += 'scale=iw:ih/%s' % Options.ipar
            if Options.opar is None:
                filter_complex += ',setsar=1'
        if Options.opar is not None:
            if len(filter_complex): filter_complex += ','
            filter_complex += 'setsar=%s' % Options.opar
        if Options.resize is not None:
            if len(filter_complex): filter_complex += ','
            resize = Options.resize.split('x')
            if len(resize) < 2:
                hresize.append('-1')
            filter_complex += 'scale=%s:-1,crop=%s:min(%s\\,ih),pad=%s:%s:0:max((%s-ih)/2\\,0)' % (resize[0], resize[0],resize[1], resize[0],resize[1],resize[1])
            Output += '.r%s' % Options.resize
        if Options.watermark is not None:
            if not os.path.isfile( Options.watermark):
                print('ERROR: Watermark file does not exist:\n' + Options.watermark)
                sys.exit(1)
            auxargs += ' -i "%s"' % Options.watermark
            if len(filter_complex): filter_complex += ','
            filter_complex += 'overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2'
        auxargs += ' -filter_complex "%s"' % filter_complex
    if Options.timestart:
        auxargs += ' -ss "%s"' % Options.timestart
    if Options.duration:
        auxargs += ' -t "%s"' % Options.duration
    if Options.audio is not None:
        auxargs += ' -i "%s" -shortest -codec:a %s' % (Options.audio,Options.acodec)

    avcmd = Options.avcmd
    if StartNumber:
        avcmd += ' -start_number ' + str(StartNumber)

    cmd = cmd.replace('@AVCMD@', avcmd)
    cmd = cmd.replace('@INPUT@', Input)
    cmd = cmd.replace('@MOVIEMAKER@', MOVIEMAKER)
    cmd = cmd.replace('@CODECSDIR@', CODECSDIR)
    cmd = cmd.replace('@FPS@', Options.fps)
    cmd = cmd.replace('@CONTAINER@', Options.container)
    cmd = cmd.replace('@AUXARGS@', auxargs)
    cmd = cmd.replace('@OUTPUT@', Output)


print(cmd)

try:
    process = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
except Exception as e:
    print('Command execution error:')
    print(str(e))
    sys.exit(1)

re_duration = re.compile(r'Duration: (\d\d:\d\d:\d\d)\.(\d\d)')
re_video = re.compile(r'.*Stream.*Video:\s*(.*)')
re_fps = re.compile(r'.*Stream.*: Video:.*(\d\d) fps')

video        = None
seconds      = -1
frames_total = -1
fps          = -1
frame        = -1
progress     = -1
progress_old =  0
frame_old    = -1
framereached = False
output       = ''
img_old      = None
time_img     = 0

while True:
    data = process.stderr.read(1)
    if data is None:
        break
    #print( str( type( data)))
    if len(data) < 1:
        break
    if not isinstance(data, str):
        try:
            data = str(data, 'ascii')
        except:
            data = '@'


    data = data.replace('\r', '\n')
    sys.stdout.write(data)


    if data[-1] == '\n':

        if output.find('error') != -1 or output.find('Error') != -1 or output.find('ERROR') != -1:
            process.kill()
            print('[ PARSER BAD RESULT ]')
            break

        # Search for duration (seconds):
        if seconds == -1 and frame == -1:
            reobj = re_duration.search(output)
            if reobj is not None:
                time_s, time_f = reobj.groups()
                time_s = time_s.split(':')
                time_slen = len(time_s)
                if time_slen > 0:
                    seconds = 0
                    i = time_slen - 1
                    mult = 1
                    while i >= 0:
                        seconds += int(time_s[i]) * mult
                        mult *= 60
                        i -= 1
                    seconds = seconds * 100 + int(time_f)
                print('SECONDS = %d' % seconds)

        # Search for fps:
        if fps == -1 and frame == -1:
            reobj = re_fps.search(output)
            if reobj is not None:
                fps = int(reobj.groups()[0])
                print('FPS = %d' % fps)

        #if video is None and output.find('Video') != -1:
        if video is None:
            re_obj = re_video.search(output)
            if re_obj:
                video = re_obj.groups()[0]
                print('REPORT: Input: ' + video)


        if frame_old != frame:
            frame_info = 'Frame = %d' % frame
            if frames_total != -1:
                frame_info += ' of %d' % frames_total
            print(frame_info)
            if progress != -1:
                print('PROGRESS: %d%%' % progress)

                # Output thumbnail on-the-fly but not often than 10 % and 5 seconds:
                if progress >= progress_old and time.time() > time_img + 5:
                    if len(Sequence):
                        img = int( .01 * len(Sequence) * progress)
                        if img >= len(Sequence): img = len(Sequence) - 1
                        if img != img_old:
                            print('@IMAGE!@' + Sequence[img])
                            img_old = img
                    elif frame > -1:
                        if Codec is None:
                            print('@IMAGE!@' + Output % frame)
                    progress_old += 5
                    time_img = time.time()

            frame_old = frame
        sys.stdout.flush()

        output = ''

        continue


    output += data


    if frame == -1 and fps != -1 and seconds != -1 and frames_total == -1:
        frames_total = 1 + seconds * fps / 100
        progress = 0

    if output == 'frame=':
        framereached = True
        output = ''
        continue

    if framereached and output[-4:] == 'fps=':
        try:
            frame = int(output[:-4])
            if progress != -1 and frames_total > 0:
                progress = int(100 * frame / frames_total)
        except Exception as e:
            print(str(e))
        framereached = False
        output = ''
        continue


returncode = process.wait()
sys.exit(returncode)

