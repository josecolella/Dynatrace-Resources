from __future__ import print_function
from selenium import webdriver
from abc import ABCMeta, abstractmethod

class AbstractPortal(object):
    __metaclass__ = ABCMeta

    def __init__(self, username, password):
        self.driver = webdriver.PhantomJS()
        self.username = username
        self.password = password

    @abstractmethod
    def login(self):
        pass

class GPNPortal(AbstractPortal):

    def login(self):
        print("Hello World")
