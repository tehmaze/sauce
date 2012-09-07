from sauce import SAUCE
import datetime

def show(sauce):
    print 'Version.:', sauce.version
    print 'Title...:', sauce.title
    print 'Author..:', sauce.author
    print 'Group...:', sauce.group
    print 'Date....:', sauce.date
    print 'FileSize:', sauce.filesize
    print 'DataType:', sauce.datatype, sauce.datatype_str
    print 'FileType:', sauce.filetype, sauce.filetype_str
    print 'Flags...:', sauce.flags, sauce.flags_str
    print 'Record..:', len(sauce.record), repr(sauce.record)


s = SAUCE('test.txt')
s.author   = 'Wijnand Modderman'
s.group    = 'freecode.nl'
s.title    = 'SAUCE test record'
s.datatype = 1
s.date     = datetime.datetime.now()
s.filesize = len(str(s))
print repr(s.sauce())
print len(s.sauce())
show(s)
