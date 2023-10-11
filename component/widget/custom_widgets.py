import ipyvuetify as v
from traitlets import Bool, Int, link


class CheckboxState(v.Flex):

    v_model = Bool().tag(sync=True)

    def __init__(self, label, *args, **kwargs):
        self.class_ = "d-flex"
        super().__init__(*args, **kwargs)

        self.label = label
        self.state = v.Icon(class_="ml-2", children=["mdi-circle"], x_small=True)
        self.checkbox = v.Checkbox(label=self.label)

        self.children = [
            self.checkbox,
            Tooltip(self.state, "Not processed", bottom=False, right=True),
        ]

        link((self, "v_model"), (self.checkbox, "v_model"))

    def done(self):
        """Change state icon to done."""
        self.state.color = "green"

        self.children = [
            self.checkbox,
            Tooltip(self.state, "Process done", bottom=False, right=True),
        ]

    def error(self):
        """Change state icon to done."""
        self.state.color = "red"
        self.children = [
            self.checkbox,
            Tooltip(self.state, "Process failed", bottom=False, right=True),
        ]

    def running(self):
        """Change state icon to done."""
        self.state.color = "yellow"
        self.children = [
            self.checkbox,
            Tooltip(self.state, "Running...", bottom=False, right=True),
        ]


class Tabs(v.Card):

    current = Int(0).tag(sync=True)

    def __init__(self, titles, content, **kwargs):

        self.background_color = "primary"
        self.dark = True

        self.tabs = [
            v.Tabs(
                v_model=self.current,
                children=[
                    v.Tab(children=[title], key=key) for key, title in enumerate(titles)
                ],
            )
        ]

        self.content = [
            v.TabsItems(
                v_model=self.current,
                children=[
                    v.TabItem(children=[content], key=key)
                    for key, content in enumerate(content)
                ],
            )
        ]

        self.children = self.tabs + self.content

        link((self.tabs[0], "v_model"), (self.content[0], "v_model"))

        super().__init__(**kwargs)


class Tooltip(v.Tooltip):
    def __init__(self, widget, tooltip, *args, **kwargs):
        """
        Custom widget to display tooltip when mouse is over widget
        Args:
            widget (DOM.widget): widget used to display tooltip
            tooltip (str): the text to display in the tooltip.

        Example:
            btn = v.Btn(children=['Button'])
            Tooltip(widget=btn, tooltip='Click over the button')

        Warning:
            Don't change any trait of the Tooltip class, it will make
            disappear your widget because a bug in ipyvuetify.

        """
        self.tooltip = tooltip
        self.bottom = True
        self.widget = widget
        self.v_slots = [
            {"name": "activator", "variable": "tooltip", "children": self.widget}
        ]
        self.widget.v_on = "tooltip.on"
        self.children = [self.tooltip]

        super().__init__(*args, **kwargs)
