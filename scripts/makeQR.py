import segno

first = "set do_factory_setup 1"
second = "saveenv"
third = "reset"

# Use high error correction and a larger quiet zone (border) + bigger scale
# to improve scan reliability when printed or displayed.
qr = segno.make(r"set do_factory_setup 1", error='h')
# Save as PNG with larger module size and border. Increase further if needed.
qr.save("factory_setup.png", scale=20, border=6, dark='black', light='white')

# Optionally also save an SVG (vector) for highest-quality printing:
