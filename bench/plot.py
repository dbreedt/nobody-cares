import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import io

file_path = '/tmp/crap'

# 1. Manually filter the file for only the data rows
data_rows = []
with open(file_path, 'r') as f:
    for line in f:
        # Only keep lines that start with a timestamp (digit) 
        if line.strip() and line.strip()[0].isdigit():
            data_rows.append(line)

# 2. Convert the filtered lines into a DataFrame
# We treat the list of strings as a file using io.StringIO
raw_data = "".join(data_rows)
df = pd.read_csv(io.StringIO(raw_data), sep=r'\s+', header=None)

# 3. Manually name the columns based on pidstat's output order
df.columns = [
    'Time', 'UID', 'PID', '%usr', '%system', '%guest', 
    '%wait', '%CPU', 'CPU', 'minflt/s', 'majflt/s', 
    'VSZ', 'RSS', '%MEM', 'Command'
]

# 4. Convert types
df['%CPU'] = pd.to_numeric(df['%CPU'])
df['RSS_MB'] = pd.to_numeric(df['RSS']) / 1024
df['%wait'] = pd.to_numeric(df['%wait'])

# 5. Plotting
fig, ax1 = plt.subplots(figsize=(12, 6))

ax1.set_xlabel('Time')

# Plot CPU (Left Axis)
ax1.set_ylabel('CPU (%)', fontweight='bold')
ax1.plot(df['Time'], df['%CPU'], color='#FF8C00', label='CPU Usage %', linewidth=2)
ax1.tick_params(axis='y')

ax1.plot(df['Time'], df['%wait'], color='#D3D3D3', label='CPU wait %', linewidth=2)


# Plot RSS (Right Axis)
ax2 = ax1.twinx()
#ax2.yaxis.set_major_locator(ticker.MultipleLocator(base=5))
ax2.set_ylabel('RSS (MB)', color='#FF0000', fontweight='bold')
ax2.plot(df['Time'], df['RSS_MB'], color='#FF0000', label='RSS (MB)', linewidth=2)
ax2.tick_params(axis='y', labelcolor='#FF0000')

# Formatting
plt.title('Process Resource Usage', fontsize=14)
ax1.xaxis.set_major_locator(plt.MaxNLocator(10)) # Keep X-axis readable
plt.xticks(rotation=45)
plt.grid(True, linestyle=':', alpha=0.6)
fig.tight_layout()

# 1. Ask both axes for their handles and labels
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()

# 2. Combine them and create a single legend
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

plt.savefig('resource_usage.png')
print(f"Successfully processed {len(df)} data points.")
print("Graph saved as resource_usage.png")
