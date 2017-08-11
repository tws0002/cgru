#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import subprocess
import sys
import time

import cgruconfig
import cgruutils

from Qt import QtCore, QtGui, QtWidgets

# Save files settings:
FilePrefix = 'moviemaker.'
FileSuffix = '.txt'
FileLast = 'last'
FileRecent = 'recent'

# Command arguments:

from optparse import OptionParser
Parser = OptionParser(usage="%prog [options] [file or folder]\ntype \"%prog -h\" for help", version="%prog 1.0")
Parser.add_option('-a', '--avcmd',           dest='avcmd',           type  ='string',     default='ffmpeg',       help='AV tool command')
Parser.add_option('-s', '--slate',           dest='slate',           type  ='string',     default='dailies_slate',help='Slate frame template')
Parser.add_option('-t', '--template',        dest='template',        type  ='string',     default='dailies_withlogo', help='Sequence frame template')
Parser.add_option('-c', '--codec',           dest='codec',           type  ='string',     default='h264_mid.ffmpeg', help='Codec preset')
Parser.add_option('-f', '--format',          dest='format',          type  ='string',     default='1280x720',     help='Resolution')
Parser.add_option('-n', '--container',       dest='container',       type  ='string',     default='mp4',          help='Container')
Parser.add_option('--aspect_in',             dest='aspect_in',       type  ='float',      default=-1.0,           help='Input image aspect, -1 = no changes')
Parser.add_option('--aspect_auto',           dest='aspect_auto',     type  ='float',      default=-1.0,           help='Auto image aspect (2 if w/h <= aspect_auto), -1 = no changes')
Parser.add_option('--aspect_out',            dest='aspect_out',      type  ='float',      default=-1.0,           help='Output movie aspect, "-1" = no changes')
Parser.add_option('--tmpformat',             dest='tmpformat',       type  ='string',     default='tga',          help='Temporary images format')
Parser.add_option('--tmpquality',            dest='tmpquality',      type  ='string',     default='',             help='Temporary images format quality options')
Parser.add_option('--noidentify',            dest='noidentify',      action='store_true', default=False,          help='Disable image identification')
Parser.add_option('--colorspace',            dest='colorspace',      type  ='string',     default='auto',         help='Input images colorspace')
Parser.add_option('--correction',            dest='correction',      type  ='string',     default='',             help='Add custom color correction parameters')
Parser.add_option('--stereodub',             dest='stereodub',       action='store_true', default=False,          help='Stereo mode by default')
Parser.add_option('--fps',                   dest='fps',             type  ='string',     default='25',           help='Frames per second')
Parser.add_option('--company',               dest='company',         type  ='string',     default='',             help='Company name')
Parser.add_option('--project',               dest='project',         type  ='string',     default='',             help='Project name')
Parser.add_option('--artist',                dest='artist',          type  ='string',     default='',             help='Artist name')
Parser.add_option('--naming',                dest='naming',          type  ='string',     default='',             help='Auto movie naming rule: [s]_[v]_[d]')
Parser.add_option('--cacher_aspect',         dest='cacher_aspect',   type  ='float',      default=1.85,           help='Cacher aspect')
Parser.add_option('--cacher_opacity',        dest='cacher_opacity',  type  ='int',        default=0,              help='Cacher opacity')
Parser.add_option('--line_aspect',           dest='line_aspect',     type  ='float',      default=1.85,           help='Cacher line aspect')
Parser.add_option('--line_color',            dest='line_color',      type  ='string',     default='',             help='Cacher line opacity')
Parser.add_option('--draw169',               dest='draw169',         type  ='int',        default=0,              help='Draw 16:9 cacher opacity')
Parser.add_option('--draw235',               dest='draw235',         type  ='int',        default=0,              help='Draw 2.35 cacher opacity')
Parser.add_option('--line169',               dest='line169',         type  ='string',     default='',             help='Draw 16:9 line color: "255,255,0"')
Parser.add_option('--line235',               dest='line235',         type  ='string',     default='',             help='Draw 2.35 line color: "255,255,0"')
Parser.add_option('--fffirst',               dest='fffirst',         action='store_true', default=False,          help='Draw first frame as first, and not actual first frame number.')
Parser.add_option('--lgspath',               dest='lgspath',         type  ='string',     default='logo.png',     help='Slate logo')
Parser.add_option('--lgssize',               dest='lgssize',         type  ='int',        default=25,             help='Slate logo size, percent of image')
Parser.add_option('--lgsgrav',               dest='lgsgrav',         type  ='string',     default='southeast',    help='Slate logo positioning gravity')
Parser.add_option('--lgfpath',               dest='lgfpath',         type  ='string',     default='logo.png',     help='Frame logo')
Parser.add_option('--lgfsize',               dest='lgfsize',         type  ='int',        default=10,             help='Frame logo size, percent of image')
Parser.add_option('--lgfgrav',               dest='lgfgrav',         type  ='string',     default='north',        help='Frame logo positioning gravity')
Parser.add_option('-A', '--afanasy',         dest='afanasy',         action='store_true', default=False,          help='Send Afanasy job')
Parser.add_option(      '--afpriority',      dest='afpriority',      type  ='int',        default=-1,             help='Afanasy job priority')
Parser.add_option(      '--afmaxhosts',      dest='afmaxhosts',      type  ='int',        default=-1,             help='Afanasy job maximum hosts')
Parser.add_option(      '--afhostsmask',     dest='afhostsmask',     type  ='string',     default='',             help='Afanasy job hosts mask')
Parser.add_option(      '--afhostsmaskex',   dest='afhostsmaskex',   type  ='string',     default='',             help='Afanasy job exclude hosts mask')
Parser.add_option(      '--afdependmask',    dest='afdependmask',    type  ='string',     default='',             help='Afanasy job depend mask')
Parser.add_option(      '--afdependmaskgl',  dest='afdependmaskgl',  type  ='string',     default='',             help='Afanasy job global depend mask')
Parser.add_option(      '--afcapacity',      dest='afcapacity',      type  ='int',        default=-1,             help='Afanasy job tasks capacity')
Parser.add_option(      '--afpause',         dest='afpause',         action='store_true', default=False,          help='Start Afanasy job paused')
Parser.add_option('-D', '--debug',           dest='debug',           action='store_true', default=False,          help='Debug mode')

Parser.add_option(      '--wndicon',         dest='wndicon',         type  ='string',     default='dailies',      help='Set dialog window icon filename.')

Options, args = Parser.parse_args()

if len(args) > 2:
    Parser.error('Too many arguments provided.')

InFile0 = ''
InFile1 = ''

if len(args) > 0:
    InFile0 = os.path.abspath(args[0])
if len(args) > 1:
    InFile1 = os.path.abspath(args[1])

# Initializations:
DialogPath = os.path.dirname(os.path.abspath(sys.argv[0]))
TemplatesPath = os.path.join(DialogPath, 'templates')
LogosPath = os.path.join(DialogPath, 'logos')
CodecsPath = os.path.join(DialogPath, 'codecs')
FormatsPath = os.path.join(DialogPath, 'formats')
FPS = ['23.976', '24', '25', '30', '48', '50']
TimeFormat = 'd MMM yyyy, h:mm'

Activities = ['comp', 'render', 'anim', 'dyn', 'sim', 'stereo', 'cloth',
              'part', 'skin', 'setup', 'clnup', 'mtpnt', 'rnd', 'test']
FontsList = ['', 'Arial', 'Courier-New', 'Impact', 'Tahoma', 'Times-New-Roman',
             'Verdana']
Encoders = ['ffmpeg', 'mencoder', 'nuke']
Gravity = ['SouthEast', 'South', 'SouthWest', 'West', 'NorthWest', 'North',
           'NorthEast', 'East', 'Center']

Namings = [
    '(s)_(v)_(d)',
    '(S)_(V)_(D)',
    '(s)_(a)_(v)_(d)',
    '(S)_(A)_(V)_(D)',
    '(s)_(v)_(a)_(d)',
    '(S)_(V)_(A)_(D)',
    '(P)_(S)_(V)_(D)_(A)_(C)_(U)',
    '(p)_(s)_(v)_(d)_(a)_(c)_(u)'
]
if Options.naming != '' and not Options.naming in Namings:
    Namings.append(Options.naming)

AudioCodecNames = ['MP3 (Mpeg-1 Layer 3)', 'AAC (Advanced Audio Codec)',
                   'Vorbis', 'FLAC (Free Lossless Audio Codec)']
AudioCodecValues = ['libmp3lame', 'libfaac', 'libvorbis', 'flac']

# Process Containers:
Containers = ['mov', 'avi', 'mp4', 'm4v', 'mxf', 'ogg']
if not str(Options.container) in Containers:
    Containers.append(str(Options.container))

# Process Cacher:
CacherNames = ['None', '25%', '50%', '75%', '100%']
CacherValues = ['0', '25', '50', '75', '100']
if not str(Options.draw169) in CacherValues:
    CacherNames.append(str(Options.draw169))
    CacherValues.append(str(Options.draw169))

if not str(Options.draw235) in CacherValues:
    CacherNames.append(str(Options.draw235))
    CacherValues.append(str(Options.draw235))

# Precess Artist:
Artist = Options.artist
if Artist == '':
    Artist = os.getenv('USER', os.getenv('USERNAME', 'user'))

# cut DOMAIN from username:
dpos = Artist.rfind('/')
if dpos == -1:
    dpos = Artist.rfind('\\')
if dpos != -1:
    Artist = Artist[dpos + 1:]
Artist = Artist.capitalize()

# Process formats:
FormatNames = []
FormatValues = []
FormatFiles = []
allFiles = os.listdir(FormatsPath)
for afile in allFiles:
    afile = os.path.join(FormatsPath, afile)
    if os.path.isfile(afile):
        FormatFiles.append(afile)
FormatFiles.sort()
for afile in FormatFiles:
    file = open(afile)
    FormatNames.append(file.readline().strip())
    FormatValues.append(file.readline().strip())
    file.close()
FormatNames.append('Encode "as is" only')
FormatValues.append('')
if not Options.format in FormatValues:
    FormatValues.append(Options.format)
    FormatNames.append(Options.format)

# Process colorspace:
Colorspaces = ['auto', 'extension', 'RGB', 'sRGB', 'Log']
if Options.colorspace not in Colorspaces:
    Colorspaces.append(Options.colorspace)

# Process temporary images format:
TmpImgFormats = ['tga', 'jpg', 'dpx', 'png', 'tif']
if Options.tmpformat not in TmpImgFormats:
    TmpImgFormats.append(Options.tmpformat)

# Process templates:
Templates = ['']
TemplateF = 0
TemplateS = 0
if os.path.isdir(TemplatesPath):
    files = os.listdir(TemplatesPath)
    files.sort()
    index = 0
    for afile in files:
        if afile[0] == '.':
            continue
        index += 1
        Templates.append(afile)
        if afile == Options.slate:
            TemplateS = index
        if afile == Options.template:
            TemplateF = index


# Process codecs:
CodecNames = []
CodecFiles = []
allFiles = os.listdir(CodecsPath)
for afile in allFiles:
    afile = os.path.join(CodecsPath, afile)
    if os.path.isfile(afile):
        parts = afile.split('.')
        if len(parts):
            if parts[len(parts) - 1] in Encoders:
                CodecFiles.append(afile)
CodecFiles.sort()
for afile in CodecFiles:
    with open(afile) as f:
        name = f.readline().strip()
    CodecNames.append(name)


def getComboBoxString(comboBox):
    data = comboBox.itemData(comboBox.currentIndex())
    if data is None:
        return ''
    if isinstance(data, str):
        return data
    if isinstance(data, unicode):
        return data
    return comboBox.itemData(comboBox.currentIndex()).toString()


class Dialog(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle(
            'Make Movie - CGRU ' + cgruconfig.VARS['CGRU_VERSION'])

        self.constructed = False
        self.evaluated = False
        self.running = False
        self.decode = False
        self.inputPattern = None
        self.inputPattern2 = None

        mainLayout = QtWidgets.QVBoxLayout(self)
        tabwidget = QtWidgets.QTabWidget(self)
        mainLayout.addWidget(tabwidget)

        generalwidget = QtWidgets.QWidget(self)
        tabwidget.addTab(generalwidget, 'General')
        generallayout = QtWidgets.QVBoxLayout(generalwidget)

        drawingwidget = QtWidgets.QWidget(self)
        tabwidget.addTab(drawingwidget, 'Drawing')
        drawinglayout = QtWidgets.QVBoxLayout(drawingwidget)

        parameterswidget = QtWidgets.QWidget(self)
        tabwidget.addTab(parameterswidget, 'Parameters')
        parameterslayout = QtWidgets.QVBoxLayout(parameterswidget)

        stereowidget = QtWidgets.QWidget(self)
        tabwidget.addTab(stereowidget, 'Stereo')
        stereolayout = QtWidgets.QVBoxLayout(stereowidget)

        decodewidget = QtWidgets.QWidget(self)
        tabwidget.addTab(decodewidget, 'Decode')
        decodeLayout = QtWidgets.QVBoxLayout(decodewidget)

        audiowidget = QtWidgets.QWidget(self)
        tabwidget.addTab(audiowidget, 'Audio')
        audioLayout = QtWidgets.QVBoxLayout(audiowidget)

        afanasywidget = QtWidgets.QWidget(self)
        tabwidget.addTab(afanasywidget, 'Afanasy')
        afanasylayout = QtWidgets.QVBoxLayout(afanasywidget)

        # General:
        self.fields = dict()

        # Format:
        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel('Format:', self)
        label.setToolTip(
            'Movie resolution.\n'
            'Format presets located in\n' + FormatsPath
        )
        layout.addWidget(label)
        self.fields['format'] = QtWidgets.QComboBox(self)

        i = 0
        for format in FormatValues:
            self.fields['format'].addItem(FormatNames[i], format)
            if format == Options.format:
                self.fields['format'].setCurrentIndex(i)
            i += 1

        self.fields['format'].currentIndexChanged.connect( self.evaluate)
        layout.addWidget(self.fields['format'])

        label = QtWidgets.QLabel('FPS:', self)
        label.setToolTip('Frame rate.')
        layout.addWidget(label)
        self.fields['fps'] = QtWidgets.QComboBox(self)
        i = 0
        for fps in FPS:
            self.fields['fps'].addItem(fps)
            if fps == Options.fps:
                self.fields['fps'].setCurrentIndex(i)
            i += 1
        self.fields['fps'].currentIndexChanged.connect( self.evaluate)
        layout.addWidget(self.fields['fps'])

        label = QtWidgets.QLabel('Codec:', self)
        label.setToolTip('Codec presets located in\n' + CodecsPath)
        self.fields['codec'] = QtWidgets.QComboBox(self)
        i = 0
        for name in CodecNames:
            self.fields['codec'].addItem(name, CodecFiles[i])
            if os.path.basename(CodecFiles[i]) == Options.codec:
                self.fields['codec'].setCurrentIndex(i)
            i += 1
        self.fields['codec'].currentIndexChanged.connect( self.evaluate)
        layout.addWidget(label)
        layout.addWidget(self.fields['codec'])

        label = QtWidgets.QLabel('Container:')
        label.setToolTip(
            'Video stream container.\n'
            'Movie file name extension will be set according to it.'
        )
        layout.addWidget(label)
        self.fields['container'] = QtWidgets.QComboBox(self)
        i = 0
        for cont in Containers:
            self.fields['container'].addItem(cont)
            if cont == Options.container:
                self.fields['container'].setCurrentIndex(i)
            i += 1
        self.fields['container'].currentIndexChanged.connect( self.evaluate)
        layout.addWidget(self.fields['container'])

        generallayout.addLayout(layout)

        group = QtWidgets.QGroupBox('Information')
        grouplayout = QtWidgets.QVBoxLayout()
        group.setLayout(grouplayout)
        generallayout.addWidget(group)

        layout = QtWidgets.QHBoxLayout()
        grouplayout.addLayout(layout)
        label = QtWidgets.QLabel('Company:', self)
        layout.addWidget(label)
        label.setToolTip(
            'Draw company name.\n'
            'Leave empty to skip.'
        )
        self.fields['company'] = QtWidgets.QLineEdit(Options.company, self)
        layout.addWidget(self.fields['company'])
        self.fields['company'].editingFinished.connect( self.evaluate)
        label = QtWidgets.QLabel('Project:', self)
        layout.addWidget(label)
        label.setToolTip('Project name.')
        self.fields['project'] = QtWidgets.QLineEdit(Options.project, self)
        layout.addWidget(self.fields['project'])
        self.fields['project'].editingFinished.connect( self.evaluate)
        label = QtWidgets.QLabel('Shot:', self)
        layout.addWidget(label)
        label.setToolTip('Shot name.')
        self.fields['shot'] = QtWidgets.QLineEdit('', self)
        layout.addWidget(self.fields['shot'])
        self.fields['shot'].editingFinished.connect( self.evaluate)
        label = QtWidgets.QLabel('Version:', self)
        layout.addWidget(label)
        label.setToolTip('Shot version.')
        self.fields['version'] = QtWidgets.QLineEdit('', self)
        layout.addWidget(self.fields['version'])
        self.fields['version'].editingFinished.connect( self.evaluate)
        self.fields['autotitles'] = QtWidgets.QCheckBox('Auto', self)
        layout.addWidget(self.fields['autotitles'])
        self.fields['autotitles'].setToolTip(
            'Try to fill values automatically parsing input '
            'file name and folder.'
        )
        self.fields['autotitles'].setChecked(True)
        self.fields['autotitles'].stateChanged.connect( self.autoTitles)

        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel('Artist:', self)
        label.setToolTip('Artist name.')
        layout.addWidget(label)
        self.fields['artist'] = QtWidgets.QLineEdit(Artist, self)
        layout.addWidget(self.fields['artist'])
        self.fields['artist'].editingFinished.connect( self.evaluate)
        label = QtWidgets.QLabel('Activity:', self)
        label.setToolTip('Shot activity to show.')
        layout.addWidget(label)
        self.fields['activity'] = QtWidgets.QLineEdit('', self)
        layout.addWidget(self.fields['activity'])
        self.fields['activity'].editingFinished.connect( self.evaluate)
        self.cbActivity = QtWidgets.QComboBox(self)
        for act in Activities:
            self.cbActivity.addItem(act)
        layout.addWidget(self.cbActivity)
        self.cbActivity.currentIndexChanged.connect( self.activityChanged)
        grouplayout.addLayout(layout)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel('Comments:', self))
        self.fields['comments'] = QtWidgets.QLineEdit(self)
        self.fields['comments'].editingFinished.connect( self.evaluate)
        layout.addWidget(self.fields['comments'])
        grouplayout.addLayout(layout)

        group = QtWidgets.QGroupBox('Input Sequence Pattern')
        grouplayout = QtWidgets.QVBoxLayout()
        group.setLayout(grouplayout)
        generallayout.addWidget(group)

        self.fields['input0'] = QtWidgets.QLineEdit(InFile0, self)
        self.fields['input0'].setToolTip(
            'Input files(s).\n'
            'You put folder name, file name or files patters here.\n'
            'Pattern digits can be represented by "%04d" or "####".'
        )
        self.fields['input0'].textEdited.connect( self.inputFileChanged)
        grouplayout.addWidget(self.fields['input0'])

        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel('Files count:', self)
        label.setToolTip('Files found matching pattern.')
        layout.addWidget(label)
        self.editInputFilesCount = QtWidgets.QLineEdit(self)
        self.editInputFilesCount.setEnabled(False)
        layout.addWidget(self.editInputFilesCount)
        label = QtWidgets.QLabel('Pattern:', self)
        label.setToolTip('Recognized files pattern.')
        layout.addWidget(label)
        self.editInputFilesPattern = QtWidgets.QLineEdit(self)
        self.editInputFilesPattern.setEnabled(False)
        layout.addWidget(self.editInputFilesPattern)

        label = QtWidgets.QLabel('Frames:', self)
        label.setToolTip('Frame range.')
        layout.addWidget(label)
        self.fields['framestart'] = QtWidgets.QSpinBox(self)
        self.fields['framestart'].setRange(-1, -1)
        self.fields['framestart'].valueChanged.connect( self.evaluate)
        layout.addWidget(self.fields['framestart'])
        self.sbFrameLast = QtWidgets.QSpinBox(self)
        self.sbFrameLast.setRange(-1, -1)
        self.sbFrameLast.valueChanged.connect( self.evaluate)
        layout.addWidget(self.sbFrameLast)
        self.fields['fffirst'] = QtWidgets.QCheckBox('F.F.First', self)
        self.fields['fffirst'].setChecked(Options.fffirst)
        self.fields['fffirst'].setToolTip(
            'First Frame First:\n'
            'Draw first frame number as one.'
        )
        self.fields['fffirst'].stateChanged.connect( self.evaluate)
        layout.addWidget(self.fields['fffirst'])

        self.btnBrowseInput = QtWidgets.QPushButton('Browse Sequence', self)
        self.btnBrowseInput.pressed.connect( self.browseInput)
        layout.addWidget(self.btnBrowseInput)
        grouplayout.addLayout(layout)

        lIdentify = QtWidgets.QHBoxLayout()
        self.cbIdentify = QtWidgets.QCheckBox('Identify:', self)
        self.cbIdentify.setChecked(not Options.noidentify)
        self.cbIdentify.setToolTip('Input file identification.')
        self.editIdentify = QtWidgets.QLineEdit(self)
        self.editIdentify.setEnabled(False)
        self.btnIdentify = QtWidgets.QPushButton('Refresh', self)
        self.btnIdentify.pressed.connect( self.inputFileChanged)
        lIdentify.addWidget(self.cbIdentify)
        lIdentify.addWidget(self.editIdentify)
        lIdentify.addWidget(self.btnIdentify)
        grouplayout.addLayout(lIdentify)

        group = QtWidgets.QGroupBox('Output File')
        grouplayout = QtWidgets.QVBoxLayout()
        group.setLayout(grouplayout)
        generallayout.addWidget(group)

        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel('Name:', self)
        label.setToolTip(
            'Result movie name.\n'
            'Extension will be added according to video stream container.\n'
            'It is configuted in codec preset files.'
        )
        layout.addWidget(label)
        self.fields['outputname'] = QtWidgets.QLineEdit(self)
        layout.addWidget(self.fields['outputname'])
        self.fields['outputname'].editingFinished.connect( self.evaluate)
        self.fields['usenamerule'] = QtWidgets.QCheckBox('Rule:', self)
        self.fields['usenamerule'].setChecked(True)
        self.fields['usenamerule'].setToolTip('Use Naming Rule.')
        self.fields['usenamerule'].stateChanged.connect( self.autoOutputName)
        layout.addWidget(self.fields['usenamerule'])
        naming = Options.naming
        if naming == '':
            naming = Namings[0]
        self.fields['namerule'] = QtWidgets.QLineEdit(naming, self)
        self.fields['namerule'].editingFinished.connect( self.evaluate)
        self.fields['namerule'].setMaximumWidth(150)
        layout.addWidget(self.fields['namerule'])
        self.cbNaming = QtWidgets.QComboBox(self)
        i = 0
        for rule in Namings:
            self.cbNaming.addItem(rule)
            if rule == Options.naming:
                self.cbNaming.setCurrentIndex(i)
            i += 1
        self.cbNaming.setMaximumWidth(120)
        self.cbNaming.currentIndexChanged.connect( self.namingChanged)
        layout.addWidget(self.cbNaming)
        grouplayout.addLayout(layout)

        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel('Folder:', self)
        label.setToolTip('Result movie will be placed in this directory.')
        layout.addWidget(label)
        self.fields['outputfolder'] = QtWidgets.QLineEdit(self)
        self.fields['outputfolder'].editingFinished.connect( self.evaluate)
        layout.addWidget(self.fields['outputfolder'])
        self.btnBrowseOutputDir = QtWidgets.QPushButton('Browse', self)
        self.btnBrowseOutputDir.pressed.connect( self.browseOutputFolder)
        layout.addWidget(self.btnBrowseOutputDir)
        grouplayout.addLayout(layout)

        # Drawing:
        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel('Slate Template:', self)
        layout.addWidget(label)
        label.setToolTip(
            'Slate frame template.\n'
            'Templates are located in\n' + TemplatesPath
        )
        self.fields['slate'] = QtWidgets.QComboBox(self)
        layout.addWidget(self.fields['slate'])
        label = QtWidgets.QLabel('Frame Template:', self)
        layout.addWidget(label)
        label.setToolTip(
            'Frame template.\n'
            'Templates are located in\n' + TemplatesPath
        )
        self.fields['template'] = QtWidgets.QComboBox(self)
        layout.addWidget(self.fields['template'])
        for template in Templates:
            self.fields['slate'].addItem(template)
            self.fields['template'].addItem(template)
        self.fields['slate'].setCurrentIndex(TemplateS)
        self.fields['template'].setCurrentIndex(TemplateF)
        self.fields['slate'].currentIndexChanged.connect( self.evaluate)
        self.fields['template'].currentIndexChanged.connect( self.evaluate)
        drawinglayout.addLayout(layout)

        self.fields['addtime'] = QtWidgets.QCheckBox('Add Time To Date', self)
        self.fields['addtime'].setChecked(False)
        self.fields['addtime'].stateChanged.connect( self.evaluate)
        drawinglayout.addWidget(self.fields['addtime'])

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel('Cacher Aspect:', self))
        self.fields['cacher_aspect'] = QtWidgets.QDoubleSpinBox(self)
        self.fields['cacher_aspect'].setRange(0.1, 10.0)
        self.fields['cacher_aspect'].setDecimals(6)
        self.fields['cacher_aspect'].setValue(Options.cacher_aspect)
        self.fields['cacher_aspect'].valueChanged.connect( self.evaluate)
        layout.addWidget(self.fields['cacher_aspect'])
        layout.addWidget(QtWidgets.QLabel('Cacher Opacity:', self))
        self.fields['cacher_opacity'] = QtWidgets.QComboBox(self)
        i = 0
        for cacher in CacherNames:
            self.fields['cacher_opacity'].addItem(cacher, CacherValues[i])
            if CacherValues[i] == str(Options.cacher_opacity):
                self.fields['cacher_opacity'].setCurrentIndex(i)
            i += 1
        self.fields['cacher_opacity'].currentIndexChanged.connect( self.evaluate)
        layout.addWidget(self.fields['cacher_opacity'])
        drawinglayout.addLayout(layout)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel('Cacher Line Aspect:', self))
        self.fields['line_aspect'] = QtWidgets.QDoubleSpinBox(self)
        self.fields['line_aspect'].setRange(0.1, 10.0)
        self.fields['line_aspect'].setDecimals(6)
        self.fields['line_aspect'].setValue(Options.line_aspect)
        self.fields['line_aspect'].valueChanged.connect( self.evaluate)
        layout.addWidget(self.fields['line_aspect'])
        tCacherLine = QtWidgets.QLabel('Cacher Line Color:', self)
        tCacherLine.setToolTip('Example "255,255,0" - yellow.')
        layout.addWidget(tCacherLine)
        self.fields['line_color'] = QtWidgets.QLineEdit(Options.line_color, self)
        self.fields['line_color'].editingFinished.connect( self.evaluate)
        layout.addWidget(self.fields['line_color'])
        drawinglayout.addLayout(layout)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel('16:9 Cacher:', self))
        self.cbCacher169 = QtWidgets.QComboBox(self)
        layout.addWidget(self.cbCacher169)
        i = 0
        for cacher in CacherNames:
            self.cbCacher169.addItem(cacher, CacherValues[i])
            if CacherValues[i] == str(Options.draw169):
                self.cbCacher169.setCurrentIndex(i)
            i += 1
        self.cbCacher169.currentIndexChanged.connect( self.evaluate)
        layout.addWidget(QtWidgets.QLabel('2.35 Cacher:', self))
        self.cbCacher235 = QtWidgets.QComboBox(self)
        layout.addWidget(self.cbCacher235)
        i = 0
        for cacher in CacherNames:
            self.cbCacher235.addItem(cacher, CacherValues[i])
            if CacherValues[i] == str(Options.draw235):
                self.cbCacher235.setCurrentIndex(i)
            i += 1
        self.cbCacher235.currentIndexChanged.connect( self.evaluate)
        drawinglayout.addLayout(layout)

        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel('Line 16:9 Color:', self)
        label.setToolTip('Example "255,255,0" - yellow.')
        layout.addWidget(label)
        self.fields['line169'] = QtWidgets.QLineEdit(Options.line169, self)
        layout.addWidget(self.fields['line169'])
        self.fields['line169'].editingFinished.connect( self.evaluate)
        label = QtWidgets.QLabel('Line 2.35 Color:', self)
        label.setToolTip('Example "255,255,0" - yellow.')
        layout.addWidget(label)
        self.fields['line235'] = QtWidgets.QLineEdit(Options.line235, self)
        layout.addWidget(self.fields['line235'])
        self.fields['line235'].editingFinished.connect( self.evaluate)
        drawinglayout.addLayout(layout)

        # Logos:
        # Slate logo:
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel('Slate Logo:', self))
        self.fields['lgspath'] = QtWidgets.QLineEdit(Options.lgspath, self)
        layout.addWidget(self.fields['lgspath'])
        self.fields['lgspath'].editingFinished.connect( self.evaluate)
        self.btnBrowseLgs = QtWidgets.QPushButton('Browse', self)
        self.btnBrowseLgs.pressed.connect( self.browseLgs)
        layout.addWidget(self.btnBrowseLgs)
        layout.addWidget(QtWidgets.QLabel('Size:', self))
        self.fields['lgssize'] = QtWidgets.QSpinBox(self)
        self.fields['lgssize'].setRange(1, 100)
        self.fields['lgssize'].setValue(Options.lgssize)
        self.fields['lgssize'].valueChanged.connect( self.evaluate)
        layout.addWidget(self.fields['lgssize'])
        layout.addWidget(QtWidgets.QLabel('%  Position:', self))
        self.fields['lgsgrav'] = QtWidgets.QComboBox(self)
        i = 0
        for grav in Gravity:
            self.fields['lgsgrav'].addItem(grav)
            if grav.lower() == Options.lgsgrav:
                self.fields['lgsgrav'].setCurrentIndex(i)
            i += 1
        layout.addWidget(self.fields['lgsgrav'])
        self.fields['lgsgrav'].currentIndexChanged.connect( self.evaluate)
        drawinglayout.addLayout(layout)

        # Frame logo:
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel('Frame Logo:', self))
        self.fields['lgfpath'] = QtWidgets.QLineEdit(Options.lgfpath, self)
        layout.addWidget(self.fields['lgfpath'])
        self.fields['lgfpath'].editingFinished.connect( self.evaluate)
        self.btnBrowseLgf = QtWidgets.QPushButton('Browse', self)
        self.btnBrowseLgf.pressed.connect( self.browseLgf)
        layout.addWidget(self.btnBrowseLgf)
        layout.addWidget(QtWidgets.QLabel('Size:', self))
        self.fields['lgfsize'] = QtWidgets.QSpinBox(self)
        self.fields['lgfsize'].setRange(1, 100)
        self.fields['lgfsize'].setValue(Options.lgfsize)
        self.fields['lgfsize'].valueChanged.connect( self.evaluate)
        layout.addWidget(self.fields['lgfsize'])
        layout.addWidget(QtWidgets.QLabel('%  Position:', self))
        self.fields['lgfgrav'] = QtWidgets.QComboBox(self)
        i = 0
        for grav in Gravity:
            self.fields['lgfgrav'].addItem(grav)
            if grav.lower() == Options.lgfgrav:
                self.fields['lgfgrav'].setCurrentIndex(i)
            i += 1
        layout.addWidget(self.fields['lgfgrav'])
        self.fields['lgfgrav'].currentIndexChanged.connect( self.evaluate)
        drawinglayout.addLayout(layout)

        # Font:
        lFont = QtWidgets.QHBoxLayout()
        tFont = QtWidgets.QLabel('Annotations Text Font:', self)
        lFont.addWidget(tFont)
        self.fields['font'] = QtWidgets.QLineEdit('', self)
        lFont.addWidget(self.fields['font'])
        self.fields['font'].editingFinished.connect( self.evaluate)
        self.cbFont = QtWidgets.QComboBox(self)
        for font in FontsList:
            self.cbFont.addItem(font)
        lFont.addWidget(self.cbFont)
        self.cbFont.currentIndexChanged.connect( self.fontChanged)
        drawinglayout.addLayout(lFont)


        # Parameters
        layout = QtWidgets.QHBoxLayout()
        parameterslayout.addLayout(layout)
        label = QtWidgets.QLabel('AV tool command:', self)
        layout.addWidget(label)
        label.setToolTip('AV tools command.')
        self.fields['avcmd'] = QtWidgets.QLineEdit(Options.avcmd, self)
        self.fields['avcmd'].editingFinished.connect( self.evaluate)
        layout.addWidget(self.fields['avcmd'])

        # Fake time:
        layout = QtWidgets.QHBoxLayout()
        parameterslayout.addLayout(layout)
        self.cbFakeTime = QtWidgets.QCheckBox('Fake Time:', self)
        self.cbFakeTime.setChecked(False)
        self.cbFakeTime.stateChanged.connect( self.evaluate)
        layout.addWidget(self.cbFakeTime)
        self.fakeTime = QtWidgets.QDateTimeEdit(
            QtCore.QDateTime.currentDateTime(),
            self
        )
        self.fakeTime.setDisplayFormat(TimeFormat)
        self.fakeTime.setCalendarPopup(True)
        layout.addWidget(self.fakeTime)
        self.fakeTime.dateTimeChanged.connect( self.evaluate)

        # Image Aspect:
        group = QtWidgets.QGroupBox('Aspect')
        parameterslayout.addWidget(group)
        grouplayout = QtWidgets.QVBoxLayout()
        group.setLayout(grouplayout)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel('Input Images Aspect', self))
        self.fields['aspect_in'] = QtWidgets.QDoubleSpinBox(self)
        self.fields['aspect_in'].setRange(-1.0, 10.0)
        self.fields['aspect_in'].setDecimals(6)
        self.fields['aspect_in'].setValue(Options.aspect_in)
        self.fields['aspect_in'].valueChanged.connect( self.evaluate)
        layout.addWidget(self.fields['aspect_in'])
        layout.addWidget(QtWidgets.QLabel(' (-1 = no changes) ', self))
        grouplayout.addLayout(layout)

        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel('Auto Input Aspect', self)
        label.setToolTip(
            'Images with width/height ratio > this value will be treated as '
            '2:1.'
        )
        layout.addWidget(label)
        self.fields['aspect_auto'] = QtWidgets.QDoubleSpinBox(self)
        self.fields['aspect_auto'].setRange(-1.0, 10.0)
        self.fields['aspect_auto'].setDecimals(3)
        self.fields['aspect_auto'].setValue(Options.aspect_auto)
        self.fields['aspect_auto'].valueChanged.connect( self.evaluate)
        layout.addWidget(self.fields['aspect_auto'])
        layout.addWidget(QtWidgets.QLabel(' (-1 = no changes) ', self))
        grouplayout.addLayout(layout)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel('Output Movie Aspect', self))
        self.fields['aspect_out'] = QtWidgets.QDoubleSpinBox(self)
        self.fields['aspect_out'].setRange(-1.0, 10.0)
        self.fields['aspect_out'].setDecimals(6)
        self.fields['aspect_out'].setValue(Options.aspect_out)
        self.fields['aspect_out'].valueChanged.connect( self.evaluate)
        layout.addWidget(self.fields['aspect_out'])
        layout.addWidget(QtWidgets.QLabel(' (-1 = no changes) ', self))
        grouplayout.addLayout(layout)


        # Image Correction:
        group = QtWidgets.QGroupBox('Image Correction')
        grouplayout = QtWidgets.QHBoxLayout()
        group.setLayout(grouplayout)
        parameterslayout.addWidget(group)

        label = QtWidgets.QLabel('Colorspace:', self)
        label.setToolTip(
            'Specify input images colorspace:\n'
            'auto: Automatically from metadata.\n'
            'extension: Automatically from extension (exr,dpx,cin).'
        )
        grouplayout.addWidget(label)
        self.fields['colorspace'] = QtWidgets.QComboBox(self)
        i = 0
        for colorspace in Colorspaces:
            self.fields['colorspace'].addItem(colorspace)
            if colorspace == Options.colorspace:
                self.fields['colorspace'].setCurrentIndex(i)
            i += 1
        self.fields['colorspace'].currentIndexChanged.connect( self.evaluate)
        grouplayout.addWidget(self.fields['colorspace'])

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel('Gamma:', self))
        self.fields['gamma'] = QtWidgets.QDoubleSpinBox(self)
        self.fields['gamma'].setRange(0.1, 10.0)
        self.fields['gamma'].setDecimals(1)
        self.fields['gamma'].setSingleStep(0.1)
        self.fields['gamma'].setValue(1.0)
        self.fields['gamma'].valueChanged.connect( self.evaluate)
        layout.addWidget(self.fields['gamma'])
        grouplayout.addLayout(layout)

        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel('Custom Options:', self)
        layout.addWidget(label)
        label.setToolTip('Add this options to convert command.')
        self.fields['correction'] = QtWidgets.QLineEdit(Options.correction, self)
        self.fields['correction'].editingFinished.connect( self.evaluate)
        layout.addWidget(self.fields['correction'])
        grouplayout.addLayout(layout)


        # Temporary format options:
        group = QtWidgets.QGroupBox('Intermediate Images')
        parameterslayout.addWidget(group)
        grouplayout = QtWidgets.QHBoxLayout()
        group.setLayout(grouplayout)

        grouplayout.addWidget(QtWidgets.QLabel('Format:', self))
        self.fields['tmpformat'] = QtWidgets.QComboBox(self)
        i = 0
        for format in TmpImgFormats:
            self.fields['tmpformat'].addItem(format)
            if format == Options.tmpformat:
                self.fields['tmpformat'].setCurrentIndex(i)
            i += 1
        self.fields['tmpformat'].currentIndexChanged.connect( self.evaluate)
        grouplayout.addWidget(self.fields['tmpformat'])

        label = QtWidgets.QLabel('Quality Options:', self)
        grouplayout.addWidget(label)
        label.setToolTip('Add this options to temporary image saving.')
        self.fields['tmpquality'] = QtWidgets.QLineEdit(Options.tmpquality, self)
        self.fields['tmpquality'].editingFinished.connect( self.evaluate)
        grouplayout.addWidget(self.fields['tmpquality'])


        # Auto append output filename:
        layout = QtWidgets.QHBoxLayout()
        parameterslayout.addLayout(layout)
        self.fields['datesuffix'] = \
            QtWidgets.QCheckBox('Append Movie File Name With Date', self)
        self.fields['datesuffix'].setChecked(False)
        layout.addWidget(self.fields['datesuffix'])
        self.fields['datesuffix'].stateChanged.connect( self.evaluate)
        self.fields['timesuffix'] = \
            QtWidgets.QCheckBox('Append Movie File Name With Time', self)
        self.fields['timesuffix'].setChecked(False)
        layout.addWidget(self.fields['timesuffix'])
        self.fields['timesuffix'].stateChanged.connect( self.evaluate)


        # Stereo:

        self.fields['stereodub'] = \
            QtWidgets.QCheckBox('Duplicate first sequence', self)
        self.fields['stereodub'].setChecked(Options.stereodub)
        self.fields['stereodub'].stateChanged.connect( self.evalStereo)
        stereolayout.addWidget(self.fields['stereodub'])

        # Second Pattern:
        group = QtWidgets.QGroupBox('Second Sequence Pattern')
        stereolayout.addWidget(group)
        grouplayout = QtWidgets.QVBoxLayout()
        group.setLayout(grouplayout)

        self.fields['input1'] = QtWidgets.QLineEdit(InFile1, self)
        grouplayout.addWidget(self.fields['input1'])
        self.fields['input1'].textEdited.connect( self.inputFileChanged2)

        layout = QtWidgets.QHBoxLayout()
        self.btnInputFileCopy = \
            QtWidgets.QPushButton('Copy&&Paste First Sequence', self)
        layout.addWidget(self.btnInputFileCopy)
        self.btnInputFileCopy.pressed.connect( self.copyInput)
        layout.addWidget(QtWidgets.QLabel('Files count:', self))
        self.editInputFilesCount2 = QtWidgets.QLineEdit(self)
        layout.addWidget(self.editInputFilesCount2)
        self.editInputFilesCount2.setEnabled(False)
        layout.addWidget(QtWidgets.QLabel('Pattern:', self))
        self.editInputFilesPattern2 = QtWidgets.QLineEdit(self)
        layout.addWidget(self.editInputFilesPattern2)
        self.editInputFilesPattern2.setEnabled(False)
        self.btnInputFileBrowse2 = QtWidgets.QPushButton('Browse', self)
        layout.addWidget(self.btnInputFileBrowse2)
        self.btnInputFileBrowse2.pressed.connect( self.browseInput2)
        grouplayout.addLayout(layout)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel('Identify:', self))
        self.editIdentify2 = QtWidgets.QLineEdit(self)
        self.editIdentify2.setEnabled(False)
        layout.addWidget(self.editIdentify2)
        self.btnInputFileRefresh2 = QtWidgets.QPushButton('Refresh', self)
        layout.addWidget(self.btnInputFileRefresh2)
        self.btnInputFileRefresh2.pressed.connect( self.inputFileChanged2)
        grouplayout.addLayout(layout)

        layout = QtWidgets.QHBoxLayout()
        stereolayout.addLayout(layout)
        self.stereoStatusLabel = QtWidgets.QLabel('Stereo Status:', self)
        self.stereoStatusLabel.setAutoFillBackground(True)
        layout.addWidget(self.stereoStatusLabel)
        self.editStereoStatus = QtWidgets.QLineEdit(self)
        layout.addWidget(self.editStereoStatus)
        self.editStereoStatus.setReadOnly(True)


        # Decode:
        self.decodeEnable = QtWidgets.QCheckBox('Enable', self)
        decodeLayout.addWidget(self.decodeEnable)
        self.decodeEnable.stateChanged.connect( self.evaluate)
        self.decodeEnable.setChecked(True)
        group = QtWidgets.QGroupBox('Input Movie')
        decodeLayout.addWidget(group)
        grouplayout = QtWidgets.QVBoxLayout(group)
        layout = QtWidgets.QHBoxLayout()
        grouplayout.addLayout(layout)
        self.decodeInputFileName = QtWidgets.QLineEdit(self)
        layout.addWidget(self.decodeInputFileName)
        self.decodeInputFileName.textEdited.connect( self.decodeInputChanged)
        self.decodeInputBrowse = QtWidgets.QPushButton('Browse')
        layout.addWidget(self.decodeInputBrowse)
        self.decodeInputBrowse.pressed.connect( self.decodeBrowseInput)

        group = QtWidgets.QGroupBox('Output Sequence')
        decodeLayout.addWidget(group)
        grouplayout = QtWidgets.QVBoxLayout(group)
        layout = QtWidgets.QHBoxLayout()
        grouplayout.addLayout(layout)
        self.decodeOutputSequence = QtWidgets.QLineEdit(self)
        layout.addWidget(self.decodeOutputSequence)
        self.decodeOutputSequence.textEdited.connect( self.decodeOutputChanged)
        self.decodeOutputBrowse = QtWidgets.QPushButton('Browse')
        layout.addWidget(self.decodeOutputBrowse)
        self.decodeOutputBrowse.pressed.connect( self.decodeBrowseOutput)
        grouplayout.addWidget(QtWidgets.QLabel('Absolute Location:'))
        self.decodeOutputAbs = QtWidgets.QLineEdit(self)
        self.decodeOutputAbs.setReadOnly(True)
        grouplayout.addWidget(self.decodeOutputAbs)
        self.decodeEncode = QtWidgets.QCheckBox('Encode This Sequence', self)
        grouplayout.addWidget(self.decodeEncode)
        self.decodeEncode.setChecked(True)


        # Audio:
        group = QtWidgets.QGroupBox('Input Movie/Sound File')
        audioLayout.addWidget(group)
        grouplayout = QtWidgets.QVBoxLayout(group)
        layout = QtWidgets.QHBoxLayout()
        grouplayout.addLayout(layout)
        self.fields['audiofile'] = QtWidgets.QLineEdit(self)
        layout.addWidget(self.fields['audiofile'])
        self.fields['audiofile'].textEdited.connect( self.audioInputChanged)
        self.audioInputBrowse = QtWidgets.QPushButton('Browse')
        layout.addWidget(self.audioInputBrowse)
        self.audioInputBrowse.pressed.connect( self.audioBrowseInput)

        group = QtWidgets.QGroupBox('Settings')
        audioLayout.addWidget(group)
        grouplayout = QtWidgets.QVBoxLayout(group)
        layout = QtWidgets.QHBoxLayout()
        grouplayout.addLayout(layout)
        layout.addWidget(QtWidgets.QLabel('Sampling Frequency:'))
        self.fields['audiofreq'] = QtWidgets.QSpinBox(self)
        layout.addWidget(self.fields['audiofreq'])
        self.fields['audiofreq'].setRange(1, 96)
        self.fields['audiofreq'].setValue(22)
        layout.addWidget(QtWidgets.QLabel('kHz'))
        self.fields['audiofreq'].valueChanged.connect( self.evaluate)
        layout = QtWidgets.QHBoxLayout()
        grouplayout.addLayout(layout)
        layout.addWidget(QtWidgets.QLabel('Bit Rate:'))
        self.fields['audiorate'] = QtWidgets.QSpinBox(self)
        layout.addWidget(self.fields['audiorate'])
        self.fields['audiorate'].setRange(32, 256)
        self.fields['audiorate'].setValue(128)
        layout.addWidget(QtWidgets.QLabel('kB/s'))
        self.fields['audiorate'].valueChanged.connect( self.evaluate)
        layout = QtWidgets.QHBoxLayout()
        grouplayout.addLayout(layout)
        layout.addWidget(QtWidgets.QLabel('Codec:'))
        self.fields['audiocodec'] = QtWidgets.QComboBox(self)
        layout.addWidget(self.fields['audiocodec'])
        i = 0
        for acodec in AudioCodecNames:
            self.fields['audiocodec'].addItem(acodec, AudioCodecValues[i])
            i += 1
        self.fields['audiocodec'].setCurrentIndex(0)
        self.fields['audiocodec'].currentIndexChanged.connect( self.evaluate)


        # Afanasy:
        self.cAfanasy = QtWidgets.QCheckBox('Enable', self)
        self.cAfanasy.setChecked(Options.afanasy)
        self.cAfanasy.stateChanged.connect( self.evaluate)
        afanasylayout.addWidget(self.cAfanasy)

        # Priority
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel('Priority:', self))
        self.sbAfPriority = QtWidgets.QSpinBox(self)
        self.sbAfPriority.setRange(-1, 1000000)
        self.sbAfPriority.setValue(Options.afpriority)
        self.sbAfPriority.valueChanged.connect( self.evaluate)
        layout.addWidget(self.sbAfPriority)
        layout.addWidget(QtWidgets.QLabel('"-1" Means default value.', self))
        afanasylayout.addLayout(layout)

        # Hosts
        group = QtWidgets.QGroupBox('Hosts')
        afanasylayout.addWidget(group)
        grouplayout = QtWidgets.QVBoxLayout()
        group.setLayout(grouplayout)

        layout = QtWidgets.QHBoxLayout()
        grouplayout.addLayout(layout)
        layout.addWidget(QtWidgets.QLabel('Maximum Number:', self))
        self.sbAfMaxHosts = QtWidgets.QSpinBox(self)
        self.sbAfMaxHosts.setRange(-1, 1000000)
        self.sbAfMaxHosts.setValue(Options.afmaxhosts)
        self.sbAfMaxHosts.valueChanged.connect( self.evaluate)
        layout.addWidget(self.sbAfMaxHosts)
        layout.addWidget(
            QtWidgets.QLabel('"-1" Means no hosts count limit.', self)
        )

        layout = QtWidgets.QHBoxLayout()
        grouplayout.addLayout(layout)
        layout.addWidget(QtWidgets.QLabel('Hosts Names Mask:', self))
        self.editAfHostsMask = QtWidgets.QLineEdit(Options.afhostsmask, self)
        self.editAfHostsMask.textEdited.connect( self.evaluate)
        layout.addWidget(self.editAfHostsMask)
        layout.addWidget(QtWidgets.QLabel('Leave empty to run on any host.', self))

        layout = QtWidgets.QHBoxLayout()
        grouplayout.addLayout(layout)
        layout.addWidget(QtWidgets.QLabel('Exclude Hosts Names Mask:', self))
        self.editAfHostsMaskExclude = \
            QtWidgets.QLineEdit(Options.afhostsmaskex, self)
        self.editAfHostsMaskExclude.textEdited.connect( self.evaluate)
        layout.addWidget(self.editAfHostsMaskExclude)
        layout.addWidget(
            QtWidgets.QLabel('Leave empty not to exclude any host.', self))

        # Depends
        group = QtWidgets.QGroupBox('Depends')
        afanasylayout.addWidget(group)
        grouplayout = QtWidgets.QVBoxLayout()
        group.setLayout(grouplayout)

        layout = QtWidgets.QHBoxLayout()
        grouplayout.addLayout(layout)
        layout.addWidget(QtWidgets.QLabel('Depend Jobs Mask:', self))
        self.editAfDependMask = QtWidgets.QLineEdit(Options.afdependmask, self)
        self.editAfDependMask.textEdited.connect( self.evaluate)
        layout.addWidget(self.editAfDependMask)
        layout.addWidget(
            QtWidgets.QLabel('Leave empty not to wait any jobs.', self)
        )

        layout = QtWidgets.QHBoxLayout()
        grouplayout.addLayout(layout)
        layout.addWidget(QtWidgets.QLabel('Global Depend Jobs Mask:', self))
        self.editAfDependMaskGlobal = \
            QtWidgets.QLineEdit(Options.afdependmaskgl, self)
        self.editAfDependMaskGlobal.textEdited.connect( self.evaluate)
        layout.addWidget(self.editAfDependMaskGlobal)
        layout.addWidget(QtWidgets.QLabel('Set mask to wait any user jobs.', self))

        # Capacity
        group = QtWidgets.QGroupBox('Capacity')
        layout = QtWidgets.QHBoxLayout()
        group.setLayout(layout)
        afanasylayout.addWidget(group)

        self.cAfOneTask = QtWidgets.QCheckBox('One Task', self)
        self.cAfOneTask.setChecked(True)
        self.cAfOneTask.stateChanged.connect( self.evaluate)
        layout.addWidget(self.cAfOneTask)

        layout.addWidget(QtWidgets.QLabel('Capacity:', self))
        self.sbAfCapacity = QtWidgets.QSpinBox(self)
        self.sbAfCapacity.setRange(-1, 1000000)
        self.sbAfCapacity.setValue(Options.afcapacity)
        self.sbAfCapacity.valueChanged.connect( self.evaluate)
        layout.addWidget(self.sbAfCapacity)

        layout.addWidget(QtWidgets.QLabel('Convert:', self))
        self.sbAfCapConvert = QtWidgets.QSpinBox(self)
        self.sbAfCapConvert.setRange(-1, 1000000)
        self.sbAfCapConvert.setValue(Options.afcapacity)
        self.sbAfCapConvert.valueChanged.connect( self.evaluate)
        layout.addWidget(self.sbAfCapConvert)

        layout.addWidget(QtWidgets.QLabel('Encode:', self))
        self.sbAfCapEncode = QtWidgets.QSpinBox(self)
        self.sbAfCapEncode.setRange(-1, 1000000)
        self.sbAfCapEncode.setValue(Options.afcapacity)
        self.sbAfCapEncode.valueChanged.connect( self.evaluate)
        layout.addWidget(self.sbAfCapEncode)


        # Pause
        layout = QtWidgets.QHBoxLayout()
        afanasylayout.addLayout(layout)

        self.cAfPause = QtWidgets.QCheckBox('Start Job Paused', self)
        self.cAfPause.setChecked(Options.afpause)
        self.cAfPause.stateChanged.connect( self.evaluate)
        layout.addWidget(self.cAfPause)

        layout.addWidget(QtWidgets.QLabel('Start At Time:', self))
        self.editAfTime = QtWidgets.QDateTimeEdit(
            QtCore.QDateTime.currentDateTime(), self)
        self.editAfTime.setDisplayFormat(TimeFormat)
        self.editAfTime.setCalendarPopup(True)
        self.editAfTime.dateTimeChanged.connect( self.evaluate)
        layout.addWidget(self.editAfTime)


        # Output Field:

        self.cmdField = QtWidgets.QTextEdit(self)
        mainLayout.addWidget(self.cmdField)


        # Main Buttons:

        layout = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(layout)

        self.btnStart = QtWidgets.QPushButton('&Start', self)
        layout.addWidget(self.btnStart)
        self.btnStart.setEnabled(False)
        self.btnStart.pressed.connect( self.execute)

        self.btnRefresh = QtWidgets.QPushButton('&Refresh', self)
        layout.addWidget(self.btnRefresh)
        self.btnRefresh.pressed.connect( self.evaluate)

        self.btnStop = QtWidgets.QPushButton('Sto&p', self)
        self.btnStop.setEnabled(False)
        self.btnStop.pressed.connect( self.processStop)
        layout.addWidget(self.btnStop)

        layout.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding))
        layout.addWidget(QtWidgets.QLabel('Recent:', self))

        self.cbRecent = QtWidgets.QComboBox(self)
        self.cbRecent.activated.connect( self.loadRecent)
        layout.addWidget(self.cbRecent)

        self.bBrowseLoad = QtWidgets.QPushButton('Load', self)
        layout.addWidget(self.bBrowseLoad)
        self.bBrowseLoad.pressed.connect( self.browseLoad)

        self.bBrowseSave = QtWidgets.QPushButton('Save', self)
        layout.addWidget(self.bBrowseSave)
        self.bBrowseSave.pressed.connect( self.browseSave)

        # self.bQuitSave = QtWidgets.QPushButton('&Quit&&Store', self)
        # layout.addWidget(self.bQuitSave)
        # self.bQuitSave.'pressed.connect( self.quitsave)

        self.autoTitles()
        self.activityChanged()
        self.autoOutputName()
        self.inputFileChanged()
        self.inputFileChanged2()
        self.refreshRecent()
        self.constructed = True
        self.evaluate()

    # Decode:
    def decodeBrowseInput(self):
        afile, fltr = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Choose a movie file',
            self.decodeInputFileName.text()
        )
        if len(afile):
            self.decodeInputFileName.setText(afile)
            self.decodeInputChanged()

    def decodeBrowseOutput(self):
        afile, fltr = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Choose a sequence',
            self.decodeOutputSequence.text()
        )
        if len(afile):
            self.decodeOutputSequence.setText(afile)
            self.decodeOutputChanged()

    def decodeInputChanged(self):
        afile = "%s" % self.decodeInputFileName.text()
        if len(afile):
            pos = afile.rfind('file://')
            if pos >= 0:
                afile = afile[pos + 7:]
            afile = afile.strip()
            afile = afile.strip('\n')
            self.decodeInputFileName.setText(afile)
            basename = os.path.basename(afile)
            self.decodeOutputSequence.setText(
                os.path.join(
                    basename + '-png',
                    basename + '.%07d.png'
                )
            )
            self.decodeEvaluate()

    def decodeOutputChanged(self):
        self.decodeEvaluate()

    def decodeEvaluate(self):
        if not self.decodeEnable.isChecked():
            return False
        self.evaluated = False
        self.btnStart.setEnabled(False)
        if self.running:
            return False
        self.cmdField.clear()

        inputMovie = "%s" % self.decodeInputFileName.text()
        if len(inputMovie) == 0:
            self.cmdField.setText(
                'Specify input movie to explode into sequence.'
            )
            return False

        inputMovie = os.path.normpath(os.path.abspath(inputMovie))
        if not os.path.isfile(inputMovie):
            self.cmdField.setText('Movie file to decode does not exist.')
            return False

        outputSequence = "%s" % self.decodeOutputSequence.text()
        if len(outputSequence) == 0:
            self.cmdField.setText(
                'Specify output sequence to explode input movie into.')
            return False

        outputSequence = os.path.normpath(
            os.path.join(os.path.dirname(inputMovie), outputSequence)
        )
        self.decodeOutputAbs.setText(outputSequence)

        cmd = \
            os.environ['CGRU_LOCATION'] + '/utilities/moviemaker/movconvert.py'
        cmd = os.path.normpath(cmd)
        cmd = 'python "%s"' % cmd
        cmd = cmd + (' "%s" "%s"' % (inputMovie, outputSequence))

        self.cmdField.setText(cmd)
        self.evaluated = True
        self.btnStart.setEnabled(True)
        self.decode = True
        return True

    # Encode:
    def audioBrowseInput(self):
        afile, fltr = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Choose an audio or movie file with sound',
            self.fields['audiofile'].text()
        )
        if len(afile):
            self.fields['audiofile'].setText(afile)
            self.audioInputChanged()

    def audioInputChanged(self):
        afile = '%s' % self.fields['audiofile'].text()
        if len(afile):
            pos = afile.rfind('file://')
            if pos >= 0:
                afile = afile[pos + 7:]
                afile = afile.strip()
                afile = afile.strip('\n')
                self.fields['audiofile'].setText(afile)
            self.evaluate()

    def evalStereo(self):
        if self.running:
            return
        if self.inputPattern2 is None:
            self.fields['stereodub'].setEnabled(True)
            if self.fields['stereodub'].isChecked():
                self.editStereoStatus.setText('Stereo from one sequence.')
                self.stereoStatusLabel.setBackgroundRole(QtWidgets.QPalette.Dark)
            else:
                self.editStereoStatus.setText(
                    'No stereo. Specify second sequence or enable duplicate '
                    'one sequence.'
                )
                self.stereoStatusLabel.setAutoFillBackground(True)
                self.stereoStatusLabel.setBackgroundRole( QtGui.QPalette.Window)
        else:
            self.fields['stereodub'].setChecked(False)
            self.fields['stereodub'].setEnabled(False)
            if self.editInputFilesCount.text() == self.editInputFilesCount2.text():
                self.editStereoStatus.setText('Stereo from two sequences.')
                self.stereoStatusLabel.setBackgroundRole(
                    QtWidgets.QPalette.LinkVisited)
            else:
                self.inputPattern2 = None
                self.editStereoStatus.setText(
                    'Two sequences must be the same length.')
                self.evaluated = False
                self.btnStart.setEnabled(False)
                self.cmdField.setText('Sequences length mismatch.')
                return
        if self.inputPattern is not None:
            self.evaluate()

    def copyInput(self):
        files1 = self.fields['input0'].text()
        if len(files1):
            self.fields['input1'].setText(files1)
        self.inputFileChanged2()

    def autoOutputName(self):
        enable = not self.fields['usenamerule'].isChecked()
        self.fields['outputname'].setEnabled(enable)
        self.cbNaming.setEnabled(not enable)
        self.fields['namerule'].setEnabled(not enable)
        self.evaluate()

    def autoTitles(self):
        enable = not self.fields['autotitles'].isChecked()
        self.fields['project'].setEnabled(enable)
        self.fields['shot'].setEnabled(enable)
        self.fields['version'].setEnabled(enable)

    def activityChanged(self):
        self.fields['activity'].setText(self.cbActivity.currentText())
        self.evaluate()

    def namingChanged(self):
        self.fields['namerule'].setText(self.cbNaming.currentText())
        self.evaluate()

    def fontChanged(self):
        self.fields['font'].setText(self.cbFont.currentText())
        self.evaluate()

    def browseLgs(self):
        lgspath = LogosPath
        oldlogo = '%s' % self.fields['lgspath'].text()
        if oldlogo != '':
            dirname = os.path.dirname(oldlogo)
            if dirname != '':
                lgspath = dirname
        afile, fltr = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose a file', lgspath)
        if len(afile):
            self.fields['lgspath'].setText('%s' % afile)
            self.evaluate()

    def browseLgf(self):
        lgfpath = LogosPath
        oldlogo = '%s' % self.fields['lgfpath'].text()
        if oldlogo != '':
            dirname = os.path.dirname(oldlogo)
            if dirname != '':
                lgfpath = dirname
        afile, fltr = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose a file', lgfpath)
        if len(afile):
            self.fields['lgfpath'].setText('%s' % afile)
            self.evaluate()

    def browseOutputFolder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            'Choose a directory',
            os.path.dirname(
                '%s' % self.fields['outputfolder'].text()
            )
        )
        if len(folder):
            self.fields['outputfolder'].setText(folder)

    def browseInput(self):
        afile, fltr = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Choose a file',
            self.fields['input0'].text()
        )
        if len(afile):
            self.fields['input0'].setText(afile)
            self.inputFileChanged()

    def browseInput2(self):
        afile, fltr = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Choose a file',
            self.fields['input1'].text()
        )
        if len(afile):
            self.fields['input1'].setText(afile)
            self.inputFileChanged2()

    def inputFileChanged(self):
        if self.running:
            return
        self.editInputFilesCount.clear()
        self.editInputFilesPattern.clear()
        self.editIdentify.clear()
        inputfile = '%s' % self.fields['input0'].text()
        InputFile, InputPattern, FilesCount, Identify = \
            self.calcPattern(inputfile)

        self.inputPattern = InputPattern
        if InputPattern == None:
            return

        self.fields['input0'].setText(InputFile)
        self.editInputFilesPattern.setText(os.path.basename(InputPattern))
        self.editInputFilesCount.setText('%d' % FilesCount)
        self.editIdentify.setText(Identify)

        self.evaluate()

    def inputFileChanged2(self):
        if self.running:
            return
        self.editInputFilesCount2.clear()
        self.editInputFilesPattern2.clear()
        self.editIdentify2.clear()
        inputfile = '%s' % self.fields['input1'].text()
        InputFile, InputPattern, FilesCount, Identify = \
            self.calcPattern(inputfile)

        self.inputPattern2 = InputPattern
        if InputPattern is not None:
            self.fields['input1'].setText(InputFile)
            self.editInputFilesPattern2.setText(os.path.basename(InputPattern))
            self.editInputFilesCount2.setText('%d' % FilesCount)
            self.editIdentify2.setText(Identify)
        self.evalStereo()

    def calcPattern(self, InputFile):
        self.evaluated = False
        self.btnStart.setEnabled(False)

        InputPattern = None
        FilesCount = 0
        Identify = ''
        if sys.platform.find('win') == 0:
            InputFile = InputFile.replace('/', '\\')

        if len(InputFile) == 0:
            self.cmdField.setText('Choose one file from sequence.')
            return InputFile, InputPattern, FilesCount, Identify

        # Remove link and strip filename:
        pos = InputFile.rfind('file://')
        if pos >= 0:
            InputFile = InputFile[pos + 7:]
        InputFile = InputFile.strip()
        InputFile = InputFile.strip('\n')

        # If directory is specified, use the first file in it:
        if os.path.isdir(InputFile):
            dirfiles = os.listdir(InputFile)
            if len(dirfiles) == 0:
                print('Folder "%s" is empty.' % InputFile)
                return InputFile, InputPattern, FilesCount, Identify
            InputFile = os.path.join(InputFile, dirfiles[0])

        inputdir = os.path.dirname(InputFile)
        if not os.path.isdir(inputdir):
            self.cmdField.setText('Can\'t find input directory.')
            return InputFile, InputPattern, FilesCount, Identify
        filename = os.path.basename(InputFile)

        # Search %04d pattern:
        digitsall = re.findall(r'%0\dd', filename)
        if len(digitsall):
            padstr = digitsall[-1]
            padding = int(padstr[2])
            pos = filename.rfind(padstr)
            prefix = filename[: pos]
            suffix = filename[pos + 4:]
        else:
            # Search %d pattern:
            digitsall = re.findall(r'%d', filename)
            if len(digitsall):
                padstr = digitsall[-1]
                padding = -1
                pos = filename.rfind(padstr)
                prefix = filename[: pos]
                suffix = filename[pos + 2:]
            else:
                # Search #### pattern:
                digitsall = re.findall(r'(#+)', filename)
                if len(digitsall) == 0:
                    # Search digits pattern:
                    digitsall = re.findall(r'([0-9]+)', filename)
                if len(digitsall):
                    digits = digitsall[-1]
                    pos = filename.rfind(digits)
                    prefix = filename[: pos]
                    padding = len(digits)
                    suffix = filename[pos + padding:]
                    padstr = ''
                    for d in range(padding):
                        padstr += '#'
                else:
                    self.cmdField.setText(
                        'Can\'t find digits in input file name.'
                    )
                    return InputFile, InputPattern, FilesCount, Identify

        pattern = prefix + padstr + suffix

        if padding > 1:
            expr = re.compile(
                r'%(prefix)s([0-9]{%(padding)d,%(padding)d})%(suffix)s' % vars())
        else:
            expr = re.compile(r'%(prefix)s([0-9]+)%(suffix)s' % vars())
        FilesCount = 0
        framefirst = -1
        framelast = -1
        prefixlen = len(prefix)
        suffixlen = len(suffix)
        allItems = os.listdir(inputdir)
        for item in allItems:
            if not os.path.isfile(os.path.join(inputdir, item)):
                continue
            match = expr.match(item)
            if not match:
                continue
            if match.group(0) != item:
                continue
            if FilesCount == 0:
                afile = item
            FilesCount += 1
            frame = int(item[prefixlen:-suffixlen])
            if framefirst == -1:
                framefirst = frame
            if framelast == -1:
                framelast = frame
            if framefirst > frame:
                framefirst = frame
            if framelast < frame:
                framelast = frame
        if FilesCount <= 1:
            self.cmdField.setText(('None or only one file found matching pattern.\n'
                                   'prefix, padding, suffix = "%(prefix)s" '
                                   '%(padding)d "%(suffix)s\n"' % vars()) + expr.pattern)
            return InputFile, InputPattern, FilesCount, Identify
        self.fields['framestart'].setRange(framefirst, framelast)
        self.fields['framestart'].setValue(framefirst)
        self.sbFrameLast.setRange(framefirst, framelast)
        self.sbFrameLast.setValue(framelast)
        if sys.platform.find('win') == 0:
            afile = afile.replace('/', '\\')
        if self.cbIdentify.isChecked():
            afile = os.path.join(inputdir, afile)
            identify = 'convert -identify "%s"'
            if sys.platform.find('win') == 0:
                identify += ' nul'
            else:
                identify += ' /dev/null'

            Identify = subprocess.Popen(
                identify % afile,
                shell=True,
                bufsize=100000,
                stdout=subprocess.PIPE
            ).stdout.read()

            if len(Identify) < len(afile):
                self.cmdField.setText('Invalid image.\n%s' % afile)
                return InputFile, InputPattern, FilesCount, Identify
            if not isinstance(Identify, str):
                Identify = str(Identify, 'utf-8')
            Identify = Identify.strip()
            Identify = Identify.replace(afile, '')
        InputPattern = os.path.join(inputdir, pattern)

        return InputFile, InputPattern, FilesCount, Identify

    def validateEditColor(self, string, message):
        if string is None:
            return False
        if string == '':
            return True
        values = string.split(',')
        if len(values) == 3:
            passed = True
            for value in values:
                if len(value) < 1 or len(value) > 3:
                    passed = False
                    break
                for digit in value:
                    if not digit in '1234567890':
                        passed = False
                        break
            if passed:
                return True
        self.cmdField.setText(
            'Invalid %s color string. Example: "255,255,0" - yellow.' % message
        )
        return False

    def evaluate(self):
        if not self.constructed:
            return
        self.evaluated = False
        self.btnStart.setEnabled(False)
        if self.running:
            return
        if self.decodeEvaluate():
            return
        self.decode = False
        self.cmdField.clear()

        if not self.validateEditColor(str(self.fields['line169'].text()), 'line 16:9'):
            return
        if not self.validateEditColor(str(self.fields['line235'].text()), 'line 2.35'):
            return

        if self.inputPattern is None:
            self.cmdField.setText('Specify input sequence.')
            return

        audiofile = '%s' % self.fields['audiofile'].text()
        if len(audiofile):
            audiofile = os.path.abspath(os.path.normpath(audiofile))
            if not os.path.isfile(audiofile):
                self.cmdField.setText('Error: Audio file does not exist.')
                return

        self.StereoDuplicate = self.fields['stereodub'].isChecked()

        if self.fields['autotitles'].isChecked():
            self.fields['shot'].clear()
        if self.fields['usenamerule'].isChecked():
            self.fields['outputname'].clear()

        project = '%s' % self.fields['project'].text()
        if Options.project == '':
            if self.fields['autotitles'].isChecked() or project == '':
                if sys.platform.find('win') == 0:
                    pat_split = self.inputPattern.upper().split('\\')
                    if len(pat_split) > 4:
                        project = pat_split[4]
                    else:
                        project = pat_split[-1]
                else:
                    pat_split = self.inputPattern.upper().split('/')
                    if len(pat_split) > 3:
                        project = pat_split[3]
                    else:
                        project = pat_split[-1]
                self.fields['project'].setText(project)

        shot = '%s' % self.fields['shot'].text()
        if self.fields['autotitles'].isChecked() or shot == '':
            shot = os.path.basename(self.inputPattern)[:os.path.basename(self.inputPattern).find('.')]
            self.fields['shot'].setText(shot)

        version = '%s' % self.fields['version'].text()
        if self.fields['autotitles'].isChecked() or version == '':
            version = os.path.basename(os.path.dirname(self.inputPattern))
            self.fields['version'].setText(version)

        localtime = time.localtime()
        if self.cbFakeTime.isChecked():
            localtime = time.localtime(1.0 * self.fakeTime.dateTime().toTime_t())

        company = '%s' % self.fields['company'].text()
        artist = '%s' % self.fields['artist'].text()
        activity = '%s' % self.fields['activity'].text()
        comments = '%s' % self.fields['comments'].text()
        font = '%s' % self.fields['font'].text()
        date = time.strftime('%y%m%d', localtime)

        outdir = '%s' % self.fields['outputfolder'].text()
        if outdir == '':
            outdir = os.path.dirname(os.path.dirname(self.inputPattern))
            self.fields['outputfolder'].setText(outdir)

        outname = '%s' % self.fields['outputname'].text()
        if self.fields['usenamerule'].isChecked() \
                or outname is None or outname == '':
            outname = '%s' % self.fields['namerule'].text()
            outname = outname.replace('(p)', project)
            outname = outname.replace('(P)', project.upper())
            outname = outname.replace('(s)', shot)
            outname = outname.replace('(S)', shot.upper())
            outname = outname.replace('(v)', version)
            outname = outname.replace('(V)', version.upper())
            outname = outname.replace('(d)', date)
            outname = outname.replace('(D)', date.upper())
            outname = outname.replace('(a)', activity)
            outname = outname.replace('(A)', activity.upper())
            outname = outname.replace('(c)', company)
            outname = outname.replace('(C)', company.upper())
            outname = outname.replace('(u)', artist)
            outname = outname.replace('(U)', artist.upper())
            self.fields['outputname'].setText(outname)

        lgspath = '%s' % self.fields['lgspath'].text()
        if lgspath != '':
            if not os.path.isfile(lgspath):
                if not os.path.isfile(os.path.join(LogosPath, lgspath)):
                    self.cmdField.setText('No slate logo file found')
                    return

        lgfpath = '%s' % self.fields['lgfpath'].text()
        if lgfpath != '':
            if not os.path.isfile(lgfpath):
                if not os.path.isfile(os.path.join(LogosPath, lgfpath)):
                    self.cmdField.setText('No frame logo file found')
                    return

        cmd = 'makemovie.py'
        cmd = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), cmd)
        cmd = '%s "%s"' % (os.getenv('CGRU_PYTHONEXE', 'python'), cmd)
        if len(self.fields['avcmd'].text()):
            cmd += ' -a "%s"' % self.fields['avcmd'].text()
        cmd += ' -c "%s"' % getComboBoxString(self.fields['codec'])
        cmd += ' -f %s' % self.fields['fps'].currentText()
        cmd += ' -n %s' % self.fields['container'].currentText()
        cmd += ' --fs %d' % self.fields['framestart'].value()
        cmd += ' --fe %d' % self.sbFrameLast.value()

        format = getComboBoxString(self.fields['format'])
        if format != '':
            if self.fields['fffirst'].isChecked():
                cmd += ' --fffirst'
            ts = self.fields['slate'].currentText()
            tf = self.fields['template'].currentText()
            cmd += ' -r %s' % format
            cmd += ' -g %.2f' % self.fields['gamma'].value()
            if ts != '':
                cmd += ' -s "%s"' % ts
            if tf != '':
                cmd += ' -t "%s"' % tf
            if project != '':
                cmd += ' --project "%s"' % project
            if shot != '':
                cmd += ' --shot "%s"' % shot
            if version != '':
                cmd += ' --ver "%s"' % version
            if company != '':
                cmd += ' --company "%s"' % company
            if artist != '':
                cmd += ' --artist "%s"' % artist
            if activity != '':
                cmd += ' --activity "%s"' % activity
            if comments != '':
                cmd += ' --comments "%s"' % comments
            if font != '':
                cmd += ' --font "%s"' % font
            cmd += ' --tmpformat %s' % self.fields['tmpformat'].currentText()
            if len(self.fields['tmpquality'].text()):
                cmd += ' --tmpquality "%s"' % self.fields['tmpquality'].text()
            if self.fields['aspect_in'].value() > 0:
                cmd += ' --aspect_in %f' % self.fields['aspect_in'].value()
            if self.fields[
                'aspect_auto'].value() > 0:
                cmd += ' --aspect_auto %f' % self.fields['aspect_auto'].value()
            if self.fields['aspect_out'].value() > 0:
                cmd += ' --aspect_out %f' % self.fields['aspect_out'].value()
            if len(self.fields['colorspace'].currentText()):
                cmd += ' --colorspace "%s"' % self.fields[
                    'colorspace'].currentText()
            if len(self.fields['correction'].text()):
                cmd += ' --correction "%s"' % self.fields['correction'].text()
            if self.fields['addtime'].isChecked():
                cmd += ' --addtime'
            cacher = getComboBoxString(self.fields['cacher_opacity'])
            if cacher != '0':
                cmd += ' --cacher_aspect %f' % self.fields[
                    'cacher_aspect'].value()
                cmd += ' --cacher_opacity %s' % cacher
            if len(self.fields['line_color'].text()):
                cmd += ' --line_aspect "%s"' % self.fields[
                    'line_aspect'].value()
                cmd += ' --line_color "%s"' % self.fields['line_color'].text()
            cacher = getComboBoxString(self.cbCacher169)
            if cacher != '0':
                cmd += ' --draw169 %s' % cacher
            cacher = getComboBoxString(self.cbCacher235)
            if cacher != '0':
                cmd += ' --draw235 %s' % cacher
            if len(self.fields['line169'].text()):
                cmd += ' --line169 "%s"' % self.fields['line169'].text()
            if len(self.fields['line235'].text()):
                cmd += ' --line235 "%s"' % self.fields['line235'].text()
            if lgspath != '':
                cmd += ' --lgspath "%s"' % lgspath
                cmd += ' --lgssize %d' % self.fields['lgssize'].value()
                cmd += ' --lgsgrav %s' % self.fields['lgsgrav'].currentText()
            if lgfpath != '':
                cmd += ' --lgfpath "%s"' % lgfpath
                cmd += ' --lgfsize %d' % self.fields['lgfsize'].value()
                cmd += ' --lgfgrav %s' % self.fields['lgfgrav'].currentText()

        if self.fields['datesuffix'].isChecked():
            cmd += ' --datesuffix'
        if self.fields['timesuffix'].isChecked():
            cmd += ' --timesuffix'
        if self.cbFakeTime.isChecked():
            cmd += ' --faketime %d' % self.fakeTime.dateTime().toTime_t()

        if self.StereoDuplicate and self.inputPattern2 is None:
            cmd += ' --stereodub'
        if audiofile != '':
            cmd += ' --audio "%s"' % audiofile
            cmd += ' --afreq %d' % (self.fields['audiofreq'].value() * 1000)
            cmd += ' --akbits %d' % self.fields['audiorate'].value()
            cmd += ' --acodec "%s"' % getComboBoxString(
                self.fields['audiocodec'])
        if self.cAfanasy.isChecked() and not self.cAfOneTask.isChecked():
            cmd += ' -A'
            if self.sbAfCapConvert.value() != -1:
                cmd += ' --afconvcap %d' % self.sbAfCapConvert.value()
            if self.sbAfCapEncode.value() != -1:
                cmd += ' --afenccap %d' % self.sbAfCapEncode.value()
        if Options.debug:
            cmd += ' --debug'

        cmd += ' "%s"' % self.inputPattern
        if self.inputPattern2 is not None:
            cmd += ' "%s"' % self.inputPattern2
        cmd += ' "%s"' % os.path.join(outdir, outname)

        self.cmdField.setText(cmd)
        self.evaluated = True
        self.btnStart.setEnabled(True)
        print('Evaluated.')

    def execute(self):
        if not self.evaluated:
            return
        command = '%s' % self.cmdField.toPlainText()
        if len(command) == 0:
            return

        afanasy = False
        if self.cAfanasy.isChecked():
            if self.cAfOneTask.isChecked() or self.decode:
                afanasy = True
        if afanasy:
            self.btnStart.setEnabled(False)
            try:
                af = __import__('af', globals(), locals(), [])
            except:
                error = str(sys.exc_info()[1])
                print(error)
                self.cmdField.setText(
                    'Unable to import Afanasy Python module:\n%s' % error
                )
                return
            if self.decode:
                jobname = '%s' % self.decodeOutputSequence.text()
                jobname = os.path.basename(jobname)
            else:
                jobname = '%s' % self.fields['outputname'].text()
            job = af.Job(jobname)
            block = af.Block('Make Movie', 'movgen')
            if self.sbAfPriority.value() != -1:
                job.setPriority(self.sbAfPriority.value())
            if self.sbAfMaxHosts.value() != -1:
                job.setMaxHosts(self.sbAfMaxHosts.value())
            if self.sbAfCapacity.value() != -1:
                block.setCapacity(self.sbAfCapacity.value())
            hostsmask = '%s' % self.editAfHostsMask.text()
            hostsmaskexclude = '%s' % self.editAfHostsMaskExclude.text()
            dependmask = '%s' % self.editAfDependMask.text()
            dependmaskglobal = '%s' % self.editAfDependMaskGlobal.text()
            if hostsmask != '':
                job.setHostsMask(hostsmask)
            if hostsmaskexclude != '':
                job.setHostsMaskExclude(hostsmaskexclude)
            if dependmask != '':
                job.setDependMask(dependmask)
            if dependmaskglobal != '':
                job.setDependMaskGlobal(dependmaskglobal)
            datetime = self.editAfTime.dateTime()
            if datetime > QtCore.QDateTime.currentDateTime():
                job.setWaitTime(datetime.toTime_t())
            if self.cAfPause.isChecked():
                job.pause()
            job.setNeedOS('')
            job.blocks.append(block)
            task = af.Task(('%s' % self.fields['outputname'].text()))
            task.setCommand(command)

            block.tasks.append(task)
            if job.send():
                self.cmdField.setText('Afanasy job was successfully sent.')
                self.saveRecent()
                if self.decode and self.decodeEncode.isChecked():
                    self.fields['input0'].setText(self.decodeOutputAbs.text())
            else:
                self.cmdField.setText('Unable to send job to Afanasy server.')
        else:
            self.btnStart.setEnabled(False)
            self.btnRefresh.setEnabled(False)
            self.btnStop.setEnabled(True)
            self.cmdField.clear()
            self.running = True
            self.process = QtCore.QProcess(self)
            self.process.setProcessChannelMode(QtCore.QProcess.MergedChannels)
            self.process.error.connect( self.processerror)
            self.process.finished.connect( self.processfinished)
            self.process.readyRead.connect( self.processoutput)
            print('\n################################################\n')
            if sys.version_info[0] < 3:
                print(command)
            else:
                print(bytearray(command, 'utf-8'))
            self.process.start(command)

    def processerror(self, error):
        self.cmdField.setText('Failed to start a process.')
        self.processfinished(-1)

    def processfinished(self, exitCode):
        print('Exit code = %d' % exitCode)
        self.btnStop.setEnabled(False)
        self.btnRefresh.setEnabled(True)
        self.running = False
        if exitCode != 0:
            return
        if not self.decode:
            self.saveRecent()
        self.cmdField.setText('Finished.')
        if self.decode and self.decodeEncode.isChecked():
            self.decodeEnable.setChecked(False)
            self.fields['input0'].setText(self.decodeOutputAbs.text())
            self.inputFileChanged()

    def processoutput(self):
        output = self.process.readAll().data()
        if not isinstance(output, str):
            output = str(output, 'utf-8')
        output = output.strip()
        print('%s' % output)
        self.cmdField.insertPlainText(output + '\n')
        self.cmdField.moveCursor( QtGui.QTextCursor.End)

    def processStop(self):
        if self.process.pid() is None or self.process.pid() == 0:
            self.cmdField.setText('The process was not running.')
            self.processfinished(-1)
            return
        self.cmdField.setText('Stopping %d ...' % self.process.pid())
        self.process.terminate()
        if sys.platform.find('win') == 0:
            self.process.kill()

    def save(self, filename, fullPath=False):
        if not fullPath:
            filename = os.path.join(
                cgruconfig.VARS['HOME_CGRU'],
                FilePrefix
            ) + filename + FileSuffix

        if sys.version_info[0] < 3:
            file = open(filename, 'w')
        else:
            file = open(filename, 'w', buffering=-1, encoding='utf-8')

        for key in self.fields:
            value = ''
            if isinstance(self.fields[key], QtWidgets.QLineEdit):
                value = cgruutils.toStr('%s' % self.fields[key].text())
            elif isinstance(self.fields[key], QtWidgets.QSpinBox):
                value = str(self.fields[key].value())
            elif isinstance(self.fields[key], QtWidgets.QCheckBox):
                value = str(int(self.fields[key].isChecked()))
            elif isinstance(self.fields[key], QtWidgets.QComboBox):
                value = cgruutils.toStr('%s' % self.fields[key].currentText())
            line = key + '=' + value
            file.write(line + '\n')
        file.close()

    def load(self, filename, fullPath=False):
        if not fullPath:
            filename = os.path.join(cgruconfig.VARS['HOME_CGRU'], FilePrefix) + filename + FileSuffix
        if not os.path.isfile(filename):
            return False
        print('Loading "%s"' % filename)

        if sys.version_info[0] < 3:
            file = open(filename, 'r')
        else:
            file = open(filename, 'r', buffering=-1, encoding='utf-8')
        lines = file.readlines()
        file.close()

        self.constructed = False
        for line in lines:
            line = cgruutils.toStr(line)
            pos = line.find('=')
            if pos < 1:
                continue
            key = line[:pos]
            if key not in self.fields:
                continue
            value = line[pos + 1:].strip()
            if isinstance(self.fields[key], QtWidgets.QLineEdit):
                if sys.version_info[0] < 3:
                    value = value.decode('utf-8')
                self.fields[key].setText(value)
            elif isinstance(self.fields[key], QtWidgets.QSpinBox):
                self.fields[key].setValue(int(value))
            elif isinstance(self.fields[key], QtWidgets.QCheckBox):
                self.fields[key].setChecked(int(value))
            elif isinstance(self.fields[key], QtWidgets.QComboBox):
                for i in range(0, self.fields[key].count()):
                    if self.fields[key].itemText(i) == value:
                        self.fields[key].setCurrentIndex(i)
                        break
        self.inputFileChanged()
        self.inputFileChanged2()
        self.constructed = True
        self.evaluate()
        return True

    def browseSave(self):
        filename, fltr = QtWidgets.QFileDialog.getSaveFileName(self, 'Choose MovieMaker file', cgruconfig.VARS['HOME_CGRU'])
        if filename == '': return
        filendir = os.path.dirname(filename)
        filename = os.path.basename(filename)
        filename = FilePrefix + filename + FileSuffix
        filename = os.path.join(filendir, filename)
        self.save(filename, True)

    def browseLoad(self):
        filename, fltr = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose MovieMaker file', cgruconfig.VARS['HOME_CGRU'])
        if filename == '': return
        self.load(filename, True)

        # def quitsave( self):

    # self.save( FileLast)
    #     self.close()

    def getRecentFilesList(self):
        allfiles = os.listdir(cgruconfig.VARS['HOME_CGRU'])
        recfiles = []
        for afile in allfiles:
            if afile.find(FilePrefix + FileRecent) >= 0:
                recfiles.append(afile)
        recfiles.sort()
        return recfiles

    def saveRecent(self):
        recfiles = self.getRecentFilesList()
        if len(recfiles) > 0:
            for afile in recfiles:
                if afile.find(self.fields['outputname'].text()) > len(FilePrefix + FileRecent):
                    #               print('os.remove("%s")' % os.path.join( cgruconfig.VARS['HOME_CGRU'], afile))
                    os.remove(
                        os.path.join(cgruconfig.VARS['HOME_CGRU'], afile))
                    recfiles.remove(afile)
            numfiles = len(recfiles)
            if numfiles > 9:
                #            print('os.remove("%s")' % os.path.join( cgruconfig.VARS['HOME_CGRU'], recfiles[-1]))
                os.remove(
                    os.path.join(cgruconfig.VARS['HOME_CGRU'], recfiles[-1]))
                del recfiles[-1]
            recfiles.reverse()
            index = len(recfiles)
            for afile in recfiles:
                pos = afile.find(FilePrefix + FileRecent)
                if pos < 0:
                    continue
                pos = len(FilePrefix + FileRecent)
                num = int(afile[pos])
                if num != index:
                    nextfile = afile[:pos] + str(index) + afile[pos + 1:]
                    afile = os.path.join(cgruconfig.VARS['HOME_CGRU'], afile)
                    nextfile = os.path.join(cgruconfig.VARS['HOME_CGRU'], nextfile)
                    #               print('os.rename("%s"->"%s")' % ( afile, nextfile))
                    os.rename(afile, nextfile)
                index -= 1
        afile = FileRecent + '0.' + self.fields['outputname'].text()
        self.save(afile)
        self.refreshRecent()

    def refreshRecent(self):
        self.cbRecent.activated.disconnect( self.loadRecent)
        self.cbRecent.clear()
        for afile in self.getRecentFilesList():
            if afile[: len(FilePrefix)] == FilePrefix:
                afile = afile[len(FilePrefix):]
            if afile[-len(FileSuffix):] == FileSuffix:
                afile = afile[: -len(FileSuffix)]
            short = afile
            if short[: len(FileRecent)] == FileRecent:
                short = short[len(FileRecent):]
            short = short[2:]
            if len(short) > 20:
                short = short[:10] + ' .. ' + short[-10:]
            self.cbRecent.addItem(short, afile)

        self.cbRecent.activated.connect( self.loadRecent)

    def loadRecent(self):
        self.load(getComboBoxString(self.cbRecent))


app = QtWidgets.QApplication(sys.argv)
app.setWindowIcon( QtGui.QIcon(cgruutils.getIconFileName(Options.wndicon)))
dialog = Dialog()
dialog.show()
app.exec_()
