import numpy as np
import cvxpy as cp
import time

import copy
from scipy.optimize import minimize, approx_fprime
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
import time
import cProfile
import pstats
import io

#from .simple_set import SimpleSet
#from .optimizer_debugging import CheegerOptimizer
#from .tools import run_primal_dual, extract_contour, resample
#from .plot_utils import plot_primal_dual_results, plot_simple_set, plot_rectangular_set
#from .rectangular_optimizer import objective
from .rectangular_set import RectangularSet, construct_rectangular_set_from01, evaluate_inverse_fourier
from Setup.ground_truth import GroundTruth, construction_of_example_source
from .tools import run_primal_dual, extract_contour
from .plot_utils import plot_primal_dual_results
from .optimizer_debugging import run_fine_optimization

from SlidingFrankWolfe.simple_function import IndicatorFunction, SimpleFunction #, objective_wrapper_sliding, gradient_wrapper_sliding



def calculate_target_function(grid_size, deltas, max_jumps, cut_off, seed= None, noise_level = 4, plot = True):
	
	
	ground_truth = construction_of_example_source(grid_size, deltas, max_jumps, seed = seed)

	operator_applied_on_ground_truth = np.fft.fft2(ground_truth)

	freqs_x= np.fft.fftfreq(grid_size, d=1 / grid_size)
	freqs_y = np.fft.fftfreq(grid_size, d=1 / grid_size)
	freq_x, freq_y = np.meshgrid(freqs_x, freqs_y, indexing="ij")
	

	
	mask = np.zeros((grid_size, grid_size))
	mask[(np.abs(freq_x) <= cut_off) & (np.abs(freq_y) <= cut_off)] = 1

	truncated_operator_applied_on_ground_truth = operator_applied_on_ground_truth * mask

	rng = np.random.default_rng(seed)
	noise = noise_level * (rng.standard_normal((grid_size, grid_size)) + 1j * rng.standard_normal((grid_size, grid_size)))

	target_function_f = truncated_operator_applied_on_ground_truth + noise

	if plot == True:
		

		plt.plot()
		plt.imshow(ground_truth, cmap = 'bwr')
		plt.colorbar()
		plt.title("Ground Truth")
		plt.show()

		plt.plot()
		plt.imshow(truncated_operator_applied_on_ground_truth.real, cmap= 'bwr')
		plt.colorbar()
		plt.title("Truncated Fourier Frequency Image")
		plt.show()

		
		plt.plot()
		plt.imshow(np.fft.ifft2(truncated_operator_applied_on_ground_truth).real, cmap = 'bwr')
		plt.colorbar()
		plt.title("Truncated Fouried Applied on Ground Truth")
		plt.show()


	return truncated_operator_applied_on_ground_truth, ground_truth, target_function_f


def compute_cheeger_set(truncated_operator_applied_on_ground_truth, grid_size, grid_size_coarse, cut_off, max_iter_primal_dual = 10000, plot=True):
   
	h = grid_size / grid_size_coarse
	eta_bar = np.zeros((grid_size_coarse, grid_size_coarse))
	for i in range(grid_size_coarse):
		for j in range(grid_size_coarse):
			x_min = 0 + i * h
			x_max = (i+1) * h
			y_min = j * h
			y_max = (j+1) * h
			rectangle_coarse_grid = RectangularSet(x_min, x_max, y_min, y_max)

			eta_bar[i,j] = (rectangle_coarse_grid.compute_integral(cut_off, truncated_operator_applied_on_ground_truth, grid_size) / h**2).real


	u = run_primal_dual(grid_size_coarse, eta_bar, max_iter=max_iter_primal_dual, convergence_tol=None, plot=True)

	if plot == True:
		plot_primal_dual_results(u[1:-1, 1:-1], eta_bar)

	boundary_vertices = extract_contour(u)
	

	
	initial_rectangular_set = construct_rectangular_set_from01(boundary_vertices, grid_size)
	initial_coordinates = initial_rectangular_set.coordinates
	if plot == True:
		print("Rectangle created by outer boundary vertices of Primal-Dual result:")
		initial_rectangular_set.plot_rectangular_set(np.fft.ifft2(truncated_operator_applied_on_ground_truth).real, grid_size)

	x_min, x_max, y_min, y_max = initial_rectangular_set.coordinates[0], initial_rectangular_set.coordinates[1], initial_rectangular_set.coordinates[2], initial_rectangular_set.coordinates[3]

	
	weights = truncated_operator_applied_on_ground_truth
	
	optimal_rectangle,  objective_tab, gradient_tab , x_mins, x_maxs, y_mins, y_maxs =  run_fine_optimization(initial_rectangular_set, cut_off, weights, grid_size )

	if objective_tab[-1] < 0:
		return initial_rectangular_set

	if plot == True:
		print("Optimal Rectangle initialized by outer boundary vertices of Primal-Dual result:")
		optimal_rectangle.plot_rectangular_set(np.fft.ifft2(truncated_operator_applied_on_ground_truth).real, grid_size)
		print(f"initiale Koordinaten: {initial_coordinates}")
		print(f"optimale Koordinaten: {optimal_rectangle.coordinates}")
		print(f"Verschiebung: {optimal_rectangle.coordinates - initial_coordinates}")

		#fig, ax = plt.subplots()
		#ax.set_xlim(0, grid_size)
		#ax.set_ylim(0, grid_size)
		#rect = patches.Rectangle((0, 0), 1, 1, edgecolor='r', facecolor='none', linewidth=2)
	   # ax.add_patch(rect)

		def update(frame):
			rect.set_xy((y_mins[frame], grid_size - x_maxs[frame]))
			rect.set_height(x_maxs[frame] - x_mins[frame])
			rect.set_width(y_maxs[frame] - y_mins[frame])

		fig, ax = plt.subplots(figsize=(7, 7))
		x = np.linspace(0, grid_size, grid_size)
		y = np.linspace(0, grid_size, grid_size)
		x_grid, y_grid = np.meshgrid(x, y)
		z_grid = np.flipud(np.fft.ifft2(truncated_operator_applied_on_ground_truth).real)  # Hintergrundfunktion

		v_abs_max = np.max(np.abs(z_grid))
		im = ax.contourf(x_grid, y_grid, z_grid, levels=30, cmap='bwr', vmin=-v_abs_max, vmax=v_abs_max)
		plt.colorbar(im, ax=ax)

		ax.set_xlim(0, grid_size)
		ax.set_ylim(0, grid_size)

		rect = plt.Rectangle((y_mins[0], grid_size - x_maxs[0]), 
						 y_maxs[0] - y_mins[0], 
						 x_maxs[0] - x_mins[0], 
						 edgecolor='black', facecolor='none', linewidth=2)
		ax.add_patch(rect)

		ani = animation.FuncAnimation(fig, update, frames=len(x_mins), interval=200)

		ani.save("animation.gif", writer="pillow")
		plt.close(fig)  
		#plt.show()


	   # ani = animation.FuncAnimation(fig, update, frames=len(x_mins), interval=200)
		#ani.save("animation.gif", writer="pillow")
		#plt.title("development of boundary Vertices")
		#plt.show()


		plt.figure()
		plt.plot(objective_tab)
		plt.title("Objective")
		plt.show()

		plt.figure()
		plt.plot(gradient_tab)
		plt.title("Gradient")
		plt.show()

	return optimal_rectangle


def fourier_image_rectangle(rectangular_set, grid_size, cut_off):
	new_indicator_function = IndicatorFunction(rectangular_set, grid_size)
	#image = new_indicator_function.construct_image_matrix(plot=True)

	#plt.plot()
	#plt.imshow(new_indicator_function.construct_image_matrix(plot=False), cmap = 'bwr')
	#plt.colorbar()
	#plt.title("Indikatorfunktion")
	#plt.show()

	fourier_image = new_indicator_function.compute_truncated_frequency_image(cut_off, plot = False)

	return fourier_image

#def fit_weights(u, grid_size, cut_off, reg_param, target_function_f  ):
	 #k(\1_E)
	K_0 = np.zeros((u.num_atoms, grid_size, grid_size), dtype = complex)
	perimeters = np.zeros(u.num_atoms)
	for i in range(u.num_atoms):
		print(f"Gewicht und Koordinaten des Atoms {i}: {u.atoms[i].weight,u.atoms[i].support.coordinates}")
		K_0[i] = fourier_image_rectangle(u.atoms[i].support, grid_size, cut_off)
		perimeters[i] = u.atoms[i].support.compute_anisotropic_perimeter()

	alpha = reg_param 

	print("Perimeter:", perimeters)

	if u.num_atoms == 0:
		print("Fehler: Es wurden keine Atome gefunden!")
		return

	print(f"Anzahl der Atome: {u.num_atoms}")
	print(f"K_0.shape: {K_0.shape}, erwartet: ({u.num_atoms}, {grid_size}, {grid_size})")
	print(f"perimeters.shape: {perimeters.shape}, erwartet: ({u.num_atoms},)")
	print(f"target_function_f.shape: {target_function_f.shape}, erwartet: ({grid_size}, {grid_size})")

	a = cp.Variable(u.num_atoms)

	K0_sum = cp.sum(cp.multiply(a[:, None, None], K_0), axis=0)

	objective = (1/2) * cp.norm(K0_sum - target_function_f, "fro")**2 + alpha * cp.sum(cp.multiply(perimeters, cp.abs(a)))
	
	problem = cp.Problem(cp.Minimize(objective))

	print(f"Ist das Problem DCP-konform? {problem.is_dcp()} (Sollte True sein)")

	try:
		result = problem.solve(solver=cp.SCS, verbose=True)
		a_opt = a.value
		print("Optimale a Werte:", a_opt)
	except Exception as e:
		print("Fehler beim Lösen des Optimierungsproblems:", e)


	for i in range(u.num_atoms):
		u.atoms[i].weight = a_opt[i]
	
	for i in range(u.num_atoms):
		print(f"Gewicht und Koordinaten des Atoms {i} nach fit weights: {u.atoms[i].weight,u.atoms[i].support.coordinates}")
	print("Aktuelles Objective:", u.compute_objective_sliding(target_function_f, reg_param))
	u.remove_small_atoms(threshold = 1e-2)

def fit_weights(u, target_function_f, reg_param):
	def objective_scipy(a_vec):
		# Update Gewichte temporär
		for i in range(u.num_atoms):
			u.atoms[i].weight = a_vec[i]
		return u.compute_objective_sliding(target_function_f, reg_param)

	a_init = np.array([atom.weight for atom in u.atoms])
	bounds =[(-1, 1)] * u.num_atoms
	res = minimize(objective_scipy, a_init, bounds = bounds, method='L-BFGS-B')

	if res.success:
		for i in range(u.num_atoms):
			u.atoms[i].weight = res.x[i]

	print("Aktuelles Objective:", u.compute_objective_sliding(target_function_f, reg_param))
	u.remove_small_atoms(threshold = 1e-3)



def sliding_step(u,  target_function_f, reg_param):
	a = np.zeros(u.num_atoms)
	x_mins = np.zeros(u.num_atoms)
	x_maxs = np.zeros(u.num_atoms)
	y_mins = np.zeros(u.num_atoms)
	y_maxs = np.zeros(u.num_atoms)

	for i in range(u.num_atoms):
		a[i] = u.atoms[i].weight
		x_mins[i] = u.atoms[i].support.coordinates[0]
		x_maxs[i] = u.atoms[i].support.coordinates[1]
		y_mins[i] = u.atoms[i].support.coordinates[2]
		y_maxs[i] = u.atoms[i].support.coordinates[3]

	initial_parameters = np.concatenate((a, x_mins, x_maxs, y_mins, y_maxs))
	bounds =[(-1, 1)] * u.num_atoms + [(0, u.grid_size)] * u.num_atoms + [(0, u.grid_size)] * u.num_atoms + [(0, u.grid_size)] * u.num_atoms + [(0, u.grid_size)] * u.num_atoms

	objective_development = []
	gradient_development = []
	x_min_values = []
	x_max_values = []
	y_min_values = []
	y_max_values = []
	#u.compute_error_term(target_function_f)

	#correct_reconstruction = u.compute_truncated_frequency_image_sf(plot = False)

	#plt.plot()
	#plt.imshow(np.fft.ifft2(correct_reconstruction).real, cmap = 'bwr')
	#plt.title("Correct Reconstruction")
	#plt.colorbar()
	#plt.show()

	#print("berechnet")

	def callback(params):
		objective_value = u.objective_wrapper_sliding(params, target_function_f, reg_param)
		gradient_value = u.gradient_wrapper_sliding(params, target_function_f, reg_param)

		#print("gradient shape:", gradient_value.shape)
		#print("Params shape:", params.shape)
		x_min_value = u.atoms[0].support.x_min
		x_max_value = u.atoms[0].support.x_max
		y_min_value = u.atoms[0].support.y_min
		y_max_value = u.atoms[0].support.y_max

		gradient_norm = np.linalg.norm(gradient_value)
	
		objective_development.append(objective_value)
		gradient_development.append(gradient_norm)
		x_min_values.append(x_min_value)
		x_max_values.append(x_max_value)
		y_min_values.append(y_min_value)
		y_max_values.append(y_max_value)
		

	from scipy.optimize import check_grad
	

	err = check_grad(u.objective_wrapper_sliding, u.gradient_wrapper_sliding, initial_parameters, target_function_f, reg_param)
	print("Gradient check error:", err)	
	grad_num = approx_fprime(initial_parameters, u.objective_wrapper_sliding, 1e-8, target_function_f, reg_param)
	grad_ana = u.gradient_wrapper_sliding(initial_parameters, target_function_f, reg_param)
	print("Numerischer Gradient:", grad_num)
	print("Analytischer Gradient:", grad_ana)
	print("Diff:", np.linalg.norm(grad_num - grad_ana))
	print("Starting objective value:", u.compute_objective_sliding(target_function_f, reg_param))

	start_time = time.time()

	result = minimize( fun = u.objective_wrapper_sliding, x0 = initial_parameters, args =(target_function_f, reg_param),jac = u.gradient_wrapper_sliding, bounds =bounds, method='L-BFGS-B', options={'gtol': 1e-3,'maxiter': 100, 'disp': True }, callback = callback)
#method='L-BFGS-B'
#jac = gradient_wrapper_sliding
	end_time = time.time()

	print(f'Ursprüngliche Laufzeit: {end_time -start_time :.6f} Sekunden')

	print("Result status:", result.message)
	print("Number of iterations (nit):", result.nit)
	print("Number of function evaluations (nfev):", result.nfev)
	print("Number of gradient evaluations (njev):", result.njev)
	
	print("Final objective value:", result.fun)


	if not result.success:
		print("Optimization did not converge:", result.message)

	new_parameters = result.x

	new_weights = new_parameters[:u.num_atoms]
	new_x_mins = new_parameters[u.num_atoms:2*u.num_atoms]
	new_x_maxs = new_parameters[2*u.num_atoms:3*u.num_atoms]
	new_y_mins = new_parameters[3*u.num_atoms:4*u.num_atoms]
	new_y_maxs = new_parameters[4*u.num_atoms:5*u.num_atoms]

	for i in range(u.num_atoms):
		u.atoms[i].weight = new_weights[i]
		u.atoms[i].support.coordinates = (new_x_mins[i], new_x_maxs[i], new_y_mins[i], new_y_maxs[i])

	u.remove_small_atoms(threshold = 1e-3)
	return u, objective_development, gradient_development, x_min_values, x_max_values, y_min_values, y_max_values







def optimization ( ground_truth, target_function_f, grid_size, grid_size_coarse, cut_off, reg_param, max_iter_primal_dual = 10000, plot=True):
	
	atoms = []
	u = SimpleFunction(atoms, grid_size, cut_off)

	iteration = 0
	max_iter = 30

	while iteration < max_iter:   
	


		weights_in_eta = - u.compute_truncated_frequency_image_sf(cut_off, plot = True) + target_function_f

		optimal_rectangle = compute_cheeger_set(weights_in_eta, grid_size, grid_size_coarse, cut_off, max_iter_primal_dual = 10000, plot=True)

		
		#if np.abs(optimal_rectangle.compute_integral (cut_off, 1/reg_param * weights_in_eta, grid_size)) <= optimal_rectangle.compute_anisotropic_perimeter():
		 #   print("Optimierung erfolgreich")
		#    return u
			
		
		
		
		u.extend_support(optimal_rectangle)

		fit_weights(u, grid_size, cut_off, reg_param, target_function_f)

	

		#fourier_image = u.compute_truncated_frequency_image_sf(cut_off, plot = False)


		if plot == True:

			fig, ax = plt.subplots(1, 3, figsize=(18, 6))  

			# Linker Plot mit Funktionsaufruf
			data = u.construct_image_matrix_sf(plot=False) 
			vmin = min(np.min(data), np.min(ground_truth))
			vmax = max(np.max(data), np.max(ground_truth))

			im1 = ax[0].imshow(data, cmap="bwr", vmin=vmin,
							   vmax=vmax)  
			fig.colorbar(im1, ax=ax[0])
			ax[0].set_title("Current Function")

			im2 = ax[1].imshow(ground_truth, cmap = 'bwr', vmin=vmin, vmax=vmax)

			fig.colorbar(im2, ax = ax[1])
			ax[1].set_title("Ground Truth")

			diff = - data + ground_truth
			vmax_diff = np.max(np.abs(diff))
			im3 = ax[2].imshow(diff, cmap = 'bwr', vmin=-vmax_diff, vmax=vmax_diff)
			fig.colorbar(im3, ax = ax[2])
			ax[2].set_title("Difference")

			plt.tight_layout()

			plt.show()

		iteration += 1



def standard_optimization( ground_truth, target_function_f, grid_size, grid_size_coarse, cut_off, reg_param, max_iter_primal_dual = 10000, plot=True):
	
	atoms = []
	u = SimpleFunction(atoms, grid_size, cut_off)

	objective_whole_iteration = []
	
	iteration = 0
	max_iter = 30

	convergence = False

	objective_whole_iteration.append(u.compute_objective_sliding( target_function_f, reg_param))
	

	while not convergence and iteration < max_iter:   

		weights_in_eta = - u.compute_truncated_frequency_image_sf( plot = True) + target_function_f

		optimal_rectangle = compute_cheeger_set(weights_in_eta, grid_size, grid_size_coarse, cut_off, max_iter_primal_dual = 10000, plot=True)

		
		u.extend_support(optimal_rectangle)

		
		
		fit_weights(u,  target_function_f, reg_param)

		weights = []
		for atom in u.atoms:
			weights.append(atom.weight)
		print("Gewichte der atome:", weights)

		

		objective_whole_iteration.append(u.compute_objective_sliding( target_function_f, reg_param))


		if plot == True:

			fig, ax = plt.subplots(1, 3, figsize=(18, 6))  # 1 Zeile, 2 Spalten

			# Linker Plot mit Funktionsaufruf
			data = u.construct_image_matrix_sf(plot=False) 
			vmin = min(np.min(data), np.min(ground_truth))
			vmax = max(np.max(data), np.max(ground_truth))

			im1 = ax[0].imshow(data, cmap="bwr", vmin=vmin,
							   vmax=vmax)  
			fig.colorbar(im1, ax=ax[0])
			ax[0].set_title("Current Function")

			im2 = ax[1].imshow(ground_truth, cmap = 'bwr', vmin=vmin, vmax=vmax)

			fig.colorbar(im2, ax = ax[1])
			ax[1].set_title("Ground Truth")

			diff = - data + ground_truth
			vmax_diff = np.max(np.abs(diff))
			im3 = ax[2].imshow(diff, cmap = 'bwr', vmin=-vmax_diff, vmax=vmax_diff)
			fig.colorbar(im3, ax = ax[2])
			ax[2].set_title("Difference")

			plt.tight_layout()

			plt.show()


		plt.figure()
		plt.plot(objective_whole_iteration)
		plt.title("Objective development each iteration")
		plt.show()

		convergence = ((objective_whole_iteration[-2] - objective_whole_iteration[-1] ) < 10 )

		iteration += 1









def optimization_with_sliding ( ground_truth, target_function_f, grid_size, grid_size_coarse, cut_off, reg_param, max_iter_primal_dual = 10000, plot=True):
	
	atoms = []
	u = SimpleFunction(atoms, grid_size, cut_off)

	objective_whole_iteration = []
	objective_overall_development = []
	iteration = 0
	max_iter = 12

	convergence = False

	objective_whole_iteration.append(u.compute_objective_sliding( target_function_f, reg_param))
	objective_overall_development.append(u.compute_objective_sliding( target_function_f, reg_param))

	while not convergence and iteration < max_iter:   

		weights_in_eta = - u.compute_truncated_frequency_image_sf( plot = True) + target_function_f

		optimal_rectangle = compute_cheeger_set(weights_in_eta, grid_size, grid_size_coarse, cut_off, max_iter_primal_dual = 10000, plot=True)

		
		#if np.abs(optimal_rectangle.compute_integral (cut_off, 1/reg_param * weights_in_eta, grid_size)) <= optimal_rectangle.compute_anisotropic_perimeter():
		 #   print("Optimierung erfolgreich")
		#    return u
			
		
		
		
		u.extend_support(optimal_rectangle)
		
		#for atom in u.atoms:
		#	integral = atom.weight * (atom.area * atom.inner_value + (grid_size **2 - atom.area)* atom.outer_value)
		#	print("Integral nach extend support der einzelnen atome:", integral )
		
		#for atom in u.atoms:
		#	print("weight des atoms:", atom.weight)
		#	print("xmin",atom.support.x_min)
		#	print("xmax",atom.support.x_max)
		#	print("ymin",atom.support.y_min)
		#	print("ymax",atom.support.y_max)
		#	print("Area Des Atoms", atom.area)
		#	print("Mean value", atom.mean_value)
		#	print("inner value:", atom.weight * (1 - atom.mean_value))
		#	print("outer value:", atom.weight * (0 - atom.mean_value))


		#fit_weights(u, grid_size, cut_off, reg_param, target_function_f)
		fit_weights(u,  target_function_f, reg_param)

		objective_overall_development.append(u.compute_objective_sliding( target_function_f, reg_param))

		integral = 0
		for atom in u.atoms:
			integral += (atom.area * (atom.weight * (1- atom.mean_value)) +(grid_size**2 - atom.area)*(atom.weight * (0- atom.mean_value)) )

		print("Integral nach fix weights:", integral)

		#fourier_image = u.compute_truncated_frequency_image_sf(cut_off, plot = False)


		if plot == True:

			fig, ax = plt.subplots(1, 3, figsize=(18, 6))  # 1 Zeile, 2 Spalten

			# Linker Plot mit Funktionsaufruf
			data = u.construct_image_matrix_sf(plot=False) 
			vmin = min(np.min(data), np.min(ground_truth))
			vmax = max(np.max(data), np.max(ground_truth))

			im1 = ax[0].imshow(data, cmap="bwr", vmin=vmin,
							   vmax=vmax)  
			fig.colorbar(im1, ax=ax[0])
			ax[0].set_title("Current Function")

			im2 = ax[1].imshow(ground_truth, cmap = 'bwr', vmin=vmin, vmax=vmax)

			fig.colorbar(im2, ax = ax[1])
			ax[1].set_title("Ground Truth")

			diff = - data + ground_truth
			vmax_diff = np.max(np.abs(diff))
			im3 = ax[2].imshow(diff, cmap = 'bwr', vmin=-vmax_diff, vmax=vmax_diff)
			fig.colorbar(im3, ax = ax[2])
			ax[2].set_title("Difference")

			plt.tight_layout()

			plt.show()

		integral = 0
		for atom in u.atoms:
			
			res = (atom.area * (atom.weight * (1- atom.mean_value)) +(grid_size**2 - atom.area)*(atom.weight * (0- atom.mean_value)) )
			print("Integral eines Atoms:", res)
			integral+= res

		print("Gesamtintegral:", integral)
		
		v = copy.deepcopy(u)

		pr = cProfile.Profile()
		pr.enable()

		u, objective_development, gradient_development, x_min_values, x_max_values, y_min_values, y_max_values = sliding_step(u, target_function_f, reg_param)

		pr.disable()

		# Ergebnisse sortiert nach Laufzeit
		s = io.StringIO()
		ps = pstats.Stats(pr, stream=s).sort_stats('cumtime')  # Alternativ 'tottime'
		ps.print_stats(30)  # Zeige die Top 30 Zeitfresser
		print(s.getvalue())

		for i in range((u.num_atoms)):
			
			print("koordinaten von u", u.atoms[i].support.coordinates)


		if plot == True:

			print("development objective", objective_development)
			print("development gradient", gradient_development)
			print("development x_min", x_min_values)
			print("development x_max", x_max_values)
			print("development y_min", y_min_values)
			print("development y_max", y_max_values)

			plt.figure()
			plt.plot(objective_development)
			plt.title("Objective")
			plt.show()

			plt.figure()
			plt.plot(gradient_development)
			plt.title("Gradient")
			plt.show()

			

			fig, ax = plt.subplots(1, 3, figsize=(18, 6))  # 1 Zeile, 2 Spalten

			# Linker Plot mit Funktionsaufruf
			data = u.construct_image_matrix_sf(plot=False) 
			vmin = min(np.min(data), np.min(ground_truth))
			vmax = max(np.max(data), np.max(ground_truth))

			im1 = ax[0].imshow(data, cmap="bwr", vmin=vmin,
							   vmax=vmax)  
			fig.colorbar(im1, ax=ax[0])
			ax[0].set_title("Current Function")

			im2 = ax[1].imshow(ground_truth, cmap = 'bwr', vmin=vmin, vmax=vmax)

			fig.colorbar(im2, ax = ax[1])
			ax[1].set_title("Ground Truth")

			diff = - data + ground_truth
			vmax_diff = np.max(np.abs(diff))
			im3 = ax[2].imshow(diff, cmap = 'bwr', vmin=-vmax_diff, vmax=vmax_diff)
			fig.colorbar(im3, ax = ax[2])
			ax[2].set_title("Difference")

			plt.tight_layout()


			plt.show()


			integral = 0
			for atom in u.atoms:
				integral += (atom.area * (atom.weight * (1- atom.mean_value)) +(grid_size**2 - atom.area)*(atom.weight * (0- atom.mean_value)) )
			

			print("Integral der current function:", integral)

			plt.plot()
			data = v.construct_image_matrix_sf(plot=False)  - u.construct_image_matrix_sf(plot=False) 
			plt.imshow(data, cmap = 'bwr')
			plt.colorbar()
			plt.title("Differenz zwischen Funktionen")
			plt.show()

		objective_overall_development.append(u.compute_objective_sliding( target_function_f, reg_param))
		
		#fit_weights(u, grid_size, cut_off, reg_param, target_function_f)
		fit_weights(u, target_function_f, reg_param)

		objective_whole_iteration.append(u.compute_objective_sliding( target_function_f, reg_param))
		objective_overall_development.append(u.compute_objective_sliding( target_function_f, reg_param))

		plt.figure()
		plt.plot(objective_overall_development)
		plt.title("Objective overall development")
		plt.show()


		plt.figure()
		plt.plot(objective_whole_iteration)
		plt.title("Objective development each iteration")
		plt.show()

		convergence = ((objective_whole_iteration[-2] - objective_whole_iteration[-1] ) < 10 )

		iteration += 1