import numpy as np
from datetime import datetime, timedelta
from geopy.distance import geodesic


def remove_idle_data(data: np.array, tdelay: int = 600):
    res = np.array([True for _ in range(data.shape[0])])
    f_read = False
    f_start_delay = 0
    
    # Jika data[:, 3] sudah 'True' sejak awal
    if data[0, 3]:
        f_read = True
        f_start_delay = data[0, 1]
        res[0] = True
    else:
        res[0] = False
    
    for iter in range(1, data.shape[0]):
        # Jika terjadi transisi dari False ke True
        if not data[iter - 1, 3] and data[iter, 3]:
            f_read = True
            f_start_delay = data[iter, 1]
        elif data[iter - 1, 3] and not data[iter, 3]:
            f_read = False
        
        # Cek jika delay sudah lebih dari tdelay
        if f_read and data[iter, 1] - f_start_delay > np.timedelta64(tdelay, "s"):
            res[iter] = True
        else:
            res[iter] = False
    
    return data[res]


def remove_209_and_non_increasing_x(x, y):
    """
    Fungsi untuk menghapus nilai-nilai y yang sama dengan 209 dan menghapus elemen x yang berpasangan dengan y tersebut,
    serta menghapus data dengan x yang tidak bertambah.
    """
    # Buat filter untuk memilih elemen y yang tidak sama dengan 209
    valid_indices = (y != 209) & (np.diff(np.concatenate(([x[0]], x))) > 0)
    
    # Terapkan filter pada x dan y dan pastikan hasilnya berupa array
    x_filtered = np.array(x[valid_indices])
    y_filtered = np.array(y[valid_indices])
    
    return x_filtered, y_filtered


def median_filter(y):
    window_size = 50  # Pilih ukuran jendela yang tepat
    half_window = window_size // 2
    y_median = np.zeros_like(y)
    
    for i in range(len(y)):
        start = max(0, i - half_window)
        end = min(len(y), i + half_window + 1)
        y_median[i] = np.median(y[start:end])
    
    return y_median


def define_cycle(x, y_median):
    cycles_median = []
    current_cycle = []
    n = len(x)

    # Iterasi untuk mendeteksi kenaikan lebih dari 16 dalam rentang x 150
    i = 0
    while i < n - 1:
        start = i
        end = min(i + 150, n - 1)

        # Cek jika ada kenaikan lebih dari 16 dalam rentang tersebut
        if y_median[end] - y_median[start] > 16:
            if current_cycle:
                cycles_median.append(np.array(current_cycle))
                current_cycle = []
            i = end
        else:
            current_cycle.append((x[i], y_median[i]))
            i += 1

    if current_cycle:
        cycles_median.append(np.array(current_cycle))

    return cycles_median


def regression(cycles_median):
    # Plot regresi untuk setiap siklus
    regression_results = []
    for i, cycle in enumerate(cycles_median):
        if len(cycle) > 1:
            x_cycle = cycle[:, 0]
            y_cycle = cycle[:, 1]
            
            # Hitung koefisien regresi linear
            coeffs = np.polyfit(x_cycle, y_cycle, 1)
            slope = coeffs[0]
            
            # Pastikan slope < 0
            if slope < 0:
                poly_eq = np.poly1d(coeffs)
                y_pred = poly_eq(x_cycle)
                
                # Jika prediksi nilai negatif, biarkan, jika tidak, setel ke 0
                y_pred = np.maximum(y_pred, 0)
                
                # Simpan hasil regresi
                regression_results.append(np.column_stack((x_cycle, y_pred)))

    return regression_results


def fuel_cycle_calculation(np_data, data_reg):
    # Menghitung total fuel consumed dan fuel rate untuk setiap siklus
    cycle_fuel_consumed = []
    cycle_distance = []
    fuel_rate = []
    time_initial_list = []
    time_terminal_list = []

    for cycle in data_reg:
        if len(cycle) > 1:  # Memastikan ada lebih dari satu titik dalam siklus
            x_cycle = cycle[:, 0]
            y_cycle = cycle[:, 1]

            ymax = np.max(y_cycle)
            ymin = np.min(y_cycle)
            
            if ymax == ymin:
                continue

            # Menghitung total fuel consumed dan fuel rate
            total_fuel = round(ymax - ymin, 2)
            total_distance = x_cycle[np.argmin(y_cycle)] - x_cycle[np.argmax(y_cycle)]
            rate = round((total_distance / 1000) / (ymax - ymin), 2)

            cycle_fuel_consumed.append(total_fuel)
            fuel_rate.append(rate)
            cycle_distance.append(total_distance)

            # Mendapatkan time_initial dan time_terminal
            res_awal = np_data[np_data[:, 1] == x_cycle[0]]
            time_initial = datetime.fromtimestamp(res_awal[0, 0]).strftime("%Y-%m-%dT%H:%M:%SZ")
            res_akhir = np_data[np_data[:, 1] == x_cycle[-1]]
            time_terminal = datetime.fromtimestamp(res_akhir[0, 0]).strftime("%Y-%m-%dT%H:%M:%SZ")

            time_initial_list.append(time_initial)
            time_terminal_list.append(time_terminal)

    # Mengubah semua list menjadi array numpy
    cycle_fuel_consumed = np.array(cycle_fuel_consumed)
    cycle_distance = np.array(cycle_distance)
    fuel_rate = np.array(fuel_rate)
    time_initial_list = np.array(time_initial_list)
    time_terminal_list = np.array(time_terminal_list)

    # Gunakan np.column_stack untuk menggabungkan data menjadi array final, tanpa imei
    fuel_data_summary = np.column_stack((
        cycle_fuel_consumed,
        cycle_distance,
        fuel_rate,
        time_initial_list,
        time_terminal_list
    ))

    return fuel_data_summary


def calculate_total_distance(recent_total_distance, coordinates):
    """
    Menghitung jarak kumulatif dari daftar koordinat [[latitude, longitude], ...] menggunakan library geopy.
    Parameter:
    - recent_total_distance: Jarak total sebelumnya dalam meter.
    - coordinates: List of lists [[lat1, lon1], [lat2, lon2], ...].
    
    Return:
    - List of cumulative distances dalam meter, dimulai dengan recent_total_distance.
    """
    cumulative_distances = [recent_total_distance]  # Dimulai dari jarak total sebelumnya
    
    total_distance = recent_total_distance
    
    for i in range(1, len(coordinates)):
        lat1, lon1 = coordinates[i - 1]
        lat2, lon2 = coordinates[i]
        
        # Menghitung jarak antara dua titik dalam meter menggunakan geodesic
        distance = geodesic((lat1, lon1), (lat2, lon2)).meters
        total_distance += distance
        cumulative_distances.append(round(total_distance, 2))
    
    return cumulative_distances

def calculate_operating_time(dt_array):
    # Ekstraksi kolom timestamp dan operating_status dari dt_array
    timestamps = dt_array[:, 2]
    operating_status = dt_array[:, 3]
    
    # Inisialisasi total waktu operasi
    total_operating_time = timedelta(0)
    
    # Konversi timestamp ke datetime (asumsi timestamp dalam detik)
    timestamps = [datetime.utcfromtimestamp(ts) for ts in timestamps]
    
    # Loop melalui setiap entri
    for i in range(1, len(timestamps)):
        # Periksa apakah status operasi aktif (misalnya, 1 atau True) untuk dua titik waktu berturut-turut
        if operating_status[i] and operating_status[i-1]:
            # Hitung durasi antara dua timestamp berturut-turut dan tambahkan ke total_operating_time
            delta = timestamps[i] - timestamps[i-1]
            total_operating_time += delta
    
    # Mengembalikan total waktu operasi dalam detik
    return total_operating_time.total_seconds()

