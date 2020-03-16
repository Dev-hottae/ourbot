from ui.ui import *
from account.login import *


class Main():
    def __init__(self):

        # UI 실행
        self.app = QApplication(sys.argv)
        self.ui = UI_class()
        self.ui.show()
        self.app.exec_()

        # upbit access
        #Login()


if __name__ == "__main__":
    Main()