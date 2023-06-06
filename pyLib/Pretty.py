#!/usr/bin/env python2.7

class Pretty(object):
    reset       = '\033[0m'

    #
    # Foreground

    class fg:
        grey    = '\033[90m'
        red     = '\033[91m'
        green   = '\033[92m'
        yellow  = '\033[93m'
        blue    = '\033[94m'
        purple  = '\033[95m'
        cyan    = '\033[96m'
        darkgrey    = '\033[30m'
        darkred     = '\033[31m'
        darkgreen   = '\033[32m'
        darkblue    = '\033[34m'

    def gray(self, s):          return self.grey(s)
    def grey(self, s):          return self.__color("grey", s)
    def red(self, s):           return self.__color("red", s)
    def green(self, s):         return self.__color("green", s)
    def yellow(self, s):        return self.__color("yellow", s)
    def blue(self, s):          return self.__color("blue", s)
    def purple(self, s):        return self.__color("purple", s)
    def cyan(self, s):          return self.__color("cyan", s)
    # dark
    def darkgray(self, s):      return self.darkgrey(s)
    def darkgrey(self, s):      return self.__color("darkgrey", s)
    def darkred(self, s):       return self.__color("darkred", s)
    def darkgreen(self, s):     return self.__color("darkgreen", s)
    def darkblue(self, s):      return self.__color("darkblue", s)
    def __color(self, c, s):
        col = self.fg.grey      if c == "grey" \
         else self.fg.red       if c == "red" \
         else self.fg.green     if c == "green" \
         else self.fg.yellow    if c == "yellow" \
         else self.fg.blue      if c == "blue" \
         else self.fg.purple    if c == "purple" \
         else self.fg.cyan      if c == "cyan" \
         else self.fg.darkgrey  if c == "darkgrey" \
         else self.fg.darkred   if c == "darkred" \
         else self.fg.darkgreen if c == "darkgreen" \
         else self.fg.darkblue
        return "%s%s%s" % (col, s, self.reset)

    #
    # Background

    class bg:
        black   = '\033[40m'
        red     = '\033[41m'
        green   = '\033[42m'
        orange  = '\033[43m'
        blue    = '\033[44m'
        purple  = '\033[45m'
        cyan    = '\033[46m'
        lightgrey = '\033[47m'

    def blackBg(self, s):       return self.__colorBg("black", s)
    def redBg(self, s):         return self.__colorBg("red", s)
    def greenBg(self, s):       return self.__colorBg("green", s)
    def orangeBg(self, s):      return self.__colorBg("orange", s)
    def blueBg(self, s):        return self.__colorBg("blue", s)
    def purpleBg(self, s):      return self.__colorBg("purple", s)
    def cyanBg(self, s):        return self.__colorBg("cyan", s)
    def lightGreyBg(self, s):   return self.__colorBg("lightgrey", s)
    def lightGrayBg(self, s):   return self.lightGreyBg(s)
    def __colorBg(self, c, s):
        col = self.bg.black     if c == "black" \
         else self.bg.red       if c == "red" \
         else self.bg.green     if c == "green" \
         else self.bg.orange    if c == "orange" \
         else self.bg.blue      if c == "blue" \
         else self.bg.purple    if c == "purple" \
         else self.bg.cyan      if c == "cyan" \
         else self.bg.lightgrey
        return "%s%s%s" % (col, s, self.reset)

    #
    # Decorate

    class dc:
        bold        = '\033[01m'
        italic      = '\033[03m' # does not work :(
        underline   = '\033[04m'
        reverse     = '\033[07m'
        thruline    = '\033[09m' # ditto
        highlight   = '\033[100m'

    def bold(self, s):      return self.__decorate("bold", s)
    def italic(self, s):    return self.__decorate("italic", s)
    def underline(self, s): return self.__decorate("underline", s)
    def reverse(self, s):   return self.__decorate("reverse", s)
    def thruline(self, s):  return self.__decorate("thruline", s)
    def highlight(self, s): return self.__decorate("highlight", s)
    def __decorate(self, d, s):
        dec = self.dc.bold      if d == "bold" \
         else self.dc.italic    if d == "italic" \
         else self.dc.underline if d == "underline" \
         else self.dc.reverse   if d == "reverse" \
         else self.dc.thruline  if d == "thruline" \
         else self.dc.highlight
        return "%s%s%s" % (dec, s, self.reset)

    #
    # Tab

    class tab:
        # t1    single tab
        # t1p5  tab 1.5
        t1      = " ".ljust(4)
        t1p5    = " ".ljust(6)
        t2      = " ".ljust(8)
        t2p5    = " ".ljust(10)
        t3      = " ".ljust(12)
        t3p5    = " ".ljust(14)

    def t1(self, s):            return self.__tab(1, s)
    def t1p5(self, s):          return self.__tab(1.5, s)
    def t2(self, s):            return self.__tab(2, s)
    def t2p5(self, s):          return self.__tab(2.5, s)
    def t3(self, s):            return self.__tab(3, s)
    def t3p5(self, s):          return self.__tab(3.5, s)
    # deprecated
    def t1point5(self, s):      return self.t1p5(s)
    def t2point5(self, s):      return self.t2p5(s)
    def t3point5(self, s):      return self.t3p5(s)
    def __tab(self, t, s):
        tab = self.tab.t1       if t == 1 \
         else self.tab.t1p5     if t == 1.5 \
         else self.tab.t2       if t == 2 \
         else self.tab.t2p5     if t == 2.5 \
         else self.tab.t3       if t == 3 \
         else self.tab.t3p5
        return "%s%s%s" % (tab, s, self.reset)
