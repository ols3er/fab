
import os
import apt_pkg
import apt_inst
from os.path import *

from utils import *


def parse_deb_filename(filename):
    """Parses package filename -> (name, version)"""

    if not filename.endswith(".deb"):
        raise Error("not a package `%s'" % filename)

    name, version = filename.split("_")[:2]

    return name, version

class Handled:
    def __init__(self, output=None):
        self.handled = []
        self.output = output
    
    def add(self, name, version, quiet=True):
        self.handled.append([name, version])
        if not quiet:
            self.print_spec(name, version)
        
    def exists(self, name, version=None):
        for h in self.handled:
            if version:
                if h[0] == name and h[1] == version:
                    return True
            elif h[0] == name:
                return True
        return False

    def print_spec(self, name, version):
        spec = name + "=" + version
        if self.output:
            open(self.output, "a").write(spec + "\n")
        else:
            print spec
    
    def print_specs(self):
        for h in self.handled:
            self.print_spec(h[0], h[1])

class Plan:
    def __init__(self, pool):
        self.tmpdir = os.getenv('FAB_TMPDIR')
        if not self.tmpdir:
            self.tmpdir = "/var/tmp/fab"

        if not isabs(pool):
            poolpath = os.getenv('FAB_POOL_PATH')
            if poolpath:
                pool = join(poolpath, pool)
        os.environ['POOL_DIR'] = pool
    
    def get_package(self, package):
        system("pool-get --strict %s %s" % (self.tmpdir, package))
        if "=" in package:
            name, version = package.split("=", 1)
        else:
            name = package
            version = None

        for filename in os.listdir(self.tmpdir):
            filepath = join(self.tmpdir, filename)

            if not isfile(filepath) or not filename.endswith(".deb"):
                continue

            cached_name, cached_version = parse_deb_filename(filename)
            if name == cached_name and (version is None or version == cached_version):
                return filepath

        return None
    
    def _quickfix(self, name):
        #TODO: solve the provides/virtual issue properly
        if (name == "perlapi-5.8.7" or
            name == "perlapi-5.8.8"):
            return "perl-base"
        
        elif (name == "perl5"):
            return "perl"

        elif (name == "aufs-modules"):
            return "aufs-modules-2.6.20-15-386"

        elif (name == "mail-transport-agent"):
            return "postfix"

        elif (name == "libapt-pkg-libc6.4-6-3.53"):
            return "apt"
        
        else:
            return name

    def package_exists(self, package):
        err = getstatus("pool-exists " + package)
        if err:
            return False
        
        return True

    def get_package_spec(self, name):
        if not self.handled.exists(name):
            package_path = self.get_package(name)

            control = apt_inst.debExtractControl(open(package_path))
            package = apt_pkg.ParseSection(control)

            self.handled.add(name, package['Version'], quiet=False)
            if package.has_key('Depends'):
                for dep in apt_pkg.ParseDepends(package['Depends']):
                    # eg. [('initramfs-tools', '0.40ubuntu11', '>='),(...),
                    #TODO: depends on version
                    if len(dep) > 1:
                        for d in dep:
                            depname = self._quickfix(d[0])
                            if self.package_exists(depname):
                                break
                    else:
                        depname = self._quickfix(dep[0][0])
                    
                    self.get_package_spec(depname)
    
    def resolve(self, plan, output=None):
        self.handled = Handled(output)
        
        for name in plan:
            self.get_package_spec(name)
            
        
        
