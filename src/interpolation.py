"""Transfers PLAXIS displacement results onto a SOFiSTiK mesh.

Workflow:
  1. Read the PLAXIS export: node coordinates (x, y) plus the displacement
     components (ux, uy, uz) at each PLAXIS node.
  2. Read the SOFiSTiK node coordinates (x, y) that the displacements
     should be transferred onto.
  3. For each direction (x, y, z), cubic-interpolate from the PLAXIS point
     cloud onto the SOFiSTiK nodes. Nodes outside the PLAXIS convex hull
     (where cubic interpolation returns NaN) fall back to nearest-neighbour
     interpolation.
  4. Write the interpolated displacements, in SOFiSTiK node-displacement
     format, to `export_SOFiSTiK.dat` (this is the file to import into
     SOFiSTiK) and `export_SOFiSTiK.txt` (the same content, kept readable),
     plus a diagnostic 3D scatter plot per direction (raw / interpolated /
     combined) in `graphics/`.
"""
import os

import numpy as np
import pandas as pd
from scipy import interpolate
import matplotlib.pyplot as plt

FONT_SIZE = 10
plt.rc('font', size=FONT_SIZE)
plt.rc('axes', titlesize=FONT_SIZE, labelsize=FONT_SIZE)
plt.rc('xtick', labelsize=FONT_SIZE)
plt.rc('ytick', labelsize=FONT_SIZE)
plt.rc('legend', fontsize=FONT_SIZE)
plt.rc('figure', titlesize=FONT_SIZE)
plt.rcParams['font.family'] = 'Times New Roman'
CM = 1 / 2.54  # centimeters -> inches

DIRECTIONS = ('x', 'y', 'z')

# Column layout of the SOFiSTiK node table after interpolation:
# 0=Nod 1=X 2=Y 3=Z(<-uz) 4=A 5=(new, <-uy) 6=(new, <-ux)
VALUE_COLS = (3, 5, 6)  # uz, uy, ux


def load_plaxis_data(path):
    """Reads a PLAXIS displacement export (';'-delimited CSV)."""
    data = pd.read_csv(path, delimiter=';')
    x, y = data.iloc[:, 0].values, data.iloc[:, 1].values
    ux, uy, uz = data.iloc[:, 3].values, data.iloc[:, 4].values, data.iloc[:, 5].values
    return x, y, (ux, uy, uz)


def load_sofistik_nodes(path):
    """Reads SOFiSTiK node coordinates, skipping the header/footer rows."""
    return pd.read_csv(
        path, sep=r'\s+', skiprows=4, skipfooter=1, header=None,
        names=['Nod', 'X', 'Y', 'Z', 'A'], engine='python',
    )


def build_export(nodes, n_components):
    """Assembles the SOFiSTiK export table using the first `n_components` fields (uz, uy, ux order)."""
    n = len(nodes)
    columns = [
        pd.Series('knot', index=np.arange(n)),
        pd.Series('nr', index=np.arange(n)),
        nodes.iloc[:, 0],
        pd.Series('typ', index=np.arange(n)),
        pd.Series('wzz,wyy,wxx', index=np.arange(n)),
    ]
    for col in VALUE_COLS[:n_components]:
        sign = -1000 if col == 3 else 1000
        columns.append(nodes.iloc[:, col] * sign)
    return pd.DataFrame(columns).transpose()


def write_sofistik_export(export_dir, export_df):
    """Writes the interpolated node displacements for SOFiSTiK.

    `export_SOFiSTiK.dat` is the file to import into SOFiSTiK; `.txt` is
    the same data with a readability space after each comma.
    """
    txt_path = os.path.join(export_dir, 'export_SOFiSTiK.txt')
    dat_path = os.path.join(export_dir, 'export_SOFiSTiK.dat')
    n_value_cols = export_df.shape[1] - 5
    fmt = ['%s', '%s', '%d', '%s', '%s'] + ['%.20e,'] * (n_value_cols - 1) + ['%.20e']
    np.savetxt(txt_path, export_df, fmt=fmt)
    with open(txt_path) as f_in, open(dat_path, 'w') as f_out:
        f_out.write(f_in.read().replace(', ', ','))
    print(f'SOFiSTiK import file written to: {dat_path}')


def _label_axes(ax, z_label):
    ax.set_xlabel('x-axis (m)', labelpad=2)
    ax.set_ylabel('y-axis (m)', labelpad=2)
    ax.set_zlabel(z_label, labelpad=10)


def _save_figure(path):
    plt.subplots_adjust(left=-0.10, right=1, top=1.02, bottom=0.15, wspace=0.5, hspace=0.5)
    plt.savefig(path, dpi=700)


def plot_direction(direction, check_col, x_p, y_p, u_component, x_s, y_s, z_zero, grid_component, error_rows, out_dir):
    """Writes the three diagnostic scatter plots (raw / interpolated / combined) for one direction."""
    label = f'$u_{direction}$ (m)'
    has_errors = len(error_rows) > 0

    fig = plt.figure(figsize=(8.4 * CM, 6 * CM), dpi=700)
    ax = fig.add_subplot(111, projection='3d')
    ax.view_init(elev=40, azim=-60)
    ax.scatter(x_p, y_p, abs(u_component), c='k', alpha=0.3, s=0.0005)
    ax.scatter(x_s, y_s, z_zero, c='blue', s=0.1)
    _label_axes(ax, label)
    ax.set_zlim(0, 0.10)
    ax.set_zlim(ax.get_zlim()[::-1])
    _save_figure(os.path.join(out_dir, f'001_rawData_in {direction}.png'))

    fig = plt.figure(figsize=(8.4 * CM, 6 * CM), dpi=700)
    ax = plt.axes(projection='3d')
    ax.view_init(elev=40, azim=-60)
    ax.scatter(x_s, y_s, grid_component, c='green', s=1)
    if has_errors:
        ax.scatter(error_rows.iloc[:, 1], error_rows.iloc[:, 2], error_rows.iloc[:, check_col], c='red')
    _label_axes(ax, label)
    _save_figure(os.path.join(out_dir, f'002_interpolatedData_in {direction}.png'))

    fig = plt.figure(figsize=(8.4 * CM, 6 * CM), dpi=700)
    ax = plt.axes(projection='3d')
    ax.view_init(elev=40, azim=-60)
    ax.scatter(x_s, y_s, abs(grid_component), c='blue', s=0.1)
    if has_errors:
        ax.scatter(error_rows.iloc[:, 1], error_rows.iloc[:, 2], abs(error_rows.iloc[:, check_col]), c='red')
    ax.scatter(x_p, y_p, abs(u_component), c='k', alpha=0.3, s=0.0005)
    _label_axes(ax, label)
    ax.set_zlim(0, 0.10)
    ax.set_zlim(ax.get_zlim()[::-1])
    _save_figure(os.path.join(out_dir, f'003_combinedData_in {direction}.png'))


def run_interpolation(entry_pla, entry_sof, export_dir, graphics_dir=None, make_plots=True):
    x_p, y_p, u = load_plaxis_data(entry_pla)

    nodes = load_sofistik_nodes(entry_sof)
    x_s, y_s = nodes.iloc[:, 1].values, nodes.iloc[:, 2].values
    z_zero = pd.DataFrame(0, index=np.arange(len(x_s)), columns=['z'])

    grid = [interpolate.griddata((x_p, y_p), comp, (x_s, y_s), method='cubic') for comp in u]
    nodes.iloc[:, 3] = grid[2]  # Z column <- uz
    nodes.loc[:, 4] = grid[1]   # new column <- uy
    nodes.loc[:, 5] = grid[0]   # new column <- ux

    export = None
    error_rows = [None, None, None]
    for i, direction in enumerate(DIRECTIONS):
        check_col = 5 - i
        missing = nodes[nodes.iloc[:, check_col].isnull()]
        if missing.empty:
            print(f'Your data interpolation contains in {direction} direction no errors!')
            if i == 0:
                export = build_export(nodes, n_components=3)
        else:
            nearest = interpolate.griddata((x_p, y_p), u[i], (missing.iloc[:, 1], missing.iloc[:, 2]), method='nearest')
            missing = missing.copy()
            missing.iloc[:, check_col] = nearest
            nodes.update(missing)
            export = build_export(nodes, n_components=i + 1)
            print(f'Important message:\n Your data interpolation in {direction} direction contains errors '
                  f'at {len(missing)} nodes. \n Another interpolation mode (neighbour points) has been set!')
        error_rows[i] = missing

    write_sofistik_export(export_dir, export)

    if make_plots:
        os.makedirs(graphics_dir, exist_ok=True)
        for j, direction in enumerate(DIRECTIONS):
            plot_direction(direction, 5 - j, x_p, y_p, u[j], x_s, y_s, z_zero, grid[j], error_rows[j], graphics_dir)


if __name__ == '__main__':
    BASE_DIR = os.path.dirname(__file__)
    DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
    GRAPHICS_DIR = os.path.join(BASE_DIR, '..', 'graphics')
    run_interpolation(
        entry_pla=os.path.join(DATA_DIR, 'PLAXIS_export.csv'),
        entry_sof=os.path.join(DATA_DIR, 'SOFISTIK_settlements.txt'),
        export_dir=DATA_DIR,
        graphics_dir=GRAPHICS_DIR,
        make_plots=True,
    )
