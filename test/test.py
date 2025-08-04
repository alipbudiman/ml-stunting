from lib.prediction import parse_tanggal_lahir


data = parse_tanggal_lahir('1998-12-12')
print(f"Tahun: {data.tahun}, Bulan: {data.bulan}, Hari: {data.hari}")