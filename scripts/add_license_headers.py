import os

HEADER = """# Copyright [2026] Ziffan (Ziffany Firdinal)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""

def add_header_to_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if HEADER in content:
        print(f"Skipping {file_path}, header already exists.")
        return

    # Check if file starts with shebang
    if content.startswith('#!'):
        lines = content.splitlines(keepends=True)
        new_content = lines[0] + HEADER + "".join(lines[1:])
    else:
        new_content = HEADER + "\n" + content

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Added header to {file_path}")

def main():
    root_dirs = ['backend', '.'] # Add root .py files if any
    for root_dir in root_dirs:
        for root, dirs, files in os.walk(root_dir):
            if any(x in root for x in ['.venv', '__pycache__', '.git', 'node_modules']):
                continue
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    add_header_to_file(file_path)

if __name__ == "__main__":
    main()
