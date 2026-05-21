import tkinter as tk
from tkinter import Menu
from PIL import Image, ImageTk
import mss
import threading
import time
import ctypes


class MagnifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Desktop Magnifier")
        self.root.geometry("300x300")
        
        # Magnification settings
        self.magnification = 3.0
        self.running = True
        self.frame_interval = 1.0 / 30  # 30 Hz max
        
        # Create menu bar
        self.create_menu()
        
        # Create canvas for displaying magnified image
        self.canvas = tk.Canvas(root, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Screen capture object (will be initialized in thread)
        self.sct = None
        self.canvas_image_id = None
        self._update_pending = False
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Exclude this window from screen capture to prevent mirror artifacts
        self.root.after(0, self._exclude_from_capture)
        
        # Start update thread
        self.update_thread = threading.Thread(target=self.update_magnifier, daemon=True)
        self.update_thread.start()
    
    def _exclude_from_capture(self):
        """Hide this window from screen capture using Windows API"""
        try:
            WDA_EXCLUDEFROMCAPTURE = 0x00000011
            ctypes.windll.user32.SetWindowDisplayAffinity(self.root.winfo_id(), WDA_EXCLUDEFROMCAPTURE)
        except Exception as e:
            print(f"Could not exclude window from capture: {e}")

    def create_menu(self):
        """Create menu bar with magnification options"""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Quit", command=self.on_closing)
        
        # Magnification menu
        mag_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Magnification", menu=mag_menu)
        
        # Add magnification levels from 2x to 20x
        for mag in range(2, 21):
            mag_menu.add_command(
                label=f"{mag}x",
                command=lambda m=mag: self.set_magnification(m)
            )
    
    def set_magnification(self, mag):
        """Set the magnification level"""
        self.magnification = float(mag)
        self.root.title(f"Desktop Magnifier - {mag}x")
    
    def get_mouse_position(self):
        """Get current mouse position"""
        return self.root.winfo_pointerx(), self.root.winfo_pointery()
    
    def capture_and_magnify(self):
        """Capture area around mouse and magnify it"""
        try:
            # Get current canvas size
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                return None
            
            # Get mouse position
            mouse_x, mouse_y = self.get_mouse_position()
            
            # Calculate capture area (area to capture before magnification)
            capture_width = int(canvas_width / self.magnification)
            capture_height = int(canvas_height / self.magnification)
            
            # Calculate capture region centered on mouse
            left = mouse_x - capture_width // 2
            top = mouse_y - capture_height // 2
            right = left + capture_width
            bottom = top + capture_height

            # Get full virtual screen bounds so we can clamp correctly on all edges
            vm = self.sct.monitors[0]
            screen_left = vm["left"]
            screen_top = vm["top"]
            screen_right = vm["left"] + vm["width"]
            screen_bottom = vm["top"] + vm["height"]

            # Clamp the capture rect to actual screen bounds before grabbing;
            # mss returns garbage data for bottom/right overflow otherwise
            cl = max(left, screen_left)
            ct = max(top, screen_top)
            cr = min(right, screen_right)
            cb = min(bottom, screen_bottom)

            # Gray backing image — off-screen portions stay gray
            img = Image.new("RGB", (capture_width, capture_height), (128, 128, 128))

            if cr > cl and cb > ct:
                monitor = {"left": cl, "top": ct, "width": cr - cl, "height": cb - ct}
                screenshot = self.sct.grab(monitor)
                captured = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
                # Paste offset is how far the clamped origin is from the intended origin
                img.paste(captured, (cl - left, ct - top))
            
            # Resize to canvas size (magnification)
            img = img.resize((canvas_width, canvas_height), Image.NEAREST)
            
            return img
        except Exception as e:
            print(f"Error capturing: {e}")
            return None
    
    def update_magnifier(self):
        """Continuously update the magnified view"""
        # Initialize mss in this thread (mss is not thread-safe)
        self.sct = mss.mss()
        
        try:
            while self.running:
                frame_start = time.monotonic()
                try:
                    img = self.capture_and_magnify()
                    if img and not self._update_pending:
                        # Convert to PhotoImage in background thread
                        photo = ImageTk.PhotoImage(img)
                        self._update_pending = True
                        # Schedule canvas update on the main thread
                        self.root.after(0, self._apply_frame, photo)
                except Exception as e:
                    print(f"Update error: {e}")
                finally:
                    elapsed = time.monotonic() - frame_start
                    sleep_time = self.frame_interval - elapsed
                    if sleep_time > 0:
                        time.sleep(sleep_time)
        finally:
            # Clean up mss in the same thread where it was created
            if self.sct:
                try:
                    self.sct.close()
                except:
                    pass
    
    def _apply_frame(self, photo):
        """Apply a captured frame to the canvas (must run on main thread)"""
        if self.canvas_image_id is None:
            self.canvas_image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        else:
            self.canvas.itemconfig(self.canvas_image_id, image=photo)
        self.canvas.image = photo
        self._update_pending = False

    def on_closing(self):
        """Handle window close event"""
        self.running = False
        # Wait for update thread to finish and clean up
        if hasattr(self, 'update_thread') and self.update_thread.is_alive():
            self.update_thread.join(timeout=1.0)
        self.root.destroy()


def main():
    root = tk.Tk()
    app = MagnifierApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
