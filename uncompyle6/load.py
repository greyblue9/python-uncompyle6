# Copyright (c) 2000 by hartmut Goebel <h.goebel@crazy-compilers.com>
# Copyright (c) 2015 by Rocky Bernstein
from __future__ import print_function

import imp, marshal, os, py_compile, sys, tempfile

import uncompyle6.marsh
from uncompyle6 import PYTHON3
from uncompyle6 import magics

def check_object_path(path):
    if path.endswith(".py"):
        try:
            import importlib
            return importlib.util.cache_from_source(path,
                                                    optimization='')
        except:
            try:
                import imp
                imp.cache_from_source(path, debug_override=False)
            except:
                pass
            pass
        basename = os.path.basename(path)[0:-3]
        spath = path if PYTHON3 else path.decode('utf-8')
        path = tempfile.mkstemp(prefix=basename + '-',
                                suffix='.pyc', text=False)[1]
        py_compile.compile(spath, cfile=path)

    if not path.endswith(".pyc") and not path.endswith(".pyo"):
        raise ValueError("path %s must point to a .py or .pyc file\n" %
                         path)
    return path

def load_file(filename):
    '''
    load a Python source file and compile it to byte-code
    _load_file(filename: string): code_object
    filename:	name of file containing Python source code
                (normally a .py)
    code_object: code_object compiled from this source code
    This function does NOT write any file!
    '''
    fp = open(filename, 'rb')
    source = fp.read().decode('utf-8') + '\n'
    try:
        co = compile(source, filename, 'exec', dont_inherit=True)
    except SyntaxError:
        print('>>Syntax error in %s\n' % filename, file= sys.stderr)
        raise
    fp.close()
    return co

def load_module(filename):
    """
    load a module without importing it.
    load_module(filename: string): version, magic_int, code_object

    filename:	name of file containing Python byte-code object
                (normally a .pyc)

    code_object: code_object from this file
    version: Python major/minor value e.g. 2.7. or 3.4
    magic_int: more specific than version. The actual byte code version of the
               code object
    """

    with open(filename, 'rb') as fp:
        magic = fp.read(4)
        try:
            version = float(magics.versions[magic])
        except KeyError:
            if len(magic) >= 2:
                raise ImportError("Unknown magic number %s in %s" %
                                (ord(magic[0])+256*ord(magic[1]), filename))
            else:
                raise ImportError("Bad magic number: '%s'" % magic)

        if not (2.5 <= version <= 2.7) and not (3.2 <= version <= 3.4):
            raise ImportError("This is a Python %s file! Only "
                              "Python 2.5 to 2.7 and 3.2 to 3.4 files are supported."
                              % version)

        # print version
        fp.read(4) # timestamp
        magic_int = magics.magic2int(magic)
        my_magic_int = magics.magic2int(imp.get_magic())

        if my_magic_int == magic_int:
            # Note: a higher magic number necessarily mean a later
            # release.  At Python 3.0 the magic number decreased
            # significantly. Hence the range below. Also note
            # inclusion of the size info, occurred within a
            # Python magor/minor release. Hence the test on the
            # magic value rather than PYTHON_VERSION
            if 3200 <= magic_int < 20121:
                fp.read(4) # size mod 2**32
            bytecode = fp.read()
            co = marshal.loads(bytecode)
        else:
            co = uncompyle6.marsh.load_code(fp, magic_int)
        pass

    return version, magic_int, co

if __name__ == '__main__':
    co = load_file(__file__)
    obj_path = check_object_path(__file__)
    co2 = load_module(obj_path)
    assert co == co2[2]
