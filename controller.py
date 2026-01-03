import os
from source import (
    read_file,
    split_file,
    parse_header,
    create_new_header,
    merge_header_and_body,
    save_file
)
from validator import validate_input, validate_output


def process_files(selected_files, output_folder, log, progress_bar):
    """Main control logic for processing selected DMO files."""
    if not selected_files:
        log("❌ No files selected.", "error")
        return
    if not output_folder:
        log("⚠️ Please select an output folder first.", "warning")
        return

    total = len(selected_files)
    success_count = 0
    log(f"▶️ Processing {total} files...\n", "info")

    for idx, path in enumerate(selected_files, start=1):
        file_name = os.path.basename(path)
        log(f"🔹 {file_name}", "info")

        try:
            lines = read_file(path)
            header, body = split_file(lines)

            validation_in = validate_input(header, body)
            if not validation_in["is_valid"]:
                log(f"❌ Input validation failed for {file_name}:", "error")
                for e in validation_in["errors"]:
                    log(f"   - {e}", "error")
                log("⏭️ File skipped.\n", "warning")
                continue

            info = parse_header(header)
            new_header = create_new_header(info)
            merged = merge_header_and_body(new_header, body)

            validation_out = validate_output(merged)
            if not validation_out["is_valid"]:
                log(f"⚠️ Output validation failed for {file_name}:", "warning")
                for e in validation_out["errors"]:
                    log(f"   - {e}", "warning")
                log("⏭️ File skipped.\n", "warning")
                continue

            out_path = os.path.join(output_folder, file_name)
            save_file(out_path, merged)
            success_count += 1

            log(f"💾 Saved: {out_path}", "success")
            log("✅ Done.\n", "success")

        except Exception as e:
            log(f"❌ Error processing {file_name}: {e}", "error")
            log("⏭️ File skipped.\n", "warning")

        progress_bar.set(idx / total)
        progress_bar.update_idletasks()

    progress_bar.set(1)
    log(f"🏁 Processing complete. {success_count}/{total} files saved successfully.\n", "info")