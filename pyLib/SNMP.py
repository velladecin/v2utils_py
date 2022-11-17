#!/usr/bin/env python2.7
import re
import sys
import netsnmp
from pprint import pprint

# __SNMP is being hidden (__) as you may as well call netsnmp itself if you require the full functionality.
# It is here really only for the 'common' calls which there may be a few over time.

# timeout 1000000 (1s) - default in netsnmp

class __SNMP(object):
    def __init__(self, version, host, retries=2, timeout=1000000, community=None,
                    seclevel=None, secname=None, authpr=None, authpw=None, privpr=None, privpw=None):
        if version == 1 or version == 2:
            self.sess = netsnmp.Session(Version=2, DestHost=host, Community=community, Retries=retries, Timeout=timeout)
        elif version == 3:
            self.sess = netsnmp.Session(Version=3, DestHost=host, Retries=retries, Timeout=timeout,
                                        SecLevel=seclevel, SecName=secname, AuthProto=authpr, AuthPass=authpw, PrivProto=privpr, PrivPass=privpw)
        else:
            raise SnmpErr("SNMP v%d not supported" % version)

        if self.sess.sess_ptr == 0: raise SnmpErr("Could not determine (resolve?) host: %s" % host)

        # Not completely sure what this is for but it features in the test.py of the netsnmp package.
        # Sooo.. I'm using it here too :)
        self.sess.UseEnums = 1
        # '.iso.org.dod.internet.mgmt.mib-2.69.1.3.1.0'
        # 'mib-2.69.1.3.1.0'
        self.sess.UseLongNames = 1 
        # .1.3.6.1.2.1.1.1
        # 'mib-2.69.1.3.1.0'
        self.sess.UseNumeric = 0

    def __return(self, vars):
        d = dict()
        for var in vars:
            # trying to catch a (real) HEX string here
            # as opposed to an actual readable (ASCII) string
            try:
                var.val.decode('ascii')
                v = var.val
            except UnicodeDecodeError:
                v = ":".join(map(lambda x: "%0.2x" % ord(x), var.val))
            except AttributeError:
                continue
                
            # this keeps single value as single list => a[sysdescr] = ['str', 'my_description', '']
            # but multiple values as a list of lists => a[ifdescr] = [ ['str', 'iface1', '1'], ['str', 'iface2', '2'], ...]
            if not var.tag in d:
                d[var.tag] = [var.type, v, var.iid]
                continue

            # adding to existing
            if not isinstance(d[var.tag][0], list): d[var.tag] = [d[var.tag]]
            d[var.tag].append([var.type, v, var.iid])

        return d

    def _get(self, *v):
        vb = list()
        for x in v:
            if isinstance(x, list):
                vb.append(netsnmp.Varbind(*x))
            else:
                vb.append(netsnmp.Varbind(x))

        vars = netsnmp.VarList(*vb)
        self.sess.get(vars)
        return self.__return(vars)

        """
        vars = netsnmp.VarList(
                *map(lambda x: netsnmp.Varbind(x, 0), v))

        self.sess.get(vars)
        return self.__return(vars)
        """

    def _walk(self, v):
        vars = netsnmp.VarList(netsnmp.Varbind(v))
        self.sess.walk(vars)
        return self.__return(vars)

    #def _set(self, oid, iid, val, type):
    #    return self.sess.set(netsnmp.VarList(netsnmp.Varbind(oid, iid, val, SnmpType.validate(type))))
    def _set(self, *sets):
        res = list()
        for s in sets:
            try:
                oid, iid, val, type = s
            except ValueError:
                raise SnmpErr("SNMP set requires: oid, iid, val, type")

            res.append(self.sess.set(netsnmp.VarList(netsnmp.Varbind(oid, iid, val, SnmpType.validate(type)))))

        if len(res) == 1: return res[0]
        return res

    #
    # Common

    def get(self, *v): return self._get(*v)
    def set(self, *v): return self._set(*v)
            
    
    # sets
    def setSyslocation(self, location): return self._set('sysLocation', '0', location, SnmpType.String)
    def setIfadminstatus(self, val, *iid):
        if not iid or len(iid) == 0: raise SnmpErr("Iface ID(s) must be provided")
        return self._set(*map(lambda x: ['IF-MIB::ifAdminStatus', x, val, SnmpType.Int], iid)) 

    # gets
    def sysdescr(self): return self._get(['sysDescr', 0])
    def sysuptime(self): return self._get(['sysUpTime', 0])
    def syslocation(self): return self._get(['sysLocation', 0])

    # walks
    def system(self): return self._walk('system')
    def ifdescr(self): return self._walk('ifDescr')

    # mix
    def ifadminstatus(self, *fid):
        oid = 'IF-MIB::ifAdminStatus'
        res = list()
        if fid and len(fid) > 0:
            for id in fid: res.append(self._get([oid, id]))
        else:
            res = self._walk(oid)

        return res

#
# CMTS

class SnmpCmts(__SNMP):
    __RO = 'public'
    __RW = 'private'

    def __init__(self, host, mode="ro", version=2, retries=1, timeout=1000000):
        # accept CMTS1.. or ip.ad.d.r
        if not re.match(r'cmts\d+', host, re.IGNORECASE) and not re.match(r'^\d+\.\d+\.\d+\.\d+$', host):
            raise SnmpCmtsErr("Invalid CMTS host: %s" % host)

        if version == 3:
            super(SnmpCmts, self).__init__(version, host, retries, timeout,
                                            seclevel="<seclevel>",
                                            secname="<user>",
                                            authpr="<cipher>", authpw='<apw>',
                                            privpr="<priv>", privpw='<ppw>')
        elif version == 2:
            super(SnmpCmts, self).__init__(version, host, retries, timeout, self.__RW if mode == "rw" else self.__RO)
        else:
            raise SnmpErr("SNMP v%d not supported on CMTS" % version)

    # CMTS specific


#
# CM

class SnmpCm(__SNMP):
    __RO = 'public'
    __RW = 'private'
    __V  = 2

    def __init__(self, host, mode="ro", retries=1, timeout=1000000):
        if not re.match(r'^[a-fA-F0-9\:]+$', host, re.IGNORECASE):
            raise SnmpCmErr("Invalid CM host: %s" % host)

        super(SnmpCm, self).__init__(self.__V, host, retries, timeout, self.__RW if mode == "rw" else self.__RO)

    # CM specific
    def fw(self): return self._walk('.1.3.6.1.2.1.69.1.3')
    def hw(self): return self._walk('.1.3.6.1.4.1.4413.2.2.2.1.9.1.1.5.1.3')
    def log(self): return self._walk('.1.3.6.1.2.1.69.1.5.8.1.7')

    def reboot(self): return self._set('.1.3.6.1.2.1.69.1.1.3.0', '', 1, 'INTEGER')
    #def setSysLocation(self, location):
    #    return self._set('.iso.org.dod.internet.mgmt.mib-2.system.sysLocation', '0', location, SnmpType.String)


#
# Types

class SnmpType:
    Int = "INTEGER"
    String = "OCTETSTRING"
    Ticks = "TICKS"
    Oid = "OBJECTID"
    Ipaddr = "IPADDR"

    @staticmethod
    def validate(type):
        t = SnmpType.Int    if type in ["i", "int", SnmpType.Int]       else (
            SnmpType.String if type in ["s", "str", SnmpType.String]    else (
            SnmpType.Ticks  if type in ["t", "ticks", SnmpType.Ticks]   else (
            SnmpType.Oid    if type in ["o", "oid", SnmpType.Oid]       else (
            SnmpType.Ipaddr if type in ["ip", "ipaddr", SnmpType.Ipaddr]else "unknown"))))

        if t == "unknown":
            raise SnmpTypeErr("Unsupported OID type '%s'" % type)

        return t
        

#
# Exceptions

class SnmpErr(Exception):
    def __init__(self, msg): super(SnmpErr, self).__init__(msg)
class SnmpTypeErr(Exception):
    def __init__(self, msg): super(SnmpTypeErr, self).__init__(msg)
class SnmpCmErr(Exception):
    def __init__(self, msg): super(SnmpCmErr, self).__init__(msg)
class SnmpCmtsErr(Exception):
    def __init__(self, msg): super(SnmpCmtsErr, self).__init__(msg)
