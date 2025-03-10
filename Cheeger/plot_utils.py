import numpy as np
import matplotlib.pyplot as plt
from matplotlib.tri import Triangulation


# TODO: clean, comment, write docstrings

def plot_primal_dual_results(u, eta_bar):
    fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(7, 14))

    grid_size = u.shape[0]
    h = 1 / grid_size

    # 2/grid_size oder 1/grid_size... eigentlich ja Gebiet [0,1] nicht [-1,1].
    
    eta_avg = eta_bar  / h ** 2

    v_abs_max = np.max(np.abs(eta_avg))

    im = axs[0].imshow(eta_avg, cmap='bwr', vmin=-v_abs_max, vmax=v_abs_max)
    axs[0].axis('equal')
    axs[0].axis('on') # vorher off
    fig.colorbar(im, ax=axs[0])

    v_abs_max = np.max(np.abs(u))

    im = axs[1].imshow(u, cmap='bwr', vmin=-v_abs_max, vmax=v_abs_max)
    axs[1].axis('equal')
    axs[1].axis('on') # vorher off
    fig.colorbar(im, ax=axs[1])

    plt.show()


#def plot_simple_set(simple_set, eta=None, display_inner_mesh=False, boundary_color='black'):
    #fig, ax = plt.subplots(figsize=(7, 7))

    #if eta is not None:
        #x = np.arange(-1.0, 1.0, 0.01)
        #y = np.arange(-1.0, 1.0, 0.01)
        
        #x = np.arange(0, 1.0, 0.01)
        #y = np.arange(0, 1.0, 0.01)
        
        #x_grid, y_grid = np.meshgrid(x, y)
        #z_grid = np.zeros_like(x_grid)

        #for i in range(x_grid.shape[0]):
        #    for j in range(x_grid.shape[1]):
        #        z_grid[i, j] = eta(np.array([x_grid[i, j], y_grid[i, j]]))
                #z_grid[i, j] = eta(np.array([y_grid[i, j], x_grid[i, j]]))
      #  v_abs_max = np.max(np.abs(z_grid))

      #  im = ax.contourf(y_grid, 1-x_grid, z_grid, levels=30, cmap='bwr', vmin=-v_abs_max, vmax=v_abs_max)

        # original:
        #im = ax.contourf(x_grid, y_grid, z_grid, levels=30, cmap='bwr', vmin=-v_abs_max, vmax=v_abs_max)
      #  fig.colorbar(im, ax=ax)

        #test
        #print("x_grid range:", np.min(x_grid), np.max(x_grid))
        #print("y_grid range:", np.min(y_grid), np.max(y_grid))
        #print("z_grid range:", np.min(z_grid), np.max(z_grid))

    # original:
    #x_curve = np.append(simple_set.boundary_vertices[:, 0], simple_set.boundary_vertices[0, 0])
    #y_curve = np.append(simple_set.boundary_vertices[:, 1], simple_set.boundary_vertices[0, 1])

   # x_curve = np.append(simple_set.boundary_vertices[:, 1], simple_set.boundary_vertices[0, 1])
   # y_curve = np.append(1-simple_set.boundary_vertices[:, 0], 1-simple_set.boundary_vertices[0, 0])


    
   # ax.plot(x_curve, y_curve, color=boundary_color)

   # if display_inner_mesh:
  #      triangulation = Triangulation(simple_set.mesh_vertices[:, 0],
   #                                   simple_set.mesh_vertices[:, 1],
   #                                   simple_set.mesh_faces)

    #    ax.triplot(triangulation, color='black', alpha=0.3)

   # ax.axis('equal')
   # ax.axis('on') #vorher off
    #ax.set_xlim(-1, 1)
    #ax.set_ylim(-1, 1)

    #ax.set_xlim(0, 1)
   # ax.set_ylim(0, 1)
    
   # plt.show()

#def plot_rectangular_set(rectangular_set, eta=None, display_inner_mesh=False, boundary_color='black'):
   # fig, ax = plt.subplots(figsize=(7, 7))

   # if eta is not None:
    #    #x = np.arange(-1.0, 1.0, 0.01)
        #y = np.arange(-1.0, 1.0, 0.01)
        
    #    x = np.arange(0, 1.0, 0.01)
    #    y = np.arange(0, 1.0, 0.01)
        
    #    x_grid, y_grid = np.meshgrid(x, y)
    #    z_grid = np.zeros_like(x_grid)

    #    for i in range(x_grid.shape[0]):
    #        for j in range(x_grid.shape[1]):
     #           z_grid[i, j] = eta(eta.grid_size * np.array([x_grid[i, j], y_grid[i, j]]))
                #z_grid[i, j] = eta(np.array([y_grid[i, j], x_grid[i, j]]))
    #    v_abs_max = np.max(np.abs(z_grid))
     #   print("Min z_grid:", np.min(z_grid), "Max z_grid:", np.max(z_grid))

     #   im = ax.contourf(y_grid, 1-x_grid, z_grid, levels=30, cmap='bwr', vmin=-v_abs_max, vmax=v_abs_max)

        # original:
        #im = ax.contourf(x_grid, y_grid, z_grid, levels=30, cmap='bwr', vmin=-v_abs_max, vmax=v_abs_max)
      #  fig.colorbar(im, ax=ax)

        #test
        #print("x_grid range:", np.min(x_grid), np.max(x_grid))
        #print("y_grid range:", np.min(y_grid), np.max(y_grid))
        #print("z_grid range:", np.min(z_grid), np.max(z_grid))

    # original:
    #x_curve = np.append(simple_set.boundary_vertices[:, 0], simple_set.boundary_vertices[0, 0])
    #y_curve = np.append(simple_set.boundary_vertices[:, 1], simple_set.boundary_vertices[0, 1])

   # x_curve = np.append(rectangular_set.boundary_vertices[:, 1], rectangular_set.boundary_vertices[0, 1])
 #   y_curve = np.append(1-rectangular_set.boundary_vertices[:, 0], 1-rectangular_set.boundary_vertices[0, 0])


    
  #  ax.plot(x_curve, y_curve, color=boundary_color)

  # if display_inner_mesh:
  #      triangulation = Triangulation(rectangular_set.mesh_vertices[:, 0],
  #                                    rectangular_set.mesh_vertices[:, 1],
  #                                    rectangular_set.mesh_faces)

   #     ax.triplot(triangulation, color='black', alpha=0.3)

   # ax.axis('equal')
   # ax.axis('on') #vorher off
    #ax.set_xlim(-1, 1)
    #ax.set_ylim(-1, 1)

   # ax.set_xlim(0, 1)
   # ax.set_ylim(0, 1)
    
   # plt.show()


#def plot_simple_functions(u1, u2, display_inner_mesh=False, boundary_color='black', save_path=None):
  #  fig, ax = plt.subplots(figsize=(7, 7))

 #   for i in range(2):
  #      if i == 0:
  #          u = u1
 #           color = 'black'
 #       else:
 #           u = u2
 #           color = 'red'
  #          boundary_color = 'red'

 #       for atom in u.atoms:
  #          simple_set = atom.support

  #          x_curve = np.append(simple_set.boundary_vertices[:, 0], simple_set.boundary_vertices[0, 0])
  #          y_curve = np.append(simple_set.boundary_vertices[:, 1], simple_set.boundary_vertices[0, 1])

   #         ax.plot(x_curve, y_curve, color=boundary_color)

   #         if display_inner_mesh:
    #            triangulation = Triangulation(simple_set.mesh_vertices[:, 0],
     #                                         simple_set.mesh_vertices[:, 1],
    #                                          simple_set.mesh_faces)

    #            ax.triplot(triangulation, color=color, alpha=0.3)

   # ax.axis('equal')
   # ax.axis('off')
    
   # ax.set_xlim(0, 1)
   # ax.set_ylim(0, 1)
    
    #ax.set_xlim(-1, 1)
    #ax.set_ylim(-1, 1)

  # if save_path is not None:
  #      plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0)

   # plt.show()


#def plot_gradient(boundary_vertices, gradient):
   # fig, ax = plt.subplots(figsize=(7, 7))

   # x_curve = np.append(boundary_vertices[:, 0], boundary_vertices[0, 0])
   # y_curve = np.append(boundary_vertices[:, 1], boundary_vertices[0, 1])
   # u = np.append(gradient[:, 0], gradient[0, 0])
   # v = np.append(gradient[:, 1], gradient[0, 1])

  #  ax.plot(x_curve, y_curve, color='black')

  #  ax.quiver(x_curve[::2], y_curve[::2], u[::2], v[::2], color='red')

  #  ax.axis('equal')
   # ax.axis('off')
   # ax.set_xlim(-1, 1)
   # ax.set_ylim(-1, 1)
   # plt.show()
