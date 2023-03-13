# MIT License
#
# Copyright The SCons Foundation
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Platform-specific initialization for the MinGW system."""

import sys
import os
import shutil
import subprocess
import pathlib
from . import posix, win32
from SCons.Platform import TempFileMunge

MINGW_DEFAULT_PATHS = []
if sys.platform == 'win32':
    if 'MINGW_PREFIX' in os.environ:
        # it's important that we get the binaries corresponding to the *current* MSYS environment, not the other ones that may also be present.
        res = subprocess.run([shutil.which('cygpath'),'-w','/usr/bin'],stdout=subprocess.PIPE,check=True,encoding='utf8')
        MINGW_DEFAULT_PATHS = [
            str(pathlib.Path(os.environ.get('MINGW_PREFIX'))/'bin') # eg c:\msys64\ucrt64\bin
            ,str(pathlib.Path(res.stdout.strip())) # eg c:\msys64\usr\bin (where the MSYS binaries are stored)
        ]
    else:
        # this is what was here before, but it needed 'bin' added to be meaningful. but actually it's fairly useless.
        MINGW_DEFAULT_PATHS = [
            r'C:\msys64\bin',
            r'C:\msys\bin'
        ]
    #print("MINGW_DEFAULT_PATHS =",MINGW_DEFAULT_PATHS)

def msys_spawn(sh, escape, cmd, args, env):
    """
    see SCons manual under 'SPAWN'. In MSYS, we will use `sh` as the shell, allowing bash-style command strings (as on the MSYS command line)
    """
    mycmd = [sh,'-c'," ".join(args)]
    #print("spawn:",mycmd)
    res = subprocess.run(mycmd,env=env)
    return res.returncode

def msys_pspawn(sh, escape, cmd, args, env, stdout, stderr):
    """
    In MSYS, we will use `sh` as the shell, allowing bash-style command strings (as on the MSYS command line)
    """
    mycmd = [sh,'-c'," ".join(args)]
    #print("pspawn:",mycmd)
    res = subprocess.run(mycmd,env=env,stdout=stdout,stderr=stderr)
    return res.returncode

# this generate function allows for a fallback loading of 'win32' in the case
# that MSYSTEM is not defined. This is for the case that the user declares
# env = Environment(platform='mingw') but where they are not running in MSYS 
# (ie empty $MSYSTEM env var)
def generate(env):
    if os.environ.get('MSYSTEM'):
        #print("MSYSTEM")
        posix.generate(env)

        # we're still on Windows, so we need a few critical env vars, same as for win32.py.
        # see notes in win32.py; weigh carefully before adding other vars here.
        import_env = ['SystemDrive', 'SystemRoot', 'TEMP', 'TMP', 'USERPROFILE']
        for var in import_env:
            v = os.environ.get(var)
            if v:
                env['ENV'][var] = v

        if 'COMSPEC' not in env['ENV']:
            v = os.environ.get("COMSPEC")
            if v:
                env['ENV']['COMSPEC'] = v

        env.AppendENVPath('PATH', win32.get_system_root() + '\\System32')

        env['ENV']['PATHEXT'] = '.COM;.EXE;.BAT;.CMD'

        env['PROGPREFIX']  = ''
        env['PROGSUFFIX']  = '.exe'
        env['SHLIBPREFIX'] = ''
        env['SHLIBSUFFIX'] = '.dll'
        env['LIBPREFIXES'] = [ '$LIBPREFIX', '$SHLIBPREFIX', '$IMPLIBPREFIX' ]
        env['LIBSUFFIXES'] = [ '$LIBSUFFIX', '$SHLIBSUFFIX', '$IMPLIBSUFFIX' ]
        env['TEMPFILE']    = TempFileMunge
        env['TEMPFILEPREFIX'] = '@'
        env['PSPAWN']         = msys_pspawn
        env['SPAWN']          = msys_spawn
        env['MAXLINELENGTH']  = 2048
        env['HOST_OS'] = 'msys'
        env['SHELL'] = str(pathlib.Path(shutil.which('sh')))
    else:
        #print("MINGW")
        win32.generate(env)
       
# vim:sw=4:et=4
