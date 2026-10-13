import os
from src.parser import parse_eml
from src.pdf_generator import generate_print_report, generate_fillable_report

eml_path = "tests/test_email.eml"
out_dir = "tests/out"

os.makedirs(out_dir, exist_ok=True)

print("Parsing EML...")
data = parse_eml(eml_path)
print("Parsed Data:")
for k, v in data.items():
    print(f"{k}: {v}")

print("\nGenerating Print PDF...")
generate_print_report(data, os.path.join(out_dir, "test_print_report.pdf"))

print("\nGenerating Fillable PDF...")
generate_fillable_report(data, os.path.join(out_dir, "test_fillable_report.pdf"))

print("\nDone. Outputs:")
print(os.listdir(out_dir))
