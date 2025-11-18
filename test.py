from sauce import SAUCE
import datetime

# Test 1: Create from file, set properties, write to new file
s = SAUCE('test.txt')
s.author = 'Wijnand Modderman'
s.group = 'freecode.nl'
s.title = 'SAUCE test record'
s.datatype = 1
s.date = datetime.datetime.now()
s.filesize = len(bytes(s))
s.comments = 5
s.flags = 1
s.tinfo1 = 80
s.tinfo2 = 25
s.write('test_out.ans')
print(f'Written: {s.title} by {s.author}')

# Test 2: Read from file handle (IOBase)
with open('test_out.ans', 'rb') as fh:
    s2 = SAUCE(fh)
    print(f'Read: {s2.title} - {s2.datatype_str}/{s2.filetype_str}')
    print(f'TInfo: {s2.tinfo1}x{s2.tinfo2} {s2.tinfo1_name},{s2.tinfo2_name}')
    print(f'Flags: {s2.flags} Comments: {s2.comments}')
    print(f'Filler: "{s2.filler_str}"')

# Test 3: Create from data parameter (BytesIO path)
s3 = SAUCE(data=b'raw file content')
s3.title = 'New file'
s3.author = 'Test'
s3.datatype = 'Character'  # Test string argument
s3.filetype = 'ANSi'  # Test string argument
s3.date = 1234567890  # Test timestamp
s3.tinfo3 = 16
s3.tinfo4 = 8
print(f'Created: {s3.title} type={s3.datatype}/{s3.filetype}')
print(f'Date: {s3.date}')
print(f'TInfo3/4: {s3.tinfo3}/{s3.tinfo4} ({s3.tinfo3_name}/{s3.tinfo4_name})')

# Test 4: File without SAUCE record
with open('no_sauce.txt', 'wb') as f:
    f.write(b'Just plain text')
s4 = SAUCE('no_sauce.txt')
print(f'No SAUCE: author={s4.author}, record={s4.record}')

# Test 5: __str__ and __bytes__
print(f'Repr: {str(s3)[:50]}...')
print(f'Bytes len: {len(bytes(s3))}')

# Test 6: Write to file handle and more setters
with open('test_fh.ans', 'wb') as fh:
    s3.write(fh)
with open('test_fh.ans', 'rb') as fh:
    s5 = SAUCE(fh)
    s5.set_version(b'01')
    s5.set_flags(2)
    print(f'Flags str: {s5.flags_str}')

# Test 7: Graphics datatype to test different filetype paths
s6 = SAUCE(data=b'image data')
s6.datatype = 2  # Graphics
s6.filetype = 'PNG'
print(f'Graphics: {s6.filetype_str}')

# Test 8: Test date conversion methods
s7 = SAUCE(data=b'test')
s7.date = datetime.date(2024, 12, 25)
print(f'Date from date obj: {s7.date}, parsed: {s7.get_date_str()}')

# Test 9: Edge cases - check None returns and empty values
s8 = SAUCE(data=b'x' * 200)  # Larger file for edge case in _read_file
print(f'Large file SAUCE: {s8.datatype_str}, filler: "{s8.get_filler()}"')
print(f'Coverage complete!')

