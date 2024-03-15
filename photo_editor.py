from tkinter import filedialog, Button, Frame, Tk, Canvas, BooleanVar, Entry, Checkbutton, ttk, END, HORIZONTAL, Scale
from PIL import Image, ImageTk
import numpy as np
import cv2


class PhotoEditor:
    def __init__(self, window: Tk) -> None:
        self.window = window
        self.window.title("Shimp")
        self.image_states = []  # Initialize the stack for image states
        self.original_image = None
        self.display_image = None
        self.temp_image = None
        self.canvas = None
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.maintain_aspect_ratio = BooleanVar(value=False)
        self.setup_ui()

    def setup_ui(self):
        self.window.config(padx=50, pady=50, bg="lightblue")
        self.ui_frame = Frame(self.window, bg="lightblue")
        self.ui_frame.pack(expand=True, fill="both")

        # Configure the grid layout to make the image display area expandable
        self.ui_frame.grid_columnconfigure(1, weight=1)  # Make the column containing the canvas expandable
        self.ui_frame.grid_rowconfigure(0, weight=1)     # Make the rows containing the canvas expandable
        self.ui_frame.grid_rowconfigure(1, weight=1)
        self.ui_frame.grid_rowconfigure(2, weight=1) 
        self.ui_frame.grid_rowconfigure(3, weight=0) 
        self.ui_frame.grid_rowconfigure(4, weight=0) 
        self.ui_frame.grid_rowconfigure(5, weight=0)
        self.ui_frame.grid_rowconfigure(6, weight=1) 
        self.ui_frame.grid_rowconfigure(7, weight=1) 
        self.ui_frame.grid_rowconfigure(8, weight=1) 
        self.ui_frame.grid_rowconfigure(9, weight=1)   
        self.ui_frame.grid_rowconfigure(10, weight=1)  
        self.ui_frame.grid_rowconfigure(11, weight=1)  
        self.ui_frame.grid_rowconfigure(12, weight=1)  
        self.ui_frame.grid_rowconfigure(13, weight=1)  
        self.ui_frame.grid_rowconfigure(14, weight=1)  
        self.ui_frame.grid_rowconfigure(15, weight=1)  
        self.ui_frame.grid_rowconfigure(16, weight=1) 
        self.ui_frame.grid_rowconfigure(17, weight=1) 

        # Canvas for image display
        self.canvas = Canvas(self.ui_frame, bg="lightblue")
        self.canvas.grid(row=0, column=1, rowspan=18, sticky="nsew")

        # Open image button UI
        self.open_image_btn = Button(self.ui_frame, text="Open Image", command=self.open_image, bg="lemonchiffon", fg="black")
        self.open_image_btn.grid(row=0, column=0, sticky="nsew")

        # Crop button UI
        self.crop_btn = Button(self.ui_frame, text="Crop", command=self.crop_image, bg="plum", fg="black")
        self.crop_btn.grid(row=1, column=0, sticky="nsew")

        # Undo button UI
        self.undo_btn = Button(self.ui_frame, text="Undo Crop", command=self.undo_crop, bg="lightcoral", fg="black")
        self.undo_btn.grid(row=2, column=0, sticky="nsew")

        # Entry for width with placeholder
        self.width_entry = Entry(self.ui_frame, bg="white", fg="black")
        self.width_entry.grid(row=3, column=0, sticky="nsew", padx=5)
        self.set_placeholder(self.width_entry, "Width")

        # Entry for height with placeholder
        self.height_entry = Entry(self.ui_frame, bg="white", fg="black")
        self.height_entry.grid(row=4, column=0, sticky="nsew", padx=5)
        self.set_placeholder(self.height_entry, "Height")

        # Aspect ratio checkbutton UI
        self.aspect_ratio_btn = Checkbutton(self.ui_frame, text="Maintain Aspect Ratio", var=self.maintain_aspect_ratio, bg="lightblue", fg="black", command=self.toggle_aspect_ratio)
        self.aspect_ratio_btn.grid(row=5, column=0, sticky="nsew", padx=5)

        # Resize button UI
        self.resize_btn = Button(self.ui_frame, text="Resize", command=self.resize_image, bg="pink", fg="black")
        self.resize_btn.grid(row=6, column=0, sticky="nsew", padx=5)

        # Rotate button UI
        self.rotate_btn = Button(self.ui_frame, text="Rotate 90°", command=self.rotate_image, bg="thistle", fg="black")
        self.rotate_btn.grid(row=7, column=0, sticky="nsew", padx=5)

        # Horizontal Flip button UI
        self.flip_btn = Button(self.ui_frame, text="Flip Horizontal", command=self.flip_image_horizontal, bg="peachpuff", fg="black")
        self.flip_btn.grid(row=8, column=0, sticky="nsew", padx=5)

        # Vertical Flip button UI
        self.flip_btn = Button(self.ui_frame, text="Flip Vertical", command=self.flip_image_vertical, bg="peachpuff", fg="black")
        self.flip_btn.grid(row=9, column=0, sticky="nsew", padx=5)

        # Brightness slider
        self.brightness_slider = Scale(self.ui_frame, from_=-100, to=100, orient=HORIZONTAL, label="Brightness", command=self.update_brightness_contrast)
        self.brightness_slider.set(0)  # Default value
        self.brightness_slider.grid(row=10, column=0, sticky="nsew")

        # Contrast slider
        self.contrast_slider = Scale(self.ui_frame, from_=1, to=3, resolution=0.01, orient=HORIZONTAL, label="Contrast", command=self.update_brightness_contrast)
        self.contrast_slider.set(1)  # Default value
        self.contrast_slider.grid(row=11, column=0, sticky="nsew")

        # Saturation slider
        self.saturation_slider = Scale(self.ui_frame, from_=0, to=2, resolution=0.01, orient=HORIZONTAL, label="Saturation", command=self.update_saturation_hue)
        self.saturation_slider.set(1)  # Default value (no change)
        self.saturation_slider.grid(row=12, column=0, sticky="nsew")

        # Hue slider
        self.hue_slider = Scale(self.ui_frame, from_=-180, to=180, orient=HORIZONTAL, label="Hue", command=self.update_saturation_hue)
        self.hue_slider.set(0)  # Default value (no change)
        self.hue_slider.grid(row=13, column=0, sticky="nsew")


        # Button for applying the painting effect
        self.painting_btn = Button(self.ui_frame, text="Apply Painting Effect", command=self.apply_painting_effect, bg="lightpink", fg="black")
        self.painting_btn.grid(row=14, column=0, sticky="nsew", padx=5)

        # Button for applying the sketching effect
        self.sketch_btn = Button(self.ui_frame, text="Apply Sketch Effect", command=self.apply_sketch_effect, bg="lightpink", fg="black")
        self.sketch_btn.grid(row=15, column=0, sticky="nsew", padx=5)


        # Reset button UI
        self.clear_btn = Button(self.ui_frame, text="Reset", command=self.reset_adjustments, bg="lightcoral", fg="black")
        self.clear_btn.grid(row=16, column=0, sticky="nsew", padx=5)


        # Save button UI
        self.save_btn = Button(self.ui_frame, text="Save", command=self.save_image, bg="lightgreen", fg="black")
        self.save_btn.grid(row=17, column=0, sticky="nsew", padx=5)


        # Bind canvas events for cropping
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)


    def open_image(self):
        image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")])
        if image_path:
            self.original_image = Image.open(image_path)
            self.display_image = self.original_image.copy()
            self.update_image_display()

    def update_image_display(self):
        self.canvas.delete("all")  # Clear the canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        img_width, img_height = self.display_image.size
        scale_width = canvas_width / img_width
        scale_height = canvas_height / img_height
        scale = min(scale_width, scale_height)

        # If the image is larger than the canvas, resize it to fit, otherwise keep original size
        if scale < 1:
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            resized_image = self.display_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        else:
            resized_image = self.display_image

        self.temp_image = ImageTk.PhotoImage(resized_image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.temp_image)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))


    def on_press(self, event):
        # Start point for the crop rectangle
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        # Create rectangle (if not yet created)
        if not self.rect:
            self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')

    def on_drag(self, event):
        # Update the rectangle's end coords as we drag the mouse
        self.end_x = self.canvas.canvasx(event.x)
        self.end_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, self.end_x, self.end_y)

    def on_release(self, event):
        # Define actions on mouse release if necessary
        pass

    def crop_image(self):
        if not all([self.start_x, self.start_y, self.end_x, self.end_y]):
            return  # Check for valid crop coordinates
        
        # Save the current state before cropping
        self.image_states.append(self.display_image.copy())

        self.original_image = self.display_image.copy()

        self.apply_crop()

    def apply_crop(self):
        
        # Calculate the scaling factor
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        img_width, img_height = self.original_image.size
        scale_width = canvas_width / img_width
        scale_height = canvas_height / img_height
        scale = min(scale_width, scale_height)
        
        # Reverse scaling factor to map coordinates back to the original image
        if scale < 1:
            reverse_scale_x = 1 / scale
            reverse_scale_y = 1 / scale
        else:
            reverse_scale_x = 1
            reverse_scale_y = 1
        
        # Adjusting coordinates with reverse scaling
        adjusted_start_x = int(self.start_x * reverse_scale_x)
        adjusted_start_y = int(self.start_y * reverse_scale_y)
        adjusted_end_x = int(self.end_x * reverse_scale_x)
        adjusted_end_y = int(self.end_y * reverse_scale_y)
        
        # Adjusting because of canvas scrollregion
        crop_area = (adjusted_start_x, adjusted_start_y, adjusted_end_x, adjusted_end_y)
        self.display_image = self.original_image.crop(crop_area)
        self.update_image_display()

    def undo_crop(self):
        if self.image_states:
            # Revert to the last saved state
            self.display_image = self.image_states.pop()
            self.update_image_display()

            # Reset the crop rectangle and related attributes
            if self.rect:
                self.canvas.delete(self.rect)
                self.rect = None
            self.start_x = None
            self.start_y = None
            self.end_x = None
            self.end_y = None
        else:
            print("No more undo steps available.")

    def rotate_image(self):
        """Rotates the current image by 90 degrees."""
        if self.display_image:
            self.display_image = self.display_image.rotate(-90, expand=True)
            self.original_image = self.display_image.copy()
            self.update_image_display()
        else:
            print("No image to load")

    def flip_image_horizontal(self):
        """Flips the current image horizontally."""
        if self.display_image:
            self.display_image = self.display_image.transpose(Image.FLIP_LEFT_RIGHT)
            self.original_image = self.display_image.copy()
            self.update_image_display()
        else:
            print("No image to load")

    def flip_image_vertical(self):
        """Flips the current image vertically."""
        if self.display_image:
            self.display_image = self.display_image.transpose(Image.FLIP_TOP_BOTTOM)
            self.original_image = self.display_image.copy()
            self.update_image_display()
        else:
            print("No image to load")


    def resize_image(self):
        if not self.display_image:
            print("No image to load")
            return  # Ensures there's an image loaded before proceeding.

        new_width, new_height = 0, 0  # Initialize new dimensions to zero

        try:
            # Convert entry values to integers, using 0 as default if conversion fails or entries are empty.
            input_width = int(self.width_entry.get()) if self.width_entry.get() else 0
            input_height = int(self.height_entry.get()) if self.height_entry.get() else 0

            if self.maintain_aspect_ratio.get() and input_width > 0:
                # Maintain aspect ratio based on width input only, as height entry is disabled in this mode.
                aspect_ratio = self.original_image.width / self.original_image.height
                new_width = input_width
                new_height = int(new_width / aspect_ratio)
            elif not self.maintain_aspect_ratio.get() and input_width > 0 and input_height > 0:
                # Use both width and height inputs directly when not maintaining aspect ratio.
                new_width = input_width
                new_height = input_height
            else:
                print("Please enter valid width and height values.")
                return
        except ValueError:
            print("Invalid input. Please enter numeric values.")
            return

        # Resize the image and update the display, ensuring new dimensions are greater than zero.
        if new_width > 0 and new_height > 0:
            self.display_image = self.display_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.original_image = self.display_image.copy()
            self.update_image_display()
        else:
            print("Invalid dimensions for resizing.")

    
    def toggle_aspect_ratio(self):
        # toggle behavior to correctly enable/disable height entry
        if self.maintain_aspect_ratio.get():
            self.height_entry.config(state='disabled')
        else:
            self.height_entry.config(state='normal')

    
    def set_placeholder(self, entry, text):
        entry.delete(0, END)  # Ensure any existing text is cleared first
        entry.insert(0, text)
        entry.config(fg='grey')
        entry.bind("<FocusIn>", lambda e: self.clear_placeholder(e, text))
        entry.bind("<FocusOut>", lambda e: self.add_placeholder(e, text))
    
    def clear_placeholder(self, event, placeholder):
        if event.widget.get() == placeholder and event.widget.cget('fg') == 'grey':
            event.widget.delete(0, END)
            event.widget.config(fg='black')

    def add_placeholder(self, event, placeholder):
        if not event.widget.get():
            event.widget.insert(0, placeholder)
            event.widget.config(fg='grey')

    def update_brightness_contrast(self, event=None):
        if self.display_image:
            # Convert PIL Image to OpenCV format
            cv_image = cv2.cvtColor(np.array(self.display_image), cv2.COLOR_RGB2BGR)
            
            # Get current values of the sliders
            brightness = self.brightness_slider.get()
            contrast = self.contrast_slider.get()

            # Apply brightness and contrast (alpha is contrast, beta is brightness)
            adjusted = cv2.convertScaleAbs(cv_image, alpha=contrast, beta=brightness)

            # Convert back to PIL Image and update the display
            self.display_image = Image.fromarray(cv2.cvtColor(adjusted, cv2.COLOR_BGR2RGB))
            self.original_image = self.display_image.copy()
            self.update_image_display()

    def update_saturation_hue(self, event=None):
        if self.display_image:
            # Convert PIL Image to OpenCV format in BGR color space
            cv_image = cv2.cvtColor(np.array(self.display_image), cv2.COLOR_RGB2BGR)

            # Convert BGR to HSV
            hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

            # Adjust Hue and Saturation
            hue_shift = self.hue_slider.get()
            saturation_scale = self.saturation_slider.get()

            # Adding the hue shift, ensuring values wrap correctly around 180
            hsv_image[:, :, 0] = (hsv_image[:, :, 0].astype(int) + hue_shift) % 180

            # Scaling the saturation, ensuring values stay within the 0-255 range
            hsv_image[:, :, 1] = np.clip(hsv_image[:, :, 1].astype(float) * saturation_scale, 0, 255).astype(np.uint8)

            # Convert back to BGR and then to RGB
            bgr_adjusted = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
            rgb_adjusted = cv2.cvtColor(bgr_adjusted, cv2.COLOR_BGR2RGB)

            # Convert back to PIL Image and update the display
            self.display_image = Image.fromarray(rgb_adjusted)
            self.original_image = self.display_image.copy()
            self.update_image_display()

    def apply_painting_effect(self):
        if self.display_image:
            # Convert PIL Image to OpenCV format
            cv_image = cv2.cvtColor(np.array(self.display_image), cv2.COLOR_RGB2BGR)

            # Apply the painting effect
            output = cv2.stylization(cv_image, sigma_s=60, sigma_r=0.6)

            # Convert back to PIL Image and update the display
            self.display_image = Image.fromarray(cv2.cvtColor(output, cv2.COLOR_BGR2RGB))
            self.original_image = self.display_image.copy()
            self.update_image_display()

    def apply_sketch_effect(self):
        if self.display_image:
            # Convert PIL Image to OpenCV format
            cv_image = cv2.cvtColor(np.array(self.display_image), cv2.COLOR_RGB2BGR)

            # Apply the sketch effect
            output, _ = cv2.pencilSketch(cv_image, sigma_s=60, sigma_r=0.07, shade_factor=0.05)

            # Convert back to PIL Image and update the display
            self.display_image = Image.fromarray(cv2.cvtColor(output, cv2.COLOR_BGR2RGB))
            self.original_image = self.display_image.copy()
            self.update_image_display()


    def reset_adjustments(self):
        # Reset sliders to their default values
        self.brightness_slider.set(0)
        self.contrast_slider.set(1)
        self.saturation_slider.set(1)
        self.hue_slider.set(0)
        
        # Reset transformations by reverting to the original image
        if self.original_image:
            self.display_image = self.original_image.copy()
            self.update_image_display()

        # Reset the crop rectangle and related attributes
        if self.rect:
            self.canvas.delete(self.rect)
            self.rect = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None

        # Reset any additional UI elements or states in future as required
        # For example, if we have UI elements or variables tracking the rotation/flipping state, reset them here
        # Example:
        # self.rotation_angle = 0
        # self.is_flipped_horizontally = False
        # self.is_flipped_vertically = False
        
        # Update the canvas or image display if any additional reset actions were taken


    def save_image_to_file(self, image):
        """Saves the current image state to a file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                filetypes=[("PNG files", "*.png"),
                                                            ("JPEG files", "*.jpg;*.jpeg"),
                                                            ("All files", "*.*")])
        if file_path:
            # Determine the file format based on the file extension
            file_format = 'PNG'  # Default format
            if file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
                file_format = 'JPEG'
            # Save the image
            image.save(file_path, format=file_format)

    def save_image(self):
        """Handles the save button click event."""
        if self.display_image:  # Ensure there's an image loaded
            self.save_image_to_file(self.display_image)
        else:
            print("No image to save")
