=======
 sauce
=======

Parser for SAUCE or Standard Architecture for Universal Comment Extensions,
invented by Tasmaniac and Rad Man from ACid:

  ANSi's used to be just ANSi's, pictures were just pictures, loaders were just
  loaders and quite frankly, every file was just as plain tasting as every
  other. This is about to change, how- ever, because ACiD has decided to give
  their files an extra "je-ne-sais-quoi." In reality, we'll be adding SAUCE to
  every file you can imagine.

  Now, before we thoroughly confuse you, let us explain what we are doing here.
  SAUCE stands for "Standard Architecture for Universal Comment Extensions."
  Although originally intended for personal use in ANSi's and RIP screens,
  early in the developement of EFI (Extended File Information) it was decided
  that EFI should be extended to have support for more than just ANSi and RIP
  screens. Our brainchild was born and the specs were designed. The only aspect
  left undecided was the name, and after rejecting some very funny candidates,
  SAUCE was unanimously chosen. This leads us to the big question in the sky,
  "What is sauce?" SAUCE is a universal process to incorporate a full
  description for any type of file. The most outstanding aspect of this concept
  is that you have access to the complete file name, the file's title, the
  creation date, the creator of the file, the group that the creator is
  employed by, and much, much, more.


To put it short, SAUCE is a block of meta data that can be appended to various
art works made by the scene.


Usage
=====

Load the interface::

    >>> from sauce import SAUCE

Extract metadata of an ANSI file::

    >>> piece = SAUCE('artwork.ans')
    >>> print piece.group
    'ACiD'

Modify metadata of an ANSI file::

    >>> import datetime
    >>> piece = SAUCE('artwork.ans')
    >>> piece.date = datetime.datetime.now()
    >>> piece.write('artwork.new')
