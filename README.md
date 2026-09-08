# PLAXIS-SOFiSTiK Bridge
Interpolates PLAXIS displacement results (settlement/interface data) onto SOFiSTiK node coordinates, so that deformation fields computed in one FE program can be transferred and applied as boundary conditions in the other.
For each direction (x, y, z) the script interpolates cubically from the PLAXIS point cloud onto the SOFiSTiK nodes, falls back to nearest-neighbour interpolation at nodes outside the PLAXIS convex hull, and writes the combined result as a SOFiSTiK-readable `.dat`/`.txt` export. Diagnostic 3D scatter plots of the raw, interpolated, and combined fields are generated for each direction.

The repo also includes two SOFiSTiK scripts (CADINP/URSULA) that generate the input files the interpolation script needs on the SOFiSTiK side.
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
│   ├── interpolation.py                    - main interpolation script
│   ├── export_slab_displacements.dat       - SOFiSTiK script: exports slab node displacements (uz)
│   └── export_slab_support_forces.dat      - SOFiSTiK script: exports slab support forces (PZ)
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

## Generating the SOFiSTiK input data
Before running the Python script, you need `SOFISTIK_settlements.txt` and `SOFISTIK_support_forces.txt` in `data/`. These come from your own SOFiSTiK model, using the two scripts in `src/`:

- `export_slab_displacements.dat` finds the slab nodes and reads their vertical displacement (uz).
- `export_slab_support_forces.dat` finds the same nodes and reads the vertical support force (PZ) instead.

Both scripts have a `USER PARAMETERS` block at the top — set the slab elevation, plan boundary, and load case number for your model. Run them in SOFiSTiK's Teddy/URSULA environment, then copy the resulting `.txt` files into `data/`.

## Dependencies
`numpy`, `pandas`, `scipy`, `matplotlib`
## Citation
This approach was developed for and described in:
> Felić, H., Schlicke, D., Granitzer, A.-N., Tschuchnigg, F. (2023). *Enhanced Interoperability between Geotechnical and Structural Engineering for 3D Building Models*. RILEM Bookseries. DOI: [10.1007/978-3-031-33211-1_20](https://doi.org/10.1007/978-3-031-33211-1_20)
```bibtex
@incollection{felic2023interoperability,
  author    = {Feli{\'c}, Haris and Schlicke, Dirk and Granitzer, Andreas-Nizar and Tschuchnigg, Franz},
  title     = {Enhanced Interoperability between Geotechnical and Structural Engineering for 3D Building Models},
  booktitle = {International RILEM Conference on Synergising Expertise towards Sustainability and Robustness of Cement-based Materials and Concrete Structures},
  series    = {RILEM Bookseries},
  year      = {2023},
  doi       = {10.1007/978-3-031-33211-1_20}
}
```
## Citing this repository
If you use this code itself, please cite it as:
> Felić, H. (2026). *plaxis-sofistik-bridge* [Software]. Zenodo. https://doi.org/10.5281/zenodo.22661264
```bibtex
@software{felic2026plaxissofistikbridge,
  author    = {Feli{\'c}, Haris},
  title     = {plaxis-sofistik-bridge},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.22661264},
  url       = {https://doi.org/10.5281/zenodo.22661264}
}
```
(see [`CITATION.cff`](CITATION.cff) for a machine-readable version — GitHub also exposes this via the "Cite this repository" button in the sidebar.)
## License
See `LICENSE`.
