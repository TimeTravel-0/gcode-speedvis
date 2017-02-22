#!/usr/bin/env python

import pygame
from pygame import gfxdraw
from math import sin, cos

def gcode_parseline(line):
    line=line.split(";")[0]
    parms=dict()
    line=line.split()
    if len(line)<1:
        return {"CMD":"-"}
        
    parms["CMD"]=line[0]
    for l in line:
        parms[l[0]]=float(l[1:])
    return parms

def calc_gcode(l):
    p = gcode_parseline(l)
    if p["CMD"]=="G1":
        if "X" in p.keys() and "Y" in p.keys() and "Z" in p.keys():
            
            
            return [p["X"],p["Y"],p["Z"]]
            
def screen_transform(x,y,z,screen_width,screen_height,scale,x_ofs,y_ofs,z_ofs, rot):
    trans_x = (x-x_ofs)*sin(rot) + (y-y_ofs)*cos(rot)
    trans_y = (x-x_ofs)*sin(rot+3.14/2) + (y-y_ofs)*cos(rot+3.14/2)
    
    return (trans_x)* scale + screen_width/2 , ((trans_y)+-(z-z_ofs))* scale * 0.5 + screen_height/2  # -(z-z_ofs))*0.5

def minmaxc(val_min, val_max, val_cur):
    if val_min > val_cur or val_min == False:
        val_min = val_cur
    if val_max < val_cur or val_max == False:
        val_max = val_cur
        
    return val_min, val_max
    
def relc(val_min, val_max, val):
    val = ((val - val_min)/ (val_max - val_min))
                
    if val<0:
        val = 0
    if val>1:
        val = 1
        
    return val
                
def multiminmaxc(lines, keys):
    
    minvals = dict()
    maxvals = dict()
    
    for k in keys:
        minvals[k]=False
        maxvals[k]=False
    
    for line in lines:
        
        # only if "G1" line...
        if line[0:2]!="G1":
            continue
        p = gcode_parseline(line)
        for k in keys:
            if k in p.keys():
                minvals[k], maxvals[k] = minmaxc(minvals[k], maxvals[k], p[k])
    return minvals, maxvals
    
    
def prep_gcodes(lines):
    
    
    minvals, maxvals = multiminmaxc(lines, ["X","Y","Z","E","F"])
    
    return minvals, maxvals
    
            
def draw_gcodes(lines, surface,linefrom, lineto, extvals, rot):
    f = lines
    
    minvals, maxvals = extvals
    
    
    f_min = minvals["F"]
    f_max = maxvals["F"]
    z_min = minvals["Z"]
    z_max = maxvals["Z"]
                
    #print f_max, f_min
    
    currentpos = [False,False,False,False,False]
    linenum=0
    oldpos = False
    for line in f:
        linenum+=1
        if linenum<linefrom:
            continue
        if linenum>lineto:
            #print "!"
            return False
            
        
        # only if "G1" line...
        if line[0:2]!="G1":
            continue
            
        p = gcode_parseline(line)
        if p["CMD"]=="G1":
            lastpos = currentpos
            if "X" in p.keys():
                currentpos[0]=p["X"]
            if "Y" in p.keys():
                currentpos[1]=p["Y"]
            if "Z" in p.keys():
                currentpos[2]=p["Z"]
            if "E" in p.keys():
                currentpos[3]=p["E"]
            if "F" in p.keys():
                currentpos[4]=p["F"]
                
        if False in currentpos:
            continue

        x_rel, y_rel, z_rel, f_rel=0,0,0,0
        if "X" in p.keys():
            x_rel = relc(minvals["X"], maxvals["X"], p["X"])
        if "Y" in p.keys():
            y_rel = relc(minvals["Y"], maxvals["Y"], p["Y"])
        if "Z" in p.keys():
            z_rel = relc(minvals["Z"], maxvals["Z"], p["Z"])
        if "F" in p.keys():
            f_rel = relc(minvals["F"], maxvals["F"], p["F"])
            
                
        zoom = 1
        
        zoom_v = surface.get_height() / (maxvals["Z"]-minvals["Z"])
        
        zoom = zoom_v
                
        newpos = screen_transform(\
         currentpos[0],\
         currentpos[1],\
         currentpos[2],\
         surface.get_width(),\
         surface.get_height(),\
         zoom,\
         0.5*(maxvals["X"]+minvals["X"]),\
         0.5*(maxvals["Y"]+minvals["Y"]),\
         0.5*(maxvals["Z"]+minvals["Z"]),\
         rot) # x,y,z
         
        f_rel = (1-f_rel)*(1-f_rel)
        
        color = (x_rel*255 * f_rel,y_rel*255 * f_rel,z_rel*255 * f_rel)
        
        if not oldpos:
            oldpos=newpos
            
        if f_rel>0: # not max speed (=at max speed, printer is just jumping between extrusions, not printing, hide these!)
            pygame.draw.line(surface,color,newpos,oldpos,2)
        
        #pygame.gfxdraw.line(surface,int(newpos[0]),int(newpos[1]),int(oldpos[0]),int(oldpos[1]),color)
        oldpos=newpos
        
        #pygame.display.flip()
    return True
    
    
def capture_to_file(surf,fn):
    pygame.image.save(surf, fn)
        
def main():
    """ Set up the game and run the main game loop """
    pygame.init()      # Prepare the pygame module for use
    surface_sz = [1920,1080]
    
    #gcodefile = "exampleInputOutput/CurveacousVaseAfter.gcode"
    gcodefile = "watervase21ProcessedLargeOption2.gcode"

    # Create surface of (width, height), and its window.
    main_surface = pygame.display.set_mode(surface_sz)
    pygame.display.set_caption(gcodefile)
    
    l=0
    rot=0
    
    lines = file(gcodefile).readlines()
    
    extvals = prep_gcodes(lines)

    main_surface.fill((128,128,128))
    i = 0
    j = 0
    while True:
        ev = pygame.event.poll()    # Look for any event
        if ev.type == pygame.QUIT:  # Window close button clicked?
            break                   #   ... leave game loop

        
        if draw_gcodes(lines,main_surface,l,l+3003,extvals,rot):
            main_surface.fill((128,128,128))
            l=0
            i+=1
            rot=3.14/20*i
            if rot>3.14*2:
                break # die
        else:
            l=l+3003
            
        capture_to_file(main_surface,"capture/%.8i.png"%(j))
        j+=1
        

        # Now the surface is ready, tell pygame to display it!
        pygame.display.flip()

    pygame.quit()     # Once we leave the loop, close the window.

main()
