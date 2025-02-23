import gzip
import fitparse
import pandas as pd

# File paths
gz_file = "./4672709179.fit.gz"
fit_file = "./4672709179.fit"

# Decompress the GZ file
with gzip.open(gz_file, "rb") as f_in, open(fit_file, "wb") as f_out:
    f_out.write(f_in.read())

# Parse the FIT file
fit_data = fitparse.FitFile(fit_file)

# Extract records into a list of dictionaries
data = []
for record in fit_data.get_messages(
    "record"
):  # 'record' messages contain time-series data
    record_data = {}
    for field in record:
        if field.name and field.value is not None:
            record_data[field.name] = field.value
    data.append(record_data)

# Convert to DataFrame
df = pd.DataFrame(data)

# Display the first few rows
print(df.head())
