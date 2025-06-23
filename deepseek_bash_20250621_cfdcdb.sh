# 1. Navigate to your game folder
cd ~/Desktop/"NumCrunch Academy"

# 2. List files to verify the correct filename
ls

# 3. Run the game (with quotes around the filename)
python3 "NumCrunch Academy.py"

# If you get a "ModuleNotFoundError: No module named 'pygame'":
pip3 install pygame && python3 "NumCrunch Academy.py"

# Alternative: Rename the file to remove spaces first (optional)
# mv "NumCrunch Academy.py" NumCrunchAcademy.py
# python3 NumCrunchAcademy.py