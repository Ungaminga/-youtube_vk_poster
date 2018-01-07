# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 17:48:39 2018

@author: loljkpro
"""

import configparser
def main():
    Config = configparser.ConfigParser()
    Config.read("conf.ini")
    if (Config.sections() != ['YouTube', 'Vk']):
        print("Wrong Configs")
        return
    
if __name__ == "__main__":
    main()