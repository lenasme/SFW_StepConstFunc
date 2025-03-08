import numpy as np
import matplotlib.pyplot as plt


class RectangularSet:

	def __init__(self, x_min, x_max, y_min, y_max):
		
		self.x_min = x_min
		self.x_max = x_max
		self.y_min = y_min
		self.y_max = y_max

		self.coordinates = np.array([x_min, x_max, y_min, y_max])


	
	@property
	def coordinates(self):
		return  np.array([self.x_min, self.x_max, self.y_min, self.y_max])

	@coordinates.setter
	def coordinates(self, new_coordinates):
		self.x_min = new_coordinates[0]
		self.x_max = new_coordinates[1]
		self.y_min = new_coordinates[2]
		self.y_max = new_coordinates[3]

	
	def plot_rectangle(self):
		plt.figure(figsize=(8, 8))
	
		plt.plot(np.array([self.x_min, self.x_max, self.x_max, self.x_min, self.x_min]), np.array([self.y_min, self.y_min, self.y_max, self.y_max, self.y_min]))
		
		plt.xlabel("X")
		plt.ylabel("Y")
		plt.title("Rectangle")
		plt.axis("equal") 
		plt.show()


	
	""" Berechnung von Bausteinen für min \ frac{Per(E)}{abs(\int_E \eta)}"""

	
	
	def compute_anisotropic_perimeter(self):
		"""
		Per(E)
		
		"""
		return 2 * ((self.x_max - self.x_min) + (self.y_max - self.y_min))
	
	
	def compute_anisotropic_perimeter_gradient(self):
		""" 
		(\ frac{d}{d x_min} Per(E), \ frac{d}{d x_max} Per(E), \ frac{d}{d y_min} Per(E), \ frac{d}{d y_max} Per(E) ) 
		
		"""
		gradient = np.array([-2, 2, -2, 2])
		return gradient



	

	def compute_integral(self, cut_off, weights, grid_size):
		"""
		  \int_{x_min} ^{x_max} \int_{y_min} ^{y_max} \sum_{k,j = -\Phi}^{\Phi} w_{k,j} e^{2 \pi i (k j)*(x y)} dy dx 
		  S.8 in Notizen für Formel

		"""

		weights[0,0] = 0 #sichert Nullintegral

		res = 0
		for k in range (- cut_off, cut_off +1 ):
			for l in range (- cut_off, cut_off + 1):

				if k == 0 and l == 0:
					res += 0 #Absicherung, dass tatsächlich Nullintegral, da w_00 eh 0 ist, ändert diese abkürzung nichts
				
				elif k == 0: 
					res += weights[(k+grid_size[0]) % grid_size[0], (l+grid_size[1]) % grid_size[1]] / (grid_size[0]*2*np.pi*1j *l)* (self.x_max * (np.exp(2*np.pi*1j*((l*self.y_max)/grid_size[1])) -  np.exp(2*np.pi*1j*((l*self.y_min)/grid_size[1])) )
																													   + self.x_min * (np.exp(2*np.pi*1j*((l*self.y_min)/grid_size[1])) -  np.exp(2*np.pi*1j*((l*self.y_max)/grid_size[1])) ))

				elif l == 0:
					res += weights[(k+grid_size[0]) % grid_size[0], (l+grid_size[1]) % grid_size[1]] / (grid_size[0]*2*np.pi*1j *k)* (self.y_max * (np.exp(2*np.pi*1j*((k*self.x_max)/grid_size[0])) -  np.exp(2*np.pi*1j*((k*self.x_min)/grid_size[0])) )
																													   + self.y_min * (np.exp(2*np.pi*1j*((k*self.x_min)/grid_size[0])) -  np.exp(2*np.pi*1j*((k*self.x_max)/grid_size[0])) ))

				else:
					res += weights[(k+grid_size[0]) % grid_size[0], (l+grid_size[1]) % grid_size[1]] / (-(2*np.pi)**2 * k * l) *(np.exp(2*np.pi*1j * (k *self.x_max / grid_size[0] + l* self.y_max / grid_size[1])) - np.exp( 2 * np.pi *1j * (k* self.x_max/grid_size[0] + l* self.y_min/grid_size[1])) 
																												  - np.exp( 2 * np.pi *1j *(k* self.x_min/grid_size[0] + l* self.y_max/grid_size[1])) + np.exp(2 * np.pi *1j*(k* self.x_min/grid_size[0] + l* self.y_min/grid_size[1])))
		return res


	def compute_integral_gradient(self, cut_off, weights, grid_size):
		"""
		Ableitung von compute_integral, Beibehaltung der Fallunterscheidung
		S.11-13 in Notizen für Formel
		Speicherung des Gradienten in der Reihenfolge x_min, x_max, y_min, y_max

		"""
		weights[0,0] = 0
		gradient = np.array([0, 0, 0, 0])

		for k in range (- cut_off, cut_off +1 ):
			for l in range (- cut_off, cut_off + 1):

				if k == 0 and l == 0:
					gradient[0] += 0
					gradient[1] += 0
					gradient[2] += 0
					gradient[3] += 0 #Absicherung, dass tatsächlich Nullintegral, da w_00 eh 0 ist, ändert diese abkürzung nichts

				elif k == 0: 
					gradient[0] += weights[(k+grid_size[0]) % grid_size[0], (l+grid_size[1]) % grid_size[1]] / (grid_size[0] * 2*np.pi*1j*l ) *(np.exp( 2*np.pi* 1j * ( l * self.y_min)/ grid_size[1] )  - np.exp( 2*np.pi* 1j * ( l * self.y_max)/ grid_size[1] ) )

					gradient[1] += weights[(k+grid_size[0]) % grid_size[0], (l+grid_size[1]) % grid_size[1]] / (grid_size[0] * 2*np.pi*1j*l ) *(np.exp( 2*np.pi* 1j * ( l * self.y_max)/ grid_size[1] )  - np.exp( 2*np.pi* 1j * ( l * self.y_min)/ grid_size[1] ) )

					gradient[2] += weights[(k+grid_size[0]) % grid_size[0], (l+grid_size[1]) % grid_size[1]] / (grid_size[0] *grid_size[1] ) *  (- np.exp( 2*np.pi* 1j * ( l * self.y_min)/ grid_size[1] ) * self.x_max + np.exp( 2*np.pi* 1j * ( l * self.y_min)/ grid_size[1] ) * self.x_min )

					gradient[3] += weights[(k+grid_size[0]) % grid_size[0], (l+grid_size[1]) % grid_size[1]] / (grid_size[0] *grid_size[1] ) *  ( np.exp( 2*np.pi* 1j * ( l * self.y_max)/ grid_size[1] ) * self.x_max - np.exp( 2*np.pi* 1j * ( l * self.y_max)/ grid_size[1] ) * self.x_min )

				elif l == 0:
					gradient[0] += weights[(k+grid_size[0]) % grid_size[0], (l+grid_size[1]) % grid_size[1]] / (grid_size[0] *grid_size[1] ) *  (- np.exp( 2*np.pi* 1j * ( k * self.x_min)/ grid_size[0] ) * self.y_max + np.exp( 2*np.pi* 1j * ( k * self.x_min)/ grid_size[0] ) * self.y_min )

					gradient[1] +=  weights[(k+grid_size[0]) % grid_size[0], (l+grid_size[1]) % grid_size[1]] / (grid_size[0] *grid_size[1] ) *  ( np.exp( 2*np.pi* 1j * ( k * self.x_max)/ grid_size[0] ) * self.y_max - np.exp( 2*np.pi* 1j * ( k * self.x_max)/ grid_size[0] ) * self.y_min )

					gradient[2] += weights[(k+grid_size[0]) % grid_size[0], (l+grid_size[1]) % grid_size[1]] / (grid_size[1] * 2*np.pi*1j*k ) *(np.exp( 2*np.pi* 1j * ( k * self.x_min)/ grid_size[0] )  - np.exp( 2*np.pi* 1j * ( k * self.x_max)/ grid_size[0] ) )

					gradient[3] +=  weights[(k+grid_size[0]) % grid_size[0], (l+grid_size[1]) % grid_size[1]] / (grid_size[1] * 2*np.pi*1j*k ) *(np.exp( 2*np.pi* 1j * ( k * self.x_max)/ grid_size[0] )  - np.exp( 2*np.pi* 1j * ( k * self.x_min)/ grid_size[0] ) )
				
				else:
					gradient[0] += weights[(k+grid_size[0]) % grid_size[0], (l+grid_size[1]) % grid_size[1]] * ( (1j) / ( - 2 * np.pi *l * grid_size[0]) ) * ( - np.exp( 2 * np.pi * 1j * ((k * self.x_min) / (grid_size[0]) + (l * self.y_max)/(grid_size[1]))) 
																																			   + np.exp(  2 * np.pi * 1j * ((k * self.x_min) / (grid_size[0]) + (l * self.y_min)/(grid_size[1]))))  

					gradient[1] += weights[(k+grid_size[0]) % grid_size[0], (l+grid_size[1]) % grid_size[1]] * ( (1j) / ( - 2 * np.pi *l * grid_size[0]) ) * (  np.exp( 2 * np.pi * 1j * ((k * self.x_max) / (grid_size[0]) + (l * self.y_max)/(grid_size[1]))) 
																																			   - np.exp(  2 * np.pi * 1j * ((k * self.x_max) / (grid_size[0]) + (l * self.y_min)/(grid_size[1]))))  

					gradient[2] += weights[(k+grid_size[0]) % grid_size[0], (l+grid_size[1]) % grid_size[1]] * ( (1j) / ( - 2 * np.pi * k * grid_size[1]) ) * ( - np.exp( 2 * np.pi * 1j * ((k * self.x_max) / (grid_size[0]) + (l * self.y_min)/(grid_size[1]))) 
																																			   + np.exp(  2 * np.pi * 1j * ((k * self.x_min) / (grid_size[0]) + (l * self.y_min)/(grid_size[1]))))  

					gradient[3] += weights[(k+grid_size[0]) % grid_size[0], (l+grid_size[1]) % grid_size[1]] * ( (1j) / ( - 2 * np.pi * k * grid_size[1]) ) * (  np.exp( 2 * np.pi * 1j * ((k * self.x_max) / (grid_size[0]) + (l * self.y_max)/(grid_size[1]))) 
																																			   - np.exp(  2 * np.pi * 1j * ((k * self.x_min) / (grid_size[0]) + (l * self.y_max)/(grid_size[1]))))  
					
		return gradient



	def compute_objective(self, cut_off, weights, grid_size ):
		res = self.compute_anisotropic_perimeter() /  np.abs(self.compute_integral(cut_off, weights, grid_size) )
		return res
	
	def compute_objective_wrapper(self, x, cut_off, weights, grid_size):
		
		"""brauche ich, um es in scipy.optimize.minimize einbinden kann"""
		
		self.x_min = x[0]
		self.x_max = x[1]
		self.y_min = x[2]
		self.y_max = x[3]
		
		
		return self.compute_objective(cut_off, weights, grid_size)
	
	def compute_objective_gradient(self, cut_off, weights, grid_size ):

		perimeter = self.compute_anisotropic_perimeter()
		perimeter_gradient = self.compute_anisotropic_perimeter_gradient()
		integral = self.compute_integral(cut_off, weights, grid_size)
		integral_gradient = self.compute_integral_gradient(cut_off, weights, grid_size)
		
		gradient = np.sign(integral) * (perimeter_gradient * integral - integral_gradient * perimeter) / integral ** 2

		return  gradient
	
	def objective_gradient_wrapper(self, x, cut_off, weights, grid_size):
		""""
		brauche ich, um es in scipy.optimize.minimize einbinden kann
		"""
		self.x_min = x[0]
		self.x_max = x[1]
		self.y_min = x[2]
		self.y_max = x[3]

		return self.compute_objective_gradient(cut_off, weights, grid_size)

	
def construct_rectangular_set(simple_set):
	x_values = [v[0] for v in simple_set.boundary_vertices]
	y_values = [v[1] for v in simple_set.boundary_vertices]                 

	x_min= np.clip(min(x_values), 0,1)
	x_max= np.clip(max(x_values), 0,1)
	y_min= np.clip(min(y_values), 0,1)
	y_max= np.clip(max(y_values), 0,1)

	rectangular_set = RectangularSet(x_min, x_max, y_min, y_max)

	return rectangular_set