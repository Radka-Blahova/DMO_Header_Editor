import re


def read_file(path):
    """Read a DMO file and return its lines."""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.readlines()


def split_file(lines):
    """Split a DMO file into header and body, ending header before 'RECALL/'."""
    header, body, header_done = [], [], False
    for line in lines:
        if not header_done:
            header.append(line)
            if line.strip().startswith("RECALL/"):
                header_done = True
        else:
            body.append(line)
    return header, body


def parse_header(header_lines):
    """Extract key information from the DMO header using regex patterns and format adjustments."""
    info, text = {}, "\n".join(header_lines)

    # --- FILNAM ---
    m = re.search(r"FILNAM/'([A-Za-z0-9_]+)'", text)
    info["FILNAM"] = m.group(1).replace("Re", "").replace("Li", "") if m else ""

    # --- DATE / TIME ---
    info["DATE"] = re.search(r"DATE\s*=\s*([0-9/]+)", text).group(1) if re.search(r"DATE\s*=\s*([0-9/]+)", text) else ""
    info["TIME"] = re.search(r"TIME\s*=\s*([0-9:]+)", text).group(1) if re.search(r"TIME\s*=\s*([0-9:]+)", text) else ""

    # --- GS (Gen.state or PR(KENN)) ---
    m = re.search(r"PR\(KENN\)\s*=\s*'?(?P<gs>[A-Za-z0-9]+)'?", text) or re.search(r"Gen\.state\s*[:=]\s*(?P<gs>[A-Za-z0-9]+)", text)
    info["GS"] = m.group("gs") if m else ""

    # --- MESSMITTEL ---
    m = re.search(r"DI\(MESSMITTEL\)\s*=\s*'([^']+)'", text)
    if m:
        raw = m.group(1).strip()
        parts = re.split(r"[_\s-]+", raw)
        if len(parts) >= 2:
            brand = parts[0].capitalize()
            model = "_".join(p.upper() for p in parts[1:])
            info["MESSMITTEL"] = f"{brand}_{model}"
        else:
            info["MESSMITTEL"] = raw.capitalize()
    else:
        info["MESSMITTEL"] = ""

    # --- PRUEFER (OP(Pruefer) or Executed by) ---
    m = re.search(r"(OP\(Pruefer\)|Executed by)\s*[:=]\s*'?([A-Za-z0-9_]+)'?", text)
    if m:
        surname = m.group(2).strip().upper()
        info["PRUEFER"] = f"FIRMA_{surname}"
    else:
        info["PRUEFER"] = ""

    # --- TEIL_NR / LFD_NR ---
    m = re.search(r"PN\(TEIL_NR\)\s*=\s*'?(?P<teil>[A-Za-z0-9]+)'?", text) or re.search(r"Zákaz\.číslo\s*[:=]\s*(?P<teil>[A-Za-z0-9]+)", text)
    info["TEIL_NR"] = m.group("teil") if m else ""

    m = re.search(r"PS\(LFD_NR\)\s*=\s*'?(?P<lfd>[A-Za-z0-9]+)'?", text) or re.search(r"Číslo\s*kusu\s*[:=]\s*(?P<lfd>[A-Za-z0-9]+)", text)
    info["LFD_NR"] = m.group("lfd") if m else ""

    # --- BEMI1 / BEMI2 ---
    info["BEMI1"] = re.search(r"MD\(BEMI1\)\s*=\s*'([^']+)'", text).group(1) if re.search(r"MD\(BEMI1\)\s*=\s*'([^']+)'", text) else ""
    info["BEMI2"] = re.search(r"MD\(BEMI2\)\s*=\s*'([^']+)'", text).group(1) if re.search(r"MD\(BEMI2\)\s*=\s*'([^']+)'", text) else ""

    return info


def create_new_header(info):
    """Generate a standardized DMO header based on parsed information."""
    teil, lfd, filnam = info.get("TEIL_NR", "").strip(), info.get("LFD_NR", "").strip(), info.get("FILNAM", "").strip()

    if filnam and "_" not in filnam[:12]:
        filnam = filnam.replace(teil, f"{teil}_")
    if not filnam:
        filnam = f"{teil}_PROJEKT_XYZ_{lfd}"

    header = [
        f"FILNAM/'{filnam.strip()}', 04.0\n",
        "OUTPUT/ R(DAY)\n",
        f"DATE = {info.get('DATE', '')}\n",
        "TEXT/OUTFIL, '*****************************'\n",
        "OUTPUT/ R(TIM)\n",
        f"TIME = {info.get('TIME', '')}\n",
        "TEXT/OUTFIL, '*****************************'\n",
        "OUTPUT/ R(P3)\n",
        f"PS(KENN) = '{info.get('GS', '')}'\n",
        "OUTPUT/ R(M1)\n",
        f"DI(MESSMITTEL) = '{info.get('MESSMITTEL', '')}'\n",
        "OUTPUT/ R(O1)\n",
        f"OP(Pruefer) = '{info.get('PRUEFER', '')}'\n",
        "OUTPUT/ R(P1)\n",
        f"PN(TEIL_NR) = '{info.get('TEIL_NR', '')}'\n",
        "OUTPUT/ R(P2)\n",
        f"PS(LFD_NR) = '{info.get('LFD_NR', '')}'\n",
        "OUTPUT/ R(B1)\n",
        f"MD(BEMI1) = '{info.get('BEMI1', '')}'\n",
        "OUTPUT/ R(B2)\n",
        f"MD(BEMI2) = '{info.get('BEMI2', '')}'\n",
        "$$\n$$ ----------------------------------------------\n",
    ]
    return header


def merge_header_and_body(header_lines, body_lines):
    """Merge new header with original body section."""
    if not header_lines:
        raise ValueError("Header is empty.")
    if not body_lines:
        raise ValueError("Body is empty.")
    return header_lines + body_lines


def save_file(path, lines):
    """Save all lines to a new DMO file."""
    with open(path, "w", encoding="utf-8", errors="ignore") as f:
        f.writelines(lines)