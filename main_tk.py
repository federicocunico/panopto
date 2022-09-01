from panopto_downloader.configs import initialize_app
from panopto_downloader.models.panopto_model import PanoptoModel

from panopto_downloader.models.view_model import MainWindow

config = initialize_app()
model = PanoptoModel(config)
window = MainWindow(model)
window.mainloop()
