import matplotlib.pyplot as plt

# 1. Prepare your data
# Format: 'Name': [Processing Time, RAM Used, Cores Used]
data = {
    'C': [20, 48, 1],
    'Java': [38, 410, 3],
    '': [39, 410, 3], # java-capped
    'C#': [63, 170, 5],
    'Deno': [48, 480, 1],
    'golang': [26, 19, 2],
    'python': [291, 55, 1],
    'python-forked': [95, 325, 4]
}

names = list(data.keys())
times = [v[0] for v in data.values()]
ram = [v[1] for v in data.values()]
cores = [v[2] for v in data.values()]

# 2. Set bubble sizes
# Multiply cores by a factor (e.g., 200) so they are visible on the chart
sizes = [c * 200 for c in cores]

plt.figure(figsize=(10, 6))

# 3. Create the scatter (bubble) plot
# 'c' maps color to cores, 'cmap' sets the color theme
scatter = plt.scatter(times, ram, s=sizes, c=cores, cmap='viridis_r', 
            alpha=0.6, edgecolors="grey", linewidth=2)

# 4. Add labels for each individual point
for i, name in enumerate(names):
    plt.annotate(name, (times[i], ram[i]), textcoords="offset points", 
                 xytext=(0, 10), ha='center', fontweight='bold')

# 5. Formatting the graph
plt.xlabel('Processing Time (seconds) → Lower is Better')
plt.ylabel('RAM Used (GB) → Lower is Better')
plt.title('Performance Efficiency Comparison')

# Add a color bar to explain the core counts
cbar = plt.colorbar(scatter)
cbar.set_label('Number of Cores (Smaller/Lighter is Better)')

# Add a grid and set axis starts to 0 to show scale clearly
plt.grid(True, linestyle='--', alpha=0.5)
plt.xlim(0, max(times) * 1.2)
plt.ylim(0, max(ram) * 1.2)

# Visual cue for the "Winner" area
#plt.text(5, 0.5, '← Ideal Zone', color='green')

plt.tight_layout()
plt.savefig('performance_bubble_chart.png')
plt.show()
