# PLAXIS-SOFiSTiK Bridge

Interpolates PLAXIS displacement results (settlement/interface data) onto SOFiSTiK node coordinates, so that deformation fields computed in one FE program can be transferred and applied as boundary conditions in the other.

For each direction (x, y, z) the script interpolates cubically from the PLAXIS point cloud onto the SOFiSTiK nodes, falls back to nearest-neighbour interpolation at nodes outside the PLAXIS convex hull, and writes the combined result as a SOFiSTiK-readable `.dat`/`.txt` export. Diagnostic 3D scatter plots of the raw, interpolated, and combined fields are generated for each direction.

---

## Structure

```
├── data/                       - input/output data files
│   ├── PLAXIS_export.csv       - PLAXIS displacement export (tracked via Git LFS)
│   ├── SOFISTIK_settlements.txt
│   ├── SOFISTIK_support_forces.txt
│   ├── export_SOFiSTiK.txt     - interpolated output, readable copy (generated)
│   └── export_SOFiSTiK.dat     - interpolated output, import this into SOFiSTiK (generated)
├── graphics/                   - diagnostic plots per direction (generated)
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

```bash
python src/interpolation.py
```

This runs against the sample data already in `data/` and writes the export files there plus diagnostic plots to `graphics/`. To use your own data, replace `data/PLAXIS_export.csv` (`;`-delimited CSV) and `data/SOFISTIK_settlements.txt`, or point `entry_pla` / `entry_sof` in the `__main__` block of `src/interpolation.py` at different files.

## Dependencies

`numpy`, `pandas`, `scipy`, `matplotlib`

## Citation

This approach was developed for and described in:

> Felić, H., Schlicke, D., Granitzer, A.-N., Tschuchnigg, F. (2023). *Enhanced Interoperability between Geotechnical and Structural Engineering for 3D Building Models*. RILEM Bookseries. DOI: [10.1007/978-3-031-33211-1_20](https://doi.org/10.1007/978-3-031-33211-1_20)

## License

See `LICENSE`.
