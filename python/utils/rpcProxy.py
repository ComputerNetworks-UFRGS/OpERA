"""
Copyright 2013 OpERA

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
"""

import xmlrpclib
import inspect

from threading import Thread

from abc import ABCMeta
from abc import abstractmethod

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler


#::TODO:: descricao de metodos das classes e de seus parametros.
class RPCBaseProxy(object):
    """
    Abstract class to proxy method calls
    To implement a concrete proxy class, just inherit this class and implement the _imp_proxy_method(self, name, func).
    Call _proxy_class_methods(self, instance) to add the methods of object instance to the proxy.
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        """
        CTOR
        """
        pass

    def _proxy_class_methods(self, instance):
        """
        Adds methods of instance to be acessible externally
        @param instance Object instance
        """
        methods = [(name, func)
                   for name, func in inspect.getmembers(instance, predicate=inspect.ismethod)
                   if name is not '__init__']

        print methods

        for name, func in methods:
            self.register_function(func, name)  #pylint: disable=E1101

    @abstractmethod
    def _imp_proxy_method(self, name, func):
        """
        Proxy method implementation.
        @param name Original function name.
        @param func Proxied object pointer to function.
        @return Return a pointer to a function. This function proxies the calls to function 'name'.
        """
        pass


class RPCExporter(Thread, RPCBaseProxy):
    """
    Class to export methods of objects to a RPC server.
    Methods can be called by using a xmlrpclib.ServerProxy object.
    """

    def __init__(self, addr=("localhost", 8000)):
        """
        CTOR.
        @param addr Tuple (ip, port).
        """

        Thread.__init__(self)
        RPCBaseProxy.__init__(self)

        self.__instances = []

        self.__server = SimpleXMLRPCServer(addr=addr, logRequests=False, requestHandler=SimpleXMLRPCRequestHandler)
        self.__server.register_instance(self)


    def register_function(self, name, func):
        """
        @param name
        @param func
        """
        setattr(self, name, self._imp_proxy_method(name, func))

    def register_instance(self, obj):
        """
        Entry point to proxy class functions. 
        @param obj Instance of object to proxy.
        """
        self.__instances.append(obj)
        self._proxy_class_methods(obj)

    def _imp_proxy_method(self, name, func):
        """
        Implementation of base class abstract method.
        @param name Proxied function name.
        @param func Pointer to proxied class function.
        @param return Pointer to function proxy.
        """
        # We just return the original function
        return func


    def run(self):
        """
        Thread abstract method implementation.
        """
        self.__server.serve_forever()


class RPCImporter(RPCBaseProxy):
    """
    Class to import methods from a RPC server.
    ::KLUDGE:: Ideally RPCImporter should check all methods available in a given RPC server
                and import then. However, the function to list the methods in the RPC ser-
                ver is not working properly. So, instead of listing the functions, this
                class uses the register_instance(self, obj) to import the name of the
                functions of obj. The functions called, however, are of the ServerProxy.
    """

    def __init__(self, addr=None):
        """
        CTOR.
        @param addr
        """
        RPCBaseProxy.__init__(self)
        self._client = xmlrpclib.ServerProxy((addr))


    def register_instance(self, obj):
        """
        @param obj
        """
        self._proxy_class_methods(obj)


    def register_function(self, name):
        """
        @param name
        """
        setattr(self, name, self._imp_proxy_method(name, None))


    def _imp_proxy_method(self, name, func):
        """
        @param name
        @param func
        """
        return eval("self._client.%s" % name)
