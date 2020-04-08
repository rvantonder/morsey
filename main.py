__version__ = '2.2'

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import NumericProperty, ReferenceListProperty,\
  ObjectProperty, ListProperty, DictProperty, BooleanProperty, StringProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.core.window import Window
from time import time
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.core.audio import SoundLoader
from kivy.uix.modalview import ModalView
from kivy.utils import platform
from kivy.logger import Logger
from kivy.network.urlrequest import UrlRequest

import random
import colorsys
import os
import socket

from sets import Set

platform = platform() # deprecated 
app = None

# Logger.debug('Platform: %s' % platform)

if platform == 'android':
  import gs_android

leaderboard_highscore = 'CgkInKa1_t8UEAIQHA'

achievement_heart = 'CgkInKa1_t8UEAIQAQ'
achievement_spiral = 'CgkInKa1_t8UEAIQAg'
achievement_red_square = 'CgkInKa1_t8UEAIQAw'
achievement_star = 'CgkInKa1_t8UEAIQBA'
achievement_snow = 'CgkInKa1_t8UEAIQBQ'
achievement_clover = 'CgkInKa1_t8UEAIQGQ'

achievement_void = 'CgkInKa1_t8UEAIQCg'

achievement_az = 'CgkInKa1_t8UEAIQGA'

achievement_5k = 'CgkInKa1_t8UEAIQDA'
achievement_10k = 'CgkInKa1_t8UEAIQDw'
achievement_12k = 'CgkInKa1_t8UEAIQEA' 
achievement_15k = 'CgkInKa1_t8UEAIQEQ'

achievement_100_tiles = 'CgkInKa1_t8UEAIQEg'
achievement_250_tiles = 'CgkInKa1_t8UEAIQEw'
achievement_500_tiles = 'CgkInKa1_t8UEAIQFA'
achievement_1000_tiles = 'CgkInKa1_t8UEAIQFQ'
achievement_5000_tiles = 'CgkInKa1_t8UEAIQFg'
achievement_10000_tiles = 'CgkInKa1_t8UEAIQFw'

achievement_multipass = 'CgkInKa1_t8UEAIQGg'
achievement_multiheart = 'CgkInKa1_t8UEAIQCA' 
achievement_multisnow = 'CgkInKa1_t8UEAIQCQ'
achievement_multibrick = 'CgkInKa1_t8UEAIQCw'
achievement_multispiral = 'CgkInKa1_t8UEAIQDQ'
achievement_multistar = 'CgkInKa1_t8UEAIQDg'

achievement_sos = 'CgkInKa1_t8UEAIQGw'

from kivy.uix.popup import Popup
class GooglePlayPopup(Popup):
  pass
class FirstTimePopup(Popup):
  pass
#else:
#  achievements = {}

class HSV:
  s = 1
  v = 1
  RED    = (1.0,s,v)
  PINK   = (0.9,s,v) 
  BLUE = (.5416, s, v)
  GREEN = (0.3833, s, v)
  CYAN   = (0.5,s,v)
  YELLOW = (0.18,s,v)
  ORANGE = (0.083,s,v)
  PURPLE = (0.793,s,v)
  GRAY = (0,0,.1)
  BLACK = (0,0,0) 

class BONUS:
  HEX = "snowflake.png" #"hex.png"
  SPIRAL = "spiral.png"
  #SQUARE = "green_square.png"
  SQUARE = "red_square.png"
  STAR = "star.png"
  NONE = "blank.png"
  MULT = "mult_classifier" # not a png, we used this to get to one of the below two
  MULT3 = "mult_3.png"
  MULT5 = "mult_5.png"
  LIFE = "heart_tile.png"
  CLOVER = "clover.png"

class MODE:
  SP = 1
  MP = 2
  TRAIN_EASY = 3
  TRAIN_MEDIUM = 4
  TRAIN_HARD = 5

class Markup:
  base = "[color=%s][b]%s[/b][/color]"
  WHITE = base %  ("ffffff", "%s")
  YELLOW = base % ("f3ff00", "%s")
  RED = base % ("ff0000", "%s")

class BottomMenu(GridLayout):
  def __init__(self, **kwargs):
    super(BottomMenu, self).__init__(**kwargs)     

class Piece(RelativeLayout): # for animating background of menus
  velocity_x = NumericProperty(0)
  velocity_y = NumericProperty(0)
  velocity = ReferenceListProperty(velocity_x, velocity_y)

  def __init__(self, **kwargs):
    super(Piece, self).__init__()
    
    self.scale = .5
    self.velocity = [random.random()*2*(Window.height/480.), 0] # TODO not good enough
    self.start_pos = [(-40, random.randint(self.im.texture_size[1]/2, Window.height-(self.im.texture_size[1]/2))),
                      (Window.width+40, random.randint(self.im.texture_size[1]/2, Window.height-(self.im.texture_size[1]/2)))]
    p = random.randint(0,1)
    self.center = self.start_pos[p]
    
    self.rotation_factor = random.random() * 1.5
    if p:
      self.velocity_x = -self.velocity_x
      self.rotation_factor = -self.rotation_factor

  def move(self):
    self.pos = Vector(*self.velocity) + self.pos

class Tile(RelativeLayout):
  velocity_x = NumericProperty(0)
  velocity_y = NumericProperty(0)

  prev_y = NumericProperty(0)

  velocity = ReferenceListProperty(velocity_x, velocity_y)

  value = StringProperty(None)
  bonus = StringProperty(None)
  resist = NumericProperty(0)

  captured = BooleanProperty(False) # flag for removal

  def __init__(self, **kwargs):
    super(Tile, self).__init__()

    self.bonuses = [BONUS.HEX, BONUS.SQUARE, BONUS.STAR, BONUS.MULT, BONUS.LIFE, BONUS.NONE]
    self.bonus = random.sample(self.bonuses, 1)[0]
    self.bonus = random.sample([self.bonus] + [BONUS.NONE], 1)[0]

    if self.bonus == BONUS.SQUARE:
      self.resist = 1

    if self.bonus == BONUS.MULT: # choose one of the multipliers
      self.bonus = random.sample([BONUS.MULT3, BONUS.MULT5], 1)[0]

    if (random.random()*90 < 1): #spiral
      self.bonus = BONUS.SPIRAL

    if (random.random()*10000 < 1): # clover
      self.bonus = BONUS.CLOVER
  
    self.t_imag_bonus.source = "pngs/%s" % self.bonus

    self.prev_y = self.velocity_y

    self.alpha = 1

    self.t_imag.source = "pngs/0.png"
    self.set_color(HSV.PINK) # DEFAULT 

    self.rotation_enabled = False

  def move(self):
    self.pos = Vector(*self.velocity) + self.pos

  def set_color(self, c):
    q = colorsys.hsv_to_rgb(*c) + (self.alpha,)
    self.t_imag.color = q

  def set_source(self, src):
    self.t_imag.source = src

class PongGame(Widget):

    magic_scale_value = Window.height/480.
    print "MAGIC SCALE VALUE IS:",magic_scale_value

    letters_captured = Set([]) # this is for the A-Z achievement

    background_color = ListProperty([1,1,1]) # Doesn't really matter, it's set in __init__

    tiles = ListProperty(None)
    player1 = ObjectProperty(None)

    streak = ListProperty(None)

    alphabet = DictProperty(None)

    score = NumericProperty(0)
    highscore = NumericProperty(0)

    morse_alphabet = DictProperty(None)

    assist = BooleanProperty(False)

    alphabet_points = DictProperty(None)
    alphabet_colors = DictProperty(None)

    blocks_destroyed = NumericProperty(0)

    total_blocks_destroyed = NumericProperty(0) # THIS IS FOR ACHIEVEMENTS

    total_bonuses = ListProperty(None)

    lives = NumericProperty(0)

    widget_reference = ListProperty(None)

    first_spiral = False
    first_freeze = False
    first_brick = False
    first_star = False
    first_life = False
    first_mult = False

    def __init__(self, first_play, **kwargs):
      super(PongGame, self).__init__(**kwargs)

      self.letters_captured = Set([])

      if first_play:
        self.first_spiral = True
        self.first_freeze = True
        self.first_brick = True
        self.first_star = True
        self.first_life = True
        self.first_mult = True

      self.max_velocity = 2 * (Window.height/1080.) # TODO change
      self.MAX_NUM_TILES = 10
      
      self.lives = 3

      self.background_color = (1,0,0)

      self.alphabet_points = dict((i,1) for i in ["E", "T", "A", "M", "I", "N", "S"])
      self.alphabet_points.update(dict((i,2) for i in ["H", "R", "D", "L", "C"]))
      self.alphabet_points.update(dict((i,5) for i in ["U", "O", "W", "F", "G", "Y"]))
      self.alphabet_points.update(dict((i,8) for i in ["P", "B", "V", "K"]))
      self.alphabet_points.update(dict((i,10) for i in ["J", "X", "Q", "Z"]))

      self.alphabet_colors = dict((i,HSV.PINK) for i in ["E", "T", "A", "M", "I", "N", "S"])
      self.alphabet_colors.update(dict((i,HSV.YELLOW) for i in ["H", "R", "D", "L", "C"]))
      self.alphabet_colors.update(dict((i,HSV.BLUE) for i in ["U", "O", "W", "F", "G", "Y"]))
      self.alphabet_colors.update(dict((i,HSV.PURPLE) for i in ["P", "B", "V", "K"]))
      self.alphabet_colors.update(dict((i,HSV.ORANGE) for i in ["J", "X", "Q", "Z"]))

      self.delta_press = 0
      self.delta_pause = 0
      self.time_last_up = 0
      self.down = False

      self.frame_count = 0
      self.freeze_active = False

      self.tick_sound = SoundLoader.load("sounds/tick.ogg")
      self.twinkle_sound = SoundLoader.load("sounds/twinkle.ogg")
      self.brick_sound = SoundLoader.load("sounds/brick.ogg")
      self.error_sound = SoundLoader.load("sounds/error.ogg")
      self.whoosh_sound = SoundLoader.load("sounds/whoosh.ogg")
      self.background_sound = SoundLoader.load("sounds/back.ogg")
      self.beep_sound = SoundLoader.load("sounds/beep.ogg")
      self.background_sound.loop = True 

      self.bind(tiles=self.on_tiles_changed) # tiles refers to self.tiles
      self.bind(assist=self.on_assist_toggle)
      self.bind(lives=self.on_lives_changed)
      self.bind(widget_reference=self.on_widget_reference_changed)

    def on_widget_reference_changed(self, instance, value):
      pass
#     print "Child size: %d" % len(self.children)

    def init_level(self, mode=MODE.SP, firstplay=False):
      self.lives = 3 # initialize lives
      for i in xrange(1, self.lives+1): # set the sources
        getattr(self, 'heart%d' % i).source = 'pngs/heart.png'

      alphabet = {"A":".-", "B":"-...", "C":"-.-.", "D":"-..", "E":".", "F":"..-.",
                             "G":"--.","H":"....", "I":"..", "J":".---", "K":"-.-", "L":".-..",
                             "M":"--", "N":"-.", "O":"---", "P":".--.", "Q":"--.-", "R":".-.",
                             "S":"...", "T":"-", "U":"..-", "V":"...-", "W":".--", "X":"-..-", 
                             "Y":"-.--", "Z":"--.."}

      alph = [chr(x) for x in xrange(65, 91)] # generate list of letters to use with lookup
      self.h_label_left_text = '\n'.join(map(lambda x: "%s %s" % (x, alphabet[x]), alph[:len(alph)/2]))
      self.h_label_right_text = '\n'.join(map(lambda x: "%s %s" % (alphabet[x], x), alph[len(alph)/2:]))

      if mode == MODE.TRAIN_EASY:
        a = dict((i,alphabet[i]) for i in ["E", "T", "A", "M", "I", "N", "S"])
        self.MAX_NUM_TILES = len(a.values())
        self.assist = True
        self.hint.source='pngs/hint_down.png'
      elif mode == MODE.TRAIN_MEDIUM: 
        a = dict((i,alphabet[i]) for i in ["H", "R", "D", "K", "C", "U", "O", "W", "G", "J"])
        self.MAX_NUM_TILES = len(a.values())
        self.assist = True
        self.hint.source='pngs/hint_down.png'
      elif mode == MODE.TRAIN_HARD:
        a = dict((i,alphabet[i]) for i in ["F", "Y", "P", "B", "V", "L", "X", "Q", "Z"])
        self.MAX_NUM_TILES = len(a.values())
        self.assist = True
        self.hint.source='pngs/hint_down.png'
      #elif mode == MODE.MP:
      #  a = alphabet
      #  self.assist = False
      else: # easy
        a = alphabet
        self.assist = False

      self.alphabet = a
      self.morse_alphabet = dict(zip(self.alphabet.values(), self.alphabet.keys()))

      for i in xrange(3): # start with 3
        self.add_tile_to_queue()

      self.background_sound.play()

    # we are not going to do it this way.
    def clear_level(self):

      Clock.unschedule(self.update) # first do this
      self.background_sound.stop()

      for w in self.widget_reference:
        try:
          self.remove_widget(w)
        except:
#         print "ex"
          pass

      self.widget_reference[:] = []

      self.tiles[:] = []

      self.total_bonuses[:] = []

      self.blocks_destroyed = 0
      self.total_blocks_destroyed = 0

      self.freeze_active = False
      self.frame_count = 0

      self.max_velocity = 2 * (Window.height/1080.)
      self.score = 0

      self.letters_captured = Set([])

    def on_lives_changed(self, instance, value):
      pass
#     print "XXX lives now %d" % self.lives

    def add_tile_to_queue(self):
#     print "MAX VEL %f" % self.max_velocity
      if len(self.tiles) == self.MAX_NUM_TILES:
        return 

      # TODO optimize:
      letter = random.sample(set(self.alphabet.keys())-set([t.value for t in self.tiles]), 1)[0]
      t = Tile()
      s = t.size[0] 
      t.center = (random.randint(int(s/2), int(Window.width-(s/2))), Window.height+int((t.size[1])/2.)) # 92 is the width of tiles
      t.value = letter
      t.set_color(self.alphabet_colors[t.value])
      t.t_label.text = Markup.WHITE % t.value
      
      self.add_widget(t)
      self.widget_reference.append(t)
      self.tiles.append(t)

      if self.max_velocity > 4: # Tag
        b = random.sample([True,False,False], 1)[0]
        t.rotation_enabled = b

      if self.freeze_active:
        t.velocity = (0,0)
        t.prev_y = -((self.max_velocity+0.0)/random.randint(1,5))
      else:
        # UPDATE THE SPEED
        t.velocity = (0, 0-((self.max_velocity+0.0)/random.randint(1,5)))

    def update(self, dt):

        self.delta_pause = time() - self.time_last_up

        self.frame_count += 1

        if self.freeze_active and self.frame_count == 1:
          self.tick_sound.play()
          for t in self.tiles:
            if t.velocity_y != 0: # only if its not zero, this is important if multiple freeze bonuses are found
              t.prev_y = t.velocity_y # save
              t.set_color(HSV.CYAN)
            t.velocity_y = 0
        elif self.freeze_active and self.frame_count < 180:
          pass
        elif self.freeze_active and self.frame_count >= 180:
          self.tick_sound.stop()
          self.freeze_active = False
          for t in self.tiles:
            if not t.captured: # else they will move 
              t.velocity_y = t.prev_y # TODO temp
              t.set_color(self.alphabet_colors[t.value])

        if self.delta_pause > 0.50 and len(self.streak) > 0 and self.down == False: # clear streak, too long
          self.beep_sound.stop()
          self.match_tiles()
          self.streak  = []

        for i,t in enumerate(self.tiles):
          t.move()

          if t.x + t.t_imag.size[0] < self.x or t.x - t.t_imag.size[0] > Window.width: # remove widget that we have 'killed'
#           print "Widgets before removing: %d" % len(self.children)
            
            self.remove_widget(t) 
#           print "Widgets after removing: %d" % len(self.children)
            del self.tiles[i]
            self.add_tile_to_queue() # XXX possible fix
            self.blocks_destroyed += 1 # NEEDS MORE CAREFUL THOUGHT
            self.total_blocks_destroyed += 1
        
          if t.y < self.y + self.menu.size[1]: # stop above menu, but not killed/removed TODO not good enough!
            #self.remove_widget(t) # XXX remove if you dont want red tiles at the bottom
            try: 
              from jnius import autoclass
              Hardware = autoclass('org.renpy.android.Hardware')
              Hardware.vibrate(.4) 
            except:
              pass

            if self.lives == 0: # on game over, don't enter the following code
              return

            try: # ew.
              self.error_sound.play()
              getattr(self, 'heart%d' % self.lives).source = 'pngs/empty_heart.png'
#             print "Before decreasing lives: %d" % self.lives
              self.lives -= 1
#             print "Decreasing lives AFTER: %d" % self.lives
              t.velocity_y = 0
              t.set_color(HSV.RED)
              del self.tiles[i]
              self.add_tile_to_queue() # TODO check if re-adding is ok
            except:
              pass

    def on_assist_toggle(self, instance, value):
      if value == True:
        self.h_label_left.text = self.h_label_left_text
        self.h_label_right.text = self.h_label_right_text
      else:
        self.h_label_left.text = ""
        self.h_label_right.text = ""

    def on_tiles_changed(self, instance, value):
      pass
#     print "ZZZ Tiles is %d but lives is %d" % (len(value), self.lives)

    def do_spiral_bonus(self):
      for i,t in enumerate(self.tiles):
        if t.captured == False:
          if t.bonus == BONUS.STAR:
            self.twinkle_sound.play()
            self.score += self.alphabet_points[t.value]*10*10 # x10 points, but let's change this
          elif t.bonus == BONUS.MULT3:
            self.score += self.alphabet_points[t.value]*10*3
          elif t.bonus == BONUS.MULT5:
            self.score += self.alphabet_points[t.value]*10*5
          else:
            self.score += self.alphabet_points[t.value]*10

          t.set_color(HSV.GREEN)
          t_prev_y = 0
          direction = random.sample([1,-1], 1)[0]
          t.velocity = (7*direction, 0)
          t.captured = True

      self.whoosh_sound.play()
        
    def match_tiles(self):
      try:
        if ''.join(self.streak) == '...---...': # SOS achievement
          app.gs_unlock(achievement_sos)

        v = self.morse_alphabet[''.join(self.streak)] # convert morse to letter
      except:
        return

      for i,t in enumerate(self.tiles):
        if t.value == v and t.captured == False:
#         print "Taking out %s" % v

          self.letters_captured.add(v)

#         Logger.debug('Alphabet set: %s' % self.letters_captured)
          if len(self.letters_captured) == 26:
            app.gs_unlock(achievement_az)


          if t.bonus == BONUS.SPIRAL:
            if self.first_spiral:
              app.gs_unlock(achievement_spiral)
              self.popup("Your first Spiral! It clears the screen of all tiles (and gives lots of points)", "achievement_sprites/pngs/spiral.png")
              self.first_spiral = False

            self.total_bonuses.append('sp')
            self.do_spiral_bonus()
            break

          if t.bonus == BONUS.HEX:
            if self.first_freeze:
              app.gs_unlock(achievement_snow)
              self.popup("Your first Freeze! \n It freezes all the tiles for a few seconds", "achievement_sprites/pngs/snowflake.png")
              self.first_freeze = False

            self.freeze_active = True
            self.frame_count = 0
            self.total_bonuses.append('sn')

          if t.bonus == BONUS.SQUARE:
            if self.first_brick:
              app.gs_unlock(achievement_red_square)
              self.popup("Your first Brick! \n You have to enter this one's code twice :(", "achievement_sprites/pngs/red_square.png")
              self.first_brick = False

            self.brick_sound.play()
            if t.resist == 1:
              t.set_source('pngs/5.png') # harder to break
              t.resist -= 1
              return 

            self.total_bonuses.append('b')

          if t.bonus == BONUS.STAR:
            if self.first_star:
              app.gs_unlock(achievement_star)
              self.popup("Your first Star! \n It multiplies the tile's value by 10", "achievement_sprites/pngs/star.png")
              self.first_star = False

            self.twinkle_sound.play()
            self.total_bonuses.append('st')
            self.score += self.alphabet_points[t.value]*10*10 # x10 points, but let's change this
          elif t.bonus == BONUS.LIFE:
            if self.first_life:
              app.gs_unlock(achievement_heart)
              self.popup("Your first Heart! \n It gives you an extra life, to a maximum of 10 lives", "achievement_sprites/pngs/heart.png")
              self.first_life = False
          
            if self.lives != self.MAX_NUM_TILES:
              try: 
                from jnius import autoclass
                Hardware = autoclass('org.renpy.android.Hardware')
                Hardware.vibrate(.2) # TODO burst?
              except:
                pass
              self.blocks_destroyed = 0 # reset this, otherwise too many lives
              self.add_tile_to_queue() # introduce a new tile XXX WHY
              self.lives += 1
              getattr(self, 'heart%d' % self.lives).source = 'pngs/heart.png'
              self.total_bonuses.append('h')
          elif t.bonus == BONUS.MULT3:
            if self.first_mult:
              self.popup("Your first Multiplier! \n It multiplies the tile's value by 3",
                  "pngs/mult_3.png")
              self.first_mult = False

            self.score += self.alphabet_points[t.value]*10*3
          elif t.bonus == BONUS.MULT5:
            if self.first_mult:
              self.popup("Your first Multiplier! \n It multiplies the tile's value by 5",
                  "pngs/mult_5.png")
              self.first_mult = False

            self.score += self.alphabet_points[t.value]*10*5
          elif t.bonus == BONUS.CLOVER:
            app.gs_unlock(achievement_clover)
          else:
            self.score += self.alphabet_points[t.value]*10

          t.captured = True
          t.set_color(HSV.GREEN)
          t.prev_y = 0 # set it to 0 so that we don't move it down if it was caught in a freeze and then resumed
          direction = random.sample([1,-1], 1)[0]
          t.velocity = (7*direction*(Window.height/1080.), 0)
          self.whoosh_sound.play()

          return # take the first one, not necessarily the one lowest to the bottom

    def popup(self, msg, icon):
      # pause
      Clock.unschedule(self.update)

      popup = FirstTimePopup()
      popup.image.source = icon
      popup.label.text = msg # "Your first Spiral! It clears the screen of all tiles (and gives lot's of points)"

      def resume(x): 
#       print x
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        return False

      popup.bind(on_dismiss=resume)
      popup.open()

    
    def on_touch_down(self, touch):
        
      if touch.y > 50*self.magic_scale_value:
        self.background_color = HSV.GRAY

        self.down = True 
        self.delta_press = time()
        self.beep_sound.play()

      if self.lightning.collide_point(*touch.pos):
        self.lightning.source='pngs/lightning_down.png'
      
      if self.hint.collide_point(*touch.pos):
        if self.assist == True:
          self.assist = False
          self.hint.source='pngs/hint.png'
        else:
          self.hint.source='pngs/hint_down.png'
          self.assist = True

    def on_touch_up(self, touch):
      self.beep_sound.stop()
      if touch.y > 50*self.magic_scale_value:
        self.delta_press = time() - self.delta_press

        if self.delta_press <= 0.15:
          self.streak.append(".")
        else:
          self.streak.append("-")

        self.down = False
        self.delta_pause = time()
        self.time_last_up = time()
      
        self.background_color = HSV.BLACK

      if self.lightning.collide_point(*touch.pos):
        self.match_tiles()
        self.streak  = []

      self.lightning.source='pngs/lightning.png'

class TrainingScreen(Screen):
  def __init__(self, **kwargs):
    super(TrainingScreen, self).__init__(**kwargs)

    self.box_layout = BoxLayout(orientation='vertical', spacing=10)

    bs = (.21, None)
    ps = {'center_x':0.5}

    self.title = Image(source='pngs/training_alphabets.png', size_hint=(.7,None), pos_hint=ps, allow_stretch=True)

    self.easy_button = Image(source='pngs/easy.png', size_hint=bs, pos_hint=ps)
    self.medium_button = Image(source='pngs/medium.png', size_hint=bs, pos_hint=ps)
    self.hard_button = Image(source='pngs/hard.png', size_hint=bs, pos_hint=ps)
    self.back_button = Image(source='pngs/back.png', size_hint=bs, pos_hint=ps)

    self.box_layout.add_widget(Label())
    self.box_layout.add_widget(self.title)
    self.box_layout.add_widget(Label())
    self.box_layout.add_widget(self.easy_button)
    self.box_layout.add_widget(self.medium_button)
    self.box_layout.add_widget(self.hard_button)
    self.box_layout.add_widget(self.back_button)
    self.box_layout.add_widget(Label())

    self.add_widget(self.box_layout)

  def on_touch_down(self, touch):
    if self.easy_button.collide_point(*touch.pos):
      self.easy_button.source='pngs/easy_down.png' 
    elif self.medium_button.collide_point(*touch.pos):
      self.medium_button.source='pngs/medium_down.png'
    elif self.hard_button.collide_point(*touch.pos):
      self.hard_button.source='pngs/hard_down.png'
    elif self.back_button.collide_point(*touch.pos):
      self.back_button.source='pngs/back_down.png'

  def on_touch_up(self, touch):
    if self.easy_button.collide_point(*touch.pos):
      self.manager.get_screen("game").init_level(MODE.TRAIN_EASY)
      self.manager.get_screen("game").start_game() 
    elif self.medium_button.collide_point(*touch.pos):
      self.manager.get_screen("game").init_level(MODE.TRAIN_MEDIUM)
      self.manager.get_screen("game").start_game() 
    elif self.hard_button.collide_point(*touch.pos):
      self.manager.get_screen("game").init_level(MODE.TRAIN_HARD)
      self.manager.get_screen("game").start_game() 
    elif self.back_button.collide_point(*touch.pos):
      self.manager.current = "title"

    self.easy_button.source='pngs/easy.png'
    self.medium_button.source='pngs/medium.png'
    self.hard_button.source='pngs/hard.png'
    self.back_button.source='pngs/back.png'

class ContinueScreen(Screen):
  def __init__(self, **kwargs):
    super(ContinueScreen, self).__init__(**kwargs)

    self.box_layout = BoxLayout(orientation='vertical', spacing=0)

    bs = (.5, 1)
    ps = {'center_x':0.5}

    self.continue_button = Image(source='pngs/continue_button.png', size_hint=bs, pos_hint=ps, allow_stretch=True)
    self.quit_button = Image(source='pngs/main_menu.png', size_hint=bs, pos_hint=ps, allow_stretch=True)

    self.label_top = Label()
    self.label_bottom = Label(markup=True)
    self.label_bottom.font_size=28 * Window.height/580 # TODO not good enough
    self.label_bottom.font_name='fonts/Kavoon-Regular.ttf'

    self.box_layout.add_widget(self.label_top)
    self.box_layout.add_widget(self.continue_button)
    self.box_layout.add_widget(self.label_bottom)
    self.box_layout.add_widget(self.quit_button)
    self.box_layout.add_widget(Label())

    self.add_widget(self.box_layout)

  def on_touch_down(self, touch):
    if self.quit_button.collide_point(*touch.pos): # quit to main menu
      self.quit_button.source='pngs/main_menu_down.png'
    elif self.continue_button.collide_point(*touch.pos) and self.continue_button.source == 'pngs/continue_button.png': # cheap way to check its not the 'button'
      self.continue_button.source='pngs/continue_button_down.png'

  def on_touch_up(self, touch):
    if self.quit_button.collide_point(*touch.pos): # quit to main menu
      self.manager.current = "title" # TODO confirmation box?
      self.manager.get_screen("title").resume_animation()
      self.manager.get_screen("game").pong_game.clear_level() 
    elif self.continue_button.collide_point(*touch.pos) and self.continue_button.source == 'pngs/continue_button_down.png':
      self.manager.get_screen("game").resume_game()

    if self.continue_button.source == 'pngs/continue_button_down.png':
      self.continue_button.source='pngs/continue_button.png'

    self.quit_button.source='pngs/main_menu.png'

class GameOverScreen(Screen):
  def __init__(self, **kwargs):
    super(GameOverScreen, self).__init__(**kwargs)

    self.box_layout = BoxLayout(orientation='vertical', spacing=0)

    bs = (.5, 1)
    ps = {'center_x':0.5}

    self.continue_button = Image(source='pngs/game_over.png', size_hint=bs, pos_hint=ps, allow_stretch=True)
    self.quit_button = Image(source='pngs/main_menu.png', size_hint=bs, pos_hint=ps, allow_stretch=True)

    self.label_top = Label()
    self.label_bottom = Label(markup=True)
    self.label_bottom.font_size=36 * Window.height/480 # TODO not good enough
    self.label_bottom.font_name='fonts/Kavoon-Regular.ttf'

    self.box_layout.add_widget(self.label_top)
    self.box_layout.add_widget(self.continue_button)
    self.box_layout.add_widget(self.label_bottom)
    self.box_layout.add_widget(self.quit_button)
    self.box_layout.add_widget(Label())

    self.add_widget(self.box_layout)

  def do_end_game_achievements(self):
      pg = self.manager.get_screen("game").pong_game

      self.label_bottom.text = "Score: %s" % pg.score

      v = pg.total_blocks_destroyed
      if v > 0:
        app.gs_increment(achievement_100_tiles, v)
        app.gs_increment(achievement_250_tiles, v)
        app.gs_increment(achievement_500_tiles, v)
        app.gs_increment(achievement_1000_tiles, v)
        app.gs_increment(achievement_5000_tiles, v)
        app.gs_increment(achievement_10000_tiles, v)

      l = pg.total_bonuses
      if len(l) > 0:
        app.gs_increment(achievement_multipass, len(l))

        if l.count('h') > 0:
          app.gs_increment(achievement_multiheart, l.count('h'))
        if l.count('sn') > 0:
          app.gs_increment(achievement_multisnow, l.count('sn'))
        if l.count('b') > 0:
          app.gs_increment(achievement_multibrick, l.count('b'))
        if l.count('sp') > 0:
          app.gs_increment(achievement_multispiral, l.count('sp'))
        if l.count('st') > 0:
          app.gs_increment(achievement_multistar, l.count('st'))

      app.gs_score(pg.score)

      if pg.score == 0:
        app.gs_unlock(achievement_void)
      if pg.score > 5000:
        app.gs_unlock(achievement_5k)
      if pg.score > 10000:
        app.gs_unlock(achievement_10k)
      if pg.score > 12000:
        app.gs_unlock(achievement_12k)
      if pg.score > 15000:
        app.gs_unlock(achievement_15k)

  def on_touch_down(self, touch):
    if self.quit_button.collide_point(*touch.pos): # quit to main menu
      self.quit_button.source='pngs/main_menu_down.png'

  def on_touch_up(self, touch):
    if self.quit_button.collide_point(*touch.pos): # quit to main menu
      self.manager.current = "title" # TODO confirmation box?
      self.manager.get_screen("title").resume_animation()
      self.manager.get_screen("game").pong_game.clear_level() 

    self.quit_button.source='pngs/main_menu.png'


class TitleScreen(Screen):
  def __init__(self, **kwargs):
    super(TitleScreen, self).__init__(**kwargs) 

    self.box_layout = BoxLayout(orientation='vertical', spacing=10, padding=15)

    bs = (.3,.3)
    ps = {'center_x':0.5}

    self.title = Image(source='pngs/title.png', size_hint=(.5,.5), pos_hint=ps, allow_stretch=True)

    self.sp_button = Image(source='pngs/sp.png', size_hint=(.9,1), allow_stretch=True)

    self.mp_button = Image(source='pngs/mp.png', size_hint=bs, pos_hint=ps)

    self.training_button = Image(source='pngs/training.png', size_hint=bs, pos_hint=ps, allow_stretch=True)
    self.leaderboard_button = Image(source='pngs/leaderboard.png', size_hint=(.9,1), allow_stretch=True) #, size_hint=bs, pos_hint=ps)
    self.achievements_button = Image(source='pngs/achievements.png', size_hint=(.9,1), allow_stretch=True) #, size_hint=bs, pos_hint=ps)
    self.instructions_button = Image(source='pngs/instructions_button.png', size_hint=bs, pos_hint=ps, allow_stretch=True)
    self.quit_button = Image(source='pngs/quit.png', size_hint=bs, pos_hint=ps, allow_stretch=True)

    self.box_layout.add_widget(self.title)

    # use 60% width to fit in the 3 things.
    self.play_services_layout = BoxLayout(orientation='horizontal', spacing=0, padding=0, size_hint=(.9,.3), pos_hint=ps)#pos_hint=ps, ) #size_hint=bs) #, size_hint=bs, pos_hint=ps)

    self.play_services_layout.add_widget(self.leaderboard_button)
    self.play_services_layout.add_widget(self.sp_button)
    self.play_services_layout.add_widget(self.achievements_button)
    self.box_layout.add_widget(self.play_services_layout)

#   self.box_layout.add_widget(self.sp_button)
    #self.box_layout.add_widget(self.mp_button)
    self.box_layout.add_widget(self.training_button)

    self.box_layout.add_widget(self.instructions_button)
    self.box_layout.add_widget(self.quit_button)
#   self.box_layout.add_widget(Label()) # put this in so it puts the rest at the top

    self.pieces = []
    for i in xrange(6):
      p = Piece()
      p.im.source = "pngs/piece%d.png" % (i % 5)
      self.pieces.append(p)
      self.add_widget(p)

    self.add_widget(self.box_layout) # put the animation objects behind the menu

    self.resume_animation()

  def pause_animation(self):
    Clock.unschedule(self.update)

  def resume_animation(self):
    Clock.schedule_interval(self.update, 1.0 / 60.0)

  def update(self, dt):
    for p in self.pieces:
      p.move()

  def on_touch_down(self, touch):

    if self.sp_button.collide_point(*touch.pos):
      self.sp_button.source='pngs/sp_down.png'
    elif self.mp_button.collide_point(*touch.pos):
      self.mp_button.source='pngs/mp_down.png'
    elif self.training_button.collide_point(*touch.pos):
      self.training_button.source='pngs/training_down.png'
    elif self.leaderboard_button.collide_point(*touch.pos):
      self.leaderboard_button.source = 'pngs/leaderboard_down.png'
    elif self.achievements_button.collide_point(*touch.pos):
      self.achievements_button.source = 'pngs/achievements_down.png'
    elif self.instructions_button.collide_point(*touch.pos):
      self.instructions_button.source = 'pngs/instructions_button_down.png'
    elif self.quit_button.collide_point(*touch.pos):
      self.quit_button.source='pngs/quit_down.png'

  def on_touch_up(self, touch):

    if self.sp_button.collide_point(*touch.pos):
      self.manager.get_screen("game").init_level() # default is sp
      self.manager.get_screen("game").start_game() 
    #elif self.mp_button.collide_point(*touch.pos):
    #  self.manager.get_screen("game").init_level(MODE.MP)
    #  self.manager.get_screen("game").start_game() 
    elif self.training_button.collide_point(*touch.pos):
      self.manager.current = 'training' 
    elif self.leaderboard_button.collide_point(*touch.pos):
      app.gs_show_leaderboard()
    elif self.achievements_button.collide_point(*touch.pos):
      app.gs_show_achievements()
    elif self.instructions_button.collide_point(*touch.pos):
      self.manager.current = 'instructions'
    elif self.quit_button.collide_point(*touch.pos):
      App.get_running_app().stop()

    self.sp_button.source='pngs/sp.png'
    self.mp_button.source='pngs/mp.png'
    self.training_button.source='pngs/training.png'
    self.leaderboard_button.source='pngs/leaderboard.png'
    self.achievements_button.source='pngs/achievements.png'
    self.instructions_button.source='pngs/instructions_button.png'
    self.quit_button.source='pngs/quit.png'

class InstructionsScreen(Screen):
  def __init__(self, **kwargs):
    super(InstructionsScreen, self).__init__(**kwargs)
    self.layout = BoxLayout()
    self.im = Image(source='pngs/instructions.png', allow_stretch=True)
    self.layout.add_widget(self.im)
    self.add_widget(self.layout)

class GameScreen(Screen):
  def __init__(self, **kwargs):
    super(GameScreen, self).__init__(**kwargs)

    try:
      f = open("%s/firstplay.dat" % os.getcwd(), "r")
      first_play = False
    except:
      f = open("%s/firstplay.dat" % os.getcwd(), "w+")
      f.write("1")
      first_play = True

    f.close()

    self.pong_game = PongGame(first_play)
    self.add_widget(self.pong_game)

    self.pong_game.bind(blocks_destroyed=self.on_blocks_destroyed)
    self.pong_game.bind(lives=self.on_lives_changed)

  def init_level(self, mode=MODE.SP):

    try:
      f = open("%s/m.dat" % os.getcwd(), "r")
      self.pong_game.highscore = int(f.readlines()[0])
    except: 
#     print "FAILED TO OPEN"
      f = open("%s/m.dat" % os.getcwd(), "w+") # write 0 if not exists
      f.write("0")
      self.pong_game.highscore = 0

    f.close()
   
    self.pong_game.init_level(mode)

  def on_blocks_destroyed(self, instance, value): # value is the score, instance is the game

      if self.pong_game.total_blocks_destroyed > 15: # achievement counter
        v = self.pong_game.total_blocks_destroyed
        app.gs_increment(achievement_100_tiles, v)
        app.gs_increment(achievement_250_tiles, v)
        app.gs_increment(achievement_500_tiles, v)
        app.gs_increment(achievement_1000_tiles, v)
        app.gs_increment(achievement_5000_tiles, v)
        app.gs_increment(achievement_10000_tiles, v)
        self.pong_game.total_blocks_destroyed = 0

      if self.pong_game.total_blocks_destroyed > 25:
        l = self.pong_game.total_bonuses

        if len(l) > 0:
          app.gs_increment(achievement_multipass, len(l))

          if l.count('h') > 0:
            app.gs_increment(achievement_multiheart, l.count('h')) # error
          if l.count('sn') > 0:
            app.gs_increment(achievement_multisnow, l.count('sn'))
          if l.count('b') > 0:
            app.gs_increment(achievement_multibrick, l.count('b'))
          if l.count('sp') > 0:
            app.gs_increment(achievement_multispiral, l.count('sp'))
          if l.count('st') > 0:
            app.gs_increment(achievement_multistar, l.count('st'))
          self.pong_game.total_bonuses[:] = []

      # value is blocks_destroyed
      if value == 5: #TODO remember this also needs to be checked to return false to the Clock
        if self.pong_game.lives != self.pong_game.MAX_NUM_TILES:
          self.pong_game.lives += 1
          getattr(self.pong_game, 'heart%d' % self.pong_game.lives).source = 'pngs/heart.png'

        if len(self.pong_game.tiles) != self.pong_game.MAX_NUM_TILES:
          self.pong_game.add_tile_to_queue() # only add up to max tiles (10)
           
        self.pong_game.max_velocity += .4 * self.pong_game.magic_scale_value # TODO not good enough
        self.pong_game.blocks_destroyed = 0

  def on_lives_changed(self, instance, value):
    if value == 0:
      # GAME OVER
      # send block achievements

      self.manager.current = "gameover"
      self.manager.get_screen("gameover").do_end_game_achievements()
      self.manager.get_screen("game").pong_game.clear_level() # have to do this so we pause animation and all

  def pause_game(self):
    Clock.unschedule(self.pong_game.update)
    self.manager.current = "continue"

  def resume_game(self):
    self.manager.current = "game"
    Clock.schedule_interval(self.pong_game.update, 1.0 / 40.0)

  def start_game(self):
    self.manager.get_screen("title").pause_animation()
    self.manager.current = "game"
    Clock.schedule_interval(self.pong_game.update, 1.0 / 40.0)

# root is a screen manager, not a widget
class PongApp(App):
    use_kivy_settings = False #??

    def build_config(self, config):
      if platform == 'android':
        config.setdefaults('play', {'use_google_play': '0'})

    def build(self):
        global app
        app = self

        if platform == 'android':
          self.use_google_play = self.config.getint('play', 'use_google_play')
          if self.use_google_play:
            gs_android.setup(self)
          else:
            Clock.schedule_once(self.ask_google_play, .5)
        else:
           pass

        self.root = game = ScreenManager(transition=FadeTransition())

        self.title_screen = TitleScreen(name="title")
        self.game_screen = GameScreen(name="game")
        self.continue_screen = ContinueScreen(name="continue")
        self.gameover_screen = GameOverScreen(name="gameover")
        self.training_screen = TrainingScreen(name="training")
        self.instructions_screen = InstructionsScreen(name="instructions")

        self.root.add_widget(self.title_screen)
        self.root.add_widget(self.gameover_screen)
        self.root.add_widget(self.training_screen)
        self.root.add_widget(self.continue_screen)
        self.root.add_widget(self.instructions_screen)
        self.root.add_widget(self.game_screen) # order significant

        from kivy.base import EventLoop
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)

        return game

    def gs_score(self, score):
      if platform == 'android':
        if self.use_google_play:
          gs_android.leaderboard(leaderboard_highscore, score)

    def gs_show_leaderboard(self):
      if platform == 'android':
        if self.use_google_play:
          gs_android.show_leaderboard(leaderboard_highscore)

    def gs_show_achievements(self):
      if platform == 'android':
        if self.use_google_play:
          gs_android.show_achievements()

    def gs_unlock(self, uid):
      if platform == 'android' and self.use_google_play:
        gs_android.unlock(uid)

    def gs_increment(self, uid, count):
      if platform == 'android' and self.use_google_play:
        gs_android.increment(uid, count)

    def ask_google_play(self, *args):
      popup = GooglePlayPopup()
      popup.open()

    def activate_google_play(self):
      self.config.set('play', 'use_google_play', '1')
      self.config.write()
      self.use_google_play = 1
      gs_android.setup(self)

    # TODO check current screen
    def on_pause(self):
      if self.root.current == "game":
        self.game_screen.pause_game()
      if platform == 'android':
        gs_android.on_stop()
      return True

    def on_resume(self):
      if platform == 'android':
        gs_android.on_start()

    def hook_keyboard(self, window, key, *largs):
      if key == 27:
        if self.root.current == "title":
          pass # Exit, don't stay where you are
        if self.root.current == "game":
          self.game_screen.pause_game()
          return True
        if self.root.current == "training": 
          self.root.current = "title"
          return True # stay where you are
        if self.root.current == "gameover":
          return True # just stay where you are
        if self.root.current == "continue":
          return True # stay where you are
        if self.root.current == "instructions":
          self.root.current = "title"
          return True

      if key == 319: # don't do anything on menu key
        return True
  
if __name__ == '__main__':
    import sys
#   print "ENCODING %s" % sys.getdefaultencoding()
    PongApp().run()
