from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '500')
from kivy.app import App
# kivy.require("1.8.0")
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color, Rectangle
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from PIL import Image
import sympy as sp
import pytesseract
import re
import alignedtextinput
import multiexpressionbutton

top_passed_num = ''
bot_passed_num = ''
"""
MainWindow
---ScreenSelector
---MainMenu
"""


class MainWindow(GridLayout):
    """This class has is the main body of the app. It is made up of the screens that switch and the drop-down menu."""
    def __init__(self, **kwargs):
        """Constructor method, has screen manager and menu. The menu will be stationary, but screens switch according
        to selection made in menu."""
        super(MainWindow, self).__init__(**kwargs)
        self.cols = 1
        self.rows = 2
        self.calc_type_selection = ScreenSelector()
        self.calc_type_menu = MainMenu(screen_manager=self.calc_type_selection, text='Basic', font_size='40sp',
                                       size_hint=(1, 0.15), background_color=(0.5, 0.7, 0.8, 1))
        self.add_widget(self.calc_type_selection)
        self.add_widget(self.calc_type_menu)


class ScreenSelector(ScreenManager):
    """Class for handling the three main screens."""
    def __init__(self, **kwargs):
        super(ScreenSelector, self).__init__(**kwargs)
        self.transition = FadeTransition(duration=0.5)
        basic_input_screen = BasicInputScreen()    # Loads basic input screen into screen manager.
        self.add_widget(basic_input_screen)

        math_char_input_screen = MathCharInputScreen()  # Loads math OCR screen into screen manager.
        self.add_widget(math_char_input_screen)

        self.current = 'basic_input'


class MainMenu(Button):
    """Class to establish menu for all screens"""
    screen_manager = ObjectProperty()    # Gives ability to access instantiated object outside of class by adding kwarg

    def __init__(self, **kwargs):
        super(MainMenu, self).__init__(**kwargs)
        self.drop_list = DropDown()
        types = ['Basic', 'Write']    # We have two main screens. May need to add a 'Graph' and 'Equations' screen.
        for i in types:
            button = Button(text=i, font_size="40sp", size_hint_y=None, height="60sp",
                            background_color=(0.6, 0.8, 0.9, 1))
            button.bind(on_release=lambda btn: self.drop_list.select(btn.text))
            self.drop_list.add_widget(button)
        self.bind(on_release=self.drop_list.open)
        self.drop_list.bind(on_select=lambda instance, x: setattr(self, 'text', x))
        self.drop_list.bind(on_select=self.menu_selection)

    def menu_selection(self, instance, x):
        """Drop-list selection changes to one of three screens"""
        if x == 'Basic':
            self.screen_manager.current = 'basic_input'
        elif x == 'Write':
            self.screen_manager.current = 'written_input'


"""
BasicInputScreen
---BasicInputLayout
"""


class BasicInputScreen(Screen):
    """#1: Creates basic calculator screen."""
    def __init__(self, **kwargs):
        super(BasicInputScreen, self).__init__(**kwargs)
        self.name = 'basic_input'
        default = BasicInputLayout()
        self.bind(on_pre_enter=lambda x: default.update_display())
        self.add_widget(default)


class BasicInputLayout(GridLayout):
    """Class to provide grid for keypad and numerical display"""
    def __init__(self, **kwargs):
        super(BasicInputLayout, self).__init__(**kwargs)

        self.operated_state = False
        self.cols = 1
        self.rows = 3
        self.top_basic_eq_display = alignedtextinput.AlignedTextInput(font_size=24, size_hint=(1, 0.15), halign='right',
                                                                      valign='bottom',
                                                                      foreground_color=(0.25, 0.25, 0.25, 1))
        self.add_widget(self.top_basic_eq_display)
        self.bot_basic_eq_display = alignedtextinput.AlignedTextInput(font_size=30, size_hint=(1, 0.15), halign='right',
                                                                      valign='bottom')
        self.add_widget(self.bot_basic_eq_display)

        self.keypad = GridLayout(cols=4, rows=6)
        self.canvas.before.add(Color(0.65, 0.7, 0.7))   # Light slate blue
        self.canvas.before.add(Rectangle(pos=self.pos, size=(5000, 5000)))
        self.keypad.spacing = [2, 2]
        button_symbols = [(str(U'\u0025'), 0), (str(U'\u221a'), 0), ('x' + str(U'\u00b2'), 0), (str(U'\u00b9') + '/x', 0),
                          ('CE', 0), ('C', 0), (str(U'\u21e6'), 0), (str(U'\u00f7'), 1),
                          ('7', 2), ('8', 2), ('9', 2), (str(U'\u00d7'), 1),
                          ('4', 2), ('5', 2), ('6', 2), ('-', 1),
                          ('1', 2), ('2', 2), ('3', 2), ('+', 1),
                          (str(U'\u00b1'), 2), ('0', 2), ('.', 2), ('=', 1)]
        for button_symbol in button_symbols:
            keypad_button = multiexpressionbutton.MultiExpressionButton(text=button_symbol[0], font_name='L_10646',
                                                                        font_size='40sp')
            keypad_button.bind(on_single_press=self.equate_math)
            keypad_button.bind(on_double_press=self.change_symbol)
            keypad_button.bind(on_long_press=self.equate_math)
            if button_symbol[1] == 0:
                keypad_button.background_color = (1, 1, 1, 1)
            elif button_symbol[1] == 2:
                keypad_button.background_color = (0.55, 0.55, 0.6, 1)
            else:
                keypad_button.background_color = (0.65, 0.65, 0.7, 1)
            self.keypad.add_widget(keypad_button)

        self.add_widget(self.keypad)

    def update_display(self):
        global top_passed_num
        global bot_passed_num
        self.top_basic_eq_display.text = top_passed_num
        self.bot_basic_eq_display.text = bot_passed_num

    def change_symbol(self, instance):
        numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        symbols = [str(U'\u00f7'), str(U'\u00d7'), '/', '*', '-', '+']
        if instance.text in numbers:
            if self.bot_basic_eq_display.text == '':
                self.equate_math(instance)
            else:
                self.bot_basic_eq_display.text = self.bot_basic_eq_display.text[:-1] + instance.text
        elif instance.text in symbols:
            if self.top_basic_eq_display.text == '':
                self.equate_math(instance)
            else:
                self.top_basic_eq_display.text = self.top_basic_eq_display.text[:-1] + instance.text
        else:
            self.equate_math(instance)

    def equate_math(self, instance):
        global top_passed_num
        global bot_passed_num
        """Takes text from button pressed and adds the text to display"""
        if self.bot_basic_eq_display.text in "Invalid Input":
            self.bot_basic_eq_display.text = ''
        try:
            if instance.text == '=':
                equation = self.top_basic_eq_display.text + self.bot_basic_eq_display.text
                self.top_basic_eq_display.text = self.solver(equation)
                self.bot_basic_eq_display.text = ''

            elif instance.text == U'\u0025':    # Percentage sign
                if len(self.bot_basic_eq_display.text) != 0:
                    equation = self.bot_basic_eq_display.text + '*0.01'
                    self.top_basic_eq_display.text = self.solver(equation)
                    self.bot_basic_eq_display.text = ''
                    self.operated_state = True

            elif instance.text == U'\u221a':    # Square root sign
                if len(self.bot_basic_eq_display.text) != 0:
                    equation = 'sqrt(' + self.bot_basic_eq_display.text + ')'
                    self.top_basic_eq_display.text = self.solver(equation)
                    self.bot_basic_eq_display.text = ''
                    self.operated_state = True

            elif instance.text == 'x' + U'\u00b2':    # Square sign
                if len(self.bot_basic_eq_display.text) != 0:
                    equation = self.bot_basic_eq_display.text + '**2'
                    self.top_basic_eq_display.text = self.solver(equation)
                    self.bot_basic_eq_display.text = ''
                    self.operated_state = True

            elif instance.text == U'\u00b9' + '/x':    # Reciprocal sign
                if len(self.bot_basic_eq_display.text) != 0:
                    equation = '1/' + self.bot_basic_eq_display.text
                    self.top_basic_eq_display.text = self.solver(equation)
                    self.bot_basic_eq_display.text = ''
                    self.operated_state = True

            elif instance.text == U'\u00f7':    # Division sign
                self.operator(instance)

            elif instance.text == U'\u00d7':    # Multiplication sign
                self.operator(instance)

            elif instance.text == '+':
                self.operator(instance)

            elif instance.text == '-':
                self.operator(instance)

            elif instance.text == 'C':
                self.bot_basic_eq_display.text = ''

            elif instance.text == 'CE':
                self.top_basic_eq_display.text = ''
                self.bot_basic_eq_display.text = ''

            elif instance.text == str(U'\u21e6'):  # Back arrow, erases one character.
                self.bot_basic_eq_display.text = self.bot_basic_eq_display.text[:-1]

            elif instance.text == str(U'\u00b1'):  # Negates the number, adds or removes minus sign.
                if self.bot_basic_eq_display.text:
                    if '-' not in self.bot_basic_eq_display.text:
                        self.bot_basic_eq_display.text = '-' + self.bot_basic_eq_display.text
                    else:
                        self.bot_basic_eq_display.text = self.bot_basic_eq_display.text[1:]

            elif instance.text == '.':
                if '.' not in self.bot_basic_eq_display.text:
                    if self.bot_basic_eq_display.text:
                        self.bot_basic_eq_display.text += instance.text
                    elif self.operated_state is True or len(self.top_basic_eq_display.text) == 0:
                        self.bot_basic_eq_display.text = '0.'
                    else:
                        self.bot_basic_eq_display.text = "Invalid Input"

            else:
                self.number(instance)

        except SyntaxError:
            self.bot_basic_eq_display.text = "Invalid Input"
        top_passed_num = self.top_basic_eq_display.text
        bot_passed_num = self.bot_basic_eq_display.text

    def solver(self, equation):
        replacement_pairs = {'/': U'\u00f7', '*': U'\u00d7'}  # Characters that won't be recognized operators
        try:
            for k, v in replacement_pairs.items():
                equation = equation.replace(v, k)
            equation_pattern = re.compile('^(\-?\d+\.?\d*[+\-*/]{1})|(sqrt\()\-?\d+\.?\d*(\))+|(\*\*2)+$')
            result = equation_pattern.match(equation)
            if result:
                equation_total = sp.sympify(equation)
                result_total = sp.pretty(sp.latex(equation_total.evalf()))
                self.operated_state = False
                return str(result_total)
            else:
                return "Invalid Input"
        except AttributeError:
            return "Invalid Input"

    def number(self, instance):
        if self.operated_state is True or len(self.top_basic_eq_display.text) == 0:
            self.bot_basic_eq_display.text += instance.text
        else:
            self.top_basic_eq_display.text = ""
            self.bot_basic_eq_display.text = instance.text

    def operator(self, instance):
        if self.operated_state:
            equation = self.top_basic_eq_display.text + self.bot_basic_eq_display.text
            self.top_basic_eq_display.text = self.solver(equation) + instance.text
            self.bot_basic_eq_display.text = ''
            self.operated_state = True
        else:
            if len(self.top_basic_eq_display.text) == 0:
                self.top_basic_eq_display.text = self.bot_basic_eq_display.text + instance.text
                self.bot_basic_eq_display.text = ''
                self.operated_state = True
            else:
                self.top_basic_eq_display.text = self.top_basic_eq_display.text + instance.text
                self.bot_basic_eq_display.text = ''
                self.operated_state = True


"""
MathCharInputScreen
---MathCharInputLayout
------BlackBoard
------MathCharInputMenu
"""


class MathCharInputScreen(Screen):
    """#2: Creates the writing screen for OCR input."""
    def __init__(self, **kwargs):
        super(MathCharInputScreen, self).__init__(**kwargs)
        self.name = 'written_input'
        math_char_input_layout = MathCharInputLayout()
        self.bind(on_pre_enter=lambda x: math_char_input_layout.math_char_input_menu.update_display())
        self.add_widget(math_char_input_layout)


class MathCharInputLayout(FloatLayout):
    def __init__(self, **kwargs):
        super(MathCharInputLayout, self).__init__(**kwargs)
        self.cols = 1
        self.rows = 2
        blackboard = BlackBoard()

        self.math_char_input_menu = MathCharInputMenu(draw_board=blackboard, size_hint=(1, 0.32), pos_hint={'top': 1})
        self.add_widget(self.math_char_input_menu)

        self.add_widget(blackboard, index=1)


class BlackBoard(Widget):
    """Class for character recognition canvas."""
    def __init__(self, **kwargs):
        super(BlackBoard, self).__init__(**kwargs)
        self.size = (5000, 5000)
        self.canvas.before.add(Color(0.75, 0.8, 0.8))     # Light slate blue
        self.canvas.before.add(Rectangle(pos=self.pos, size=self.size))

    def on_touch_down(self, touch):
        """Selects the point on canvas for initial mark."""
        with self.canvas:
            Color(0.25, 0.28, 0.28)
            if self.collide_point(*touch.pos):
                touch.ud["line"] = Line(points=(touch.x, touch.y), width=4)

    def on_touch_move(self, touch):
        """Continues the line from the initial mark made on_touch_down"""
        if self.collide_point(*touch.pos):
            try:
                if touch.ud["line"].points[-2:] != [touch.x, touch.y]:  # If statement added to avoid duplicate points.
                    touch.ud["line"].points += (touch.x, touch.y)
            except KeyError:
                pass

    def clear_content(self):
        """Clears the canvas of all lines and marks made."""
        self.canvas.clear()


class MathCharInputMenu(GridLayout):
    draw_board = ObjectProperty()

    def __init__(self, **kwargs):
        super(MathCharInputMenu, self).__init__(**kwargs)
        self.cols = 1
        self.rows = 3
        self.top_char_eq_display = alignedtextinput.AlignedTextInput(font_size=24, size_hint=(1, 0.5), halign='right',
                                                                     valign='bottom',
                                                                     foreground_color=(0.0, 0.0, 0.0, 1))
        self.add_widget(self.top_char_eq_display)

        self.bot_char_eq_display = alignedtextinput.AlignedTextInput(font_size=30, size_hint=(1, 0.5), halign='right',
                                                                     valign='bottom')
        self.add_widget(self.bot_char_eq_display)
        button_container = BoxLayout(size_hint_y=0.40)

        self.submit_button = Button(text='Submit', on_release=self.submit_math)
        button_container.add_widget(self.submit_button)

        self.equate_button = Button(text='Equate', on_release=self.equate_math)
        button_container.add_widget(self.equate_button)

        self.add_widget(button_container)

    def update_display(self):
        global top_passed_num
        global bot_passed_num
        self.top_char_eq_display.text = top_passed_num
        self.bot_char_eq_display.text = bot_passed_num

    def equate_math(self, event):
        """Handler takes interpreted characters from display and performs the calculation."""
        global top_passed_num
        global bot_passed_num
        self.draw_board.clear_content()    # Clears BlackBoard instance using method.
        try:
            equation_total = eval(self.bot_char_eq_display.text)
            self.bot_char_eq_display.text = str(equation_total)
        except SyntaxError:
            self.bot_char_eq_display.text = "Invalid Input"
        top_passed_num = self.top_char_eq_display.text
        bot_passed_num = self.bot_char_eq_display.text

    def submit_math(self, event):
        """Handler for submit button. Converts the BlackBoard into png image to be interpreted by OCR Tesseract."""
        global top_passed_num
        global bot_passed_num
        self.draw_board.export_to_png('im.png')
        threshold = 100
        im = Image.open('im.png').convert('L').point(lambda x: 255 if x > threshold else 0, mode='1')
        rgb_im = im.convert('RGB')
        rgb_im.save('new_im.jpg', dpi=(5000, 5000))
        new_im = Image.open('new_im.jpg')
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        written_eq = pytesseract.image_to_string(new_im, lang="eng", config="--psm 8 -c tessedit_char_blacklist=|ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz tessedit_char_whitelist=0123456789*/+-")
        print(written_eq)
        self.bot_char_eq_display.text = written_eq
        top_passed_num = self.top_char_eq_display.text
        bot_passed_num = self.bot_char_eq_display.text


"""
OptionsScreen
---OptionsLayout
"""


class EquationInputScreen(Screen):
    """#1: Creates basic calculator screen."""
    def __init__(self, **kwargs):
        super(EquationInputScreen, self).__init__(**kwargs)
        self.name = 'equation_input'
        database = EquationInputLayout()
        self.add_widget(database)


class EquationInputLayout(BoxLayout):
    """Class to provide scroll view for options/settings menu"""
    def __init__(self, **kwargs):
        super(EquationInputLayout, self).__init__(**kwargs)
        self.cols = 1
        self.rows = 1
        scroll_menu = GridLayout(cols=1, size_hint_y=None)
        scroll_menu.bind(minimum_height=scroll_menu.setter('height'))
        for i in range(100):
            btn = Button(text=str(i), size_hint_y=None, height=40)
            scroll_menu.add_widget(btn)
        root = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        root.add_widget(scroll_menu)
        self.add_widget(root)


"""MAIN APP"""


class MathCat(App):
    def build(self):
        self.icon = 'MathCat.bmp'
        self.title = 'Math Cat'
        main = MainWindow()
        return main


if __name__ == "__main__":
    MathCat().run()
