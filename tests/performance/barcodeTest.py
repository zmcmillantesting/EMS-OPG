import segno

# GS1 DataMatrix content with FNC1 prefix (use ASCII 29 as separator)
# ASCII 29 = Group Separator (GS), used between AIs
gs1_data = "setfset -u ethaddr=00:13:C6:13:0F:00"

# Generate DataMatrix
dm = segno.make(gs1_data, micro=False)

# Save as PNG
dm.save('gs1_datamatrix.png', scale=5)
