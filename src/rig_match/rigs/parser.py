"""Best-effort parser for Kemper rig files (``.krig`` / ``.kipr``) and Rig Manager blobs.

Kemper does not document the format. What has been observed so far:

Container, modelled on Standard MIDI Files (``MThd`` / ``MTrk``)::

    "KThd" <u32 be length=6> <u16 format> <u16 ntracks> <u16 division>
    "KTrk" <u32 be length> <track bytes>        repeated ntracks times

A rig is format 0 with one track, division 480. (Performance files use format 1
with six tracks; they are parsed as far as the container goes but not used.)

Track: a sequence of events, each ``<delta: VLQ> F0 <length: VLQ> <payload...> F7``
where the payload starts with Kemper's SysEx manufacturer id ``00 20 33``, a
function byte, and then the message body.

Bodies seen in a rig (35 messages in a typical one):

* function ``0x00``, body ``00 03 <a> <b> <c> <text> 00`` : a string parameter at
  address ``(a, b, c)``. ``(0,0,1)`` rig name, ``(0,0,2)`` author, ``(0,0,3)`` date,
  ``(0,0,4)`` comment, ``(0,0,0x20)`` cabinet name, ``(0,0,0x21)`` cabinet author,
  ``(0,0,0x24)`` location, ``(0,0x4e,0x0e)`` firmware version string, and more.
* function ``0x00``, body ``00 02 ...`` : numeric parameters (encoding not decoded).
* function ``0x02`` : larger fixed-size blocks (amp / cab / effect settings, not decoded).
* function ``0x33`` : one message, meaning unknown.

Only the container walk and the string parameters are implemented. Decoding the
numeric and block parameters (gain, definition, clarity, cab, stack, effect
slots ...) is open work; the Kemper MIDI parameter documentation and the
``Gain`` / ``Amp Name`` columns Rig Manager derives from the same blob are the
obvious cross-checks.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

HEADER_MAGIC = b"KThd"
TRACK_MAGIC = b"KTrk"
KEMPER_SYSEX_ID = b"\x00\x20\x33"
SYSEX_START = 0xF0
SYSEX_END = 0xF7

# Addresses of the string parameters identified so far.
RIG_NAME = (0, 0, 0x01)
RIG_AUTHOR = (0, 0, 0x02)
RIG_DATE = (0, 0, 0x03)
RIG_COMMENT = (0, 0, 0x04)
CABINET_NAME = (0, 0, 0x20)
CABINET_AUTHOR = (0, 0, 0x21)


class RigParseError(ValueError):
    pass


@dataclass
class SysExMessage:
    delta: int
    payload: bytes  # from the manufacturer id up to (not including) F7

    @property
    def function(self) -> int:
        return self.payload[3]

    @property
    def body(self) -> bytes:
        return self.payload[4:]


@dataclass
class RigFile:
    format: int
    division: int
    tracks: list[list[SysExMessage]]

    @property
    def messages(self) -> list[SysExMessage]:
        """All messages of all tracks, in file order."""
        return [m for track in self.tracks for m in track]

    def strings(self) -> dict[tuple[int, int, int], str]:
        """String parameters keyed by their 3-byte address."""
        out: dict[tuple[int, int, int], str] = {}
        for m in self.messages:
            b = m.body
            if m.function == 0x00 and len(b) >= 5 and b[:2] == b"\x00\x03":
                text = b[5:].split(b"\x00", 1)[0]
                # Character set unknown; latin-1 never fails and is right for ASCII.
                out[(b[2], b[3], b[4])] = text.decode("latin-1")
        return out

    @property
    def name(self) -> str | None:
        return self.strings().get(RIG_NAME)


def _read_vlq(buf: bytes, pos: int) -> tuple[int, int]:
    """MIDI variable-length quantity at ``pos``; returns (value, next position)."""
    value = 0
    while True:
        if pos >= len(buf):
            raise RigParseError("truncated variable-length quantity")
        byte = buf[pos]
        pos += 1
        value = (value << 7) | (byte & 0x7F)
        if not byte & 0x80:
            return value, pos


def _iter_messages(track: bytes) -> Iterator[SysExMessage]:
    pos = 0
    while pos < len(track):
        delta, pos = _read_vlq(track, pos)
        if pos >= len(track) or track[pos] != SYSEX_START:
            raise RigParseError(f"expected SysEx start at track offset {pos}")
        length, pos = _read_vlq(track, pos + 1)
        chunk = track[pos : pos + length]
        if len(chunk) != length or chunk[-1] != SYSEX_END:
            raise RigParseError(f"bad SysEx message at track offset {pos}")
        pos += length
        payload = chunk[:-1]
        if not payload.startswith(KEMPER_SYSEX_ID):
            raise RigParseError(f"not a Kemper SysEx message at track offset {pos}")
        yield SysExMessage(delta=delta, payload=payload)


def _chunk(data: bytes, pos: int, magic: bytes) -> tuple[bytes, int]:
    if data[pos : pos + 4] != magic:
        raise RigParseError(f"expected {magic!r} at offset {pos}")
    length = int.from_bytes(data[pos + 4 : pos + 8], "big")
    body = data[pos + 8 : pos + 8 + length]
    if len(body) != length:
        raise RigParseError(f"truncated {magic!r} chunk")
    return body, pos + 8 + length


def parse_rig_bytes(data: bytes) -> RigFile:
    header, pos = _chunk(data, 0, HEADER_MAGIC)
    if len(header) != 6:
        raise RigParseError(f"unexpected header length {len(header)}")
    fmt, ntracks, division = (int.from_bytes(header[i : i + 2], "big") for i in (0, 2, 4))
    tracks: list[list[SysExMessage]] = []
    for _ in range(ntracks):
        track, pos = _chunk(data, pos, TRACK_MAGIC)
        tracks.append(list(_iter_messages(track)))
    if pos != len(data):
        raise RigParseError(f"{len(data) - pos} trailing bytes after the last track chunk")
    return RigFile(format=fmt, division=division, tracks=tracks)


def parse_rig_file(path: Path) -> RigFile:
    return parse_rig_bytes(Path(path).read_bytes())
