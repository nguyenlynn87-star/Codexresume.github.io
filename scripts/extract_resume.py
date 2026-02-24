#!/usr/bin/env python3
import json
import re
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "lynnresumepdf.pdf"
OUT_PATH = ROOT / "assets" / "resume.json"


def _iter_objects(pdf_bytes: bytes):
    for m in re.finditer(rb"(\d+) \d+ obj(.*?)endobj", pdf_bytes, re.S):
        yield int(m.group(1)), m.group(2)


def _extract_stream(obj: bytes):
    if b"stream" not in obj:
        return None
    head, rest = obj.split(b"stream", 1)
    stream = rest.split(b"endstream", 1)[0].strip(b"\r\n")
    if b"/FlateDecode" in head:
        stream = zlib.decompress(stream)
    return stream


def _read_cmaps(pdf_bytes: bytes):
    cmaps = []
    for _, obj in _iter_objects(pdf_bytes):
        stream = _extract_stream(obj)
        if not stream:
            continue
        text = stream.decode("latin1", "ignore")
        if "begincmap" not in text:
            continue
        cmap = {}
        for key_hex, val_hex in re.findall(r"<([0-9A-F]+)> <([0-9A-F]+)>", text):
            if len(key_hex) == 4:
                cmap[int(key_hex, 16)] = bytes.fromhex(val_hex).decode("utf-16-be", "ignore")
        for start, end, start_val in re.findall(r"<([0-9A-F]+)> <([0-9A-F]+)> <([0-9A-F]+)>", text):
            s, e, sv = int(start, 16), int(end, 16), int(start_val, 16)
            for i, key in enumerate(range(s, e + 1)):
                cmap[key] = chr(sv + i)
        cmaps.append(cmap)
    return cmaps


def extract_text(pdf_bytes: bytes):
    cmaps = _read_cmaps(pdf_bytes)
    chunks = []
    for _, obj in _iter_objects(pdf_bytes):
        stream = _extract_stream(obj)
        if not stream:
            continue
        text = stream.decode("latin1", "ignore")
        if " Tf" not in text or " Tj" not in text:
            continue
        for bt in re.findall(r"BT(.*?)ET", text, re.S):
            vals = re.findall(r"<([0-9A-F]+)>\s*Tj", bt)
            if not vals:
                continue
            out = ""
            for h in vals:
                code = int(h, 16)
                ch = None
                for cmap in cmaps:
                    if code in cmap:
                        ch = cmap[code]
                        break
                out += ch if ch is not None else ""
            if out.strip():
                chunks.append(out)
    joined = " ".join(chunks)
    joined = joined.replace("\ufb01", "fi").replace("\u2013", "-")
    joined = re.sub(r"\s+", " ", joined).strip()
    return joined


def parse_resume(text: str):
    data = {
        "name": "",
        "headline": "",
        "summary": "",
        "contact": {"phone": "", "email": "", "linkedin": ""},
        "skills": [{"category": "Core Skills", "items": []}],
        "experience": [],
        "education": [],
    }

    name_match = re.search(r"^(.*?) Enterprise Account Executive", text)
    if name_match:
        data["name"] = name_match.group(1).strip()

    headline_match = re.search(r"(Enterprise Account Executive \| Strategic SaaS & Services Partnerships)", text)
    if headline_match:
        data["headline"] = headline_match.group(1)

    summary_match = re.search(r"Summary (.*?) Work experience", text)
    if summary_match:
        data["summary"] = summary_match.group(1).strip(" +")

    phone = re.search(r"(\d{3}\.\d{3}\.\d{4})", text)
    email = re.search(r"([\w.\-]+\s*@gmail\.com)", text)
    if phone:
        data["contact"]["phone"] = phone.group(1)
    if email:
        data["contact"]["email"] = email.group(1).replace(" ", "")

    link = re.search(r"https://www\.linkedin\.com/in/[^)\s>]+", PDF_PATH.read_text("latin1", errors="ignore"))
    if link:
        data["contact"]["linkedin"] = link.group(0)

    skills_match = re.search(r"Skills (.*?) Education", text)
    if skills_match:
        skills_text = skills_match.group(1)
        items = [s.strip() for s in re.split(r"\s\+\s", skills_text) if s.strip()]
        data["skills"][0]["items"] = [i.strip(" +") for i in items]

    exp_match = re.search(r"Work experience (.*?) Contact", text)
    if exp_match:
        exp_text = exp_match.group(1)
        patterns = [
            (
                r"SMARTLING \| Enterprise Account Executive\s+2020 - present\s+(.*?)(?=LINGOTEK \| Account Executive)",
                "SMARTLING",
                "Enterprise Account Executive",
                "2020 - present",
            ),
            (
                r"LINGOTEK \| Account Executive\s+2017-2020\s+(.*?)(?=TRANSPERFECT \| Director, Business Development)",
                "LINGOTEK",
                "Account Executive",
                "2017-2020",
            ),
            (
                r"TRANSPERFECT \| Director, Business Development\s+2014-2017\s+(.*?)$",
                "TRANSPERFECT",
                "Director, Business Development",
                "2014-2017",
            ),
        ]
        for pat, company, title, dates in patterns:
            m = re.search(pat, exp_text)
            if not m:
                continue
            bullets = [b.strip(" +•") for b in re.split(r"\s•\s|\s•", m.group(1)) if b.strip()]
            data["experience"].append({
                "company": company,
                "title": title,
                "dates": dates,
                "highlights": bullets,
            })

    edu_match = re.search(r"Education \+ University of Denver \+ 2005-2009 \+ (.*?)$", text)
    if edu_match:
        data["education"].append(
            {
                "school": "University of Denver",
                "degree": edu_match.group(1).strip(" +"),
                "dates": "2005-2009",
            }
        )

    return data


def main():
    pdf_bytes = PDF_PATH.read_bytes()
    text = extract_text(pdf_bytes)
    data = parse_resume(text)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
