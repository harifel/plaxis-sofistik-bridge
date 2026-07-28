# PLAXIS-SOFiSTiK Bridge

Interpolates PLAXIS displacement results (settlement/interface data) onto SOFiSTiK node coordinates, so that deformation fields computed in one FE program can be transferred and applied as boundary conditions in the other.

For each direction (x, y, z) the script interpolates cubically from the PLAXIS point cloud onto the SOFiSTiK nodes, falls back to nearest-neighbour interpolation at nodes outside the PLAXIS convex hull, and writes the combined result as a SOFiSTiK-readable `.dat`/`.txt` export. Diagnostic 3D scatter plots of the raw, interpolated, and combined fields are generated for each direction.

---

## Structure

```
├── data/                       - input/output data files
│   ├── PLAXIS_export.csv       - PLAXIS displacement export (add your own; not tracked)
│   ├── SOFISTIK_settlements.txt
│   ├── SOFISTIK_support_forces.txt
│   ├── export_SOFiSTiK.txt     - interpolated output (generated)
│   └── export_SOFiSTiK.dat     - interpolated output (generated)
├── src/
│   └── interpolation.py        - main interpolation script
└── environment.txt             - Python dependencies
```

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows — or: source venv/bin/activate
pip install -r environment.txt
```

Place your PLAXIS export (`;`-delimited CSV) and SOFiSTiK node file in `data/`, then run:

```bash
python src/interpolation.py
```

Update the `entry_pla` / `entry_sof` filenames in `src/interpolation.py` if yours differ from the defaults.

## Dependencies

`numpy`, `pandas`, `scipy`, `matplotlib`

## License

See `LICENSE`.
