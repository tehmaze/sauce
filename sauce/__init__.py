#! /usr/bin/env python
#
#                          _______
#    ____________ _______ _\__   /_________        ___  _____
#   |    _   _   \   _   |   ____\   _    /       |   |/  _  \
#   |    /   /   /   /   |  |     |  /___/    _   |   |   /  /
#   |___/___/   /___/____|________|___   |   |_|  |___|_____/
#           \__/                     |___|
#
# (c) 2006-2012 Wijnand Modderman-Lenstra - https://maze.io/
#

'''
Parser for SAUCE or Standard Architecture for Universal Comment Extensions.
'''

__author__    = 'Wijnand Modderman-Lenstra <maze@pyth0n.org>'
__copyright__ = '(C) 2006-2012 Wijnand Modderman-Lenstra'
__license__   = 'LGPL'
__version__   = '1.4'
__url__       = 'https://github.com/tehmaze/sauce'

import datetime
import os
import struct
from io import BytesIO
from io import IOBase

class SAUCE(object):
    '''
    Parser for SAUCE or Standard Architecture for Universal Comment Extensions,
    as defined in http://www.acid.org/info/sauce/s_spec.htm.

    :param filename:    file name or file handle
    :property author:   Name or 'handle' of the creator of the file
    :property datatype: Type of data
    :property date:     Date the file was created
    :property filesize: Original filesize NOT including any information of
                        SAUCE
    :property group:    Name of the group/company the creator is employed by
    :property title:    Title of the file

    Example::

        >>> art = open('31337.ANS', 'rb')
        >>> nfo = sauce.SAUCE(art)
        >>> nfo.author
        'maze'
        ...
        >>> nfo.group
        ''
        >>> nfo.group = 'mononoke'
        >>> raw = str(nfo)

    Saving the new file::

        >>> sav = open('31337.NEW', 'wb')
        >>> nfo.write(sav)
        >>> # OR you can do:
        >>> sav = nfo.write('31337.NEW')

    '''

    # template
    template  = (
        # name           default         size type
        ('SAUCE',        b'SAUCE',       5,   '5s'),
        ('SAUCEVersion', b'00',          2,   '2s'),
        ('Title',        b'\x00' * 35,  35,   '35s'),
        ('Author',       b'\x00' * 20,  20,   '20s'),
        ('Group',        b'\x00' * 20,  20,   '20s'),
        ('Date',         b'\x00' * 8,    8,   '8s'),
        ('FileSize',     [0],            4,   'I'),
        ('DataType',     [0],            1,   'B'),
        ('FileType',     [0],            1,   'B'),
        ('TInfo1',       [0],            2,   'H'),
        ('TInfo2',       [0],            2,   'H'),
        ('TInfo3',       [0],            2,   'H'),
        ('TInfo4',       [0],            2,   'H'),
        ('Comments',     [0],            1,   'B'),
        ('Flags',        [0],            1,   'B'),
        ('Filler',       [b'\x00'] * 22, 22,   '22c'),
    )
    templates = [t[0] for t in template]
    datatypes = ['None', 'Character', 'Graphics', 'Vector', 'Sound',
                 'BinaryText', 'XBin', 'Archive', 'Executable']
    filetypes = {
        'None': {
            'filetype': ['Undefined'],
        },
        'Character': {
            'filetype': ['ASCII', 'ANSi', 'ANSiMation', 'RIP', 'PCBoard',
                         'Avatar', 'HTML', 'Source'],
            'flags':    {0: 'None', 1: 'iCE Color'},
            'tinfo': (
                ('width', 'height',     None, None),
                ('width', 'height',     None, None),
                ('width', 'height',     None, None),
                ('width', 'height', 'colors', None),
                ('width', 'height',     None, None),
                ('width', 'height',     None, None),
                (None,    None,         None, None),
            ),
        },
        'Graphics': {
            'filetype': ['GIF', 'PCX', 'LBM/IFF', 'TGA', 'FLI', 'FLC',
                         'BMP', 'GL', 'DL', 'WPG', 'PNG', 'JPG', 'MPG',
                         'AVI'],
            'tinfo':    (('width', 'height', 'bpp')) * 14,
        },
        'Vector': {
            'filetype': ['DX', 'DWG', 'WPG', '3DS'],
        },
        'Sound': {
            'filetype': ['MOD', '669', 'STM', 'S3M', 'MTM', 'FAR', 'ULT',
                         'AMF', 'DMF', 'OKT', 'ROL', 'CMF', 'MIDI', 'SADT',
                         'VOC', 'WAV', 'SMP8', 'SMP8S', 'SMP16', 'SMP16S',
                         'PATCH8', 'PATCH16', 'XM', 'HSC', 'IT'],
            'tinfo':    ((None,)) * 16 + (('Sampling Rate',)) * 4,
        },
        'BinaryText': {
            'flags':    {0: 'None', 1: 'iCE Color'},
        },
        'XBin': {
            'tinfo':    (('width', 'height'),),
        },
        'Archive': {
            'filetype': ['ZIP', 'ARJ', 'LZH', 'ARC', 'TAR', 'ZOO', 'RAR',
                         'UC2', 'PAK', 'SQZ'],
        },
    }

    def __init__(self, filename='', data=''):
        assert (filename or data), 'Need either filename or record'

        if filename:
            if isinstance(filename, IOBase):
                self.filehand = filename
            else:
                self.filehand = open(filename, 'rb')
            self._size = os.path.getsize(self.filehand.name)
        else:
            self._size = len(data)
            self.filehand = BytesIO(data)

        self.record, self.data = self._read()

    def __str__(self):
        return repr(self)

    def __bytes__(self):
        return b''.join(list(self._read_file()))

    def _read_file(self):
        # Buffered reader (generator), reads the original file without SAUCE
        # record.
        self.filehand.seek(0)
        # Check if we have SAUCE data
        if self.record:
            reads, rest = divmod(self._size - 128, 1024)
        else:
            reads, rest = divmod(self._size, 1024)
        for x in range(0, reads):
            yield self.filehand.read(1024)
        if rest:
            yield self.filehand.read(rest)

    def _read(self):
        if self._size >= 128:
            self.filehand.seek(self._size - 128)
            record = self.filehand.read(128)
            if record.startswith(b'SAUCE'):
                self.filehand.seek(0)
                return record, self.filehand.read(self._size - 128)

        self.filehand.seek(0)
        return None, self.filehand.read()

    def _gets(self, key):
        if self.record is None:
            return None

        name, default, offset, size, stype = self._template(key)
        data = self.record[offset:offset + size]
        data = struct.unpack(stype, data)
        if stype[-1] in 'cs':
            return b''.join(data)
        elif stype[-1] in 'BI' and len(stype) == 1:
            return data[0]
        else:
            return data

    def _puts(self, key, data):
        name, default, offset, size, stype = self._template(key)
        #print offset, size, data, repr(struct.pack(stype, data))
        if self.record is None:
            self.record = self.sauce()
        self.record = b''.join([
            self.record[:offset],
            struct.pack(stype, data),
            self.record[offset + size:]
        ])
        return self.record

    def _template(self, key):
        index = self.templates.index(key)
        name, default, size, stype = self.template[index]
        offset = sum([self.template[x][2] for x in range(0, index)])
        return name, default, offset, size, stype

    def sauce(self):
        '''
        Get the raw SAUCE record.
        '''
        if self.record:
            return self.record
        else:
            data = b'SAUCE'
            for name, default, size, stype in self.template[1:]:
                #print stype, default
                if stype[-1] in 's':
                    data += struct.pack(stype, default)
                else:
                    data += struct.pack(stype, *default)
            return data

    def write(self, filename):
        '''
        Save the file including SAUCE data to the given file(handle).
        '''
        fh = filename if isinstance(filename, IOBase) else open(filename, 'wb')
        for part in self._read_file():
            fh.write(part)
        fh.write(self.sauce())
        return fh

    # SAUCE meta data

    def get_author(self):
        result = self._gets('Author')
        if result is not None:
            return result.strip().decode('latin-1')
        return None

    def set_author(self, author):
        if isinstance(author, str):
            author = author.encode('latin-1')
        self._puts('Author', author)
        return self

    def get_comments(self):
        return self._gets('Comments')

    def set_comments(self, comments):
        self._puts('Comments', comments)
        return self

    def get_datatype(self):
        return self._gets('DataType')

    def get_datatype_str(self):
        datatype = self.datatype
        if datatype is None:
            return None
        if datatype < len(self.datatypes):
            return self.datatypes[datatype]
        else:
            return None

    def set_datatype(self, datatype):
        if type(datatype) == str:
            datatype = datatype.lower().title()  # fOoBAR -> Foobar
            datatype = self.datatypes.index(datatype)
        self._puts('DataType', datatype)
        return self

    def get_date(self):
        result = self._gets('Date')
        if result is not None:
            return result.decode('latin-1')
        return None

    def get_date_str(self, format='%Y%m%d'):
        return datetime.datetime.strptime(self.date, format)

    def set_date(self, date=None, format='%Y%m%d'):
        if date is None:
            date = datetime.datetime.now().strftime(format)
        elif type(date) in [datetime.date, datetime.datetime]:
            date = date.strftime(format)
        elif type(date) in [int, float]:
            date = datetime.datetime.fromtimestamp(date).strftime(format)
        if isinstance(date, str):
            date = date.encode('latin-1')
        self._puts('Date', date)
        return self

    def get_filesize(self):
        return self._gets('FileSize')

    def set_filesize(self, size):
        self._puts('FileSize', size)

    def get_filler(self):
        return self._gets('Filler')

    def get_filler_str(self):
        filler = self._gets('Filler')
        if filler is None:
            return ''
        else:
            return filler.rstrip(b'\x00')

    def get_filetype(self):
        return self._gets('FileType')

    def get_filetype_str(self):
        datatype = self.datatype_str
        filetype = self.filetype

        if datatype is None or filetype is None:
            return None

        if datatype in self.filetypes and \
            'filetype' in self.filetypes[datatype] and \
                filetype < len(self.filetypes[datatype]['filetype']):
            return self.filetypes[datatype]['filetype'][filetype]
        else:
            return None

    def set_filetype(self, filetype):
        datatype = self.datatype_str
        if type(filetype) == str:
            filetype = filetype.lower().title()  # fOoBAR -> Foobar
            filetype = [name.lower().title() for name in self.filetypes[datatype]['filetype']].index(filetype)
        self._puts('FileType', filetype)
        return self

    def get_flags(self):
        return self._gets('Flags')

    def set_flags(self, flags):
        self._puts('Flags', flags)
        return self

    def get_flags_str(self):
        datatype = self.datatype_str
        filetype = self.filetype

        if datatype is None or filetype is None:
            return None

        if datatype in self.filetypes and \
            'flags' in self.filetypes[datatype] and \
                filetype < len(self.filetypes[datatype]['filetype']):
            return self.filetypes[datatype]['filetype'][filetype]
        else:
            return None

    def get_group(self):
        result = self._gets('Group')
        if result is not None:
            return result.strip().decode('latin-1')
        return None

    def set_group(self, group):
        if isinstance(group, str):
            group = group.encode('latin-1')
        self._puts('Group', group)
        return self

    def _get_tinfo_name(self, i):
        datatype = self.datatype_str
        filetype = self.filetype

        if datatype is None or filetype is None:
            return None

        try:
            return self.filetypes[datatype]['tinfo'][filetype][i - 1]
        except (KeyError, IndexError):
            return ''

    def get_tinfo1(self):
        return self._gets('TInfo1')[0]

    def get_tinfo1_name(self):
        return self._get_tinfo_name(1)

    def set_tinfo1(self, tinfo):
        self._puts('TInfo1', tinfo)
        return self

    def get_tinfo2(self):
        return self._gets('TInfo2')[0]

    def get_tinfo2_name(self):
        return self._get_tinfo_name(2)

    def set_tinfo2(self, tinfo):
        self._puts('TInfo2', tinfo)
        return self

    def get_tinfo3(self):
        return self._gets('TInfo3')[0]

    def get_tinfo3_name(self):
        return self._get_tinfo_name(3)

    def set_tinfo3(self, tinfo):
        self._puts('TInfo3', tinfo)
        return self

    def get_tinfo4(self):
        return self._gets('TInfo4')[0]

    def get_tinfo4_name(self):
        return self._get_tinfo_name(4)

    def set_tinfo4(self, tinfo):
        self._puts('TInfo4', tinfo)
        return self

    def get_title(self):
        result = self._gets('Title')
        if result is not None:
            return result.strip().decode('latin-1')
        return None

    def set_title(self, title):
        if isinstance(title, str):
            title = title.encode('latin-1')
        self._puts('Title', title)
        return self

    def get_version(self):
        result = self._gets('SAUCEVersion')
        if result is not None:
            return result.decode('latin-1')
        return None

    def set_version(self, version):
        if isinstance(version, str):
            version = version.encode('latin-1')
        self._puts('SAUCEVersion', version)
        return self

    # properties
    author       = property(get_author,   set_author)
    comments     = property(get_comments, set_comments)
    datatype     = property(get_datatype, set_datatype)
    datatype_str = property(get_datatype_str)
    date         = property(get_date,     set_date)
    filesize     = property(get_filesize, set_filesize)
    filetype     = property(get_filetype, set_filetype)
    filetype_str = property(get_filetype_str)
    filler       = property(get_filler)
    filler_str   = property(get_filler_str)
    flags        = property(get_flags,    set_flags)
    flags_str    = property(get_flags_str)
    group        = property(get_group,    set_group)
    tinfo1       = property(get_tinfo1,   set_tinfo1)
    tinfo1_name  = property(get_tinfo1_name)
    tinfo2       = property(get_tinfo2,   set_tinfo2)
    tinfo2_name  = property(get_tinfo2_name)
    tinfo3       = property(get_tinfo3,   set_tinfo3)
    tinfo3_name  = property(get_tinfo3_name)
    tinfo4       = property(get_tinfo4,   set_tinfo4)
    tinfo4_name  = property(get_tinfo4_name)
    title        = property(get_title,    set_title)
    version      = property(get_version)


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print('{} <file>'.format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)
    else:
        test = SAUCE(sys.argv[1])

        def show(sauce):
            print('Version.:', sauce.version)
            print('Title...:', sauce.title)
            print('Author..:', sauce.author)
            print('Group...:', sauce.group)
            print('Date....:', sauce.date)
            print('FileSize:', sauce.filesize)
            print('DataType:', sauce.datatype, sauce.datatype_str)
            print('FileType:', sauce.filetype, sauce.filetype_str)
            print('TInfo1..:', sauce.tinfo1)
            print('TInfo2..:', sauce.tinfo2)
            print('TInfo3..:', sauce.tinfo3)
            print('TInfo4..:', sauce.tinfo4)
            print('Flags...:', sauce.flags, sauce.flags_str)
            print('Record..:', len(sauce.record), repr(sauce.record))
            print('Filler..:', sauce.filler_str)

        if test.record:
            show(test)
        else:
            print('No SAUCE record found')
            test = SAUCE(data=test.sauce())
            show(test)
