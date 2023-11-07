import screennorm
import keyboardcb
import keyleds
import joystick
import asyncio
import gc9a01
import vectoros
import vos_debug
from vos_state import vos_state



screen=vectoros.get_screen()

BACK=-1
EXIT=1
CONT=0

SUBMENU=[]

def m_back(arg):
    return BACK

def m_exit(arg):
    return EXIT

class Menu:
    """
    A class that manages a menu.

    Attributes:
        fg (int): The foreground color.
        bg (int): The background color.
        clear_after (bool): A flag to indicate if the menu should be cleared after exit.
        joycontroller (Joystick): The joystick controller.
        scanrate (int): The scan rate.
        cursor (int): The position of the screen cursor.
        dispmenu (int): The top line of the display.
        current (list): The current menu string.
        level (int): The current level in the submenus.
        stack (list): The stack of how we got here.
        clear_after (bool): A flag to indicate if the menu should be cleared after exit.
        fg (int): The foreground color.
        bg (int): The background color.
        update_callback (function): A function to call to update the menu in real time.
    """
    
    def __init__(self, fg_color=gc9a01.color565(45, 217, 80), bg_color=gc9a01.color565(0, 0, 0),cursor_fg=gc9a01.color565(120,247,180),
                 cursor_bg=None,clear_after=False, joy_controller=None, scan_rate=0):
        """
        The constructor for Menu class.

        Args:
            fg_color (int): The foreground color. Default is gc9a01.color565(243,191,16).
            bg_color (int): The background color. Default is gc9a01.color565(26,26,26).
            clear_after (bool): A flag to indicate if the menu should be cleared after exit. Default is False.
            joycontroller (Joystick): The joystick controller. Default is None.
            scanrate (int): The scan rate. Default is 0.
        """
        
        if joy_controller != None:
            self.joy=joy_controller
            self._extjoy=True
        else:
            self.joy=None
            self._extjoy=False
        
        if scan_rate!=0:
            joystick.Joystick.run(scan_rate)     
            
        self.cursor=0         
        self.dispmenu=0       
        self.current=[]       
        self.level=0          
        self.stack=[]         
        self.clear_after=clear_after   
        self.fg=fg_color            
        self.bg=bg_color
        if cursor_fg==None:
            self.cfg=self.bg
        else:
            self.cfg=cursor_fg
        if cursor_bg==None:
            self.cbg=self.fg
        else:
            self.cbg=cursor_bg
        self.update_callback=None
        self.font=None
        self.scale=1.0

    def __enter__(self):
        return self
    
    def __exit__(self,exc_type,exc_val,exc_tb):
        if self.joy!=None:
            self.joy.detach()

    def detach(self):
        """
        Method to detach the joystick from the menu.
        
         Returns:
            Task: The created task.
         """
        
        self.joy.detach()
        
    def set_font(self,font,scale=1.0):
        """
        Method to set a font and scale factor.
        Default: use default font (set to None)
        "*": use default vector font (romans)
        Or you can load a vector font and pass it
        
        Args:
            font (font or string or None): See above
            scale (float): Text scale (defaults to 1.0)
        """
        if font=="*":
            self.font=screen.get_vfont()
        else:
            self.font=font
        self.scale=scale
        
    async def menu_custom(self):
        """
        Method you can override to customize the menu in real time
        Or, if you don't want to subclass, you can use set_callback
        and the default will call that
        """
        
        if self.update_callback!=None:
            try:
                await self.update_callback(self)
            except TypeError:
                pass
                

    def set_callback(self,func):
         """
         Method to set a callback function.

         Args:
             func (function): The function to set as the callback.
         """
         
         self.update_callback=func
         

    async def menu_update(self):
         """
         Method to update the menu with cursor, scrolling, etc.

         This method updates the menu based on the current state of the cursor and calls the custom update function if it is set.
         """
         
         screen.clear(self.bg)
         await self.menu_custom()
         
         for i in range(0,min(4,len(self.current))):
             if i==self.cursor:
                 xfg=self.cfg
                 xbg=self.cbg
             else:
                 xfg=self.fg
                 xbg=self.bg
             
             # screen.tft.fill_rect(24,40*(i+1),195,40,xbg)
             if self.font==None:
                 screen.text(24,40*(i+1),self.current[self.dispmenu+i][0],xfg,xbg)
             else:
                 screen.text_font(self.font,24,40*(i+1)+20,self.current[self.dispmenu+i][0],xfg,self.scale)





# the controller callback for the keyboard
# all the real work happens here
    async def _menu_control(self,key):
        """
        Method to handle joystick events.

        This method updates the menu based on the joystick event. It can move the cursor, select a menu item, 
        go to a submenu, or exit the menu.

        Args:
            key (int): The keycode of the joystick event.
        """
        rv=0 
        if self.level<=0:
            return                # no menu
        if key==keyleds.JOY_UP:
            if self.cursor>0:
                self.cursor=self.cursor-1
            else:
                if self.dispmenu>0:
                    self.dispmenu=self.dispmenu-1
            await self.menu_update()
            
        if key==keyleds.JOY_DN:
            if self.cursor<min(3,len(self.current)-1):
                self.cursor=self.cursor+1
            else:
                if self.dispmenu<len(self.current)-4:  
                    self.dispmenu=self.dispmenu+1
            await self.menu_update()
            
        if key==keyleds.JOY_PRESS or key==keyleds.JOY_RT:
            
            cmd=self.current[self.cursor+self.dispmenu][1]
            arg=self.current[self.cursor+self.dispmenu][2]
            if cmd==None:   # replace with ret val from built-in callback
                rv=-1
            elif cmd==[]:
                self.stack.append(self.current)
                self.current=arg
                self.cursor=0
                self.dispmenu=0
                self.level=self.level+1
            else:
                if len(self.current[self.cursor+self.dispmenu])<4:
                    rv=self.current[self.cursor+self.dispmenu][1](self.current[self.cursor+self.dispmenu][2])
                else:
                    rv=await self.current[self.cursor+self.dispmenu][1](self.current[self.cursor+self.dispmenu][2])
                if rv==1:
                    self.stack=[]
                    rv=-1   # make sure we exit
            await self.menu_update()

        if key==keyleds.JOY_LT or rv==-1:
            self.level=self.level-1
            
            if self.stack==[]:
                self.level=-1
                self.current=None
            else:
                self.current=self.stack.pop()
                self.cursor=0
                self.dispmenu=0
                await self.menu_update()


# This is how you kick off the menu. The menu list is a list
# with a sublist for each entry. The sublists have three items:
# A text string, a function, and an argument
# Pro tip: pass a single list, tuple, etc as an argument and you can pass as much as you want
    async def do_menu(self,menulist):
        """
        Method to start the menu.

        This method starts the menu and runs a loop until the level is less than 0. It also updates the menu after each event.

        Args:
            menulist (list): The list of menu items. Each item is a sublist with three items: a text string, a function, and an argument.
        """
        
        if self._extjoy==False:
            self.joy=joystick.Joystick(self._menu_control,True)
        
        self.current=menulist
        self.stack=[]
        self.dispmenu=0
        self.cursor=0
        self.level=1
        
        screen.clear()
        await self.menu_update()
        
        while self.level>=0:
            await asyncio.sleep(0)
        
        if self.clear_after:
            screen.clear()
        
        if (self._extjoy):
            self.joy.detach()

            
# launch a tag (global, use in menus)
def launch(tag):
    vos_state.show_menu=False     # get the menu of the way
    vectoros.launch_task(tag)
    return EXIT
        
