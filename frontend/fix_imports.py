import os
import re

root_dir = r"c:\Users\niyan\OneDrive\Desktop\pilot\frontend\app\(authenticated)"

for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        if filename.endswith(".tsx") or filename.endswith(".ts"):
            filepath = os.path.join(dirpath, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            new_content = re.sub(r'([\"\'`])(\.\./)+(components|services)/', r'\1@/\3/', content)

            if new_content != content:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Updated {filepath}")
