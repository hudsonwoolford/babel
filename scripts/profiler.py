import pstats

# Load the saved profile data
p = pstats.Stats('program.prof')

# Strip directory paths for cleaner terminal reading
p.strip_dirs()

# Sort by total internal time and display the top 20 worst offenders
p.sort_stats('tottime').print_stats(20)

# Filter out specific functions (e.g., only show method calls containing "join")
p.print_stats('join')