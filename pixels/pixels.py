import math, random, time
import neopixel
# import numpy
from neopixel import GRB

class BasePixel(object):

    def __init__(self,r,g,b,mode=neopixel.GRB, pixel_func=None,params={}):

        if mode!=neopixel.RGB and mode!=neopixel.GRB:
            raise ValueError(
                'Invalid pixel mode %s.' % mode
            )
        self.r = r
        self.g = g
        self.b = b
        self.mode = mode
        self.pixel_func = pixel_func
        self.params = params


    @property
    def color(self):
        if self.mode==neopixel.GRB:
            return self.g,self.r,self.b
        elif self.mode==neopixel.RGB:
            return self.r,self.g,self.b
        else:
            raise ValueError(
                'Invalid pixel mode %s.' % self.mode
            )
        
    @color.setter
    def color(self,color):
        if isinstance(color,str):
            raise ValueError('Pixel.color must be an iterable.')
        if len(color) != len(self.mode):
            raise ValueError('Pixel.color must match Pixel.mode: %s' % self.mode)
        for ii, c in enumerate(color):
            if self.mode[ii]=='R':
                self.r = c
            elif self.mode[ii]=='G':
                self.g = c
            elif self.mode[ii]=='B':
                self.b = c

    @property
    def rgb(self):
        return self.r, self.g, self.b
    
    @property
    def hex(self):
        return "#%02x%02x%02x" % self.rgb
    
    @property
    def np(self):
        return 
    def next(self, *args, **kwargs):
        raise NotImplementedError(
            'Subclasses of BasePixel must override the next() method.'
        )
        
    
    def progress(self):
        self.color = self.next()


class Pixel(BasePixel):

    def __init__(self, r, g, b, mode=neopixel.GRB, params={}):
        super().__init__(r, g, b, mode, None, params)

    def next(self):
        if self.pixel_func is None:
            raise NotImplementedError(
                'Subclasses of Pixel should declare a pixel_func attribute \
                or override next().'
            )
        return self.pixel_func(self)
    
class PixelManager:

    def __init__(self,pixels):
        self.pixels = pixels

    def __iter__(self):
        for pixel in self.pixels:
            yield pixel

    def next(self):
        for pixel in self.pixels:
            pixel.next()

    def progress(self):
        for pixel in self.pixels:
            pixel.progress()

    def as_colors(self):
        return [pixel.color for pixel in self.pixels]
    
class StaticPixel(Pixel):
    
    def next(self):
        return self.color
    
    def progress(self):
        pass


class SinPixel(Pixel):

    def __init__(self,*args, t0=0, a=5, **kwargs):
        self.t0 = t0
        super().__init__(*args,**kwargs)
        self._r0 = self.r
        self._g0 = self.g
        self._b0 = self.b
        self._c0 = self.color
        self.a=a

    def next(self):
        t = self.t0+1
        f = (math.sin(t/self.a)+1)/2
        
        vs = [round(c*f) for c in self._c0]

        return vs
    
    def progress(self):
        self.t0 = self.t0+1

        self.color = self.next()
        
class WanderPixel(Pixel):

    def __init__(self, r, g, b, mode=neopixel.GRB, params={}):
        self.v = [random.choice([-1,0,1]) for ii in range(0,3)]
        super().__init__(r, g, b, mode, params)

    def update_v(self):
        for ii,_v in enumerate(self.v):
            self.v[ii] += random.choice([-1,0,1])

    def next(self):
        new_color = []
        for ii,c in enumerate(self.color):
            nc = c+self.v[ii]
            if nc > 255:
                nc = 255
                self.v[ii] = -self.v[ii]
            elif nc < 0:
                nc = 0
                self.v[ii] = -self.v[ii]
            new_color.append(nc)
        return new_color
        

    def progress(self):
        super().progress()
        self.update_v()
        
