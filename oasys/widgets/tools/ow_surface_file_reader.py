import os, sys

import numpy
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtWidgets import QApplication, QMessageBox, QLabel, QSizePolicy
from PyQt5.QtGui import QTextCursor, QFont, QPalette, QColor, QPixmap

from matplotlib import cm
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from orangewidget import gui, widget
from orangewidget.settings import Setting

from oasys.widgets.widget import OWWidget
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence

from oasys.util.oasys_objects import OasysSurfaceData

import oasys.util.oasys_util as OU

try:
    from mpl_toolkits.mplot3d import Axes3D  # necessario per caricare i plot 3D
except:
    pass

class OWSurfaceFileReader(OWWidget):
    name = "Surface File Reader"
    id = "surface_file_reader"
    description = "Surface File Reader"
    icon = "icons/surface.png"
    author = "Luca Rebuffi"
    maintainer_email = "lrebuffi@anl.gov"
    priority = 2
    category = ""
    keywords = ["surface_file_reader"]

    outputs = [{"name": "Surface Data",
                "type": OasysSurfaceData,
                "doc": "Surface Data",
                "id": "Surface Data"}]

    want_main_area = 1
    want_control_area = 1

    MAX_WIDTH = 1320
    MAX_HEIGHT = 700

    IMAGE_WIDTH = 860
    IMAGE_HEIGHT = 645

    CONTROL_AREA_WIDTH = 405
    TABS_AREA_HEIGHT = 618

    xx = None
    yy = None
    zz = None

    surface_file_name = Setting('surface.hdf5')

    def __init__(self):
        super().__init__()

        geom = QApplication.desktop().availableGeometry()
        self.setGeometry(QRect(round(geom.width() * 0.05),
                               round(geom.height() * 0.05),
                               round(min(geom.width() * 0.98, self.MAX_WIDTH)),
                               round(min(geom.height() * 0.95, self.MAX_HEIGHT))))

        self.setMaximumHeight(self.geometry().height())
        self.setMaximumWidth(self.geometry().width())

        gui.separator(self.controlArea)

        button_box = oasysgui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Render Surface", callback=self.render_surface)
        button.setFixedHeight(45)

        input_box_l = oasysgui.widgetBox(self.controlArea, "Input", addSpace=True, orientation="horizontal", height=self.TABS_AREA_HEIGHT)

        self.le_surface_file_name = oasysgui.lineEdit(input_box_l, self, "surface_file_name", "Surface File Name",
                                                        labelWidth=120, valueType=str, orientation="horizontal")

        gui.button(input_box_l, self, "...", callback=self.selectSurfaceFile)


        self.figure = Figure(figsize=(600, 600))
        self.figure.patch.set_facecolor('white')

        self.axis = self.figure.add_subplot(111, projection='3d')

        self.axis.set_zlabel("Z [m]")

        self.figure_canvas = FigureCanvasQTAgg(self.figure)

        self.mainArea.layout().addWidget(self.figure_canvas)

        gui.rubber(self.mainArea)


    def render_surface(self):
        try:
            self.surface_file_name = congruence.checkDir(self.surface_file_name)

            #### LENGTH

            xx, yy, zz = OU.read_surface_file(self.surface_file_name)

            self.xx = xx
            self.yy = yy
            self.zz = zz

            self.axis.clear()

            x_to_plot, y_to_plot = numpy.meshgrid(self.xx, self.yy)

            self.axis.plot_surface(x_to_plot, y_to_plot, zz,
                                   rstride=1, cstride=1, cmap=cm.autumn, linewidth=0.5, antialiased=True)

            self.axis.set_xlabel("X [m]")
            self.axis.set_ylabel("Y [m]")
            self.axis.set_zlabel("Z [m]")
            self.axis.mouse_init()

            self.figure_canvas.draw()

            self.send("Surface Data", OasysSurfaceData(xx=self.xx, yy=self.yy, zz=self.zz, surface_data_file=self.surface_file_name))

        except Exception as exception:
            QMessageBox.critical(self, "Error",
                                 exception.args[0],
                                 QMessageBox.Ok)

            if self.IS_DEVELOP: raise exception

    def selectSurfaceFile(self):
        self.le_surface_file_name.setText(oasysgui.selectFileFromDialog(self, self.surface_file_name, "Select Input File", file_extension_filter="HDF5 Files (*.hdf5)"))


