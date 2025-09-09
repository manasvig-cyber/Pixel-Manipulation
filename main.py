import sys
import hashlib
import numpy as np
from PIL import Image
from PyQt5 import QtWidgets, QtGui, QtCore

# -----------------------
# Helpers: key -> seed
# -----------------------
def key_to_seed(key: str) -> int:
    if isinstance(key, int):
        return int(key) & 0xFFFFFFFF
    h = hashlib.sha256(key.encode('utf-8')).digest()
    return int.from_bytes(h[:4], 'big')

# -----------------------
# Image conversions
# -----------------------
def pil_to_numpy(pil_img: Image.Image) -> np.ndarray:
    return np.array(pil_img.convert('RGB'), dtype=np.uint8)

def numpy_to_pil(arr: np.ndarray) -> Image.Image:
    return Image.fromarray(arr.astype(np.uint8), 'RGB')

def numpy_to_qimage(arr: np.ndarray) -> QtGui.QImage:
    h, w, c = arr.shape
    arr_contig = np.ascontiguousarray(arr)
    bytes_per_line = 3 * w
    return QtGui.QImage(arr_contig.data.tobytes(), w, h, bytes_per_line, QtGui.QImage.Format_RGB888)

# -----------------------
# Encryption primitives
# -----------------------
def invert_pixels(arr: np.ndarray) -> np.ndarray:
    """Simple value inversion: 255 - pixel"""
    return 255 - arr

# -----------------------
# Save/load package
# -----------------------
def save_image(path: str, arr: np.ndarray):
    numpy_to_pil(arr).save(path)

def save_package_npz(path: str, arr: np.ndarray, method: str, seed: int):
    np.savez_compressed(path, data=arr, method=np.array([method]), seed=np.array([seed], dtype=np.uint64))

def load_package_npz(path: str):
    z = np.load(path, allow_pickle=True)
    data = z['data']
    method = str(z['method'][0])
    seed = int(z['seed'][0])
    return data, method, seed

# -----------------------
# MainWindow
# -----------------------
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SkillCraft Image Encryption Tool")
        self.resize(1200, 700)

        # Navy blue and white theme
        self.setStyleSheet("""
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                        stop:0 #001f3f, stop:1 #001840);
        }
        QPushButton {
            color: white;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #003366, stop:1 #004080);
            border-radius: 8px;
            padding: 6px 12px;
            font-weight: bold;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #004080, stop:1 #0059b3);
        }
        QLabel {
            color: white;
            background: transparent;
            font-weight: bold;
        }
        QComboBox, QLineEdit {
            color: white;
            background: #003366;
            border: 1px solid #0059b3;
            border-radius: 5px;
            padding: 4px;
            font-weight: bold;
        }
        """)

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        # Topbar
        topbar = QtWidgets.QHBoxLayout()
        layout.addLayout(topbar)
        self.btn_load = QtWidgets.QPushButton("Upload Image")
        self.btn_encrypt = QtWidgets.QPushButton("Encrypt")
        self.btn_decrypt = QtWidgets.QPushButton("Decrypt")
        self.btn_save_png = QtWidgets.QPushButton("Save Image")
        self.btn_load_pkg = QtWidgets.QPushButton("Load Package")
        for b in [self.btn_load, self.btn_encrypt, self.btn_decrypt, self.btn_save_png, self.btn_load_pkg]:
            topbar.addWidget(b)
        topbar.addStretch()

        self.cmb_method = QtWidgets.QComboBox()
        self.cmb_method.addItems(["xor", "invert"])
        topbar.addWidget(QtWidgets.QLabel("Method:"))
        topbar.addWidget(self.cmb_method)
        self.line_key = QtWidgets.QLineEdit()
        self.line_key.setEchoMode(QtWidgets.QLineEdit.Password)
        self.line_key.setPlaceholderText("Enter password/key")
        topbar.addWidget(QtWidgets.QLabel("Key:"))
        topbar.addWidget(self.line_key)

        # Image labels
        images_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(images_layout)
        self.lbl_original = QtWidgets.QLabel("Original")
        self.lbl_encrypted = QtWidgets.QLabel("Encrypted")
        self.lbl_decrypted = QtWidgets.QLabel("Decrypted")
        for lbl in [self.lbl_original, self.lbl_encrypted, self.lbl_decrypted]:
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            lbl.setFixedSize(360, 360)
            lbl.setStyleSheet("background: #1E2A38; border-radius: 8px;")
            images_layout.addWidget(lbl)

        # Status bar
        bottom = QtWidgets.QHBoxLayout()
        layout.addLayout(bottom)
        self.status_label = QtWidgets.QLabel("Ready")
        bottom.addWidget(self.status_label)

        # Signals
        self.btn_load.clicked.connect(self.load_image)
        self.btn_encrypt.clicked.connect(self.encrypt_image)
        self.btn_decrypt.clicked.connect(self.decrypt_image)
        self.btn_save_png.clicked.connect(self.save_image_file)
        self.btn_load_pkg.clicked.connect(self.load_package)

        # State
        self.original_arr = None
        self.encrypted_arr = None
        self.decrypted_arr = None

    # -----------------------
    # UI helpers
    # -----------------------
    def show_in_label(self, label, arr):
        qimg = numpy_to_qimage(arr)
        pix = QtGui.QPixmap.fromImage(qimg).scaled(label.width(), label.height(),
                                                    QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        label.setPixmap(pix)

    # -----------------------
    # Actions
    # -----------------------
    def load_image(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if not path:
            return
        pil = Image.open(path)
        arr = pil_to_numpy(pil)
        self.original_arr = arr
        self.show_in_label(self.lbl_original, arr)
        self.status_label.setText(f"Loaded {path}")

    def encrypt_image(self):
        if self.original_arr is None:
            self.status_label.setText("No image loaded")
            return
        method = self.cmb_method.currentText()
        if method == "xor":
            out = np.fliplr(self.original_arr)  # Just flip horizontally
        elif method == "invert":
            out = invert_pixels(self.original_arr)
        else:
            out = self.original_arr.copy()
        self.encrypted_arr = out
        self.show_in_label(self.lbl_encrypted, out)
        self.status_label.setText("Encryption complete")

    def decrypt_image(self):
        if self.encrypted_arr is None:
            self.status_label.setText("No encrypted image")
            return
        method = self.cmb_method.currentText()
        if method == "xor":
            out = np.fliplr(self.encrypted_arr)  # Flip back
        elif method == "invert":
            out = invert_pixels(self.encrypted_arr)
        else:
            out = self.encrypted_arr.copy()
        self.decrypted_arr = out
        self.show_in_label(self.lbl_decrypted, out)
        self.status_label.setText("Decryption complete")

    def save_image_file(self):
        if self.encrypted_arr is None:
            self.status_label.setText("No image to save")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Image (*.png)")
        if not path:
            return
        save_image(path, self.encrypted_arr)
        self.status_label.setText(f"Saved {path}")

    def load_package(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Load Package", "", "NPZ Package (*.npz)")
        if not path:
            return
        data, method, seed = load_package_npz(path)
        self.encrypted_arr = data
        self.show_in_label(self.lbl_encrypted, self.encrypted_arr)
        self.status_label.setText(f"Loaded package {path}")

# -----------------------
# Run
# -----------------------
def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
