"""Optional arbitrary CPP definitions to effect plan preprocessing:
  -D <name>      Predefine name as a macro, with definition 1
  -U <name>      Cancel any previous definition of name
  -I <dir>       Include dir to add to list of dirs searched for header files

"""

import os
import sys
import getopt

def parse(argv, longopts=[]):
    cmd_cpp = ['cpp']
    long_optval = []
    
    try:
        opts, args = getopt.gnu_getopt(argv, "I:D:U:", longopts)
    except getopt.GetoptError, e:
        print >> sys.stderr, e
        sys.exit(1)
    
    if argv.count("-") == 1:
        args.insert(0, "-")

    inc = os.getenv('FAB_PLAN_INCLUDE_PATH')
    if inc:
        cmd_cpp.append("-I" + inc)
    
    if not args[0] == '-':
        cmd_cpp.append("-I" + os.path.dirname(args[0]))
    
    for opt, val in opts:
        if opt == '-I':
            cmd_cpp.append("-I" + val)
        elif opt == '-D':
            cmd_cpp.append("-D" + val)
        elif opt == '-U':
            cmd_cpp.append("-U" + val)
        elif opt in longopts:
            long_optval.append([opt, val])
    
    if longopts:
        return cmd_cpp, args, long_optval
    
    return cmd_cpp, args

