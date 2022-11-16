#!/usr/bin/env python2.7
import json
import os

class ExecutionerSystemError(Exception):
    def __init__(self, fn, msg):
        super(ExecutionerSystemError, self).__init__("Executioner.%s(): %s" % (fn, msg))

class ExecutionerBadArgs(Exception):
    def __init__(self, fn, msg):
        super(ExecutionerBadArgs, self).__init__("Executioner.%s(): %s" % (fn, msg))

class Executioner:
    @staticmethod
    def swings(**kwargs):
        self = "swings"

        # **kwargs
        # 1. maxpid - max num of threads to run at one time
        #       total number of threads/runs is defined by args below
        # 2. axes   - compulsory
        #       list of arguments [ function/method, args(optional) ]

        try:
            maxpid = int(kwargs["maxpid"])
            axes = kwargs["axes"]

            for i in axes:
                if type(i) != list: raise ValueError()
                if len(i) < 1: raise ValueError()
        except (KeyError, ValueError):
            raise ExecutionerBadArgs(self, "required: maxpid=int, axes=[[fn(), args], ..]")

        return Executioner.__run(maxpid, axes)

    @staticmethod
    def swing(**kwargs):
        self = "swing"

        # **kwargs
        # 1. axe    - function/method to execute
        # 2. heads  - total number of threads/runs we want
        # 3. maxpid - max num of threads to run at one time
        # 4. args   - optional
        #       single: same args will be passed to all the heads/threads
        #       multi:  each head/thread will be passed its own set of args,
        #               num of heads/threads *must* equal num of args!

        try:
            fn = kwargs["axe"]
            heads = int(kwargs["heads"])
            maxpid = int(kwargs["maxpid"])
        except (KeyError, ValueError):
            raise ExecutionerBadArgs(self, "required: axe=fn(), heads=int, maxpid=int")

        args = []
        for i in range(0, heads):
            # no arguments
            if not "args" in kwargs:
                args.append([fn])
                continue

            # same args for all
            if "single" in kwargs["args"]:
                args.append([fn, kwargs["args"]["single"]])
                continue

            # different args for each
            if "multi" in kwargs["args"]:
                try:
                    args.append([fn, kwargs["args"]["multi"][i]])
                except IndexError:
                    raise ExecutionerBadArgs(self, "args['multi'] and 'heads' do not match")
                continue

            raise ExecutionerSystemError(self, "Uknown args definition")
        return Executioner.__run(maxpid, args)

    @staticmethod
    def __run(maxpid, x):
        # actual execution below
        # do this in batches (maxpid) and collect results in to "results"
        # failing to fork() will result in less output then input and will
        # be confusing to user as to what happened, see TODO below

        lx = len(x)
        results = list()
        for i in xrange(0, lx, maxpid):
            max = i+maxpid
            if max > lx:
                max -= (max-lx)

            readers = list()
            for j in xrange(i, max):
                try:
                    r, w = os.pipe()
                    readers.append(r)
                    pid = os.fork()
                except OSError:
                    # TODO what to do here??
                    # TODO will miss this execution altogether
                    print("ERROR: fork() failed")
                    continue

                # child
                if pid == 0:
                    os.close(r)
                    res = dict()

                    fn = x[j][0]
                    args = x[j][1:]

                    try:
                        res["return"] = fn(args) if len(args) > 0 else fn()
                    except Exception as e:
                        res["error"] = "%s" % e

                    w = os.fdopen(w, 'w')
                    w.write(json.dumps(res))
                    w.close()

                    os._exit(0)

                # parent
                os.close(w)

            for r in readers:
                res = json.loads(os.fdopen(r).read())
                results.append(res)

        return results
