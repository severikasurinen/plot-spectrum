import os
import colour
import csv
from matplotlib import pyplot as plt


spectrum_domain = (400, 800)    # Spectrum domain in nm (min, max)
sub_path = 'Spectrum'
csv_headers = ('Wavelength λ (nm)', 'Intensity (counts)')   # Plot axis labels


# Plot spectral distribution graph
def plot_spectrum(spectrum_file, base_spectrum):
    # Read baseline values
    base_noise = {}
    measurement_count = {}
    spectrum_csv = read_csv(base_spectrum)[1]
    for i in range(len(spectrum_csv)):
        elem = (round(float(str(spectrum_csv[i][0]).split('\t')[0])), float(str(spectrum_csv[i][0]).split('\t')[1]))
        if elem[0] in base_noise:
            base_noise[elem[0]] += elem[1]
        else:
            base_noise[elem[0]] = elem[1]
        if elem[0] in measurement_count:
            measurement_count[elem[0]] += 1
        else:
            measurement_count[elem[0]] = 1

    for key in base_noise:
        base_noise[key] /= measurement_count[key]

    # Read actual spectral data
    measurement_count = {}
    spectrum_csv = read_csv(spectrum_file)[1]
    spectrum_data = {}
    avg_noise = [0, 0]
    for i in range(len(spectrum_csv)):
        elem = (round(float(str(spectrum_csv[i][0]).split('\t')[0])), float(str(spectrum_csv[i][0]).split('\t')[1]))
        if elem[0] < spectrum_domain[0] or elem[0] > spectrum_domain[1]:
            avg_noise[0] += 1
            avg_noise[1] += elem[1] - base_noise[elem[0]]   # Subtract baseline from data
        if elem[0] in measurement_count:
            measurement_count[elem[0]] += 1
        else:
            measurement_count[elem[0]] = 1

    avg_noise = avg_noise[1] / avg_noise[0]     # Calculate average noise

    # Calculate final values
    for i in range(len(spectrum_csv)):
        elem = (round(float(str(spectrum_csv[i][0]).split('\t')[0])), float(str(spectrum_csv[i][0]).split('\t')[1]))
        cur_noise = base_noise[elem[0]] - avg_noise
        if spectrum_domain[0] - 1 <= elem[0] <= spectrum_domain[1] + 1:
            if elem[0] not in spectrum_data:
                spectrum_data[elem[0]] = (elem[1] - cur_noise) / measurement_count[elem[0]]
            else:
                spectrum_data[elem[0]] = spectrum_data[elem[0]] + (elem[1] - cur_noise) / measurement_count[elem[0]]

    axis_ranges = (spectrum_domain[0], spectrum_domain[1], 0, max(spectrum_data.values()) + 100)
    # Plot result
    colour.plotting.plot_single_sd(colour.SpectralDistribution(spectrum_data), title=f"{'Spectral Distribution'}",
                                   x_label=csv_headers[0], y_label=csv_headers[1], bounding_box=axis_ranges)


# Read data from .csv file
def read_csv(in_name):
    csv_path = sub_path
    if not os.path.exists(os.path.join(csv_path, in_name + '.csv')):
        print("CSV file not found.")
        return None

    headers = None
    out_data = []
    with open(os.path.join(csv_path, in_name + '.csv'), 'r', encoding='UTF8', newline='') as f:

        for row in csv.reader(f, delimiter=','):    # Comma default delimiter
            raw_cells = []
            for cell in row:
                raw_cells.append(cell.split(' '))   # Cells values split by space if 3D data
            cells = []
            for i in range(len(raw_cells)):
                cells.append([])
                for o in range(len(raw_cells[i])):
                    raw_cells[i][o] = raw_cells[i][o].strip()
                    if raw_cells[i][o] != '':
                        try:
                            raw_cells[i][o] = float(raw_cells[i][o])
                        except:
                            pass
                        cells[i].append(raw_cells[i][o])

            if len(cells) == 1:
                cells = cells[0]
            if headers is None:
                headers = cells
            else:
                out_data.append(cells)

    return headers, out_data


spectrum_name = input("Spectrum name: ")
base_name = input("Baseline name: ")
print()

plot_spectrum(spectrum_name, base_name)     # Plot spectral distribution
