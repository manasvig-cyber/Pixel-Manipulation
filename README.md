
Image Encryption and pixel manipulation Tool (PyQt5 + Pillow)

A simple, GUI-based image encryption tool built with **PyQt5** and **Pillow**.  
This project demonstrates how image encryption can be done at the **pixel level** using operations like addition and subtraction on RGB values.  

---

 Project Summary
- Upload an image (PNG / JPG / JPEG).
- Encrypt the image using pixel manipulation.
- Decrypt the encrypted image to recover the original.
- Beginner-friendly but extensible to advanced methods.


🚀 Features
- Minimal PyQt5 GUI (Upload, Encrypt, Decrypt).
- Simple encryption using pixel RGB shifts.
- Decryption restores the original image.
- Encrypted/decrypted images saved as PNG files.

---

 🛠 Software Requirements
- Python 3.8+ (3.10 recommended)
- pip

Python libraries:
- PyQt5  
- Pillow  

Install with:


pip install pyqt5 pillow


📖 Step-by-step Implementation

 1. Create project folder

mkdir image\_encryptor
cd image\_encryptor

### 2. Create and activate virtual environment
Windows (PowerShell):


python -m venv .venv
..venv\Scripts\activate

If you get an error about scripts being disabled, run this in Administrator PowerShell:


Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser


Linux / macOS:


python3 -m venv .venv
source .venv/bin/activate



 3. Install required libraries


pip install pyqt5 pillow



4. Create `main.py`
Paste the project code into a file named **main.py**.

 5. Run the application


python main.py


- Click Upload Image → select an image.  
- Click Encrypt Image → creates and displays `encrypted_image.png`.  
- Click Decrypt Image → creates and displays `decrypted_image.png`.  


 Image Encryption & Pixel Manipulation

Pixels
- An image is made of pixels.
- Each pixel has 3 values: **R**, **G**, **B** (0–255).

Example pixel: `(100, 150, 200)`

 Simple Pixel Operations for Encryption
1. Addition (mod 256)


Encrypted = (Original + 50) % 256


Example: `(100,150,200)` → `(150,200,250)`

Decryption:


Decrypted = (Encrypted - 50) % 256

`(150,200,250)` → `(100,150,200)`

2. Bitwise XOR

Encrypted = Original ^ Key


Example: `100 ^ 128 = 228`  
Decryption: `228 ^ 128 = 100`

3.Permutation
Shuffle pixels based on a key. More secure but complex.

 Why use it?
- Prevents direct visibility of sensitive images.
- Demonstrates the basics of cryptography applied to multimedia.


 📂 File Structure


image\_encryptor/
│── main.py
│── encrypted\_image.png   # Generated
│── decrypted\_image.png   # Generated
│── .venv/                # Virtual environment


🔧 Troubleshooting
Error: cannot activate .venv on Windows
Fix by running:


Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

PyQt5 window not showing (Linux)  
Run inside desktop environment (X11/Wayland). Won’t work on headless server.

 📈 Advanced Extensions
- XOR with keystream generated from password.  
- Pixel permutation (scrambling).  
- Combine methods: XOR + Shift + Shuffle.  
- Store metadata (method & key) for reproducible decryption.  
- Add progress bar & multi-threading for large images.  

 📜 License
This project is under the MIT License  
