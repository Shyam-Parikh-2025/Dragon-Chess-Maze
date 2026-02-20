from pathlib import Path

# ===== CONFIG =====
ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = ROOT_DIR / "combined_output.txt"

INCLUDE_EXTENSIONS = {".py"}  # Add ".md", ".txt" if needed
EXCLUDE_FOLDERS = {"__pycache__", ".git", "venv", ".venv", ".idea"}


def combine_files():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:

        for file_path in sorted(ROOT_DIR.rglob("*")):

            if (
                file_path.is_file()
                and file_path.suffix in INCLUDE_EXTENSIONS
                and not any(part in EXCLUDE_FOLDERS for part in file_path.parts)
            ):

                relative_path = file_path.relative_to(ROOT_DIR)

                # Write header
                outfile.write("\n")
                outfile.write("=" * 70 + "\n")
                outfile.write(f"----- {relative_path} -----\n")
                outfile.write("=" * 70 + "\n\n")

                # Write file contents
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        outfile.write(f.read())
                        outfile.write("\n\n")
                except Exception as e:
                    outfile.write(f"[Error reading file: {e}]\n\n")

    print(f"✅ Combined file created at: {OUTPUT_FILE}")


if __name__ == "__main__":
    combine_files()
