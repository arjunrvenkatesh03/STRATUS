import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import scrolledtext
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import os
import numpy as np
import time

from pyhdf.SD import SD, SDC
from pyhdf.HDF import HDF, HC
from pyhdf.VS import *
from geopy.distance import geodesic
import matplotlib.colors as mcolors

###############################################################################
#                           Transmission Functions
###############################################################################

def parse_hdf_file_transmission(filename):
    """
    Expects a CALIPSO L2 05kmAPro/CPro HDF with Extinction_Coefficient_532.
    Returns data532, data1064=0, lat, long, alt, timeStamp, data532_Unc, data1064_Unc=0, flagCount_532.
    """
    hdf_CPro = SD(filename, SDC.READ)

    data532_CPro = hdf_CPro.select("Extinction_Coefficient_532").get()
    data532_CPro = np.clip(data532_CPro, -5555.0, 10.0)

    flagCount_532 = (
        np.sum(np.where(data532_CPro == -333.0, 1, 0)) +
        np.sum(np.where(data532_CPro == -444.0, 1, 0))
    )

    data532 = data532_CPro
    dataUnc532 = hdf_CPro.select("Extinction_Coefficient_Uncertainty_532").get()

    data1064 = 0
    dataUnc1064 = 0

    lat = hdf_CPro.select('Latitude').get().flatten()
    long = hdf_CPro.select('Longitude').get().flatten()

    # read altitude from metadata
    hdfFile = HDF(filename, HC.READ)
    vs = hdfFile.vstart()
    vd = vs.attach('metadata')
    rec = vd.read()
    alt = rec[0][-1]  # Typically 399 bins from -0.5 km to 30.1 km
    vd.detach()
    vs.end()
    hdfFile.close()

    # parse time
    timeStamp = hdf_CPro.select('Profile_UTC_Time').get()
    timeStamp = str(timeStamp[0]).split(".")[0]
    timeStamp = timeStamp[1:]
    timeStamp = f"{timeStamp[2:4]}/{timeStamp[4:6]}/{timeStamp[0:2]}"

    return data532, data1064, lat, long, alt, timeStamp, dataUnc532, dataUnc1064, flagCount_532

def lat_long_to_km(start_lat, start_long, end_lat, end_long):
    return geodesic((start_lat, start_long), (end_lat, end_long)).kilometers

def generate_normal(mean, std_dev, num_samples):
    return np.round(np.random.normal(loc=mean, scale=std_dev, size=num_samples)).astype(int)

def generate_random(min_val, max_val, num_samples):
    return np.round(np.random.randint(min_val, max_val, num_samples)).astype(int)

def generate_coordinates(mean, std_dev, min_val, max_val, num_samples):
    altIdx = generate_normal(mean, std_dev, num_samples)
    longlatIdx = generate_random(min_val, max_val, num_samples)
    return list(zip(longlatIdx, altIdx))

def sample_within_longitudinal_range_corrected(first_x, min_sep, max_sep, min_val, max_val):
    potential_xs = []
    for x in range(min_val, max_val + 1):
        separation = abs(x - first_x)
        if min_sep <= separation <= max_sep:
            potential_xs.append(x)
    return np.random.choice(potential_xs) if potential_xs else None

def generate_coordinate_pairs_trans(a1, a2, std_dev, min_val, max_val, num_paths, min_sep, max_sep):
    initial_sources = generate_coordinates(a1, std_dev, min_val, max_val, num_paths)
    final_sources = []
    dests = []
    for scoord in initial_sources:
        x_candidate = sample_within_longitudinal_range_corrected(
            scoord[0], min_sep, max_sep, min_val, max_val
        )
        if x_candidate is not None:
            alt_candidate = generate_normal(a2, std_dev, 1)[0]
            final_sources.append(scoord)
            dests.append((x_candidate, alt_candidate))
    return list(zip(final_sources, dests))

def bezier_curve(pair, n_points=30):
    (x0, y0), (x1, y1) = pair
    t = np.linspace(0, 1, n_points)
    x_vals = (1 - t)*x0 + t*x1
    y_vals = (1 - t)*y0 + t*y1
    coords = np.vstack([y_vals, x_vals]).T.astype(int)
    coords = coords[(coords[:,0]>=0)&(coords[:,1]>=0)]
    return coords

def transmission_sim_main(filepath, sourceAlt, logger=print):
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    start_time = time.time()
    logger("Reading and parsing HDF file (Cloud Profile)...")
    (data532, data1064, latitude, longitude, alt, timeStamp,
     data532_Unc, data1064_Unc, flagCount_532) = parse_hdf_file_transmission(filepath)

    logger("Calculating pixel width from latitude/longitude...")
    startLat, endLat = latitude[0], latitude[-1]
    startLong, endLong = longitude[0], longitude[-1]
    pixelWidth = lat_long_to_km(startLat, startLong, endLat, endLong) / data532.shape[1]

    logger(f"Using sourceAlt (array index) = {sourceAlt}")
    destAlt = sourceAlt
    num_paths = 1000
    std_dev = 3
    min_separation = 8
    max_separation = 12

    logger("Generating coordinate pairs for paths...")
    coordinatePairs = generate_coordinate_pairs_trans(
        sourceAlt, destAlt, std_dev,
        min_val=0, max_val=data532.shape[0]-1,  # CAREFUL if OOB
        num_paths=num_paths,
        min_sep=min_separation,
        max_sep=max_separation
    )

    logger("Creating paths via Bezier curves...")
    pathArray = []
    for pair in coordinatePairs:
        path = bezier_curve(pair)
        if path.shape[0] > 1:
            pathArray.append(path)

    data532 = np.rot90(data532)
    data532 = np.rot90(data532)
    data532_Unc = np.rot90(data532_Unc)
    data532_Unc = np.rot90(data532_Unc)

    logger("Summing extinction coefficients along each path...")
    extincCoefList532 = []
    extCoefUncList_532 = []
    transmissions_532 = []
    total_flagCount_532 = 0

    for path in pathArray:
        ext532_sum = 0.0
        unc532_sum = 0.0
        flagUsed = False
        out_of_bounds = False

        for (i, j) in path:
            # check bounds
            if i<0 or i>=data532.shape[0] or j<0 or j>=data532.shape[1]:
                out_of_bounds = True
                break
            val_532 = data532[i,j]
            if val_532 < 0:
                if not flagUsed:
                    total_flagCount_532 += 1
                    flagUsed = True
                val_532 = 0
            ext532_sum += val_532
            unc532_sum += data532_Unc[i,j]

        if out_of_bounds:
            continue

        extincCoefList532.append(ext532_sum)
        extCoefUncList_532.append(unc532_sum)

        # path length
        startCoord = path[0]
        endCoord   = path[-1]
        dAlt = endCoord[1] - startCoord[1]
        dHor = endCoord[0] - startCoord[0]
        pathLength = np.sqrt((dAlt*0.08)**2 + (dHor*5)**2)
        T_532 = np.exp(-ext532_sum * pathLength)
        transmissions_532.append(T_532)

    threshold = 0.9
    countAbove = sum(1 for t in transmissions_532 if t > threshold)
    percentageMean532 = countAbove / len(transmissions_532) if transmissions_532 else 0

    numPaths = len(pathArray)

    logger(f"Number of valid paths = {numPaths}")
    logger(f"Flagged coefficient count (negative ext. detection) = {total_flagCount_532}")
    logger(f"Fraction of transmissions > {threshold} = {percentageMean532:.3f}")

    logger("Plotting histogram of 532 nm transmissions...")
    fig, ax = plt.subplots(figsize=(6,4))
    ax.hist(transmissions_532, bins=40, range=(0,1), alpha=0.7, color='green')
    ax.set_title("Transmission at 532 nm")
    ax.set_xlabel("Transmission")
    ax.set_ylabel("Frequency")

    end_time = time.time()
    elapsed = end_time - start_time
    logger(f"Time elapsed: {elapsed:.2f} seconds (Transmission Simulation)")

    # Build a dictionary of stats for the analysis table
    stats_dict = {
        "Timestamp": timeStamp,
        "#Paths": f"{numPaths}",
        "Neg. Ext. Flags": f"{total_flagCount_532}",
        "Frac > 0.9": f"{percentageMean532:.3f}",
        "Time Elapsed (s)": f"{elapsed:.2f}"
    }

    return (
        fig, ax,
        transmissions_532,
        percentageMean532,
        total_flagCount_532,
        numPaths,
        timeStamp,
        stats_dict
    )

###############################################################################
#                          Backscatter Functions
###############################################################################

def parse_hdf_file_backscatter(filepath, logger=lambda *args: None):
    logger("  -> Checking HDF file for backscatter & altitude...")

    DATAFIELD_NAME = 'Total_Attenuated_Backscatter_532'
    hdf = SD(filepath, SDC.READ)

    data_532 = hdf.select(DATAFIELD_NAME).get()
    data_532 = np.rot90(data_532)
    data_532[data_532 == -9999] = 0

    alt = None
    all_sds = list(hdf.datasets().keys())
    if "Altitude" in all_sds:
        alt_candidate = hdf.select("Altitude").get()
        if alt_candidate.ndim == 1 and alt_candidate.size > 1:
            if alt_candidate[0] < alt_candidate[-1]:
                alt_candidate = alt_candidate[::-1]
            alt = alt_candidate

    if alt is None:
        nAlts = data_532.shape[0]
        alt = np.linspace(30.0, 0.0, nAlts)

    latitude = hdf.select('Latitude').get().flatten()
    longitude = hdf.select('Longitude').get().flatten()

    def avg_horz_data(data, N):
        nAlts = data.shape[0]
        nProfiles = latitude.shape[0]
        out = np.zeros((nAlts, nProfiles))
        for i in range(nProfiles - 1):
            out[:, i] = np.mean(data[:, i*N:(i+1)*N - 1], axis=1)
        return out

    x2 = len(longitude)
    averaging_width = int(x2 / 1000)
    averaging_width = max(5, min(averaging_width, 15))
    latitude = latitude[::averaging_width]

    avg_dataset = avg_horz_data(data_532, averaging_width)
    avg_dataset = np.clip(avg_dataset, 0, 0.11)

    highAlt  = avg_dataset[0:33, :]
    midAlt   = avg_dataset[33:88, :]
    lowAlt   = avg_dataset[88:288, :]
    highSurf = avg_dataset[288:578, :]
    lowSurf  = avg_dataset[578:, :]

    return highAlt, midAlt, lowAlt, highSurf, lowSurf, latitude, longitude, alt

def homogenize_pixels_backscatter(highAlt, midAlt, lowAlt, highSurf, lowSurf, alt):
    def resize_along_alt(original, new_shape):
        rows_orig, cols_orig = original.shape
        rows_target, _ = new_shape
        resized = np.zeros((rows_target, cols_orig))
        for c in range(cols_orig):
            resized[:, c] = np.interp(
                np.linspace(0, rows_orig, rows_target),
                np.linspace(0, rows_orig, rows_orig),
                original[:, c]
            )
        return resized

    targets = {
        'highAlt':  (33*10, highAlt.shape[1]),
        'midAlt':   (55*6,  midAlt.shape[1]),
        'lowAlt':   (200*2, lowAlt.shape[1]),
        'highSurf': (290,   highSurf.shape[1]),
        'lowSurf':  (5*10,  lowSurf.shape[1])
    }
    highAlt_rs  = resize_along_alt(highAlt,  targets['highAlt'])
    midAlt_rs   = resize_along_alt(midAlt,   targets['midAlt'])
    lowAlt_rs   = resize_along_alt(lowAlt,   targets['lowAlt'])
    highSurf_rs = resize_along_alt(highSurf, targets['highSurf'])
    lowSurf_rs  = resize_along_alt(lowSurf,  targets['lowSurf'])

    combinedData = np.concatenate(
        (highAlt_rs, midAlt_rs, lowAlt_rs, highSurf_rs, lowSurf_rs),
        axis=0
    )

    original_length = alt.size
    target_length   = combinedData.shape[0]
    x_original      = np.linspace(0, 1, original_length)
    x_target        = np.linspace(0, 1, target_length)
    alt_interp      = np.interp(x_target, x_original, alt)

    return combinedData, alt_interp

def backscatter_sim_main(filepath, logger=print):
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    start_time = time.time()

    logger("Reading and parsing HDF file...")
    (highAlt, midAlt, lowAlt, highSurf, lowSurf,
     latitude, longitude, alt) = parse_hdf_file_backscatter(filepath, logger=logger)

    logger("Homogenizing pixels...")
    parsedData, interpolatedAlt = homogenize_pixels_backscatter(
        highAlt, midAlt, lowAlt, highSurf, lowSurf, alt
    )

    # We'll compute minimal stats:
    min_val = float(np.min(parsedData))
    max_val = float(np.max(parsedData))
    shape_str = str(parsedData.shape)

    logger("Plotting results...")
    fig, ax = plt.subplots(figsize=(7,5))
    cmap = plt.cm.viridis

    levs = np.linspace(0, 0.11, 1000)
    norm = mcolors.Normalize(vmin=0, vmax=0.11)

    cs = ax.contourf(latitude, interpolatedAlt, parsedData, levels=levs, cmap=cmap, norm=norm)
    fig.colorbar(cs, ax=ax, spacing='uniform')
    ax.set_ylim(0, 30.1)
    ax.set_xlabel("Latitude")
    ax.set_ylabel("Altitude (km)")
    ax.set_title("CALIPSO Backscatter Simulation")

    end_time = time.time()
    elapsed = end_time - start_time
    logger(f"Time elapsed: {elapsed:.2f} seconds")

    stats_dict = {
        "Min Backscatter": f"{min_val:.4f}",
        "Max Backscatter": f"{max_val:.4f}",
        "Data Shape": shape_str,
        "Time Elapsed (s)": f"{elapsed:.2f}"
    }

    return fig, ax, parsedData, interpolatedAlt, latitude, [], stats_dict

###############################################################################
#                              MAIN GUI
###############################################################################

class StratusGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("STRATUS GUI - GA-ASI")
        self.geometry("1250x900")

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#2b2b2b")
        style.configure("TLabel",
                        background="#2b2b2b",
                        foreground="white",
                        font=("Helvetica", 11))
        style.configure("TButton",
                        background="#444",
                        foreground="white",
                        font=("Helvetica", 10, "bold"))
        style.map("TButton",
                  background=[("active", "#666")],
                  foreground=[("active", "white")])

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True)

        # Create frames for each tab
        self.learn_frame = ttk.Frame(self.notebook)
        self.backscatter_frame = ttk.Frame(self.notebook)
        self.transmission_frame = ttk.Frame(self.notebook)
        self.vfm_frame = ttk.Frame(self.notebook)
        self.info_frame = ttk.Frame(self.notebook)

        # Add tabs
        self.notebook.add(self.learn_frame, text="Welcome")
        self.notebook.add(self.backscatter_frame, text="Backscatter Simulation")
        self.notebook.add(self.transmission_frame, text="Transmission Simulation")
        self.notebook.add(self.vfm_frame, text="VFM Simulation")
        self.notebook.add(self.info_frame, text="More Info")

        # Build each tab
        self.build_learn_tab()
        self.build_backscatter_tab()
        self.build_transmission_tab()
        self.build_vfm_tab()
        self.build_info_tab()

    ###########################################################################
    # Backscatter Tab
    ###########################################################################
    def build_backscatter_tab(self):
        title_label = ttk.Label(self.backscatter_frame, text="CALIPSO Backscatter", font=("Helvetica", 14, "bold"))
        title_label.pack(pady=(5, 5))

        instructions = (
            "Instructions:\n"
            "1. Select a CALIPSO L1 Standard HDF file with 'Total_Attenuated_Backscatter_532'.\n"
            "2. Click 'Run Simulation' to see a 2D backscatter plot.\n\n"
            "Interpreting the Results:\n"
            " - The color scale (0.0 to ~0.11) reflects the intensity of backscatter.\n"
            " - Brighter areas may correspond to clouds or higher aerosol concentrations.\n"
            " - X-axis is Latitude, Y-axis is Altitude (km)."
        )
        instr_label = ttk.Label(self.backscatter_frame, text=instructions, font=("Helvetica", 10))
        instr_label.pack(padx=5, pady=2, anchor="w")

        top_bar = ttk.Frame(self.backscatter_frame)
        top_bar.pack(fill="x", pady=5)

        self.backscatter_file_label = ttk.Label(top_bar, text="No file selected.", width=60)
        self.backscatter_file_label.pack(side="left", padx=5)

        browse_button = ttk.Button(top_bar, text="Browse HDF File", command=self.browse_backscatter_file)
        browse_button.pack(side="left", padx=5)

        run_button = ttk.Button(top_bar, text="Run Simulation", command=self.run_backscatter_simulation)
        run_button.pack(side="left", padx=5)

        self.log_text_back = tk.Text(self.backscatter_frame, height=6, wrap="word", bg="#1e1e1e", fg="white")
        self.log_text_back.config(state="disabled")
        self.log_text_back.pack(fill="x", padx=5, pady=5)

        # Plot & Analysis area
        self.backscatter_plot_frame = ttk.Frame(self.backscatter_frame)
        self.backscatter_plot_frame.pack(fill="both", expand=True)

        # A frame for the stats table
        self.backscatter_stats_frame = ttk.Frame(self.backscatter_frame)
        self.backscatter_stats_frame.pack(fill="x", pady=5)

        self.backscatter_canvas = None

    def log_message_back(self, message):
        self.log_text_back.config(state="normal")
        self.log_text_back.insert(tk.END, message + "\n")
        self.log_text_back.see(tk.END)
        self.log_text_back.config(state="disabled")
        self.log_text_back.update()

    def browse_backscatter_file(self):
        filetypes = [("HDF Files", "*.hdf"), ("All Files", "*.*")]
        filepath = filedialog.askopenfilename(title="Select HDF File", filetypes=filetypes)
        if filepath:
            self.backscatter_file_label.config(text=filepath)
        else:
            self.backscatter_file_label.config(text="No file selected.")

    def run_backscatter_simulation(self):
        filepath = self.backscatter_file_label.cget("text")
        if (not filepath) or (not os.path.isfile(filepath)):
            messagebox.showerror("Error", "Please select a valid HDF file first.")
            return

        if self.backscatter_canvas:
            self.backscatter_canvas.get_tk_widget().destroy()
            self.backscatter_canvas = None

        # Clear old stats
        for widget in self.backscatter_stats_frame.winfo_children():
            widget.destroy()

        def gui_logger(msg):
            self.log_message_back(msg)

        try:
            fig, ax, parsedData, interpolatedAlt, latitude, paths, back_stats = backscatter_sim_main(filepath, logger=gui_logger)

            self.backscatter_canvas = FigureCanvasTkAgg(fig, master=self.backscatter_plot_frame)
            self.backscatter_canvas.draw()
            self.backscatter_canvas.get_tk_widget().pack(fill="both", expand=True)

            # Create a small stats table
            stats_label = ttk.Label(self.backscatter_stats_frame, text="Analysis Table:", font=("Helvetica", 11, "bold"))
            stats_label.pack(anchor="w", padx=5)

            table_frame = ttk.Frame(self.backscatter_stats_frame)
            table_frame.pack(anchor="w", padx=10, pady=3)
            row_idx = 0
            for key, val in back_stats.items():
                klabel = ttk.Label(table_frame, text=f"{key}:", font=("Helvetica", 10, "bold"))
                vlabel = ttk.Label(table_frame, text=str(val), font=("Helvetica", 10))
                klabel.grid(row=row_idx, column=0, sticky="w", padx=5)
                vlabel.grid(row=row_idx, column=1, sticky="w", padx=5)
                row_idx += 1

        except Exception as e:
            messagebox.showerror("Error", f"Backscatter simulation failed:\n{e}")

    ###########################################################################
    # Transmission Tab
    ###########################################################################
    def build_transmission_tab(self):
        title_label = ttk.Label(self.transmission_frame, text="CALIPSO Transmission", font=("Helvetica", 14, "bold"))
        title_label.pack(pady=(5, 5))

        instructions = (
            "Instructions:\n"
            "1. Select a CALIPSO L2 05kmAPro/CPro HDF with 'Extinction_Coefficient_532'.\n"
            "2. Specify a 'Source Alt (index)' – e.g. 240 ~ 60k ft (within 399 altitude bins).\n"
            "3. Click 'Run Transmission' to simulate paths & get a histogram of 532 nm Transmission.\n\n"
            "Interpreting the Results:\n"
            " - The histogram shows how many paths maintain a certain fraction of transmission.\n"
            " - 1.0 => no attenuation, 0 => fully attenuated.\n"
            " - The log shows fraction of paths above 0.9, negative-ext flags, etc."
        )
        instr_label = ttk.Label(self.transmission_frame, text=instructions, font=("Helvetica", 10))
        instr_label.pack(padx=5, pady=2, anchor="w")

        top_bar = ttk.Frame(self.transmission_frame)
        top_bar.pack(fill="x", pady=5)

        self.transmission_file_label = ttk.Label(top_bar, text="No file selected.", width=60)
        self.transmission_file_label.pack(side="left", padx=5)

        browse_button = ttk.Button(top_bar, text="Browse HDF File", command=self.browse_transmission_file)
        browse_button.pack(side="left", padx=5)

        alt_label = ttk.Label(top_bar, text="Source Alt (index):")
        alt_label.pack(side="left", padx=5)

        self.altitude_entry = ttk.Entry(top_bar, width=5)
        self.altitude_entry.insert(0, "240")
        self.altitude_entry.pack(side="left")

        run_button = ttk.Button(top_bar, text="Run Transmission", command=self.run_transmission_simulation)
        run_button.pack(side="left", padx=5)

        self.log_text_trans = tk.Text(self.transmission_frame, height=6, wrap="word", bg="#1e1e1e", fg="white")
        self.log_text_trans.config(state="disabled")
        self.log_text_trans.pack(fill="x", padx=5, pady=5)

        self.transmission_plot_frame = ttk.Frame(self.transmission_frame)
        self.transmission_plot_frame.pack(fill="both", expand=True)

        self.transmission_stats_frame = ttk.Frame(self.transmission_frame)
        self.transmission_stats_frame.pack(fill="x", pady=5)

        self.transmission_canvas = None

    def log_message_trans(self, message):
        self.log_text_trans.config(state="normal")
        self.log_text_trans.insert(tk.END, message + "\n")
        self.log_text_trans.see(tk.END)
        self.log_text_trans.config(state="disabled")
        self.log_text_trans.update()

    def browse_transmission_file(self):
        filetypes = [("HDF Files", "*.hdf"), ("All Files", "*.*")]
        filepath = filedialog.askopenfilename(title="Select HDF File", filetypes=filetypes)
        if filepath:
            self.transmission_file_label.config(text=filepath)
        else:
            self.transmission_file_label.config(text="No file selected.")

    def run_transmission_simulation(self):
        filepath = self.transmission_file_label.cget("text")
        if (not filepath) or (not os.path.isfile(filepath)):
            messagebox.showerror("Error", "Please select a valid HDF file first.")
            return

        if self.transmission_canvas:
            self.transmission_canvas.get_tk_widget().destroy()
            self.transmission_canvas = None

        for widget in self.transmission_stats_frame.winfo_children():
            widget.destroy()

        def gui_logger(msg):
            self.log_message_trans(msg)

        try:
            source_alt_str = self.altitude_entry.get()
            try:
                source_alt_val = int(source_alt_str)
            except ValueError:
                source_alt_val = 240

            (fig, ax, transmissions_532, percMean532, totalFlag,
             numPaths, timeStamp, trans_stats) = transmission_sim_main(
                 filepath, source_alt_val, logger=gui_logger
            )

            self.transmission_canvas = FigureCanvasTkAgg(fig, master=self.transmission_plot_frame)
            self.transmission_canvas.draw()
            self.transmission_canvas.get_tk_widget().pack(fill="both", expand=True)

            # Build stats table
            stats_label = ttk.Label(self.transmission_stats_frame, text="Analysis Table:", font=("Helvetica", 11, "bold"))
            stats_label.pack(anchor="w", padx=5)

            table_frame = ttk.Frame(self.transmission_stats_frame)
            table_frame.pack(anchor="w", padx=10, pady=3)
            row_idx = 0
            for k, v in trans_stats.items():
                klabel = ttk.Label(table_frame, text=f"{k}:", font=("Helvetica", 10, "bold"))
                vlabel = ttk.Label(table_frame, text=str(v), font=("Helvetica", 10))
                klabel.grid(row=row_idx, column=0, sticky="w", padx=5)
                vlabel.grid(row=row_idx, column=1, sticky="w", padx=5)
                row_idx += 1

        except Exception as e:
            messagebox.showerror("Error", f"Transmission simulation failed:\n{e}")

    ###########################################################################
    # VFM Tab
    ###########################################################################
    def build_vfm_tab(self):
        title_label = ttk.Label(self.vfm_frame, text="CALIPSO Vertical Feature Mask (VFM)", font=("Helvetica", 14, "bold"))
        title_label.pack(pady=(5, 5))

        banner_msg = (
            "UNDER CONSTRUCTION\n\n"
            "This VFM Simulation module is not ready yet.\n\n"
            "Planned features:\n"
            " - Parse L2 Vertical Feature Mask files\n"
            " - Identify cloud vs aerosol vs clear air\n"
            " - Simulate paths to estimate cloud encounter probability\n\n"
            "Stay tuned for updates!"
        )
        banner_label = ttk.Label(self.vfm_frame, text=banner_msg, font=("Helvetica", 10, "italic"), foreground="#ffcc00")
        banner_label.pack(padx=5, pady=15)

    ###########################################################################
    # Info Tab
    ###########################################################################
    def build_info_tab(self):
        info_text = scrolledtext.ScrolledText(self.info_frame, wrap="word", bg="#1e1e1e", fg="white")
        info_text.pack(fill="both", expand=True, padx=10, pady=10)

        overview_str = (
            "STRATUS GUI - Overview\n"
            "-----------------------------------\n"
            "This repository provides tools to:\n"
            " 1) Read and parse CALIPSO L1 files (backscatter)\n"
            "    and L2 05kmAPro/CPro files (extinction) or VFM files.\n"
            " 2) Homogenize pixel/voxel sizes for consistent simulations.\n"
            " 3) Sample random 'paths' through the data.\n"
            " 4) Perform path-based analytics (cloud encounters or transmission).\n\n"

            "Tabs:\n"
            "-----------------------------------\n"
            "Backscatter Simulation:\n"
            " - Needs L1 Standard data with 'Total_Attenuated_Backscatter_532'.\n"
            " - Displays a 2D cross-section (Latitude vs. Altitude).\n\n"
            "Transmission Simulation:\n"
            " - Needs L2 05kmAPro/CPro data with 'Extinction_Coefficient_532'.\n"
            " - Generates random paths, calculates Beer-Lambert transmission.\n"
            " - Plots a histogram of transmissions.\n\n"
            "VFM Simulation:\n"
            " - (Coming soon.) Will parse L2 VFM for cloud vs. clear classification.\n\n"
            "Implementation Steps:\n"
            " 1) Reading & Parsing HDF\n"
            " 2) Homogenizing pixel/voxel size\n"
            " 3) Generating sample points\n"
            " 4) Path Simulation\n"
            " 5) Statistical Analysis\n\n"

            "Author:\n"
            "Arjun Venkatesh (Mission Analysis Engineer)\n"
            "Contact for questions or enhancements.\n"
        )

        info_text.insert(tk.END, overview_str)
        info_text.config(state="disabled")

    ###########################################################################
    # Learn Tab
    ###########################################################################
    def build_learn_tab(self):
        learn_text = scrolledtext.ScrolledText(self.learn_frame, wrap="word", bg="#1e1e1e", fg="white")
        learn_text.pack(fill="both", expand=True, padx=10, pady=10)

        plain_explanation = (
            "Welcome to the STRATUS GUI!\n\n"
            "If you're not a expert on this tool, here's the big idea:\n"
            " - We have special files from a NASA satellite called CALIPSO.\n"
            " - These files tell us where clouds are and how thick they are,\n"
            "   by measuring how much laser light bounces off.\n\n"
            "The Backscatter tab shows a color picture:\n"
            " - 'Backscatter' is basically how much laser light returns.\n"
            " - Big numbers mean thicker clouds!\n\n"
            "The Transmission tab estimates how much light can get through those clouds:\n"
            " - We use a formula (Beer-Lambert Law) that says if clouds are thick,\n"
            "   they block more light.\n"
            " - We draw random 'paths' in the data to see how often the light\n"
            "   makes it through.\n\n"
            "The VFM tab will, in the future, show exactly where clouds vs.\n"
            "clear skies are, so we can see the chance of flying through clouds.\n\n"
            "In short, STRATUS helps us figure out:\n"
            " - Where clouds are in the atmosphere\n"
            " - How difficult it is for lasers or signals to pass through them\n\n"
        )

        learn_text.insert(tk.END, plain_explanation)
        learn_text.config(state="disabled")


###############################################################################
# Run the GUI
###############################################################################
if __name__ == "__main__":
    app = StratusGUI()
    app.mainloop()
