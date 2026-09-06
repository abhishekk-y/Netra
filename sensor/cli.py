"""Explicit file import or opt-in live capture: python -m sensor.cli --help."""
import argparse
import json
from pathlib import Path
import sys
from urllib.request import Request, urlopen
from .ingest import packet_flow, preserve_evidence, read_logs, read_pcap


def submit(api_url, flows):
    request = Request(api_url.rstrip("/") + "/api/ingest/flows",
                      data=json.dumps({"flows": flows}).encode(),
                      headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def main():
    parser = argparse.ArgumentParser(description="Import measured traffic or explicitly capture an interface")
    parser.add_argument("--api-url", default="http://127.0.0.1:8000")
    parser.add_argument("--dry-run", action="store_true", help="Print flow JSON without sending it")
    modes = parser.add_subparsers(dest="mode", required=True)
    imported = modes.add_parser("import", help="Import PCAP/PCAPNG, Zeek conn.log, or Suricata flow JSON")
    imported.add_argument("path", type=Path)
    imported.add_argument("--format", choices=["pcap", "zeek", "suricata"], default="pcap")
    imported.add_argument("--evidence-dir", default="./evidence/imports")
    live = modes.add_parser("live", help="Capture only on an explicitly named interface")
    live.add_argument("--interface", required=True)
    live.add_argument("--seconds", type=int, default=30)
    live.add_argument("--filter", default="ip or ip6")
    live.add_argument("--pcap", type=Path, required=True, help="New PCAP path for captured evidence")
    args = parser.parse_args()
    try:
        if args.mode == "live":
            if args.seconds <= 0:
                parser.error("--seconds must be positive")
            if args.pcap.exists():
                parser.error("--pcap must name a new file; existing evidence is never overwritten")
            from scapy.all import sniff
            from scapy.utils import PcapWriter
            args.pcap.parent.mkdir(parents=True, exist_ok=True)
            with PcapWriter(str(args.pcap), sync=True) as writer:
                sniff(iface=args.interface, filter=args.filter, timeout=args.seconds,
                      store=False, prn=writer.write)
            args.path, args.format = args.pcap, "pcap"
            args.evidence_dir = str(args.pcap.parent / "manifests")
        manifest = preserve_evidence(args.path, args.evidence_dir)
        print(json.dumps({"evidence": manifest}), file=sys.stderr)
        stored_path = Path(args.evidence_dir) / manifest["storedName"]
        records = read_pcap(stored_path) if args.format == "pcap" else read_logs(stored_path, args.format)
        batch, total = [], 0
        for record in records:
            record["evidenceSha256"] = manifest["sha256"]
            record["evidenceRef"] = manifest["storedName"]
            batch.append(record)
            if len(batch) == 1000:
                print(json.dumps({"flows": batch} if args.dry_run else submit(args.api_url, batch)))
                total += len(batch)
                batch = []
        if batch:
            print(json.dumps({"flows": batch} if args.dry_run else submit(args.api_url, batch)))
            total += len(batch)
        print(json.dumps({"processedFlows": total, "dryRun": args.dry_run}), file=sys.stderr)
    except Exception as exc:
        parser.exit(1, f"Sensor import failed: {exc}\n")


if __name__ == "__main__":
    main()
