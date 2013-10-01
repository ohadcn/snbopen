snbopen
=======

convert samsung S-note files (.snb) to pdf or open them.

use
=======
just run snbopen.py snbfilename [pdffilename].
the script converts the file into pdf and open it with your default application for pdf files.
if you supply the script with a pdffilename, it will save the pdf to the required file insteed of opening it.

dependencies
=======
the script should run on python (v2), and require reportlab and PIL (python-imaging).

TODO
=======
the script is not yet full, text handling is very poor, and the background of the file is ignored.