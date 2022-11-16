#!/usr/bin/python
import os, os.path
import sys, re
import errno
from datetime import datetime

class Log:
    def __init__(self, logfile):
        if os.path.isdir(logfile):
            print "Logfile is directory (not a file): %s" % logfile
            sys.exit(1)

        logdir = os.path.dirname(logfile)
        if logdir == "":
            logdir = "."

        if not os.path.isdir(logdir):
            print "Logdir does not exist: %s" % logdir
            sys.exit(2)

        self.logfile = logfile

        try:
            self.logfh = open('%s' % self.logfile, 'a', 0)
        except IOError as e:
            print "Couldn't open logfile: %s" % self.logfile

            if debug:
                print "DEBUG: %s" % str(e)

            sys.exit(3)

    def info(self, msg):
        self._log('INFO', msg)

    def warn(self, msg):
        self._log('WARN', msg)

    def crit(self, msg):
        self._log('CRIT', msg)

    def close(self):
        self.logfh.close()


    #
    # protected

    def _log(self, level, msg):
        now = self.__now()
        self.logfh.write("%s [%s]  %s\n" % (now, level, msg))


    #
    # private

    def __now(self, format="%Y-%m-%d %H:%M:%S"):
        return datetime.today().strftime(format)

class LogGlobal:
    LOGGING = __import__("logging")
    DEFAULT_LOGSET = {
        "dir":     '/var/log',
        "level":   LOGGING.DEBUG,
        "format":  '%(asctime)s %(levelname)-8s %(name)s - %(message)s',
        "datefmt": '%Y-%m-%d %H:%M:%S'
    }

    def __init__(self, logfile=None):
        self.rebuild(logfile)

    def getLogger(self):
        return self.logger

    def rebuild(self, logfile=None):
        self.LOGGING.root.handlers = []

        if logfile:
            lfile, name_nofix = self.__validateLogfileName(logfile)

            self.LOGGING.basicConfig(filename = lfile,
                                     level    = self.DEFAULT_LOGSET["level"],
                                     format   = self.DEFAULT_LOGSET["format"],
                                     datefmt  = self.DEFAULT_LOGSET["datefmt"])
        else:
            name_nofix = "default"

            # console logging
            self.LOGGING.basicConfig(level    = self.DEFAULT_LOGSET["level"],
                                     format   = self.DEFAULT_LOGSET["format"],
                                     datefmt  = self.DEFAULT_LOGSET["datefmt"])

        self.logger = self.LOGGING.getLogger(name_nofix)
        return self.logger

    def __validateLogfileName(self, logfile):
        # if logfile starts with '/' or './' it's absolute path
        # otherwise append it to the default dir (above)

        if re.match('^/', logfile) or re.match('^./', logfile):
            lfile = logfile
        else:
            lfile = "%s/%s" % (self.DEFAULT_LOGSET["dir"], logfile)

        logdir = os.path.dirname(lfile)
        if logdir != "":
            try:
                os.makedirs(logdir)
            except OSError as e:
                if e.errno != errno.EEXIST or not os.path.isdir(logdir):
                    raise

        try:
            namenosuffix = re.search('(.*)\.log$', lfile).group(1)
        except AttributeError:
            namenosuffix = lfile

        name_nofix = re.sub(r'.*/', '', namenosuffix) # remove any /dir/subdir/../

        return lfile, name_nofix

class LogLocal:
    def __init__(self, logfile):
        if os.path.isdir(logfile):
            print "Logfile is directory (not a file): %s" % logfile
            sys.exit(1)

        logdir = os.path.dirname(logfile)
        if logdir == "": logdir = "."

        if not os.path.isdir(logdir):
            print "Logdir does not exist: %s" % logdir
            sys.exit(2)

        self.logfile = logfile

        try:
            self.logfh = open('%s' % self.logfile, 'a', 0)
        except IOError as e:
            print "Couldn't open logfile: %s" % self.logfile
            sys.exit(3)

    def info(self, msg):
        self._log('INFO', msg)

    def warn(self, msg):
        self._log('WARN', msg)

    def crit(self, msg):
        self._log('CRIT', msg)

    def close(self):
        self.logfh.close()


    #
    # protected

    def _log(self, level, msg):
        now = self.__now()
        self.logfh.write("%s [%s]  %s\n" % (now, level, msg))


    #
    # private

    def __now(self, format="%Y-%m-%d %H:%M:%S"):
        return datetime.today().strftime(format)
