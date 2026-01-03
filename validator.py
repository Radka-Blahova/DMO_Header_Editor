from typing import List, Dict
import re


def validate_input(header_lines: List[str], body_lines: List[str]) -> dict:
    """Validate DMO file structure and presence of required header fields (supports legacy patterns)."""
    errors, warnings = [], []

    if not header_lines:
        errors.append("[E001] Header section is empty.")
    if not body_lines:
        errors.append("[E002] Body section is empty.")
    if not header_lines:
        return {"is_valid": False, "errors": errors, "warnings": warnings}

    text = "\n".join(header_lines)

    groups = [
        ("[E010] Missing DATE =", [r"DATE\s*="]),
        ("[E011] Missing TIME =", [r"TIME\s*="]),
        ("[E012] Missing GS (PR/PS/Gen.state)", [r"PS\(KENN\)\s*=", r"PR\(KENN\)\s*=", r"Gen\.state"]),
        ("[E013] Missing DI(MESSMITTEL)=", [r"DI\(MESSMITTEL\)\s*="]),
        ("[E014] Missing operator (OP/Executed by)", [r"OP\(Pruefer\)\s*=", r"Executed by"]),
        ("[E015] Missing PN(TEIL_NR)= / Zákaz.číslo", [r"PN\(TEIL_NR\)\s*=", r"Zákaz\.číslo"]),
        ("[E016] Missing PS(LFD_NR)= / Číslo kusu", [r"PS\(LFD_NR\)\s*=", r"Číslo\s*kusu"]),
        ("[E017] Missing MD(BEMI1)=", [r"MD\(BEMI1\)\s*="]),
        ("[E018] Missing MD(BEMI2)=", [r"MD\(BEMI2\)\s*="]),
    ]

    for code, patterns in groups:
        if not any(re.search(p, text) for p in patterns):
            errors.append(code)

    if not any("FILNAM/" in line for line in header_lines):
        warnings.append("[W001] FILNAM line is missing.")
    if "OUTPUT/R(" in text:
        warnings.append("[W101] Old syntax detected: missing space after '/'.")
    if "PR(KENN)" in text and "PS(KENN)" not in text:
        warnings.append("[W102] Legacy tag 'PR(KENN)' detected.")
    if "Executed by" in text and "OP(Pruefer)" not in text:
        warnings.append("[W103] Legacy 'Executed by' detected.")
    if "Zákaz.číslo" in text and "PN(TEIL_NR)" not in text:
        warnings.append("[W104] Legacy 'Zákaz.číslo' detected.")
    if re.search(r"Číslo\s*kusu", text) and "PS(LFD_NR)" not in text:
        warnings.append("[W105] Legacy 'Číslo kusu' detected.")

    return {"is_valid": len(errors) == 0, "errors": errors, "warnings": warnings}


def validate_info(info: Dict[str, str], required_fields=None) -> dict:
    """Ensure parsed header contains all required keys with valid formats."""
    if required_fields is None:
        required_fields = [
            "TEIL_NR", "LFD_NR", "DATE", "TIME",
            "GS", "MESSMITTEL", "PRUEFER", "BEMI1", "BEMI2"
        ]

    errors, warnings = [], []

    for key in required_fields:
        val = (info.get(key) or "").strip()
        if not val:
            errors.append(f"[E2{required_fields.index(key)+10:02d}] Missing {key}")
            continue

        # --- Format checks ---
        if key == "DATE" and not re.match(r"^\d{4}/\d{2}/\d{2}$", val):
            warnings.append(f"[W201] Unexpected DATE format: {val}")

        elif key == "TIME" and not re.match(r"^\d{2}:\d{2}:\d{2}$", val):
            warnings.append(f"[W202] Unexpected TIME format: {val}")

        elif key == "PRUEFER":
            if not re.match(r"^FIRMA_[A-Z]+$", val):
                warnings.append(f"[W203] PRUEFER format should be 'FIRMA_SURNAME' (uppercase): {val}")

        elif key == "MESSMITTEL":
            if not re.match(r"^[A-Z][a-z]+_[A-Z0-9]+$", val):
                warnings.append(f"[W204] MESSMITTEL format should be 'Brand_MODEL' (model uppercase): {val}")

    return {"is_valid": len(errors) == 0, "errors": errors, "warnings": warnings}


def validate_output(merged_lines: List[str]) -> dict:
    """Validate final DMO file for structure and non-empty fields."""
    errors, warnings = [], []
    text = "\n".join(merged_lines)

    if not text.startswith("FILNAM/"):
        errors.append("[E100] Output should start with 'FILNAM/'")

    required = [
        "OUTPUT/ R(DAY)", "DATE =", "OUTPUT/ R(TIM)", "TIME =",
        "OUTPUT/ R(P3)", "PS(KENN)", "OUTPUT/ R(M1)", "DI(MESSMITTEL)",
        "OUTPUT/ R(O1)", "OP(Pruefer)", "OUTPUT/ R(P1)", "PN(TEIL_NR)",
        "OUTPUT/ R(P2)", "PS(LFD_NR)", "OUTPUT/ R(B1)", "MD(BEMI1)",
        "OUTPUT/ R(B2)", "MD(BEMI2)"
    ]
    for token in required:
        if token not in text:
            errors.append(f"[E1{required.index(token)+10:02d}] Missing or malformed: {token}")

    # Empty or missing field values
    if re.search(r"=\s*$|=\s*''|=\s*' *'", text):
        errors.append("[E150] Empty or missing field value detected.")

    if re.search(r"OUTPUT/R\(", text):
        warnings.append("[W301] Found 'OUTPUT/R(' (missing space after '/')")
    if not text.strip().endswith("----------------------------------------------"):
        warnings.append("[W303] Header does not end with expected separator line")

    return {"is_valid": len(errors) == 0, "errors": errors, "warnings": warnings}