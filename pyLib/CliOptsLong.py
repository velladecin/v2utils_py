#!/usr/bin/python
import sys
import re

class CliOptionError(Exception):
    def __init__(self, msg):
        super(CliOptionError, self).__init__(msg)

class cliOptLong(object):
    __opts = dict()
    __collection = list()
    __accepted_kwargs = {   # with defaults
        "descr": "No description",
        "default": None,

        # must be given
        "must": False,

        # expecting a value: yes/no
        # --file <file.txt>
        "value": False,

        # can be specified multiple times: yes/no
        # -f f1 --file f2 -f f3 f4 f5
        "multi": False,

        # should default be always used or only when option used on CLI
        # yes/no
        "persistent": False,

        # callback function
        "callback": None}

    def __init__(self):
        self.__name = re.sub(r'.*/', '', sys.argv[0]) # filename without path
        self.__usage = ""
        return

    def add(self, *args, **kwargs):
        # *args     is short & long version(s) of the option (-f, --file, --filespecial, ...), each of which must be unique
        # **kwargs  is optional specs for the option(s) in *args

        # check kwargs
        for k in kwargs:
            if not k in self.__accepted_kwargs:
                raise CliOptionError("Uknown definition: %s" % k)

        # check passed, assign defaults
        for k in self.__accepted_kwargs:
            if not k in kwargs: kwargs[k] = self.__accepted_kwargs[k]

        # check args
        if len(args) < 1:
            raise CliOptionError("Missing at least one option flag (eg: -f, --file, ..)")

        for a in args:
            if not re.match(r'^\-', a): raise CliOptionError("Options must start with '-' or '--'")
            if a == "-" or a == "--":   raise CliOptionError("Invalid option: %s" % a)

            for d in self.__collection:
                if a in d["args"]: raise CliOptionError("Already exists: %s" % a)

        self.__collection.append({"args": args, "kwargs": kwargs})

        a = ", ".join(args)
        b = kwargs["descr"]
        c = kwargs["default"] if kwargs["default"] else "none"
        d = "yes" if kwargs["value"] else "no"
        e = "yes" if kwargs["multi"] else "no"

        self.__usage += """
    %s
            %s
            default: %s, expects value: %s, multivalue: %s
        """ % (a, b, c, d, e)

    def usage(self, exit=0):
        print("")
        print("Usage: %s <opt> [<val>, <val>, ..], .." % self.__name)
        print("Options:")
        print(self.__usage)
        sys.exit(exit)

    def ingest(self, argv):
        # opt must be first
        try:
            if not re.match(r'^\-', argv[0]):
                raise CliOptionError("Invalid option: %s" % argv[0])
        except IndexError:
            pass
        
        specs = None
        previous_a = ""
        for a in argv:
            # option or
            # option without value
            if re.match(r'^\-', a):
                specs = None
                for d in self.__collection:
                    if a in d["args"]:
                        specs = d
                        break
                    
                if not specs: raise CliOptionError("Uknown option: %s" % a)
                k = specs["args"][0]
                if not k in self.__opts:
                    self.__opts[k] = list()

                if not specs["kwargs"]["value"]:
                    try:
                        self.__opts[k][0]
                        if not specs["kwargs"]["multi"]:
                            raise CliOptionError("Multi value not accepted for: %s" % ", ".join(specs["args"]))
                        else:
                            self.__opts[k][0] += 1
                    except IndexError:
                        self.__opts[k] = [1] 

                    # zero out specs to catch any stray values
                    specs = None

                previous_a = a
                continue

            # value
            try:
                # catch non-existent specs
                k = specs["args"][0]
            except TypeError:
                # stray value
                raise CliOptionError("Stray value (does option accept values?): %s %s" % (previous_a, a))

            if len(self.__opts[k]) != 0 and not specs["kwargs"]["multi"]:
                raise CliOptionError("+Multi value not accepted for: %s" % ", ".join(specs["args"]))

            # apply callback if required
            self.__opts[k].append(specs["kwargs"]["callback"](a) if specs["kwargs"]["callback"] else a)

        for d in self.__collection:
            k = d["args"][0]

            try:
                self.__opts[k]
                found = True
            except KeyError:
                found = False

            if d["kwargs"]["must"] and not found:
                raise CliOptionError("Missing required option: %s" % k)

            if d["kwargs"]["default"] and d["kwargs"]["persistent"]:
                if not found:
                    # apply callback (on default) if required
                    cb = d["kwargs"]["callback"]
                    df = d["kwargs"]["default"]
                    self.__opts[k] = [ cb(df) if cb else df ]

            try:
                if len(self.__opts[k]) == 0 and d["kwargs"]["value"]:
                    raise CliOptionError("Expecting value for: %s" % ", ".join(d["args"]))
            except KeyError:
                pass

        if len(self.__opts) == 0:
            self.__opts["-h"] = True

        try:
            if self.__opts["-h"]:
                self.usage()
        except KeyError:
            pass

        return self.__opts
