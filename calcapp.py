from kivy.app import App
# kivy.require("1.8.0")
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color, Rectangle
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.uix.relativelayout import RelativeLayout
from PIL import Image
import sympy as sp
import pytesseract
import evaluator


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
        self.calc_type_menu = MainMenu(screen_manager=self.calc_type_selection, text='Basic', font_size='50sp',
                                       size_hint=(1, 0.2), background_color=(0.5, 0.7, 0.8, 1))
        self.add_widget(self.calc_type_selection)
        self.add_widget(self.calc_type_menu)


class ScreenSelector(ScreenManager):
    """Class for handling the three main screens."""
    def __init__(self, **kwargs):
        super(ScreenSelector, self).__init__(**kwargs)
        self.transition = FadeTransition()
        basic_input_screen = BasicInputScreen()    # Loads basic input screen into screen manager. Number 1 in menu.
        self.add_widget(basic_input_screen)

        math_char_input_screen = MathCharInputScreen()  # Loads math OCR screen into screen manager. Number 2 in menu.
        self.add_widget(math_char_input_screen)

        equation_input_screen = EquationInputScreen()   # Loads equation database
        self.add_widget(equation_input_screen)

        self.current = 'basic_input'


class MainMenu(Button):
    """Class to establish menu for all screens"""
    screen_manager = ObjectProperty()    # Gives ability to access instantiated object outside of class by adding kwarg

    def __init__(self, **kwargs):
        super(MainMenu, self).__init__(**kwargs)
        self.drop_list = DropDown()
        types = ['Basic', 'Write', 'Equations']    # We have three main screens. May need to add a 'Graph' screen.
        for i in types:
            button = Button(text=i, font_size="50sp", size_hint_y=None, height="80sp",
                            background_color=(0.6, 0.8, 0.9, 1))
            button.bind(on_release=lambda btn: self.drop_list.select(btn.text))
            self.drop_list.add_widget(button)
        self.bind(on_release=self.drop_list.open)
        self.drop_list.bind(on_select=lambda instance, x: setattr(self, 'text', x))
        self.drop_list.bind(on_select=self.menu_selection)

    def menu_selection(self, event, x):
        """Drop-list selection changes to one of three screens"""
        if x == 'Basic':
            self.screen_manager.current = 'basic_input'
        elif x == 'Write':
            self.screen_manager.current = 'written_input'
        else:
            self.screen_manager.current = 'equation_input'


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
        self.add_widget(default)


class BasicInputLayout(GridLayout):
    """Class to provide grid for keypad and numerical display"""
    def __init__(self, **kwargs):
        super(BasicInputLayout, self).__init__(**kwargs)

        self.cols = 1
        self.rows = 2
        self.spacing = [3, 3]

        self.display = TextInput(font_size=30, size_hint=(1, 0.2))
        self.add_widget(self.display)

        self.keypad = GridLayout(cols=4, rows=5)
        self.canvas.before.add(Color(0.5, 0.6, 0.6))
        self.canvas.before.add(Rectangle(pos=self.pos, size=(5000, 5000)))
        self.keypad.spacing = [2, 2]
        button_symbols = [('CLR', 0), (str(U'\u00f7'), 0), (str(U'\u00d7'), 0), (str(U'\u21e6'), 0), ('7', 1), ('8', 1),
                          ('9', 1), ('-', 0), ('4', 1), ('5', 1), ('6', 1), ('+', 0), ('1', 1), ('2', 1), ('3', 1),
                          ('( )', 0), ('.', 0), ('0', 1), (str(U'\u00b1'), 0), ('=', 0)]
        for button_symbol in button_symbols:
            keypad_button = Button(text=button_symbol[0], font_name='L_10646', font_size='40sp',
                                   on_press=self.equate_math)
            if button_symbol[1] == 0:
                keypad_button.background_color = (1, 1, 1, 1)
            else:
                keypad_button.background_color = (0.65, 0.65, 0.7, 1)
            self.keypad.add_widget(keypad_button)

        self.add_widget(self.keypad)

    def equate_math(self, event):
        """Takes text from button pressed and adds the text to display"""
        if self.display.text == "Invalid Input":
            self.display.text = ''
        try:
            if event.text == '=':
                replacement_pairs = {'/': U'\u00f7', '*': U'\u00d7'}    # Characters that won't be recognized
                modified_string = str(self.display.text)
                for k, v in replacement_pairs.items():
                    modified_string = modified_string.replace(v, k)
                equation_total = sp.sympify(modified_string)
                result_total = sp.pretty(sp.latex(equation_total.evalf()))
                self.display.text = str(result_total)
            elif event.text == 'CLR':
                self.display.text = ''
            elif event.text == str(U'\u21e6'):
                self.display.text = self.display.text[:-1]
            elif event.text == str(U'\u00b1'):
                if self.display.text[0] == '-':
                    self.display.text = self.display.text[1:]
                else:
                    self.display.text = '-' + self.display.text
            elif event.text == '( )':
                if self.display.text[-1] != ')' and self.display.text[1] != '(':
                    self.display.text = '(' + self.display.text + ')'
                else:
                    self.display.text = self.display.text[1:-1]
            elif event.text == '.':
                if '.' not in self.display.text:
                    self.display.text += event.text
            else:
                self.display.text += event.text
        except SyntaxError:
            self.display.text = "Invalid Input"


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
        self.add_widget(math_char_input_layout)


class MathCharInputLayout(RelativeLayout):
    def __init__(self, **kwargs):
        super(MathCharInputLayout, self).__init__(**kwargs)

        blackboard = BlackBoard()
        self.add_widget(blackboard)

        math_char_input_menu = MathCharInputMenu(draw_board=blackboard)     # ObjectProperty added to pass BlackBoard in
        self.add_widget(math_char_input_menu)


class BlackBoard(Widget):
    """Class for character recognition canvas."""
    def __init__(self, **kwargs):
        super(BlackBoard, self).__init__(**kwargs)
        self.canvas.before.add(Color(1, 0.72, 0.3))     # Orange
        self.canvas.before.add(Rectangle(pos=self.pos, size=(5000, 5000)))

    def on_touch_down(self, touch):
        """Selects the point on canvas for initial mark."""
        with self.canvas:
            Color(0.25, 0.28, 0.28)
            if self.collide_point(*touch.pos):
                touch.ud["line"] = Line(points=(touch.x, touch.y), width=6)

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


class MathCharInputMenu(BoxLayout):
    draw_board = ObjectProperty()

    def __init__(self, **kwargs):
        super(MathCharInputMenu, self).__init__(**kwargs)
        self.equation_display = TextInput(size_hint=(0.6, 0.1))
        self.spacing = [3, 3]
        self.add_widget(self.equation_display)

        self.submit_button = Button(text='Submit', size_hint=(0.2, 0.1), on_release=self.submit_math)
        self.add_widget(self.submit_button)

        self.equate_button = Button(text='Equate', size_hint=(0.2, 0.1), on_release=self.equate_math)
        self.add_widget(self.equate_button)

    def equate_math(self, event):
        """Handler takes interpreted characters from display and performs the calculation."""
        self.draw_board.clear_content()     # Clears BlackBoard instance using method.
        try:
            equation_total = eval(self.equation_display.text)
            self.equation_display.text = str(equation_total)
        except SyntaxError:
            self.equation_display.text = "Invalid Input"

    def submit_math(self, event):
        """Handler for submit button. Converts the BlackBoard into png image to be interpreted by OCR Tesseract."""
        self.draw_board.export_to_png('im.png')
        threshold = 100
        im = Image.open('im.png').convert('L').point(lambda x: 255 if x > threshold else 0, mode='1')
        rgb_im = im.convert('RGB')
        rgb_im.save('new_im.jpg', dpi=(500, 500))
        new_im = Image.open('new_im.jpg')
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
        written_eq = pytesseract.image_to_string(new_im, lang="eng",
    config="--oem 0 --psm 8 -c tessedit_char_blacklist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz tessedit_char_whitelist=0123456789*/+-")
        new_eq = evaluator.EQ.examine(written_eq)   # Pre-processing before displayed.
        self.equation_display.text = new_eq


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
