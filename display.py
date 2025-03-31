import uproot as up
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm, colors
from mpl_toolkits.mplot3d import Axes3D
import argparse
import sys
from os.path import join

CrystalLength = 12
CrystalWidth = 2
CrystalThick = 2
nLayer = 12
Bias = 0.5 * CrystalLength

threshold = 0


def read_file(fname: str, tree:str, event_index: int):
    with up.open(fname) as f:
        tree = f[tree]
        EventID = tree['EventID'].array(library='np')
        Layer = tree['Layer'].array(library='np')
        Index = tree['Index'].array(library='np')
        Hit_Energy = tree['ChannelEnergy'].array(library='np')

        try:
            event = np.where(EventID == event_index)[0][0]
        except:
            print(f'===> Event {event_index} does not exist in the ROOT file  {fname}')
            print('===> Abort!')
            sys.exit(1)

        layer = Layer[event]
        index = Index[event]
        energy = Hit_Energy[event]

        print(f'Entry ID: {event}')
        print(f'Event ID: {event_index}')

        assert len(layer) == len(index) == len(energy)

        return layer, index, energy


def plot(fname: str, tree: str, event_index: int, title: str, MIPThreshold: str):
    Hit_Z, Index, Hit_Energy = read_file(fname, tree, event_index)

    Hit_X = (Hit_Z % 2 == 0) * ((6.5 - Index) * CrystalWidth - Bias)
    Hit_Y = (Hit_Z % 2 == 1) * ((Index - 0.5) * CrystalWidth - Bias)

    assert len(Hit_X) == len(Hit_Y) == len(Hit_Z) == len(Hit_Energy)

    d_xyz = dict()

    for i in np.arange(len(Hit_X)):
        if Hit_Energy[i] <= threshold:
            continue
        if (Hit_X[i], Hit_Y[i], Hit_Z[i]) not in d_xyz:
            d_xyz[(Hit_X[i], Hit_Y[i], Hit_Z[i])] = Hit_Energy[i]
        else:
            d_xyz[(Hit_X[i], Hit_Y[i], Hit_Z[i])] += Hit_Energy[i]

    x_temp = np.array(list(d_xyz.keys()))[:,0]
    y_temp = np.array(list(d_xyz.keys()))[:,1]
    z_temp = np.array(list(d_xyz.keys()))[:,2]
    energy_temp = np.array(list(d_xyz.values()))

    z, y, x, energy = (np.array(a) for a in zip(*sorted(zip(z_temp, y_temp, x_temp, energy_temp), reverse=True)))

    print(f'Maximum energy deposition: {np.max(energy):.3f} MeV')

    energy_norm = energy / np.max(energy)

    nhits = len(x)
    assert nhits == len(y) == len(z) == len(energy)

    fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
    plt.gca().set_box_aspect((CrystalLength / (nLayer * CrystalThick), 1, CrystalLength / (nLayer * CrystalThick)))
    cmap = cm.OrRd

    for i in np.arange(nhits):
        if z[i] % 2 == 1:
            xnew = np.arange(x[i] - Bias, x[i] + 2 * CrystalLength - Bias, CrystalLength)
            ynew = np.arange(y[i] - 0.5 * CrystalWidth, y[i] + 1.5 * CrystalWidth, CrystalWidth)
        else:
            xnew = np.arange(x[i] - 0.5 * CrystalWidth, x[i] + 1.5 * CrystalWidth, CrystalWidth)
            ynew = np.arange(y[i] - Bias, y[i] + 2 * CrystalLength - Bias, CrystalLength)

        xnew, ynew = np.meshgrid(xnew, ynew)
        znew = z[i] * np.ones(xnew.shape)
        enew = energy_norm[i] * np.ones(xnew.shape)

        ax.plot_surface(xnew, znew, ynew, cmap=cmap, facecolors=cmap(enew), edgecolor='k', alpha=0.8, lw=0.5, rstride=1, cstride=1, antialiased=False)
        ax.computed_zorder = False

    ax.set_xlim(-0.5 * CrystalLength, 0.5 * CrystalLength)
    ax.set_ylim(1, nLayer + 1)
    ax.set_zlim(-0.5 * CrystalLength, 0.5 * CrystalLength)
    ax.set_xticks(np.linspace(-6, 6, 7))
    ax.set_yticks(np.arange(1, nLayer + 1))
    ax.set_zticks(np.linspace(-6, 6, 7))
    ax.set_aspect(aspect='equalxz')
    ax.grid(False)

    fig.suptitle(title, y=0.95, size='xx-large')
    ax.invert_xaxis()
    ax.set_xlabel("X [cm]", size='x-large')
    ax.set_ylabel("Z [layer]", size='x-large')
    ax.set_zlabel("Y [cm]", size='x-large')

    ax.text2D(0.1, 0.9, f'Threshold: {MIPThreshold}' + r'$\,$MIP' + f'\nEvent ID: {event_index}', transform=ax.transAxes)
    ax.text2D(0.75, 0.9, r'$E_\mathrm{total} = $' + f'{np.sum(energy):.3f}' + r'$\,$MeV' + f'\n' + r'$E_\mathrm{max} = $' + f'{np.max(energy):.3f}' + r'$\,$MeV', transform=ax.transAxes)

    m = plt.cm.ScalarMappable(cmap=cmap)
    m.set_array(energy)
    plt.colorbar(m, pad=0.2, ax=plt.gca()).set_label(label="Channel Energy [MeV]", size='x-large')

    ax.view_init(elev=20, azim=-50, roll=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("-f", "--file", type=str, default='', required=True, help="Input ROOT file")
    parser.add_argument("-t", "--tree", type=str, default='EventTree', help="Input tree name (default: EventTree)")
    parser.add_argument("-i", "--title", type=str, default='', help="Title of display figure")
    parser.add_argument("-e", "--event", type=int, default=0, help="ID of the event to be displayed")
    parser.add_argument("-r", "--threshold", type=str, default=0, help="MIP threshold")
    parser.add_argument("-d", "--dir", type=str, default=None, help="Directory to save the plot")
    parser.add_argument("-o", "--output", type=str, default=None, help="File name of the output plot")
    parser.add_argument("-s", "--show", type=int, default=1, choices=[0, 1], help="Instantly display or not")
    args = parser.parse_args()

    filename = args.file
    tree = args.tree
    title = args.title
    event_index = args.event
    MIPThreshold = args.threshold
    save_dir = args.dir
    output = args.output
    show = args.show

    plot(filename, tree, event_index, title, MIPThreshold)

    if save_dir and output:
        plt.savefig(join(save_dir, output), bbox_inches='tight')
        print("---> Figure ", join(save_dir, output), " successfully created!")

    if show:
        plt.show()
