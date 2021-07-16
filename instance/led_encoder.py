import time
import board
import neopixel
import RPi.GPIO as GPIO
from threading import Thread

# Pino de conexao Raspberry
# (podem ser utilizados os pinos 10, 12, 18 ou 21)
class Gpio():
    def __init__(self, volume_init):

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        self.pixel_pin = board.D21
        self.r_pin = 12
        self.g_pin = 13
        self.b_pin = 19
        self.clk = 17
        self.dt = 27
        self.pwm_frequency = 200
        self.desliga_pin = 20
        self.volume = volume_init
        GPIO.setup(self.r_pin, GPIO.OUT)
        GPIO.setup(self.g_pin, GPIO.OUT)
        GPIO.setup(self.b_pin, GPIO.OUT)
        GPIO.setup(self.desliga_pin, GPIO.OUT)
        GPIO.setup(self.clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        teste = Thread(target=self.encoder)
        teste.start()      
        self.setup_leds()


    def setup_leds(self):
        num_pixels = 180
        
        # Ordem dos pixels de cor - RGB ou GRB
        # Em alguns módulos as cores verde e vermelha estao invertidas
        ORDER = neopixel.GRB
        
        self.pixels = neopixel.NeoPixel(self.pixel_pin, num_pixels, brightness=0.1, auto_write=False,
                               pixel_order=ORDER)        
        
        self.pwmBlue = GPIO.PWM(self.b_pin, self.pwm_frequency)
        self.pwmBlue.start(0)
         
        self.pwmRed = GPIO.PWM(self.r_pin, self.pwm_frequency)
        self.pwmRed.start(0)
        
        self.pwmGreen = GPIO.PWM(self.g_pin, self.pwm_frequency)
        self.pwmGreen.start(0)
        
    def set_rgb(self, r, g, b):
        try:
            r_map = self.maping(r, 0, 255, 0., 100.)
            g_map = self.maping(g, 0, 255, 0., 100.)
            b_map = self.maping(b, 0, 255, 0., 100.)
           
            self.pwmRed.ChangeDutyCycle(r_map)
            self.pwmGreen.ChangeDutyCycle(g_map)
            self.pwmBlue.ChangeDutyCycle(b_map)
        except Exception as e:
            print(e)
    def maping(self, x, in_min, in_max, out_min, out_max):
    
      return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)
    
    
    def wheel(self, pos):
        # Utiliza um valor entre 0 e 255 para definir a cor
     # As cores sao uma transicao r - g - b
        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = int(pos * 3)
            g = int(255 - pos*3)
            b = 0
        elif pos < 170:
            pos -= 85
            r = int(255 - pos*3)
            g = 0
            b = int(pos*3)
        else:
            pos -= 170
            r = 0
            g = int(pos*3)
            b = int(255 - pos*3)
        return (r, g, b) if ORDER == neopixel.RGB or ORDER == neopixel.GRB else (r, g, b, 0)
     
    def rainbow_cycle(self, wait):
        for j in range(5000):
            for i in range(num_pixels):
                pixel_index = (i * 256 // num_pixels) + j
                pixels[i] = wheel(pixel_index & 255)
            pixels.show()
            time.sleep(wait)
    def pix_fill(self, r, g, b):
        r_map = self.maping(r, 0, 255, 0., 100.)
        g_map = self.maping(g, 0, 255, 0., 100.)
        b_map = self.maping(b, 0, 255, 0., 100.)        
        self.pixels.fill((r_map, g_map, b_map))

    

    def change_volume(self, vol):
        pass
        
    def reset_volume(self, vol):
        self.volume = vol
       
    def encoder(self):
        clkLastState = GPIO.input(self.clk)
        try:
            while True:
                clkState = GPIO.input(self.clk)
                dtState = GPIO.input(self.dt)
                if clkState != clkLastState:
                    if dtState != clkState:
                        if self.volume < 100:
                            self.volume += 1
                            self.change_volume(self.volume)
                        
                    else:
                        if self.volume > 0:
                            self.volume -= 1
                            self.change_volume(self.volume)
                  
                    #print (self.volume)
                clkLastState = clkState
                time.sleep(0.01)
        finally:
                GPIO.cleanup()        

    def destroy(self):
        GPIO.cleanup()
           
