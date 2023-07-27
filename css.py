class CSS:
    @staticmethod
    def parse_css(css: str):
        kwargs = {}
        lines = css.split(';')
        lines = [i for i in lines if i]
        for i in lines:
            key, value, *_ = i.split(':')
            if _:
                # possibly invalid css with more syntax a : b : c
                continue
            kwargs[key] = value
        return kwargs
