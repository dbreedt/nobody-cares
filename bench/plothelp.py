import sys

def collapse_to_pidstat_format(input_file):
    # The header line to keep things compatible with your plotter
    header = "# Time            UID       PID    %usr %system  %guest   %wait    %CPU   CPU  minflt/s  majflt/s     VSZ     RSS   %MEM  Command"
    print(header)

    current_ts = None
    # Storage for the sums of the current block
    # [usr, system, guest, wait, cpu, minflt, majflt, vsz, rss, mem]
    totals = [0.0] * 10
    
    with open(input_file, 'r') as f:
        for line in f:
            if not line.strip() or line.startswith('#') or 'UID' in line:
                continue
            
            parts = line.split()
            if len(parts) < 14:
                continue

            ts = parts[0]
            
            # If we hit a new timestamp, print the accumulated totals for the previous one
            if current_ts and ts != current_ts:
                print_row(current_ts, totals)
                totals = [0.0] * 10 # Reset for next block
            
            current_ts = ts
            
            # Aggregate the numerical columns
            # Using specific indices based on your sample output
            try:
                totals[0] += float(parts[3])  # %usr
                totals[1] += float(parts[4])  # %system
                totals[2] += float(parts[5])  # %guest
                totals[3] += float(parts[6])  # %wait
                totals[4] += float(parts[7])  # %CPU
                totals[5] += float(parts[9])  # minflt/s
                totals[6] += float(parts[10]) # majflt/s
                totals[7] += float(parts[11]) # VSZ
                totals[8] += float(parts[12]) # RSS
                totals[9] += float(parts[13]) # %MEM
            except ValueError:
                continue

        # Print the final block
        if current_ts:
            print_row(current_ts, totals)

def print_row(ts, t):
    # Mimics pidstat's fixed-width spacing
    # We use '999999' as a placeholder PID and 'granian-total' as command
    row = (f"{ts:<15} 1000    999999  {t[0]:6.2f} {t[1]:7.2f} {t[2]:7.2f} "
           f"{t[3]:7.2f} {t[4]:7.2f}     0  {t[5]:8.2f}  {t[6]:8.2f} "
           f"{int(t[7]):>7} {int(t[8]):>7} {t[9]:6.2f}  server")
    print(row)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python collapse.py <file>")
    else:
        collapse_to_pidstat_format(sys.argv[1])
