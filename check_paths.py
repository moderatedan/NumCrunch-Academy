import os

# Let's check what folders exist on your Desktop
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
print("Contents of Desktop:")
try:
    for item in os.listdir(desktop_path):
        item_path = os.path.join(desktop_path, item)
        if os.path.isdir(item_path):
            print(f"📁 {item}/")
        else:
            print(f"📄 {item}")
except Exception as e:
    print(f"Error reading Desktop: {e}")

print("\n" + "="*50 + "\n")

# Check for math_munchers folder variations
possible_names = ["math_munchers", "Math_Munchers", "Math Munchers", "math-munchers"]
for name in possible_names:
    folder_path = os.path.join(desktop_path, name)
    if os.path.exists(folder_path):
        print(f"✅ Found folder: {name}")
        print(f"Contents of {name}:")
        try:
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isdir(item_path):
                    print(f"  📁 {item}/")
                    # If it's the sprites folder, show what's inside
                    if item.lower() in ['sprites', 'sprite']:
                        print(f"    Contents of {item}/:")
                        try:
                            for sprite in os.listdir(item_path):
                                print(f"      📄 {sprite}")
                        except:
                            print("      (could not read contents)")
                else:
                    print(f"  📄 {item}")
        except Exception as e:
            print(f"  Error reading folder: {e}")
        print()
    else:
        print(f"❌ No folder named: {name}")

print("\n" + "="*50 + "\n")

# Test the exact path the game is trying to use
game_path = os.path.join(os.path.expanduser("~"), "Desktop", "math_munchers", "sprites")
print(f"Game is looking for sprites at: {game_path}")
print(f"Does this path exist? {os.path.exists(game_path)}")

if os.path.exists(game_path):
    background_path = os.path.join(game_path, "background.png")
    print(f"Looking for background at: {background_path}")
    print(f"Does background.png exist? {os.path.exists(background_path)}")
else:
    print("The sprites folder path doesn't exist!")