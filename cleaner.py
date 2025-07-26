import re

def is_noisy(line):
    line = line.strip()

    # 1. Hardcoded match
    if "অনলাইন" in line and "ব্যাচ" in line and "আইসিটি" in line or line.replace(" ", "") == "অনলাইনব্যাচবাংলা-ইংরেজি:আইসিটি":
        return True

    # 2. Remove page headers
    if re.match(r"^[-–—\s]*Page\s*\d+\s*[-–—\s]*$", line, flags=re.IGNORECASE):
        return True

    if len(line) < 8:
        return True

    return False

brackets = {'(' ')', '[' ']', '{' '}'}
 
def clean_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    cleaned_lines = [line.strip().replace('(', '').replace(')', '').replace('[', '')\
        .replace(']', '').replace('{', '').replace('}', '')\
            for line in lines if not is_noisy(line)]

    with open(output_path, 'w', encoding='utf-8') as f:
        for line in cleaned_lines:
            if line:
                f.write(line + '\n')

# Run the cleaner
clean_file('bangla_easyocr_output.txt', 'cleaned_output.txt')
