"""Bounded PCAP import, immutable source evidence, and actual packet inspection."""
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import FileResponse
from starlette.concurrency import run_in_threadpool

router = APIRouter(tags=["packet evidence"])
MAX_BYTES = 16 * 1024 * 1024
MAX_PACKETS = 10000
MAGICS = (b"\xd4\xc3\xb2\xa1", b"\xa1\xb2\xc3\xd4", b"\x4d\x3c\xb2\xa1", b"\xa1\xb2\x3c\x4d", b"\x0a\x0d\x0d\x0a")


def evidence_directory():
    return Path(os.getenv("NETRA_EVIDENCE_DIR", str(Path(__file__).resolve().parents[3] / "evidence"))).resolve()


def flow_key(flow):
    return tuple(flow.get(k) for k in ("srcIp", "dstIp", "srcPort", "dstPort", "protocol"))


def import_capture(store, content, name):
    from sensor.ingest import read_packet_summaries, read_pcap
    from app.api.router import FlowInput
    sha = hashlib.sha256(content).hexdigest()
    directory = evidence_directory()
    directory.mkdir(parents=True, exist_ok=True)
    temporary = directory / f".upload-{uuid4().hex}"
    try:
        temporary.write_bytes(content)
        packets = []
        try:
            for packet in read_packet_summaries(temporary):
                if len(packets) >= MAX_PACKETS:
                    raise HTTPException(413, "Maximum 10,000 packets per import; split the capture first")
                packets.append(packet)
            raw_flows = list(read_pcap(temporary))
            flows = [FlowInput.model_validate({**f, "evidenceId": sha}).model_dump(mode="json", exclude_none=True) for f in raw_flows]
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(422, "Capture could not be parsed as valid PCAP/PCAPNG") from exc
        if not packets:
            raise HTTPException(422, "Capture has no decodable packets")
        with store.lock:
            existing = [item for item in store.all("evidence") if item["id"] == sha]
            if existing:
                return {**existing[0], "duplicate": True}
            destination = directory / f"{sha}.pcap"
            try:
                with destination.open("xb") as target:
                    target.write(content)
            except FileExistsError:
                if hashlib.sha256(destination.read_bytes()).hexdigest() != sha:
                    raise HTTPException(409, "Stored evidence failed integrity verification")
            saved = []
            for offset in range(0, len(flows), 1000):
                saved.extend(store.ingest(flows[offset:offset + 1000])["flows"])
            by_tuple = {flow_key(f): f["id"] for f in saved}
            manifest = {"id": sha, "sha256": sha, "originalName": Path(name.replace("\\", "/")).name[:200],
                "sizeBytes": len(content), "packetCount": len(packets), "flowCount": len(saved),
                "importedAt": datetime.now(timezone.utc).isoformat(), "captureStart": min(p["timestamp"] for p in packets),
                "captureEnd": max(p["timestamp"] for p in packets), "format": "pcapng" if content[:4] == MAGICS[-1] else "pcap",
                "source": "operator-upload", "integrity": "SHA-256 content-addressed original; preview bytes may be truncated"}
            with store.db:
                store.put("evidence", manifest)
                for packet in packets:
                    packet.update(id=f"{sha}:{packet['index']}", artifactId=sha, flowId=by_tuple.get(flow_key(packet)))
                    store.put("packets", packet)
                store.audit("evidence.import", sha, None, manifest)
            return {**manifest, "duplicate": False}
    finally:
        temporary.unlink(missing_ok=True)


@router.post("/evidence/pcap", status_code=201)
async def upload(request: Request):
    content = bytearray()
    async for chunk in request.stream():
        if len(content) + len(chunk) > MAX_BYTES:
            raise HTTPException(413, "Maximum upload size is 16 MiB")
        content.extend(chunk)
    if bytes(content[:4]) not in MAGICS:
        raise HTTPException(422, "Expected a PCAP or PCAPNG file, not an archive or text file")
    return await run_in_threadpool(import_capture, request.app.state.store, bytes(content), request.headers.get("x-filename", "capture.pcap"))


@router.get("/evidence")
def artifacts(request: Request):
    return request.app.state.store.page("evidence", page_size=1000)


@router.get("/evidence/{artifact_id}")
def artifact(request: Request, artifact_id: str):
    return request.app.state.store.get("evidence", artifact_id)


@router.get("/evidence/{artifact_id}/download")
def download(request: Request, artifact_id: str):
    record = request.app.state.store.get("evidence", artifact_id)
    sha = record["sha256"]
    if len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
        raise HTTPException(409, "Invalid stored evidence reference")
    path = evidence_directory() / f"{sha}.pcap"
    if not path.is_file():
        raise HTTPException(404, "Original evidence file is unavailable")
    if hashlib.sha256(path.read_bytes()).hexdigest() != sha:
        raise HTTPException(409, "Evidence hash mismatch; original may have been modified")
    return FileResponse(path, media_type="application/vnd.tcpdump.pcap", filename=record["originalName"])


@router.get("/packets")
def packets(request: Request, page: int = Query(1, ge=1), pageSize: int = Query(100, ge=1, le=1000), flowId: str | None = None, artifactId: str | None = None):
    records = request.app.state.store.all("packets")
    records = [p for p in records if (not flowId or p.get("flowId") == flowId) and (not artifactId or p.get("artifactId") == artifactId)]
    records.sort(key=lambda p: (p["timestamp"], p["index"]))
    preview = [{k: v for k, v in p.items() if k not in ("rawHex", "ascii", "layers")} for p in records[(page - 1)*pageSize:page*pageSize]]
    return {"data": preview, "total": len(records), "page": page, "pageSize": pageSize, "captureAvailable": bool(records), "recordType": "captured-packets"}


@router.get("/packets/{packet_id}")
def packet(request: Request, packet_id: str):
    return request.app.state.store.get("packets", packet_id)
