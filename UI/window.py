
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(QtWidgets.QMainWindow):
    def setupUi(self, Form, WINDOW_HEIGHT, WINDOW_WIDTH):
        Form.setObjectName("Form")
        Form.resize(WINDOW_HEIGHT, WINDOW_WIDTH)
        self.incidentList = QtWidgets.QListWidget(Form)
        self.incidentList.setGeometry(QtCore.QRect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
        self.incidentList.setObjectName("incidentList")
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Обозреватель инцидентов"))