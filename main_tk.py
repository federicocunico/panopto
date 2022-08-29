import requests
from panopto_downloader.configs import init_config
from panopto_downloader.models.panopto_model import PanoptoModel

from panopto_downloader.models.view_model import MainWindow

config = init_config()
model = PanoptoModel(config)
window = MainWindow(model)
window.mainloop()
