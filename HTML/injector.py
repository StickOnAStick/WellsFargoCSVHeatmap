from html.parser import HTMLParser

class DivInjector(HTMLParser):
    def __init__(self, target_id: str, inject_html: str):
        super().__init__()
        self.target_id = target_id
        self.inject_html = inject_html
        self.output = []
        self.in_target = False
        self.injected = False

    def handle_starttag(self, tag, attrs):
        self.output.append(self.get_starttag_text())

        if tag == "div":
            attrs_dict = dict(attrs)
            if attrs_dict.get("id") == self.target_id:
                self.in_target = True

    def handle_endtag(self, tag):
        if self.in_target and tag == "div" and not self.injected:
            self.output.append(self.inject_html)
            self.injected = True
            self.in_target = False

        self.output.append(f"</{tag}>")

    def handle_data(self, data):
        if not self.in_target:
            self.output.append(data)