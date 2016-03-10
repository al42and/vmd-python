
from setuptools import setup

from distutils.util import convert_path
from distutils.command.build import build as DistutilsBuild
from distutils.command.install import install as DistutilsInstall
from distutils.cmd import Command
from subprocess import check_call
import platform
import os
import site
import sys

packages = ['vmd']

###############################################################################

class VMDBuild(DistutilsBuild):
    def initialize_options(self):
        DistutilsBuild.initialize_options(self)

    def run(self):
        # Setup and run compilation script
        self.build_lib = convert_path(os.path.abspath(self.build_lib) + "/vmd")
        self.mkpath(self.build_lib)
        self.execute(self.compile, [], msg="Compiling VMD")
        # Run original build code
        DistutilsBuild.run(self)
        

    def compile(self):
        # Determine target to build
        target = self.get_vmd_build_target()
        srcdir = convert_path(os.path.dirname(os.path.abspath(__file__)) + "/vmd")
        builddir = self.build_lib
        pydir = convert_path(sys.executable.replace("/bin/python",""))
        instdir = convert_path(site.getsitepackages()[0] + "/vmd")

        # Execute the build
        cmd = [
                srcdir + "/install.sh",
                target,
                builddir,
                pydir,
                instdir
              ]
        check_call(cmd, cwd=srcdir)

    def get_vmd_build_target(self):
        osys = platform.system()
        mach = platform.machine()

        if "Linux" in osys:
            if "x86_64" in mach:
                target = "LINUXAMD64"
            else:
                target = "LINUX"
        elif "Darwin" in osys:
            if "x86_64" in mach:
                target = "MACOSX86_64"
            elif "PowerPC" in mach:
                target = "MACOSX"
            else:
                target = "MACOSXX86"
        elif "Windows" in osys:
            if "64" in mach:
                target = "WIN64"
            else:
                target = "WIN32"
        else:
            raise ValueError("Unsupported os '%s' and machine '%s'" % (osys, mach))

        return target

###############################################################################

class VMDInstall(DistutilsInstall):
    def initialize_options(self):
        DistutilsInstall.initialize_options(self)
#        self.build_scripts = None
        self.install_lib = convert_path(site.getsitepackages()[0] + "/vmd")
        self.src_dir = convert_path(os.path.dirname(os.path.abspath(__file__)) + "/vmd")

    def finalize_options(self):
        DistutilsInstall.finalize_options(self)
#        self.set_undefined_options('build', ('build_scripts', 'build_scripts'))

    def run(self):
        # Dir stuff I guess
        if not os.path.isdir(self.install_lib):
            os.path.mkdir(self.install_lib)

        # Run original install code
        #DistutilsInstall.run(self)

        # Copy all built files
        print("Copying %s to %s" % (self.build_lib, self.install_lib))
        self.copy_tree(self.build_lib, self.install_lib)
        self.copy_file(self.src_dir + "/__init__.py", self.install_lib+"/__init__.py")

###############################################################################

class VMDTest(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import sys, subprocess, os
        errno = subprocess.call([sys.executable, os.path.abspath('test/run_tests.py')])
        raise SystemExit(errno)

###############################################################################

setup(name='vmd',
      version='1.9.2a1',
      description='Visual Molecular Dynamics Python module',
      author='Robin Betz',
      author_email='robin@robinbetz.com',
      url='http://github.com/Eigenstate/vmd-python',
      license='VMD License',
      zip_safe=False,
#      setup_requires=['libnetcdf', 'numpy'],

      packages=['vmd'],
      package_data = { 'vmd' : ['vmd.so']},
      cmdclass={
          'build': VMDBuild,
          'install': VMDInstall,
          'test': VMDTest,
      },
)

