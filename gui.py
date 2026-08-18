import tkinter
import customtkinter

customtkinter.set_appearance_mode("System")  
customtkinter.set_default_color_theme("blue")

app = None
slider_vars = {}


def doesExist():
    global app
    if app is None:
        app = customtkinter.CTk()
        app.geometry("420x260")
        app.title("Controller Settings")
    return app

def sliderRendering(key, txtlabel, initVal, minVal, maxVal):        # Control name, initial value, min/max range
    current_app = doesExist()
    slider_var = tkinter.DoubleVar(value=float(initVal))
    step_count = max(1, int(round((float(maxVal) - float(minVal)) / 0.01)))

    #to keep valDisplay and textLabel on same line
    label_frame = customtkinter.CTkFrame(current_app, fg_color="transparent")
    label_frame.pack(padx=10, pady=10)

    textLabel = customtkinter.CTkLabel(label_frame, text=str(txtlabel+": "))   
    textLabel.pack(side="left")
    valDisplay = customtkinter.CTkLabel(label_frame, text=f"{float(initVal):.2f}")
    valDisplay.pack(side="left", padx=(5, 0))

    def slider_val(value):
        snapped_value = round(float(value), 2)
        slider_var.set(snapped_value)
        valDisplay.configure(text=f"{snapped_value:.2f}")

    slider = customtkinter.CTkSlider(
        current_app,
        command=slider_val,
        from_=float(minVal),  # type: ignore[arg-type]
        to=float(maxVal),  # type: ignore[arg-type]
        variable=slider_var,
        number_of_steps=step_count
    )
    slider.pack(padx=10, pady=10)
    slider.set(float(initVal))
    slider_vars[key] = slider_var
    return slider


def get_slider_value(key):
    slider_var = slider_vars.get(key)
    if slider_var is None:
        raise KeyError(f"Unknown slider key: {key}")
    return round(float(slider_var.get()), 2)


def process_gui():
    if app is None:
        return
    app.update_idletasks()
    app.update()

def close_gui():
    global app
    if app is not None:
        app.destroy()
        app = None
