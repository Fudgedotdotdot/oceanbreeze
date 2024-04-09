from rich.console import Console
from rich.theme import Theme


class CustomPrint(Console):
    def __init__(self, log_level="INFO"):
        super().__init__()
        self.log_level = ""
        self.INFO = "INFO"
        self.DEBUG = "DEBUG"

        if log_level != self.INFO:
            self.log_level = self.DEBUG
        else:
            self.log_level = self.INFO
        
        self.custom_theme = Theme({
            "info": "bold green",
            "debug": "blue_violet",
            "danger": "bold red"
        })
        self.rc = Console(theme=self.custom_theme, highlight=True)

    def info(self, message: str, **kwargs) -> None:
        self.rc.print(f"[info]\[+][/info] {message}", **kwargs)

    def debug(self, message: str, **kwargs) -> None:
        if self.log_level != self.DEBUG:
            return
        self.rc.print(f"[debug]\[#][/debug] {message}", **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        self.rc.print(f"[danger]\[!][/danger] [bold]{message}[/bold]", **kwargs)
    
    def set_log_level(self, loglevel: str) -> None:
        self.log_level = loglevel
