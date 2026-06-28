# ============================================================
#   UNIT CONVERTER PRO — Ultra Pro Max GUI
#   Author  : Jatoi
#   Library : CustomTkinter (Modern Python GUI)
#   Run     : python unit_converter_gui.py
# ============================================================

import customtkinter as ctk
from tkinter import StringVar, messagebox

# ── App Theme ──────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Conversion Data ────────────────────────────────────────
CATEGORIES = {
    "📏  Length": {
        "units": ["Meter (m)", "Kilometer (km)", "Centimeter (cm)",
                  "Millimeter (mm)", "Mile (mi)", "Foot (ft)",
                  "Inch (in)", "Yard (yd)"],
        "keys":  ["m", "km", "cm", "mm", "mi", "ft", "in", "yd"],
        "toBase": {"m":1, "km":1000, "cm":0.01, "mm":0.001,
                   "mi":1609.344, "ft":0.3048, "in":0.0254, "yd":0.9144}
    },
    "⚖️  Weight": {
        "units": ["Kilogram (kg)", "Gram (g)", "Milligram (mg)",
                  "Pound (lb)", "Ounce (oz)", "Tonne (t)"],
        "keys":  ["kg", "g", "mg", "lb", "oz", "t"],
        "toBase": {"kg":1, "g":0.001, "mg":0.000001,
                   "lb":0.453592, "oz":0.0283495, "t":1000}
    },
    "🌡️  Temperature": {
        "units": ["Celsius (°C)", "Fahrenheit (°F)", "Kelvin (K)"],
        "keys":  ["c", "f", "k"],
        "toBase": None  # special handling
    },
    "🚀  Speed": {
        "units": ["km/h", "m/s", "mph", "Knot (kn)", "ft/s"],
        "keys":  ["kmh", "ms", "mph", "kn", "fts"],
        "toBase": {"kmh":1/3.6, "ms":1, "mph":0.44704,
                   "kn":0.514444, "fts":0.3048}
    },
}

# ── Conversion Logic ───────────────────────────────────────
def convert_value(cat_name, val, from_key, to_key):
    cat = CATEGORIES[cat_name]

    if "Temperature" in cat_name:
        f, t = from_key, to_key
        if f == t:
            return val, "Same unit"
        formulas = {
            ("c","f"): (lambda v: (v*9/5)+32,     lambda v: f"({v} × 9/5) + 32"),
            ("f","c"): (lambda v: (v-32)*5/9,     lambda v: f"({v} − 32) × 5/9"),
            ("c","k"): (lambda v: v+273.15,        lambda v: f"{v} + 273.15"),
            ("k","c"): (lambda v: v-273.15,        lambda v: f"{v} − 273.15"),
            ("f","k"): (lambda v: (v-32)*5/9+273.15, lambda v: f"({v}−32)×5/9 + 273.15"),
            ("k","f"): (lambda v: (v-273.15)*9/5+32, lambda v: f"({v}−273.15)×9/5+32"),
        }
        fn, fm = formulas[(f, t)]
        result = fn(val)
        formula = fm(val)
        return result, formula

    base     = cat["toBase"]
    in_base  = val * base[from_key]
    result   = in_base / base[to_key]
    formula  = f"{val} × {base[from_key]} ÷ {base[to_key]}"
    return result, formula


def smart_round(n):
    if not isinstance(n, (int, float)):
        return n
    abs_n = abs(n)
    if abs_n == 0:
        return 0
    if abs_n < 0.000001 or abs_n > 1e12:
        return f"{n:.4e}"
    if abs_n >= 1000:
        return round(n, 3)
    return round(n, 6)


# ── Main App ───────────────────────────────────────────────
class UnitConverterApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Unit Converter Pro — by Jatoi")
        self.geometry("620x720")
        self.resizable(False, False)
        self.configure(fg_color="#0a0a14")

        self.current_cat = list(CATEGORIES.keys())[0]
        self.history     = []

        self._build_ui()
        self._load_category(self.current_cat)

    # ── BUILD UI ──────────────────────────────────────────
    def _build_ui(self):

        # ── HEADER ──
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(28, 8), padx=30, fill="x")

        badge = ctk.CTkLabel(
            header_frame,
            text="  ⚡ ULTRA PRO MAX  ",
            font=ctk.CTkFont("Inter", 11, "bold"),
            text_color="#a78bfa",
            fg_color="#1e1240",
            corner_radius=99,
        )
        badge.pack()

        ctk.CTkLabel(
            header_frame,
            text="Unit Converter Pro",
            font=ctk.CTkFont("Inter", 30, "bold"),
            text_color="#eeeeff",
        ).pack(pady=(10, 2))

        ctk.CTkLabel(
            header_frame,
            text="Fast  ·  Precise  ·  Professional",
            font=ctk.CTkFont("Inter", 13),
            text_color="#555577",
        ).pack()

        # ── CATEGORY TABS ──
        tab_frame = ctk.CTkFrame(self, fg_color="#10101a", corner_radius=16)
        tab_frame.pack(pady=(18, 0), padx=30, fill="x")

        self.tab_buttons = {}
        for cat in CATEGORIES:
            btn = ctk.CTkButton(
                tab_frame,
                text=cat,
                font=ctk.CTkFont("Inter", 13, "bold"),
                height=40,
                corner_radius=10,
                fg_color="transparent",
                hover_color="#1e1e30",
                text_color="#666688",
                command=lambda c=cat: self._load_category(c),
            )
            btn.pack(side="left", padx=6, pady=6, expand=True, fill="x")
            self.tab_buttons[cat] = btn

        # ── MAIN CARD ──
        self.card = ctk.CTkFrame(
            self,
            fg_color="#13131f",
            corner_radius=22,
            border_width=1,
            border_color="#22223a",
        )
        self.card.pack(pady=18, padx=30, fill="both", expand=True)

        inner = self.card
        pad   = {"padx": 26}

        # FROM / TO ROW
        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack(fill="x", pady=(24, 0), **pad)

        # From
        from_col = ctk.CTkFrame(row, fg_color="transparent")
        from_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(from_col, text="FROM", font=ctk.CTkFont("Inter", 10, "bold"),
                     text_color="#555577").pack(anchor="w")
        self.from_var = StringVar()
        self.from_menu = ctk.CTkOptionMenu(
            from_col,
            variable=self.from_var,
            values=[],
            font=ctk.CTkFont("Inter", 13),
            dropdown_font=ctk.CTkFont("Inter", 13),
            fg_color="#0b0b18",
            button_color="#7c6af7",
            button_hover_color="#6c5ae7",
            corner_radius=10,
            height=42,
            command=lambda _: self._on_unit_change(),
        )
        self.from_menu.pack(fill="x", pady=(5, 0))

        # Swap Button
        swap_col = ctk.CTkFrame(row, fg_color="transparent")
        swap_col.pack(side="left", padx=10, pady=(18, 0))
        ctk.CTkButton(
            swap_col, text="⇄",
            width=46, height=42,
            font=ctk.CTkFont("Inter", 20),
            fg_color="#1a1a2e",
            hover_color="#7c6af7",
            corner_radius=10,
            command=self._swap_units,
        ).pack()

        # To
        to_col = ctk.CTkFrame(row, fg_color="transparent")
        to_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(to_col, text="TO", font=ctk.CTkFont("Inter", 10, "bold"),
                     text_color="#555577").pack(anchor="w")
        self.to_var = StringVar()
        self.to_menu = ctk.CTkOptionMenu(
            to_col,
            variable=self.to_var,
            values=[],
            font=ctk.CTkFont("Inter", 13),
            dropdown_font=ctk.CTkFont("Inter", 13),
            fg_color="#0b0b18",
            button_color="#7c6af7",
            button_hover_color="#6c5ae7",
            corner_radius=10,
            height=42,
            command=lambda _: self._on_unit_change(),
        )
        self.to_menu.pack(fill="x", pady=(5, 0))

        # VALUE INPUT
        ctk.CTkLabel(inner, text="ENTER VALUE",
                     font=ctk.CTkFont("Inter", 10, "bold"),
                     text_color="#555577").pack(anchor="w", pady=(20, 0), **pad)

        self.value_entry = ctk.CTkEntry(
            inner,
            placeholder_text="0",
            font=ctk.CTkFont("Space Grotesk", 30, "bold"),
            height=64,
            corner_radius=14,
            fg_color="#0b0b18",
            border_color="#22223a",
            border_width=1,
            text_color="#eeeeff",
        )
        self.value_entry.pack(fill="x", pady=(6, 0), **pad)
        self.value_entry.bind("<Return>", lambda e: self._convert())
        self.value_entry.bind("<KP_Enter>", lambda e: self._convert())

        self.error_label = ctk.CTkLabel(
            inner, text="",
            font=ctk.CTkFont("Inter", 12),
            text_color="#f87171",
        )
        self.error_label.pack(anchor="w", **pad)

        # CONVERT BUTTON
        ctk.CTkButton(
            inner,
            text="⚡  Convert Now",
            font=ctk.CTkFont("Inter", 15, "bold"),
            height=52,
            corner_radius=14,
            fg_color="#7c6af7",
            hover_color="#6c5ae7",
            command=self._convert,
        ).pack(fill="x", pady=(14, 0), **pad)

        # RESULT BOX
        self.result_frame = ctk.CTkFrame(
            inner,
            fg_color="#0b0b18",
            corner_radius=14,
            border_width=1,
            border_color="#22223a",
        )
        self.result_frame.pack(fill="x", pady=(16, 0), **pad)

        ctk.CTkLabel(self.result_frame, text="RESULT",
                     font=ctk.CTkFont("Inter", 10, "bold"),
                     text_color="#555577").pack(anchor="w", padx=18, pady=(14, 0))

        self.result_label = ctk.CTkLabel(
            self.result_frame,
            text="Enter a value and press Convert",
            font=ctk.CTkFont("Space Grotesk", 26, "bold"),
            text_color="#333355",
            wraplength=480,
        )
        self.result_label.pack(anchor="w", padx=18, pady=(4, 14))

        # FORMULA
        self.formula_label = ctk.CTkLabel(
            inner, text="",
            font=ctk.CTkFont("Space Grotesk", 12),
            text_color="#34d399",
            fg_color="#0d2a1e",
            corner_radius=8,
        )

        # HISTORY
        ctk.CTkLabel(inner, text="RECENT CONVERSIONS",
                     font=ctk.CTkFont("Inter", 10, "bold"),
                     text_color="#555577").pack(anchor="w", pady=(18, 0), **pad)

        self.history_frame = ctk.CTkScrollableFrame(
            inner,
            fg_color="#0b0b18",
            corner_radius=12,
            height=100,
            border_width=1,
            border_color="#22223a",
        )
        self.history_frame.pack(fill="x", pady=(6, 20), **pad)

        self.history_placeholder = ctk.CTkLabel(
            self.history_frame,
            text="No conversions yet...",
            font=ctk.CTkFont("Inter", 12),
            text_color="#333355",
        )
        self.history_placeholder.pack(pady=8)

        # FOOTER
        ctk.CTkLabel(
            self,
            text="Unit Converter Pro  ·  Built by Jatoi  ·  Python + CustomTkinter  ·  2025",
            font=ctk.CTkFont("Inter", 11),
            text_color="#2a2a3a",
        ).pack(pady=(0, 12))

    # ── LOAD CATEGORY ─────────────────────────────────────
    def _load_category(self, cat):
        self.current_cat = cat

        # Highlight active tab
        for name, btn in self.tab_buttons.items():
            if name == cat:
                btn.configure(fg_color="#7c6af7", text_color="#ffffff")
            else:
                btn.configure(fg_color="transparent", text_color="#666688")

        data   = CATEGORIES[cat]
        units  = data["units"]

        self.from_menu.configure(values=units)
        self.to_menu.configure(values=units)

        self.from_var.set(units[0])
        self.to_var.set(units[1] if len(units) > 1 else units[0])

        self._clear_result()

    # ── UNIT CHANGE ───────────────────────────────────────
    def _on_unit_change(self):
        self._clear_result()

    # ── SWAP ──────────────────────────────────────────────
    def _swap_units(self):
        f = self.from_var.get()
        t = self.to_var.get()
        self.from_var.set(t)
        self.to_var.set(f)
        self._clear_result()

    # ── CONVERT ───────────────────────────────────────────
    def _convert(self):
        raw = self.value_entry.get().strip()

        # Validate
        try:
            val = float(raw)
        except ValueError:
            self.error_label.configure(text="❌ Please enter a valid number!")
            self.value_entry.configure(border_color="#f87171")
            return

        self.error_label.configure(text="")
        self.value_entry.configure(border_color="#22223a")

        cat     = self.current_cat
        data    = CATEGORIES[cat]
        f_label = self.from_var.get()
        t_label = self.to_var.get()

        # Get keys
        units  = data["units"]
        keys   = data["keys"]
        f_key  = keys[units.index(f_label)]
        t_key  = keys[units.index(t_label)]

        result, formula = convert_value(cat, val, f_key, t_key)
        rounded = smart_round(result)

        # Short unit labels
        f_short = f_label.split("(")[-1].replace(")", "") if "(" in f_label else f_label
        t_short = t_label.split("(")[-1].replace(")", "") if "(" in t_label else t_label

        # Show result
        self.result_frame.configure(border_color="#7c6af7")
        self.result_label.configure(
            text=f"{rounded}  {t_short}",
            text_color="#a78bfa",
        )

        # Formula
        self.formula_label.configure(
            text=f"  🔢  Formula: {formula} = {rounded}  "
        )
        self.formula_label.pack(fill="x", padx=26, pady=(0, 0))

        # History
        entry = f"  🔁  {val} {f_short}  →  {rounded} {t_short}"
        self._add_history(entry)

    # ── CLEAR RESULT ──────────────────────────────────────
    def _clear_result(self):
        self.result_label.configure(
            text="Enter a value and press Convert",
            text_color="#333355",
        )
        self.result_frame.configure(border_color="#22223a")
        self.formula_label.configure(text="")
        self.formula_label.pack_forget()
        self.error_label.configure(text="")
        self.value_entry.configure(border_color="#22223a")

    # ── HISTORY ───────────────────────────────────────────
    def _add_history(self, entry):
        self.history.insert(0, entry)
        if len(self.history) > 8:
            self.history.pop()

        # Clear frame
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        for h in self.history:
            ctk.CTkLabel(
                self.history_frame,
                text=h,
                font=ctk.CTkFont("Inter", 13),
                text_color="#9999bb",
                anchor="w",
            ).pack(anchor="w", pady=3, padx=6)


# ── RUN ────────────────────────────────────────────────────
if __name__ == "__main__":
    app = UnitConverterApp()
    app.mainloop()
