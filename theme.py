class Theme :
    def __init__(self, theme_name) :
        with open("./themes/" + theme_name + ".theme", 'r') as file:
            data = file.read().replace('\n', '')
            theme = data.split(',')

        self.name = theme_name
        self.bg = theme[0]
        self.text_colour = theme[1]
        self.font = theme[2]
        self.font_size = theme[3]
        self.token_select_colour = theme[4]
        self.last_sent_colour = theme[5]
        self.highlight_colour = theme[6]