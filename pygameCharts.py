#!/usr/bin/python
#
# Artur Skonecki 2013
# 2 column charts controlled by keyboard a,z up,down

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)




try:
    import sys
    import csv
    import random
    import math
    import os
    import getopt
    import pygame
    from socket import *
    from pygame.locals import *
except ImportError, err:
    print "couldn't load module. %s" % (err)
    sys.exit(2)

def load_png(name):
    """ Load image and return image object"""
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    return image, image.get_rect()

def toggle_fullscreen():
    screen = pygame.display.get_surface()
    tmp = screen.convert()
    caption = pygame.display.get_caption()
    cursor = pygame.mouse.get_cursor()  # Duoas 16-04-2007 
    
    w,h = screen.get_width(),screen.get_height()
    flags = screen.get_flags()
    bits = screen.get_bitsize()
    
    pygame.display.quit()
    pygame.display.init()
    
    screen = pygame.display.set_mode((w,h),flags^FULLSCREEN,bits)
    screen.blit(tmp,(0,0))
    pygame.display.set_caption(*caption)
 
    pygame.key.set_mods(0) #HACK: work-a-round for a SDL bug??
 
    pygame.mouse.set_cursor( *cursor )  # Duoas 16-04-2007
    
    return screen



class Label(pygame.sprite.Sprite):
    """Image label for the Chart
    Returns: Label object
    Functions: reinit
    Attributes: side, img"""

    def __init__(self, side, img):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png(img)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.side = side
        self.reinit()

    def reinit(self):
        self.state = "still"
        self.movepos = [0,0]
        if self.side == "left":
            self.rect.center = (self.area.midright[0]/4, self.area.midbottom[1]-self.area.midbottom[1]/4+100)
        elif self.side == "right":
            self.rect.center = (self.area.midright[0]-self.area.midright[0]/4, self.area.midbottom[1]-self.area.midbottom[1]/4 +100)

class ChartColumn(pygame.sprite.Sprite):
    """column chart
    Returns: ChartColumn object
    Functions: reinit, update, moveup, movedown
    Attributes: which, speed, side, colir"""
    
    BARWIDTH = 50
    MINHEIGHT = 1

    def __init__(self, side, color):
        pygame.sprite.Sprite.__init__(self)

        width, height = self.BARWIDTH, self.MINHEIGHT
        self.image = pygame.Surface([width, height])
        self.image.fill(color)

        self.rect = self.image.get_rect()
        
        self.color = color

        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.side = side
        self.speed = 10
        self.state = "still"
        
        self.bottom = self.area.midbottom[1]-self.area.midbottom[1]/4
        
        self.h_bottom= self.area.height-self.area.height/3
        
        myfont = pygame.font.SysFont("monospace", 15)
        self.label = myfont.render("Some text!", 1, (255,255,0))

        self.reinit()

    def reinit(self):
        self.state = "still"
        self.movepos = [0,0]
        if self.side == "left":
            self.rect.center = (self.area.midright[0]/4, self.area.midbottom[1]-self.area.midbottom[1]/4)
        elif self.side == "right":
            self.rect.center = (self.area.midright[0]-self.area.midright[0]/4, self.area.midbottom[1]-self.area.midbottom[1]/4)

    def update(self):
        h_top = self.rect.height = self.rect.height - self.movepos[1]
        h_bottom= self.area.height-self.area.height/3
        self.h_bottom = h_bottom
        self.h_top = h_top
        
        if h_top < self.MINHEIGHT:
            h_top = self.rect.height = self.MINHEIGHT
        elif h_top > h_bottom:
            h_top = self.rect.height = h_bottom
         
        self.image = pygame.Surface([self.BARWIDTH, h_top])
        self.image.fill(self.color)
        
        self.rect.y = self.area.midbottom[1]-self.area.midbottom[1]/4 - h_top

        pygame.event.pump()
        
    def set_heigth(self, value):
        
        self.image.fill(WHITE)
        
        self.image = pygame.Surface([self.BARWIDTH, value])
        self.image.fill(self.color)
        
        if self.side == 'left':
            self.rect.height = 100
        else:
            self.rect.height = 200
        self.rect.height = value
        
        #self.rect.y = self.area.midbottom[1]-self.area.midbottom[1]/4 - h_top
        pass

    def moveup(self):
        self.movepos[1] = self.movepos[1] - (self.speed)
        self.state = "moveup"

    def movedown(self):
        self.movepos[1] = self.movepos[1] + (self.speed)
        self.state = "movedown"
        
    def set_heigth_delta(self, value):
        self.movepos[1] = -value


def main():
    from optparse import OptionParser
    parser = OptionParser()
    
    parser.add_option("-i", "--stdin",
                  action="store_true", dest="stdin", default=False,
                  help="read stdin instead of keyboard input")
    
    (options, args) = parser.parse_args()
    
    # Initialise screen
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    #screen = toggle_fullscreen()
    pygame.display.set_caption('lispmob')

    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(WHITE)
    
    # set up fonts
    basicFont = pygame.font.SysFont(None, 48)
    

    # Initialise charts
    global bar1
    global bar2
    
    bar1label = Label("left", 'link.png')
    bar2label = Label("right", 'link_green.png')
    
    bar1 = ChartColumn("left", BLUE)
    bar2 = ChartColumn("right", GREEN)

    # Initialise sprites
    chartsprites = pygame.sprite.RenderPlain((bar1, bar2, bar1label, bar2label))
    #ballsprite = pygame.sprite.RenderPlain(ball)

    # Blit everything to the screen
    screen.blit(background, (0, 0))
    pygame.display.flip()

    # Initialise clock
    clock = pygame.time.Clock()
    
    #bar1.set_heigth_delta(100)
    
    # Event loop
    while 1:
        # Make sure game doesn't run at more than 60 frames per second
        clock.tick(60)
        
        if options.stdin:
            line1 = sys.stdin.readline()
            line2 = sys.stdin.readline()
            line3 = sys.stdin.readline()
            if not line1: break
            
            lines = [line1, line2, line3]
            
            spamreader = csv.reader(lines, delimiter=';', quotechar='|')

            is_iface1 = False
            is_iface2 = False

            for c,row in enumerate(spamreader):
                print row
                
                try:
                    unix_timestamp,iface_name,bytes_out_s,bytes_in_s,bytes_total_s,bytes_in,bytes_out,packets_out_s,packets_in_s,packets_total_s,packets_in,packets_out,errors_out_s,errors_in_s,errors_in,errors_out = row
                except ValueError:
                    print ('badly formatted csv')
                    continue
                max_throughput = 200
                current_throughput = float(bytes_out_s)/1400#(packets_out_s)
                max_bar_heigth = bar1.h_bottom
                
                if iface_name == 'eth0':
                    is_iface1 = True
                    bar1.set_heigth(max_bar_heigth * current_throughput / max_throughput)
                elif iface_name == 'eth2':
                    is_iface2 = True
                    bar2.set_heigth(max_bar_heigth * current_throughput / max_throughput)
                    print current_throughput
                
                #bar1.set_heigth(250)
                #bar2.set_heigth(250)
            
            if not is_iface1:
                bar1.set_heigth(0)
            if not is_iface2:
                bar2.set_heigth(0)
                
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == KEYDOWN:
                    if event.key == K_q:
                        pygame.quit()
                    if event.key == K_f:
                        screen = toggle_fullscreen()
            pass
        else:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == KEYDOWN:
                    if event.key == K_q:
                        pygame.quit()
                    if event.key == K_f:
                        screen = toggle_fullscreen()
                    if event.key == K_a:
                        bar1.moveup()
                    if event.key == K_z:
                        bar1.movedown()
                    if event.key == K_UP:
                        bar2.moveup()
                    if event.key == K_DOWN:
                        bar2.movedown()
                elif event.type == KEYUP:
                    if event.key == K_a or event.key == K_z:
                        bar1.movepos = [0,0]
                        bar1.state = "still"
                    if event.key == K_UP or event.key == K_DOWN:
                        bar2.movepos = [0,0]
                        bar2.state = "still"

        screen.blit(background, (0,0)) # had trouble with blitting bars on set_height so for now blit everything
#         screen.blit(background, bar1label.rect, bar1label.rect)
#         screen.blit(background, bar2label.rect, bar2label.rect)
#         
#         screen.blit(background, bar1.rect, bar1.rect)
#         screen.blit(background, bar2.rect, bar2.rect)
        
        chartsprites.update()
        chartsprites.draw(screen)
        pygame.display.flip()
        
        if options.stdin:
            bar1.set_heigth_delta(0)


if __name__ == '__main__': main()
