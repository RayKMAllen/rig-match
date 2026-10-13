# Local data (not committed)

Everything in this directory except this file is ignored by git. It holds
reference material pulled from the Windows side of this machine so the
pipeline can be developed against real inputs.

## Contents after `python scripts/sync_rigmanager_data.py`

```text
data/
  manifest.json                       what was copied, from where, when
  songs/                              a couple of commercial songs (MP3, tagged)
  rigmanager/                         snapshot of selected Kemper Rig Manager library DBs
    Local Library/repositoryR2.db       the hand-curated local rig library (one row per rig)
    Local Library/<pack>/repositoryR2.db  a few small profile packs (Muse, Pink Floyd, Kemper Stage GL, Michael Britt '69 Marsh)
  rigs/
    local_library/*.krig                every rig of the local library exported as a file
    rigbackups/*.krig                   .krig files Rig Manager itself wrote to disk
```

## Where it comes from

Rig Manager keeps its library in `%LOCALAPPDATA%\Kemper Amps\RigManager`
(from WSL: `/mnt/c/Users/<user>/AppData/Local/Kemper Amps/RigManager`).
Each library folder is a SQLite file `repositoryR2.db`; the `Rigs` table has
the metadata columns Rig Manager shows in its list view and `Rigs_blobs.data`
is the raw rig, byte-for-byte what a `.krig` file on disk contains.

The full tree is a couple of GB (one 80 000-rig pack alone is 500 MB), so the
sync script copies only the packs listed at the top of it. Edit that list to
pull more. Quit Rig Manager before syncing.

Songs come from the Windows `Music` folder. Both inputs are personal media and
stay local.
