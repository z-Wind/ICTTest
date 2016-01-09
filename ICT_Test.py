#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""docstring with a description"""

__author__ = "子風"
__copyright__ = "Copyright 2015, Sun All rights reserved"
__version__ = "1.0.0"

import networkx as nx
import re
import itertools
import os.path
import sys
import tkinter as tk
from tkinter import filedialog

class MyApp(object):
    """"""
 
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        self.root = parent
        self.root.title("ICT Test")        
        
        basedir = ''
        if getattr(sys, 'frozen', False):
            # we are running in a bundle
            basedir = sys._MEIPASS
        else:
            # we are running in a normal Python environment
            basedir = os.path.dirname(os.path.abspath(__file__))
        root.iconbitmap(os.path.join(basedir, "resource/moon.ico"))
        
        #self.root.geometry("400x100")
        self.frame = tk.Frame(parent)
        self.frame.pack()
 
        btn = tk.Button(self.frame, text="Run", command=self.run)
        btn.config(width=30, height=10)
        btn.pack()
        
        self.center()
 
    #----------------------------------------------------------------------
    def hide(self):
        """"""
        self.root.withdraw()
 
    #----------------------------------------------------------------------
    def run(self):
        """"""
        self.hide()
        filePath = tk.filedialog.askopenfilename(filetypes=(("Asc File", "*.asc"),
                                           ("All files", "*.*") ))
        # filePath = input("請輸入檔案位置：")
        # while not os.path.isfile(filePath):
        # filePath = input("請輸入檔案位置：")
        if filePath:
            netlist = buildGraph(filePath)
            parts, check_decal, pass_decal = ICT_Test(netlist)

            dirPath = os.path.dirname(filePath)
            fileName = os.path.basename(filePath)
            with open(os.path.join(dirPath, fileName.split('.')[0] + '_ICTTest.txt'), 'w') as fp:
                fp.write(filePath + '\n')

                str = '{:<12} = {!r}'.format('check_decal', sorted(check_decal))
                print(str)
                fp.write(str + '\n')
                str = '{:<12} = {!r}'.format('pass_decal', sorted(check_decal) + sorted(pass_decal))
                print(str)
                fp.write(str + '\n\n')

                str = '{:<12} => {!s}'.format('net', 'parts')
                print(str)
                fp.write(str + '\n')
                for net, part in sorted(parts['unchecked'].items()):
                    str = '{:<12} => {!r}'.format(net, sorted(part))
                    print(str)
                    fp.write(str + '\n')

            #os.system("pause")
            os.startfile(os.path.join(dirPath, fileName.split('.')[0] + '_ICTTest.txt'))
            
        self.show()

 
    #----------------------------------------------------------------------
    def show(self):
        """"""
        self.root.update()
        self.root.deiconify()
        
    def center(self):
        toplevel = self.root
        toplevel.update_idletasks()
        w = toplevel.winfo_screenwidth()
        h = toplevel.winfo_screenheight()
        size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
        x = w/2 - size[0]/2
        y = h/2 - size[1]/2
        toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))

        

def buildGraph(filePath):
    netlist = nx.Graph()
    decals = {}
    netname = ''
    nodes = []

    state = 'initial'
    with open(filePath, 'r') as infile:
        for line in infile:
            if state == 'initial':
                if line.startswith('*PART*'):
                    state = 'partsCreate'
            elif state == 'partsCreate':
                if line.startswith('*NET*'):
                    state = 'netsCreate'
                else:
                    m = re.match(r'([a-zA-Z0-9_\-/]+) *([a-zA-Z0-9_\-\.]+)', line)
                    if m is not None:
                        decals[m.group(1)] = m.group(2)
            elif state == 'netsCreate':
                if line.startswith('*END*'):
                    if nodes:
                        edges = itertools.combinations(nodes, 2)
                        netlist.add_edges_from(edges, netName=netname)

                    state = 'finish'
                elif line.startswith('*SIGNAL*'):
                    if nodes:
                        edges = itertools.combinations(nodes, 2)
                        netlist.add_edges_from(edges, netName=netname)

                    netname = line.split()[1]
                    nodes = []
                else:
                    nodes.extend(line.split())
            else:  # finish
                break
    for node in netlist.nodes():
        s = node.split('.')
        try:
            netlist.node[node]['decal'] = decals[s[0]]
        except:
            print('error: ' + node)

    return netlist


def ICT_Test(netlist):
    parts = {}
    check_decal = set()
    pass_decal = set()
    decalListPath = 'DecalList.txt'

    if not os.path.isfile('DecalList.txt') :
        decalListPath = tk.filedialog.askopenfilename(filetypes=(("Decal List", "*.txt"), ("All files", "*.*") ))
    if decalListPath:
        decalList = open(decalListPath, 'r')
        lines = decalList.readlines()
        check_decal = {decal.strip() for decal in lines[0].split('=')[1].split(',') if decal.strip()}
        pass_decal = {decal.strip() for decal in lines[1].split('=')[1].split(',') if decal.strip()}
        decalList.close()
    else:
        check_decal = {'TP-S-0.66', 'TP-S-0_66-G1_1', 'TP-S-0_8-P', 'JP0402', 'JP0805', 'JP1206', 'Gasket-5_3X3_7-Gap1'}
        pass_decal = {'TP-S-0_66-SR', }

    for node in netlist.nodes():
        if netlist.node[node]['decal'] in check_decal | pass_decal:
            netname = netlist.edge[node][netlist.neighbors(node)[0]]['netName']
            parts.setdefault('checked', {}).setdefault(netname, set()).add(node)
            continue

        for neighbor in netlist.neighbors(node):
            netname = netlist.edge[node][neighbor]['netName']
            if netlist.node[neighbor]['decal'] in check_decal:
                parts.setdefault('checked', {}).setdefault(netname, set()).add(node)
                break
            elif netlist.neighbors(node)[-1] is neighbor:
                parts.setdefault('unchecked', {}).setdefault(netname, set()).add(node)

    return parts, check_decal, pass_decal
    

if __name__ == '__main__':
    
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop()

