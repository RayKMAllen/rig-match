# Song-to-Kemper Rig Matcher

## Overview

Build a desktop application that:

1. Accepts songs from local audio files and/or Spotify playlists (metadata only)
2. Extracts and analyzes guitar tones section-by-section
3. Maps each distinct tone section to:
   - an existing Kemper rig
   - or a customized variant of a rig
4. Produces a complete Kemper Performance layout per song
5. Optionally iterates using user-recorded DI guitar input for refinement

The system is not intended to produce mathematically perfect reproductions of commercial recordings.

The goal is:

> Produce live-usable and mix-convincing Kemper performances that match the production intent of commercial songs.

The system should optimize for perceptual similarity and live-playable usability rather than exact waveform reproduction of commercial recordings.

---

# Core Principles

The system does NOT attempt to:

- perfectly recreate studio masters
- reverse-engineer proprietary Kemper internals
- synthesize new magical AI amp models from scratch

The system DOES:

- isolate guitar stems
- detect distinct guitar-tone sections
- classify amp/gain/cab characteristics
- search existing Kemper rigs
- optimize Kemper parameter settings
- generate post-EQ correction
- optionally refine using DI reamping

This is fundamentally:

> retrieval + analysis + optimization

—not generative AI.

---

# High-Level Workflow

```text
Song Input
    ↓
Stem Separation
    ↓
Song Structure Detection
    ↓
Guitar Tone Segmentation
    ↓
Tone Clustering
    ↓
Rig Candidate Search
    ↓
Rig Ranking
    ↓
Optional DI/Reamp Refinement
    ↓
Kemper Parameter Optimization
    ↓
Post-EQ Matching
    ↓
Performance Export
```

---

# Inputs

## Required Inputs

### Songs

Supported formats:

- WAV
- FLAC
- MP3
- AAC
- AIFF

### Song Metadata

Can come from:

- local tags
- CSV
- Spotify playlist URL

Spotify usage is metadata-only.

The app must NOT attempt to rip Spotify audio.

---

## Optional Inputs

### User Guitar Profile

```json
{
  "guitar_model": "Ibanez RG",
  "pickup_type": "high_output_humbucker",
  "tuning": "Drop C",
  "string_gauge": "10-52",
  "pickup_position": "bridge"
}
```

### User DI Recording

Optional clean DI recording of riffs/chords.

This significantly improves optimization quality.

---

# Outputs

For each song:

- detected tone sections
- grouped reusable tones
- recommended Kemper rigs
- suggested Kemper parameter changes
- optional post-EQ curve
- Kemper Performance slot layout
- performance switch timeline

---

# Example Output

```json
{
  "song": "Metallica - Enter Sandman",
  "sections": [
    {
      "section_id": "intro_clean_01",
      "start": 0.0,
      "end": 12.4,
      "tone_id": "tone_A"
    },
    {
      "section_id": "verse_01",
      "start": 12.4,
      "end": 44.0,
      "tone_id": "tone_B"
    },
    {
      "section_id": "chorus_01",
      "start": 44.0,
      "end": 70.0,
      "tone_id": "tone_C"
    }
  ],
  "tones": [
    {
      "tone_id": "tone_A",
      "recommended_rig": {
        "name": "MBritt Clean Deluxe",
        "amp_family": "Fender Deluxe",
        "confidence": 0.87
      },
      "kemper_edits": {
        "definition": 5.2,
        "clarity": 1.0,
        "gain_delta": -0.4
      },
      "post_eq": []
    },
    {
      "tone_id": "tone_B",
      "recommended_rig": {
        "name": "Recto Tight Rhythm",
        "amp_family": "Mesa Rectifier",
        "confidence": 0.91
      },
      "kemper_edits": {
        "definition": 7.8,
        "pick": 1.3,
        "compression": 0.9
      },
      "post_eq": [
        {
          "freq": 90,
          "type": "highpass"
        },
        {
          "freq": 7800,
          "type": "lowpass"
        }
      ]
    }
  ],
  "performance_map": [
    {
      "time": 0.0,
      "slot": 1,
      "tone_id": "tone_A"
    },
    {
      "time": 12.4,
      "slot": 2,
      "tone_id": "tone_B"
    }
  ]
}
```

---

# System Architecture

# 1. Song Intake Module

## Responsibilities

- import audio files
- import playlists
- map metadata
- normalize file organization

## Features

### Local File Import

Accept:

- folders
- drag/drop
- playlists
- CSV manifests

### Spotify Metadata Import

Use Spotify API for:

- title
- artist
- album
- track ordering

Do NOT depend on Spotify audio APIs.

### Internal Storage Layout

```text
/project/
  /songs/
    /song_id/
      original.wav
      metadata.json
```

---

# 2. Stem Separation Module

## Goal

Extract isolated guitar stems.

## Recommended Models

Primary:

- Demucs

Secondary:

- MDX-Net
- UVR backend

## Outputs

```text
/song_id/
  guitar.wav
  vocals.wav
  bass.wav
  drums.wav
  other.wav
```

## Optional Advanced Outputs

Attempt:

- left/right guitar separation
- rhythm vs lead separation

This should be experimental.

## Notes

Stem quality is critical.

Poor stem separation causes:

- bad spectral analysis
- wrong amp-family inference
- false tone clustering

---

# 3. Song Structure + Tone Segmentation Module

## Goal

Detect every materially distinct guitar-tone section.

This replaces simplistic:

```text
one song → one rig
```

with:

```text
one song → multiple reusable tones
```

---

## Example

```text
0:00–0:12  Intro clean
0:12–0:44  Verse crunch
0:44–1:10  Chorus high gain
1:10–1:25  Lead fill
1:25–1:58  Verse crunch
1:58–2:30  Chorus high gain
2:30–2:55  Solo
```

---

## Submodule A — Structural Segmentation

Detect:

- intro
- verse
- chorus
- bridge
- solo
- outro

### Techniques

Use:

- self-similarity matrices
- novelty curves
- chroma analysis
- onset density
- RMS energy
- spectral flux

Libraries:

- librosa
- essentia

---

## Submodule B — Guitar Tone Segmentation

Detect actual tone changes.

This is independent from musical structure.

### Example

A chorus may contain:

- rhythm layer
- octave layer
- lead overdub

Tone segmentation should identify materially different guitar textures.

### Features

Extract:

- spectral centroid
- spectral tilt
- distortion density
- transient sharpness
- stereo width
- modulation depth
- reverb tail energy
- saturation profile
- dynamic range
- cab resonance peaks

---

## Submodule C — Tone Clustering

Cluster equivalent tones.

Example:

```text
verse_01 + verse_02 → same crunch tone
chorus_01 + chorus_02 → same rhythm tone
```

### Algorithms

Recommended:

- HDBSCAN
- agglomerative clustering

---

## Final Output

Generate:

```json
{
  "tone_A": "clean intro",
  "tone_B": "verse crunch",
  "tone_C": "chorus rhythm",
  "tone_D": "solo lead"
}
```

---

# 4. Feature Extraction Module

## Goal

Convert isolated guitar sections into searchable tone descriptors.

---

## Features to Extract

### Spectral

- spectral centroid
- spectral rolloff
- spectral contrast
- spectral flatness
- spectral bandwidth

### Dynamic

- RMS
- crest factor
- transient sharpness
- envelope decay

### Distortion Metrics

- harmonic density
- odd/even harmonic balance
- saturation estimate

### Stereo Metrics

- stereo width
- correlation
- Haas delay estimate

### Production Metrics

- roominess
- delay density
- modulation detection

### Musical Metrics

- tuning estimate
- tempo
- note density
- chord density

---

## Output Example

```json
{
  "gain_estimate": 0.82,
  "brightness": 0.73,
  "tightness": 0.88,
  "mid_focus": 0.66,
  "stereo_width": 0.71,
  "transient_aggression": 0.91,
  "cab_resonance_peak": 3200
}
```

---

# 5. User DI Module

## Goal

Allow user-recorded DI for iterative refinement.

---

## DI Recording Chain

Minimum viable:

```text
Guitar → audio interface Hi-Z input → app
```

---

## Features

- record DI
- trim silence
- normalize level
- align timing
- save riff library

---

## Why This Matters

Without DI:

- performance differences distort comparisons
- optimization quality drops substantially

With DI:

- identical performance can be reamped repeatedly
- rig comparisons become objective

---

# 6. Rig Library Module

## Goal

Maintain searchable local Kemper rig database.

---

## Sources

- local rigs
- Rig Exchange imports
- commercial packs
- manually tagged rigs

---

## Supported Files

- .krig
- .kipr
- .kpreset

---

## Internal Metadata

```json
{
  "rig_name": "Recto Tight Modern",
  "amp_family": "Mesa Rectifier",
  "gain_category": "high_gain",
  "cab_type": "V30",
  "brightness": 0.77,
  "tightness": 0.91,
  "tags": ["metal", "tight", "modern"]
}
```

---

## Important Design Constraint

Do NOT rely heavily on undocumented Kemper internals.

Treat rigs primarily as:

- metadata objects
- audio-renderable candidates

---

# 7. Candidate Rig Search Module

## Goal

Find top rig candidates for each detected tone.

---

## Strategy

### Step 1 — Amp Family Classification

Classify likely family:

- Fender
- Vox
- Marshall
- Mesa
- Soldano
- 5150
- ENGL
- Orange
- Dumble

---

### Step 2 — Gain Classification

Determine:

- clean
- edge
- crunch
- hard rock
- high gain
- extreme gain

---

### Step 3 — Similarity Search

Compare:

- spectral features
- transient features
- stereo profile
- saturation profile

---

## Ranking Formula

```text
score =
  0.30 amp_family_match +
  0.25 gain_match +
  0.25 spectral_match +
  0.10 transient_match +
  0.10 user_history
```

---

## Output

Return top N candidates.

Default:

```text
Top 5 rigs per tone
```

---

# 8. Reamp + Render Comparison Module

## Goal

Compare target guitar stem against actual Kemper output.

---

## MVP Workflow

1. App suggests rig
2. User loads rig into Kemper
3. User reamps DI
4. App records Kemper output
5. App compares render to target

---

## Advanced Workflow

Automate:

- MIDI rig switching
- batch testing
- automated render capture

---

## Comparison Metrics

### Loudness-Normalized

Always normalize before comparison.

---

### Compare

- frequency response
- transient shape
- distortion density
- dynamic envelope
- stereo width

---

## Optional Null Testing

Align and phase-invert:

- target stem
- Kemper render

Residual energy estimates mismatch.

---

# 9. Kemper Optimization Module

## Goal

Optimize Kemper parameters after selecting candidate rig.

---

## Adjustable Parameters

### Amp Section

- gain
- definition
- clarity
- compressor
- pick
- tube shape
- tube bias

### Cabinet Section

- character
- high shift
- low shift
- pure cabinet

### FX

- delay
- reverb
- modulation
- EQ

---

## Optimization Strategy

Use black-box optimization.

Recommended:

- Optuna
- Nevergrad

---

## Objective Function

Minimize:

```text
perceptual_distance(
  target_stem,
  rendered_output
)
```

Not waveform identity.

---

## Human-in-the-Loop

Every few iterations:

- allow A/B comparison
- allow user weighting

Example:

```text
More aggressive
Less fizzy
Tighter low end
More open mids
```

---

# 10. Post-EQ Matching Module

## Goal

Generate final corrective EQ after Kemper output.

This is critical.

Most commercial tones contain substantial post-processing.

---

## Process

1. Compare rendered output to target stem
2. Generate smooth corrective curve
3. Limit excessive boosts/cuts

---

## Rules

### Defaults

- max ±6 dB
- smooth broad curves
- avoid narrow spikes

### Ignore Zones

Usually ignore:

- below 80 Hz
- above 10–12 kHz

unless clearly required.

---

## Export Formats

- JSON
- ReaEQ preset
- generic parametric bands
- optional FabFilter approximation

---

# 11. Performance Builder Module

## Goal

Build Kemper-style song performances.

---

## Example

```text
Performance: Enter Sandman

Slot 1 → Intro Clean
Slot 2 → Verse Crunch
Slot 3 → Chorus Rhythm
Slot 4 → Solo Lead
Slot 5 → Special FX
```

---

## Timeline Mapping

```json
[
  {
    "time": 0.0,
    "slot": 1
  },
  {
    "time": 12.4,
    "slot": 2
  },
  {
    "time": 44.0,
    "slot": 3
  }
]
```

---

## Future Extensions

- MIDI automation
- setlist mode
- live synchronization
- automatic performance switching

---

# Command-Line Interface Design

The tool should be a bare CLI application. No desktop GUI, browser shell, React, Electron, Tauri, or Qt.

The CLI should support scripted, repeatable workflows and should prioritize analysis quality over interface polish.

---

# CLI Commands

## Initialize Project

```bash
kemper-match init ./my_project
```

Creates:

```text
my_project/
  config.yaml
  songs/
  stems/
  analysis/
  rigs/
  renders/
  exports/
```

---

## Import Songs

```bash
kemper-match import-audio ./audio_folder --project ./my_project
```

Optional metadata import:

```bash
kemper-match import-playlist spotify_playlist_url --metadata-only --project ./my_project
```

Spotify import must remain metadata-only.

---

## Separate Stems

```bash
kemper-match separate --project ./my_project --song song_id
```

Batch mode:

```bash
kemper-match separate --project ./my_project --all
```

---

## Analyze Song Structure and Tones

```bash
kemper-match analyze --project ./my_project --song song_id
```

Outputs:

```text
analysis/song_id/sections.json
analysis/song_id/tones.json
analysis/song_id/features.json
```

---

## Import Rig Library

```bash
kemper-match import-rigs ./kemper_rigs --project ./my_project
```

Indexes local `.krig`, `.kipr`, and `.kpreset` files where possible.

---

## Recommend Rigs

```bash
kemper-match recommend --project ./my_project --song song_id
```

Outputs top candidates per detected tone.

---

## Record DI

```bash
kemper-match record-di --project ./my_project --song song_id --tone tone_A
```

Optional parameters:

```bash
--input-device "Focusrite USB"
--duration 20
--sample-rate 48000
```

---

## Capture Kemper Render

```bash
kemper-match capture-render --project ./my_project --song song_id --tone tone_A --rig rig_id
```

This records the Kemper output after the user manually loads the candidate rig.

---

## Compare Render to Target

```bash
kemper-match compare --project ./my_project --song song_id --tone tone_A --render render_id
```

Outputs perceptual distance metrics and EQ suggestions.

---

## Optimize Rig Settings

```bash
kemper-match optimize --project ./my_project --song song_id --tone tone_A --rig rig_id
```

The MVP may output suggested settings without automating the Kemper.

---

## Export Performance Plan

```bash
kemper-match export --project ./my_project --song song_id --format json
```

Optional:

```bash
--format markdown
--format yaml
```

---

# CLI-First Design Principles

- every command must be scriptable
- all outputs must be saved as JSON/YAML/Markdown
- no state should exist only in memory
- no GUI-only operation should be required
- all intermediate artifacts must be inspectable
- batch mode should be supported wherever practical

---

# Recommended Tech Stack

# Core Language

- Python

---

# Backend / Processing

- PyTorch
- librosa
- essentia
- scipy
- numpy
- pandas
- Optuna
- Demucs
- ffmpeg
- pyloudnorm

---

# CLI

- Typer or Click
- Rich for terminal output
- tqdm for progress bars

---

# Audio

- ffmpeg
- PortAudio
- sounddevice
- pyloudnorm

---

# Storage

- SQLite
- local cache

---

# AI / ML Components

## Required

- stem separation
- feature extraction
- clustering
- similarity search
- optimization

## Not Required

- giant foundation models
- generative transformers
- LLM inference during runtime

---

# MVP Roadmap

# Phase 1 — Offline Analyzer

Build:

- song import
- stem separation
- tone segmentation
- rig recommendation

No DI.

No optimization.

---

# Phase 2 — DI/Reamp Loop

Add:

- DI recording
- Kemper render capture
- objective comparison

---

# Phase 3 — Optimization

Add:

- Kemper parameter optimization
- post-EQ generation
- user preference weighting

---

# Phase 4 — Performance Builder

Add:

- automatic slot layout
- timeline switching
- setlists

---

# Phase 5 — Automation

Optional:

- MIDI control
- automatic Kemper switching
- live integration

---

# Critical Constraints

# 1. Commercial Mixes Are Underdetermined

Many different signal chains can produce similar outputs.

The system should optimize for:

```text
perceptual similarity
```

—not exact recreation.

---

# 2. Multi-Tracking Complicates Everything

Commercial guitars are often:

- double tracked
- quad tracked
- layered
- differently EQ'd per side

The system should focus on:

- dominant perceived tone
- live-playable approximations

---

# 3. Kemper Is Not Fully Differentiable

Kemper rigs are effectively black-box snapshots.

Optimization must occur externally.

---

# 4. Human Review Must Exist

Fully autonomous tone matching will produce many false positives.

Human approval is required.

---

# Practical Success Criteria

A successful result means:

```text
Sounds convincingly close in context.
```

—not:

```text
Waveform-identical to isolated studio tracks.
```

---

# Final System Philosophy

The system should behave like:

> an extremely knowledgeable guitar tone engineer assistant

—not:

> magical AI that perfectly clones commercial albums.

The biggest gains come from:

- stem isolation
- structured tone segmentation
- rig retrieval
- iterative reamping
- EQ matching

—not from exotic machine learning.

