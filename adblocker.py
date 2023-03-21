import os
import re

class AdBlocker:
    def __init__(self, filter_directory):
        self.filters = []
        self.load_filters(filter_directory)
    
    def generate_css_rules(self):
            css = ""
            for filter_type, pattern in self.filters:
                if filter_type == "css":
                    css += f"{pattern} {{ display: none !important; }}"
            return css    
    
    def save_css_rules_to_file(self, css_rules):
        css_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "adblocker_generated_css.css")
        with open(css_file_path, "w", encoding="utf-8") as css_file:
            css_file.write(css_rules)
        return css_file_path

    def load_filters(self, filter_directory):
        for file in os.listdir(filter_directory):
            if file.endswith(".txt"):
                file_path = os.path.join(filter_directory, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    self.filters.extend(self.parse_filters(f.readlines()))

    def parse_filters(self, lines):
        filters = []

        for line in lines:
            line = line.strip()
            if line.startswith("!") or line.startswith("[") or not line:
                continue

            if "##" in line:
                filters.append(("css", line.split("##", 1)[1]))
            elif "||" in line:
                filters.append(("url", re.escape(line.split("||", 1)[1])))

        return filters

    def should_block(self, url):
        for filter_type, pattern in self.filters:
            if filter_type == "url" and re.search(pattern, url):
                return True
        return False

    def create_css_injection(self):
        css_rules = self.generate_css_rules()
        css_file_path = self.save_css_rules_to_file(css_rules)
        return css_file_path