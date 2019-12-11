import MySQLdb as motorDB
import math
import time
import sys
import pygame

import pokesim_replay as pkrply

from random import seed
from random import randint
from tabulate import tabulate
from art import tprint

import datetime


NUM_ATTACKS = 2

# Imprimir un caracter a la vez con delay
def delay_print(s):
    for c in s:
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(0.025)
    print('')

# Pantalla pre-pelea
def figth_screen():
	time.sleep(1.5)
	for n in range(5):
		CLR_SCRN()
		time.sleep(0.5)
		tprint("FIGHT")
		time.sleep(0.5)

# Pantalla de fin de pelea
def battle_end_screen(p1, p2):
	time.sleep(1.5)
	if(p1.curr_hp == 0):
		winner = p2.name+'!'
	else:
		winner = p1.name+'!'

	for n in range(5):
		CLR_SCRN()
		time.sleep(0.5)
		print("THE WINNER OF THE BATTLE IS: ")
		tprint(winner)
		time.sleep(0.5)
	input("\n\n\n\n\nApruebenmé!")

# Función para cargar un archivo CSV
def load_csv(csv_route):
	datos = []
	f = open(csv_route)
	for line in f.readlines():
	    datos.append(line.split(','))

	for n in range(len(datos)):
	    for k in range(len(datos[n])):
	        datos[n][k]=datos[n][k].rstrip().lstrip()
	return datos

# Función para limpiar la pantalla de la consola
def CLR_SCRN(*args):
	print('\033c')
	for n in args:
		print(n)



# Clase Pokemon
class Pokemon():

	def __init__(self, num, name, hp, frc, df, spc, spd):
		self.name = name
		self.num = num
		self.tipo1 = "-"
		self.tipo2 = "-"
		self.lvl = 50

		self.hp_base = hp
		self.str_base = frc
		self.df_base = df
		self.spc_base = spc
		self.spd_base = spd

		self.hp = math.floor(self.hp_base*2*self.lvl/100)+self.lvl + 10
		self.str = math.floor(self.str_base*2*self.lvl/100)+5
		self.df = math.floor(self.df_base*2*self.lvl/100)+5
		self.spc = math.floor(self.spc_base*2*self.lvl/100)+5
		self.spd = math.floor(self.spd_base*2*self.lvl/100)+5

		self.curr_hp = self.hp
		self.hp_bars = '===================='

		self.att = []

		self.status = "ok"
		self.sleep_counter = 0
		self.confusion_counter = 0

	# Método de Pokemon para cargarle los ataques reciviendo un vector con los números de ataque
	def load_attacks(self, vect, cur, secEffect_table):
		at = []
		for i in range(len(vect)):
			cur.execute('''SELECT a.attackID, a.name, a.PWR, a.PP, a.ACC, a.PRIOR, t.name, a.description, dt.name 
							FROM attack a, type t, dmgType dt 
							WHERE dt.dmgTypeID = t.dmgTypeID AND a.typeID = t.typeID AND a.attackID ={};'''.format(vect[i]))
			at = cur.fetchone()
			self.att.append(Attack(at[0], at[1], at[2], at[3], at[4], at[5], at[6], at[7], at[8]))

			for line in secEffect_table:
				if(line[0] == vect[i]):
					self.att[i].load_secEffect(line[2], line[3])

	# Método de Pokemon para cargar su/s tipo/s
	def load_pokemon_type(self, vect):
		self.tipo1 = vect[0][1]
		if (len(vect)==2):
			self.tipo2 = vect[1][1]

	# Método de Pokemon para impormir por consola su información
	def print_pokemon_info(self):

		if(self.att == []):
			print('''#Pokemon: {}\nNombre: {}\nTipo 1: {}\nTipo 2: {}\nHP: {}\nSTR: {}\nDEF: {}\nSPC: {}\nSPD:  {}\n'''.format(self.num, self.name, 
				self.tipo1, self.tipo2, self.hp, self.str, self.df, self.spc, self.spd))
		else:
			print('''#Pokemon: {}\nNombre: {}\nTipo 1: {}\nTipo 2: {}\nHP: {}\nSTR: {}\nDEF: {}\nSPC: {}\nSPD:  {}\nAtaque 1:  {}\nAtaque 2:  {}\n
				'''.format(self.num, self.name, self.tipo1, self.tipo2, self.hp, self.str, self.df, self.spc, self.spd,
					self.att[0].name, self.att[1].name))

	# Método de Pokemon para imprimir sus barras de vida
	def print_health_bars(self):
		delay_print('\n----------{}----------'.format(self.name))
		delay_print('{}'.format(self.hp_bars))
		delay_print('HP:{}/{}'.format(self.curr_hp, self.hp))
		print('')

	# Método de Pokemon para listar sus ataques
	def show_attacks(self):
		for n in range(len(self.att)):
			print('{}) {}'.format(n+1, self.att[n].name))

	# Método de Pokemon para saber si puede atacar debido a algún estado. Devuelve True si el pokemon puede atacar, False eoc.
	def check_status(self, def_pk):
		
		if(self.status == "ok"):
			return True

		elif(self.status == "sleep"):
			delay_print("{} is fast asleep...".format(self.name))
			if(self.sleep_counter == 0):
				self.status = "ok"
				delay_print("{} woke up!".format(self.name))
				return True
			self.sleep_counter -= 1
			return False

		elif(self.status == "paralyzed"):
			if(randint(1,4) == 1): 										# 1/4 de chances de poer atacar
				return True
			else:
				print("{} is fully paralyzed.".format(self.name))
				return False

		elif(self.status == "confused"):
			delay_print("{} is confused...".format(self.name))
			if(self.confusion_counter == 0):
				self.status = "ok"
				print("{} is no more confused!".format(self.name))
				return True
			self.confusion_counter -= 1
			if(randint(1,2) == 1):
				delay_print("It hurts itself in its confusion!")
				self.curr_hp -= math.floor(((((2*self.lvl/5+2)*40*(self.str/self.df))/50)+2)) 		# Se daña como si fuese atacado
				self.curr_hp = 0 if self.curr_hp < 0 else self.curr_hp								# por un ataque de PWR 40 y daño
				self.calculate_health_bars() 														# físico, sin modificadores
				return False
			return True

		elif(self.status == "poisoned"):
			delay_print("{} is poisoned...".format(self.name))
			self.curr_hp -= math.floor(self.hp/16) 						# Pierde 1/16 de su vida total cada turno
			self.curr_hp = 0 if self.curr_hp < 0 else self.curr_hp
			self.calculate_health_bars()
			self.print_health_bars()
			def_pk.print_health_bars()

			return True

		elif(self.status == "burned"):
			delay_print("{} is burned...".format(self.name))
			self.curr_hp -= math.floor(self.hp/16) 						# Pierde 1/16 de su vida total cada turno
			self.curr_hp = 0 if self.curr_hp < 0 else self.curr_hp
			self.calculate_health_bars()
			self.print_health_bars()
			def_pk.print_health_bars()
			return True

		elif(self.status == "frozen"):
			delay_print(self.name, " is frozen solid...")
			if(randint(1,10) == 1):
				delay_print(self.name," is no more frozen!")
				self.status = "ok"
				return True
			else:
				return False

	# Método de Pokemon para realizar un ataque (daño y efectos)
	def do_attack(self, num, def_pk, weaknesses_table, reply_table, _repID):
		#https://bulbapedia.bulbagarden.net/wiki/Damage
		#https://bulbapedia.bulbagarden.net/wiki/Critical_hit#In_Generation_I
		
		att_index = num-1								# Calculo el índice de la lista de ataques: -1 a lo que ingresó el usuario
		repInfo = pkrply.ReplayInfo(_repID, self.num)	# Creo un objeto que contiene toda la info necesaria para la tabla replayInfo
		repInfo.attackID = self.att[att_index].id 		# Cargo el ataque utilizado. Ya posee el replayID y el pokemon con el contructor
		repInfo.status_prev = self.status 					# Cargo el estado de la variable status del pokemon atacante

		canAttack = self.check_status(def_pk) 			# Me fijo si puedo atacar debido a efectos secundarios
		repInfo.canAttack = canAttack 					# Guardo la data para el replay
		repInfo.status_post = self.status 				# Guardo esta información en un campo nuevo porque en check_status() pudo curarse
		
		if (canAttack == False): 						# No puede atacar debido a algún efecto secundario
			_replay_table.append(repInfo)
			del repInfo
			return
		
		delay_print("{} used {}!\n".format(self.name, self.att[att_index].name))

		#print("[DEBUG] | {} accuracy: {}".format(self.att[att_index].name, self.att[att_index].acc))

		if(self.att[att_index].acc == 0 or self.att[att_index].acc > randint(0,99)): 	# Chequeo si el ataque falla por accuracy

			repInfo.attackHit = True

			att_type = self.att[att_index].tipo 		# Tipo del ataque elegido
			def_pk_type1 = def_pk.tipo1 				# Tipo 1 del pokemon a la defensa
			def_pk_type2 = def_pk.tipo2 				# Tipo 2 del pokemon a la defensa
			
			lvl = self.lvl 								# Lvl del pokemon atacante: necesario para calcular daño crítico
			pwr = self.att[att_index].pwr				# Daño base del ataque
			pk_base_speed = self.spd_base 				# Velocidad base del pokemon atacante: necesario para calcular chance de crítico
			
			if(self.att[att_index].dt == 'Especial'): 	# Si el tipo de daño del ataque es ESPECIAL, se carga el stat ESP del atacante y defensivo
				A = self.spc 		
				D = def_pk.spc
			else: 										# Si el tipo de daño es FISICO, se carga el STR del pokemon atacante y DEF del defensivo
				A = self.str
				D = def_pk.df

			#Modifiers calculation: STAB, TYPE, RANDOM, CRIT
			if(att_type == self.tipo1 or att_type == self.tipo2): 	# Si el tipo del ataque coincide con alguno de 
				stab_mod = 1.5										# los del pokemon: STAB = 1.5
			else:
				stab_mod = 1.0

			type_mod = 1.0 											# Modificador por debilidades y resistencias
			for n in weaknesses_table:
				if(n[0] == att_type and n[1] == def_pk_type1):
					type_mod *= float(n[2])
				if(n[0] == att_type and n[1] == def_pk_type2):
					type_mod *= float(n[2]) 

			random_mod = randint(217,255)/255 						# Modificador random (Generación 1)

			crit_th = pk_base_speed/2 								# Cálculo de cŕitico: chance y daño
			if(randint(0,255)<crit_th):
				crit_mod = (2*lvl+5)/(lvl+5)
			else:
				crit_mod = 1

			modifier = random_mod * stab_mod * type_mod * crit_mod 	# Modificador total de daño
			
			dmg = 0 if pwr == 0 else math.floor(((((2*lvl/5+2)*pwr*(A/D))/50)+2)*modifier) 	# Cálculo del daño: https://bulbapedia.bulbagarden.net/wiki/Damage
			
			repInfo.attackDmg = int(dmg)

			# print("\n---Debugging Info---")
			# print("Tipo ataque: {}	DefPok tipo1: {}	DefPok tipo2: {}".format(att_type, def_pk_type1, def_pk_type2))
			# print("LVL: {}\nSpeed: {}\nPWR: {}\nA: {}\nD: {}".format(lvl,pk_base_speed,pwr,A,D))
			# print("Tipo del ataque: {}	Tipo1 del pokemon: {}	Tipo2 del pokemon: {}	STAB_mod: {}".format(att_type, self.tipo1, self.tipo2, stab_mod))
			# print("Random: {}	Stab: {}	Type: {}	Crit: {}	Modifier: {}".format(random_mod, stab_mod, type_mod, crit_mod, modifier))
			# print('Daño: ',dmg)
			# print("--------------------\n")

			if(type_mod == 0):
				delay_print("It doesn't have effect...")
				repInfo.attackHasEffect = False
			elif(crit_mod != 1 and dmg != 0):
				delay_print("It's a critical hit!")
				repInfo.attackWasCrit = True
			
			if(type_mod<1 and type_mod != 0 and dmg != 0):
				delay_print("It's not very effective...")
				repInfo.attackEffectiveness = "not effective"
			elif(type_mod>1  and dmg != 0):
				delay_print("It's super effective!")
				repInfo.attackEffectiveness = "very effective"

			def_pk.curr_hp -= dmg 							# Actualizo el HP del pokemon a la defensa
			if(def_pk.curr_hp < 0):
				def_pk.curr_hp = 0

			def_pk.calculate_health_bars()					# Actualizo las barras de HP del pokemon a la defensa

			# Evaluo efectos secundarios del ataque
			if(self.att[att_index].secEffect != "None" and type_mod != 0):
				#print("[DEBUG] | Entre al if de secondary effect porque no es NONE")
				repInfo.attackSecEffect = self.att[att_index].secEffect_methode(def_pk)		# Con secEffect_methode() le asigno el estado al pokemon a la defensa
				#print("[DEBUG] | secEffect_methode() devolvió: ", repInfo.attackSecEffect)
			#else: 																			# Ese método me devuelve el estado del pokemon y lo guardo para el replay
				#print("[DEBUG] | No tiene efecto secundario")

		else:
			delay_print("\n{} has failed...\n".format(self.att[att_index].name))

		_replay_table.append(repInfo)
		del repInfo

	# Método de Pokemon para calcular las barras de vida
	def calculate_health_bars(self):
		hp_per_bar = self.hp / 20 					
		cant_bars = math.ceil(self.curr_hp / hp_per_bar)
		aux_bars = ""
		for i in range(20):
			if i < cant_bars:
				aux_bars += '='
			else:
				aux_bars += '_'
		self.hp_bars = aux_bars


# Clase Attack
class Attack():

	def __init__(self, at_id, name, pwr, pp, acc, prior, tipo, description, dt):
		self.id = at_id
		self.name = name
		self.pwr = pwr
		self.pp = pp
		self.acc = acc
		self.prior = prior
		self.tipo = tipo
		self.description = description
		
		self.secEffect = "None"
		self.secEffectProb = 0

		self.dt = dt
		self.curr_pp = pp

	# Método de Attack para imprimir la información de un ataque
	def print_info_attack(self):
		print('''\n#Ataque ID: {}\nNombre del ataque: {}\nPotencia: {}\nPP: {}\nEfectividad: {}\nTipo: {}\nDescripcion: {}\nTipo de daño: {}\nEfecto secundario: {}\nProbabilidad de efecto secundario: {}\n'''.format(self.id,
			self.name, self.pwr, self.pp, self.acc, self.tipo, self.description, self.dt, self.secEffect, self.secEffectProb))

	# Método de Attack para carga el efecto secundario de un ataque
	def load_secEffect(self, secEff, prob):
		self.secEffect = secEff
		self.secEffectProb = prob

	# Método de Attack para aplicar los efectos secundarios de un ataque
	def secEffect_methode(self, def_pk):
		if (def_pk.status != "ok" and self.secEffect != "None"):
			delay_print("{} is alredy {}".format(def_pk.name, def_pk.status))
			return

		if(randint(0,99) < self.secEffectProb or self.secEffectProb == 100.0):

			if(self.secEffect == "Paralizar"):
				delay_print("{} is now paralyzed!".format(def_pk.name))
				def_pk.status = "paralyzed"
				def_pk.spd *= 0.25

			elif(self.secEffect == "Envenenamiento leve"):
				delay_print("{} is now poisoned!".format(def_pk.name))
				def_pk.status = "poisoned"

			elif(self.secEffect == "Quemar"):
				delay_print("{} is now burned!".format(def_pk.name))
				def_pk.status = "burned"

			elif(self.secEffect == "Congelar"):
				delay_print("{} is now frozen solid!".format(def_pk.name))
				def_pk.status = "frozen"

			elif(self.secEffect == "Confusión"):
				delay_print("{} is now confused!".format(def_pk.name))
				def_pk.status = "confused"
				def_pk.confusion_counter = randint(1,4)
				#delay_print("[DEBUG] | Quedará confundido {} turnos",format(def_pk.confusion_counter))

			elif(self.secEffect == "Dormir"):
				delay_print("{} fall sleep".format(def_pk.name))
				def_pk.status = "sleep"
				def_pk.sleep_counter = randint(1,7)
				#print("[DEBUG] | Quedará dormido {} turnos",format(def_pk.sleep_counter))
		return def_pk.status

# Función del menú para elegir un Pokemon
def choose_pokemon(cur):
	qry_res = []
	cur.execute("SELECT pokenum, name FROM pokemon")							# Query que muestra todos los Pokemon
	qry_res = cur.fetchall();

	print(tabulate(qry_res, headers=['#', 'Nombre'], tablefmt='fancy_grid'))	# Muestro el resultado
	
	print("\n\n Ingrese el número del pokemon a utilizar o una cadena de caracteres para hacer un filtrado sobre la lista\n")

	# Comienzo el loop de selección de Pokemon
	confirm_flag = False;
	while(confirm_flag == False):
		usr_string = input()
		# Si ingresó un número de pokemon, lo indexo en la lista de Pokemon
		try:	
			choose = int(usr_string)
			if(choose<=151):
				mypokemon = qry_res[choose-1]
				#Si ingresó un número de Pokemon pido confirmación
				if (input("Está seguro que quiere utilizar a {}? S/n\n".format(mypokemon[1])).lower() == 's'):
					confirm_flag = True
				else:
					print("Ingrese otra opcion:\n")
					continue
			else:
					print("[INFO] | El numero a ingresar debe ser menor o igual a 151. Ingrese otra opcion:\n")
					continue
		# Si ingresó un una cadena de caracteres, filtro los Pokemon que tengan esa cadena de caracteres
		except ValueError:
			cur.execute("SELECT pokenum, name FROM pokemon WHERE name like \"%{}%\"".format(usr_string.strip()))
			qry_filt = cur.fetchall();
			CLR_SCRN()
			print("Pokemon que contienen la cadena \"{}\"\n".format(usr_string.strip()))
			for n in qry_filt:
				print(n[0],"	",n[1])
			print("\n\n Ingrese el número del pokemon a utilizar o una cadena de caracteres para hacer un filtrado sobre la lista\n")
			continue

	# Una vez confirmado el Pokemon
	print("Utilizaras a {}\n".format(mypokemon[1]))
	mypokemon = load_pokemon(cur, choose)
	return mypokemon


# Función para cargar un pokemon a la clase Pokemon
def load_pokemon(cur, index):
	cur.execute("SELECT * FROM pokemon WHERE pokenum = {}".format(index))
	qry_res = cur.fetchall()
	mypokemon = Pokemon(qry_res[0][1],qry_res[0][2],qry_res[0][3],qry_res[0][4],qry_res[0][5],qry_res[0][6],qry_res[0][7])

	cur.execute('''SELECT pokemon.name , type.name 
					FROM pokemon, type, pokemon_type 
					WHERE pokemon_type.pokemonID = pokemon.pokemonID 
					AND pokemon_type.typeID = type.typeID 
					AND pokemon.pokemonID = {}'''.format(index))
	qry_res = cur.fetchall()
	mypokemon.load_pokemon_type(qry_res)
	return mypokemon


# Función del menú para elegir un Ataque
def load_attacks(cur, mypokemon):
	cur.execute('''SELECT attack.attackID, attack.name, attack.PWR, attack.PP, type.name  
	FROM attack, pokemon, pokemon_attack, type 
	WHERE pokemon_attack.attackID = attack.attackID AND pokemon_attack.pokemonID = pokemon.pokemonID 
	AND type.typeID = attack.typeID AND pokemon.pokemonID = {} 
	ORDER BY attack.name asc'''.format(mypokemon.num))

	qry_res = cur.fetchall()

	print(tabulate(qry_res, headers=['#ID', 'Ataque', 'PWR', 'PP', 'Tipo'], tablefmt='fancy_grid'))
	print("Elija 4 ataques ingresando su número de ID de la lista o \"info <#ID>\" para obtener una descripcion detallada del attaque.\n")

	attack_count = 0
	invalid_attack_flag = True
	pokemon_attack_num = [];
	pokemon_attack_name = []

	while(attack_count<NUM_ATTACKS):
		input_attack = input().strip()
		input_attack = input_attack.split(' ')
		if (len(input_attack) == 2 and input_attack[0].lower() == "info"):
			CLR_SCRN()
			cur.execute('''SELECT a.attackID, a.name, a.PWR, a.PP, a.ACC, a.PRIOR, t.name, a.description, dt.name 
							FROM attack a, type t, dmgType dt 
							WHERE dt.dmgTypeID = t.dmgTypeID AND a.typeID = t.typeID AND a.attackID ={};'''.format(input_attack[1]))
			qry_attack_info = cur.fetchall()
			print(tabulate(qry_attack_info, headers=['#ID','Ataque','PWR','PP','ACC','PRIOR','Tipo','Descripcion','Tipo de daño']))
			input("\nPresione una tecla para continuar\n")
			CLR_SCRN()
			print(tabulate(qry_res, headers=['#ID', 'Ataque', 'PWR', 'PP', 'Tipo'], tablefmt='fancy_grid'))
			print("Elija 4 ataques ingresando su número de ID de la lista o \"info <#ID>\" para obtener una descripcion detallada del attaque.\n")
		else:
			for n in input_attack:
				invalid_attack_flag = True
				try:
					n=int(n)
					for q in qry_res:
						if(n == q[0]):
							print("Ataque seleccionado")
							pokemon_attack_num.append(n)
							attack_count+=1
							pokemon_attack_name.append(qry_attack_list[n-1][1])
							invalid_attack_flag = False
							CLR_SCRN()
							print(tabulate(qry_res, headers=['#ID', 'Ataque', 'PWR', 'PP', 'Tipo'], tablefmt='fancy_grid'))
							print("Elija 4 ataques ingresando su número de ID de la lista o \"info <#ID>\" para obtener una descripcion detallada del attaque.\n")

				except Exception as e:
					continue
				if(invalid_attack_flag==True):
					print("ERROR | El ataque {} no corresponde a {}".format(n,mypokemon.name))
			
		print("Ataques elegidos: {}".format(pokemon_attack_name))
		if(attack_count==NUM_ATTACKS):
			if(input("Confirma los ataques seleccionados? S/n\n").lower()!='s'):
				attack_count = 0;
				pokemon_attack_name = []
				pokemon_attack_num = []
				CLR_SCRN()
				print(tabulate(qry_res, headers=['#ID', 'Ataque', 'PWR', 'PP', 'Tipo'], tablefmt='fancy_grid'))
				print("Elija 4 ataques ingresando su número de ID de la lista o \"info <#ID>\" para obtener una descripcion detallada del attaque.\n")

	#Ya elegí los 4 ataques. Se los instancio al pokemon
	mypokemon.load_attacks(pokemon_attack_num, cur, qry_attacks_with_secEffect)


	


if __name__ == '__main__':

	seed(time.time())
	_replay_table = []


	#Hago la conexion con la base de datos y creo el cursor
	conn = motorDB.connect(host='localhost', user='guest', password='guest')
	conn.autocommit(True)
	cur = conn.cursor()
	cur.execute("USE myPokemonDB")
	
	# pygame.mixer.init()
	# pygame.mixer.music.load("101 - opening.mp3")
	# pygame.mixer.music.play()

	# time.sleep(1)
	# tprint("POKESIM")
	# time.sleep(3)	
	
	# Tabla de ataques
	cur.execute('''SELECT * FROM attack ORDER BY attackID''')
	qry_attack_list = cur.fetchall()

	# Tabla de ataques con efectos secundarios
	cur.execute('''SELECT attack.attackID, attack.name, secEffect.name, attack_secEffect.prob 
					FROM attack, secEffect, attack_secEffect 
					WHERE attack.attackID = attack_secEffect.attackID AND attack_secEffect.secEffectID = secEffect.secEffectID;''')
	qry_attacks_with_secEffect = cur.fetchall()

	# Tabla de multiplicadores por debilidades y resistencias
	cur.execute('''SELECT att.name, pok.name, multiplier  
					FROM attackEffectiveness 
					INNER JOIN type att ON attackEffectiveness.attackTypeID = att.typeID  
					INNER JOIN type pok ON attackEffectiveness.pokemonTypeID = pok.typeID''')
	_attacks_effectiveness_table = cur.fetchall()



	#Menu principal del juego

	#print('''Ingrese el modo de uso:
		#(1) Simulador de batalla P2 vs P2
		#(2) Repetidor de batallas''')
	op = input('''Ingrese el modo de uso:
		(1) Simulador de batalla P2 vs P2
		(2) Repetidor de batallas
		(3) Borrar batallas guardadas\n''')


	# Opcion Simulador de batalla
	if(op == '1'):

		print("\n[INFO] | Se ejecutará el código del simulador de batalla\n")
		
		input("Presione una tecla para elegir su Pokemon y sus ataques")
		mypokemon = choose_pokemon(cur)
		load_attacks(cur, mypokemon)

		CLR_SCRN()
		print("*----------INFORMACION DE LOS ATAQUES----------*")
		for i in range(NUM_ATTACKS):
			mypokemon.att[i].print_info_attack()
		print("*----------INFORMACION DEL POKEMON----------*")	
		mypokemon.print_pokemon_info()

		input("Presione una tecla para elegir el Pokemon contrario y sus ataques")
		otherpokemon = choose_pokemon(cur)
		load_attacks(cur, otherpokemon)		

		CLR_SCRN()
		print("*----------INFORMACION DE LOS ATAQUES----------*")
		for i in range(NUM_ATTACKS):
			otherpokemon.att[i].print_info_attack()
		print("*----------INFORMACION DEL POKEMON----------*")	
		otherpokemon.print_pokemon_info()

		input("\nPresione ENTER para continuar con la batalla")

		# Comenzando la pelea
		# pygame.mixer.music.stop()
		# pygame.mixer.music.load("115 - battle.mp3")
		# pygame.mixer.music.play()

		# figth_screen()

		pkrply.create_replay_entrance(cur, conn)			# Creo una entrada en la tabla de replays para que le asigne un replayID a esta batalla
		cur.execute('''	SELECT replayID 				# Obtengo el número de replayID de esta batalla
						FROM replay
						ORDER BY replayID DESC
						LIMIT 1''')
		_replayID = cur.fetchone()
		_replayID = _replayID[0]
		#print("[DEBUG] | El replayID asignado es: ",_replayID)
		

		# Cargo dos entradas en la tabla de replayInfo con los ID de los pokemon que participarán en esta batalla
		for n in range(NUM_ATTACKS):
			cur.execute('''	INSERT INTO replayInfo (replayID, pokemonID, attackID)
							VALUES ({},{},{})
						'''.format(_replayID, mypokemon.num, mypokemon.att[n].id))

			cur.execute('''	INSERT INTO replayInfo (replayID, pokemonID, attackID)
							VALUES ({},{},{})
						'''.format(_replayID, otherpokemon.num, otherpokemon.att[n].id))
		conn.commit()

		turn = 1
		while(mypokemon.curr_hp >0 and otherpokemon.curr_hp>0):

			#print("[DEBUG] | repInfo: ", _replay_table)
			#input("input")
			
			if(mypokemon.spd > otherpokemon.spd):
				CLR_SCRN()
				delay_print('\n{} vs {} - Turno: {}\n'.format(mypokemon.name, otherpokemon.name, turn))
				mypokemon.print_health_bars()
				otherpokemon.print_health_bars()

				delay_print('Es el turno de {}'.format(mypokemon.name))
				delay_print('Elija un ataque (o \"info <#>\" para ver la informacion del ataque)')
				mypokemon.show_attacks()

				flag_attack_select = False
				while(flag_attack_select == False):

					input_attack = input().strip().split(' ')
					
					if(len(input_attack) > 2):
						delay_print("[INFO] | Ingreso incorrecto. Ingrese el número del ataque a utilizar o \"info <#>\" para ver la informacion de un ataque")
						continue

					elif (len(input_attack) == 2 and input_attack[0].lower() == "info"):
						mypokemon.att[int(input_attack[1])-1].print_info_attack()
						delay_print('\n\nElija un ataque (o \"info <#>\" para ver la informacion del ataque):')
						mypokemon.show_attacks()
						continue

					else:
						try:
							input_attack = int(input_attack[0])
							if(input_attack > 0 and input_attack <= NUM_ATTACKS):
								mypokemon.do_attack(input_attack, otherpokemon, _attacks_effectiveness_table, _replay_table, _replayID)
								flag_attack_select = True
						except:
							delay_print("Ingreso incorrecto. Ingrese el número del ataque a utilizar o \"info <#>\" para ver la informacion de un ataque")
							continue

				mypokemon.print_health_bars()
				otherpokemon.print_health_bars()

				if(mypokemon.curr_hp > 0 and otherpokemon.curr_hp > 0):
					delay_print('Es el turno de {}'.format(otherpokemon.name))
					delay_print('Elija un ataque (o \"info <#>\" para ver la informacion del ataque)')
					otherpokemon.show_attacks()

					flag_attack_select = False
					while(flag_attack_select == False):

						input_attack = input().strip().split(' ')

						if(len(input_attack) > 2):
							delay_print("[INFO] | Ingreso incorrecto. Ingrese el número del ataque a utilizar o \"info <#>\" para ver la informacion de un ataque")
							continue

						elif (len(input_attack) == 2 and input_attack[0].lower() == "info"):
							otherpokemon.att[int(input_attack[1])-1].print_info_attack()
							delay_print('\n\nElija un ataque (o \"info <#>\" para ver la informacion del ataque):')
							otherpokemon.show_attacks()
							continue

						else:
							try:
								input_attack = int(input_attack[0])
								if(input_attack > 0 and input_attack <= NUM_ATTACKS):
									otherpokemon.do_attack(input_attack, mypokemon, _attacks_effectiveness_table, _replay_table, _replayID)
									flag_attack_select = True
							except:
								delay_print("Ingreso incorrecto. Ingrese el número del ataque a utilizar o \"info <#>\" para ver la informacion de un ataque")
								continue

					mypokemon.print_health_bars()
					otherpokemon.print_health_bars()
					time.sleep(1)

			elif(mypokemon.spd < otherpokemon.spd):

				CLR_SCRN()
				delay_print('\n{} vs {} - Turno: {}\n'.format(mypokemon.name, otherpokemon.name, turn))
				mypokemon.print_health_bars()
				otherpokemon.print_health_bars()

				delay_print('Es el turno de {}'.format(otherpokemon.name))
				delay_print('Elija un ataque (o \"info <#>\" para ver la informacion del ataque):')
				otherpokemon.show_attacks()

				flag_attack_select = False
				while(flag_attack_select == False):

					input_attack = input().strip().split(' ')

					if(len(input_attack) > 2):
						delay_print("[INFO] | Ingreso incorrecto. Ingrese el número del ataque a utilizar o \"info <#>\" para ver la informacion de un ataque")
						continue

					elif (len(input_attack) == 2 and input_attack[0].lower() == "info"):
						otherpokemon.att[int(input_attack[1])-1].print_info_attack()
						delay_print('\n\nElija un ataque (o \"info <#>\" para ver la informacion del ataque):')
						otherpokemon.show_attacks()
						continue

					else:
						try:
							input_attack = int(input_attack[0])
							if(input_attack > 0 and input_attack <= NUM_ATTACKS):
								otherpokemon.do_attack(input_attack, mypokemon, _attacks_effectiveness_table, _replay_table, _replayID)
								flag_attack_select = True
						except:
							delay_print("Ingreso incorrecto. Ingrese el número del ataque a utilizar o \"info <#>\" para ver la informacion de un ataque")
							continue

				mypokemon.print_health_bars()
				otherpokemon.print_health_bars()

				if(mypokemon.curr_hp > 0 and otherpokemon.curr_hp > 0):

					delay_print('Es el turno de {}'.format(mypokemon.name))
					delay_print('Elija un ataque (o \"info <#>\" para ver la informacion del ataque)')
					mypokemon.show_attacks()

					flag_attack_select = False
					while(flag_attack_select == False):

						input_attack = input().strip().split(' ')
						
						if(len(input_attack) > 2):
							delay_print("[INFO] | Ingreso incorrecto. Ingrese el número del ataque a utilizar o \"info <#>\" para ver la informacion de un ataque")
							continue

						elif (len(input_attack) == 2 and input_attack[0].lower() == "info"):
							mypokemon.att[int(input_attack[1])-1].print_info_attack()
							delay_print('\n\nElija un ataque (o \"info <#>\" para ver la informacion del ataque):')
							mypokemon.show_attacks()
							continue

						else:
							try:
								input_attack = int(input_attack[0])
								if(input_attack > 0 and input_attack <= NUM_ATTACKS):
									mypokemon.do_attack(input_attack, otherpokemon, _attacks_effectiveness_table, _replay_table, _replayID)
									flag_attack_select = True
							except:
								delay_print("Ingreso incorrecto. Ingrese el número del ataque a utilizar o \"info <#>\" para ver la informacion de un ataque")
								continue

						mypokemon.print_health_bars()
						otherpokemon.print_health_bars()
						time.sleep(1)

			else:
				if(randint(0,1) == 0):
					delay_print('Es el turno de {}'.format(mypokemon.name))
					delay_print('Elija un ataque (o \"info <#>\" para ver la informacion del ataque)')
					mypokemon.show_attacks()
					input_attack = input().strip().split(' ')

				else:
					delay_print('Es el turno de {}'.format(otherpokemon.name))
					delay_print('Elija un ataque (o \"info <#>\" para ver la informacion del ataque):')
					otherpokemon.show_attacks()
					input_attack = input().strip().split(' ')



			turn +=1

		for n in _replay_table:
			# print("[DEBUG] | replayID: {}".format(n.replayID))
			# print("[DEBUG] | time: {}".format(n.time))
			# print("[DEBUG] | pokemonID: {}".format(n.pokemonID))
			# print("[DEBUG] | attackID: {}".format(n.attackID))
			# print("[DEBUG] | status_prev: {}".format(n.status_prev))
			# print("[DEBUG] | status_post: {}".format(n.status_post))
			# print("[DEBUG] | canAttack: {}".format(n.canAttack))
			# print("[DEBUG] | attackHit: {}".format(n.attackHit))
			# print("[DEBUG] | attackHasEffect: {}".format(n.attackHasEffect))
			# print("[DEBUG] | attackWasCrit: {}".format(n.attackWasCrit))
			# print("[DEBUG] | attackEffectiveness: {}".format(n.attackEffectiveness))
			# print("[DEBUG] | attackDmg: {}".format(n.attackDmg))
			# print("[DEBUG] | attackSecEffect: {}".format(n.attackSecEffect))

			cur.execute('''INSERT INTO replayInfo (replayID, time, pokemonID, attackID, statusPrev, statusPost, canAttack,
							attackHit, attackHasEffect, attackWasCrit, attackEffectiveness, attackDmg, attackSecEffect)
							VALUES ({},"{}",{},{},"{}","{}",{},{},{},{},"{}",{},"{}");
							'''.format(n.replayID, n.time, n.pokemonID, n.attackID, n.status_prev, n.status_post, n.canAttack, n.attackHit, n.attackHasEffect, n.attackWasCrit, n.attackEffectiveness, n.attackDmg, n.attackSecEffect))
		conn.commit()

		print("[INFO] | ReplayInfo loaded in the data base")

		# Anunciando al ganador
		if(mypokemon.curr_hp<=0):
			delay_print("{} has fainted!".format(mypokemon.name))
		else:
			delay_print("{} has fainted!".format(otherpokemon.name))
		time.sleep(1)

		# pygame.mixer.music.stop()
		# pygame.mixer.music.load("145 - ending.mp3")
		# pygame.mixer.music.play()

		# battle_end_screen(mypokemon, otherpokemon)

		input("\nPresione ENTER para salir")
		


	# Opción de replays
	elif(op == '2'):

		cur_aux = conn.cursor()

		# Tabla de pokemons
		cur_aux.execute('''SELECT pokemonID, name FROM pokemon ORDER BY pokemonID ASC''')
		qry_pokemon_table = cur_aux.fetchall()		

		qry_replay_info = []
		qry_aux = []
		pk1_attacks_vect = []
		pk2_attacks_vect = []

		last_replayID = pkrply.show_replay_list(cur)

		if(last_replayID == ()):
			print("[INFO] | No hay replays para mostrar. Saliendo del programa.")
			sys.exit(0)

		flag = False
		while(flag == False):

			replay_to_play = input("\nIngrese el número de replay que desea reproducir\n").strip()

			try:
				replay_to_play = int(replay_to_play)
				flag = True

			except:
				continue

		cur.execute('''SELECT * FROM replayInfo WHERE replayID = {} ORDER BY time ASC;
					'''.format(replay_to_play))
		
		for n in range(NUM_ATTACKS):
			qry_replay_info = cur.fetchone()
			pokemonID_1 = qry_replay_info[2];
			pk1_attacks_vect.append(qry_replay_info[3])

			qry_replay_info = cur.fetchone()
			pokemonID_2 = qry_replay_info[2]
			pk2_attacks_vect.append(qry_replay_info[3])
			

		pokemon_1 = load_pokemon(cur_aux, pokemonID_1)
		pokemon_1.load_attacks(pk1_attacks_vect, cur_aux, qry_attacks_with_secEffect)
		pokemon_2 = load_pokemon(cur_aux, pokemonID_2)
		pokemon_2.load_attacks(pk2_attacks_vect, cur_aux, qry_attacks_with_secEffect)

		CLR_SCRN()
		print("----------POKEMON 1----------")
		pokemon_1.print_pokemon_info()
		tprint("\n\n\n VS \n\n\n")
		print("----------POKEMON 2----------")
		pokemon_2.print_pokemon_info()
		#time.sleep(2)

		# Comenzando la repe
		# pygame.mixer.music.stop()
		# pygame.mixer.music.load("115 - battle.mp3")
		# pygame.mixer.music.play()
		# figth_screen()

		flag = True
		turn = 1
		while(flag == True):

			CLR_SCRN()
			qry_replay_info = cur.fetchone()
			if(qry_replay_info == None):
				flag = False
			turn_info = pkrply.LoadReplayInfo(qry_replay_info)

			delay_print('\n{} vs {} - Turno: {}\n'.format(pokemon_1.name, pokemon_2.name, turn))
			pokemon_1.print_health_bars()
			pokemon_2.print_health_bars()

			delay_print('Es el turno de {}'.format(qry_pokemon_table[turn_info.pokemonID-1][1]))
			delay_print('Elija un ataque (o \"info <#>\" para ver la informacion del ataque)')
			
			if(qry_pokemon_table[turn_info.pokemonID-1][1] == pokemon_1.name):
				pokemon_1.show_attacks()
			else:
				pokemon_2.show_attacks()
			time.sleep(0.5)

			turn_info.pokemon_do_attack(qry_pokemon_table, qry_attack_list)

			qry_replay_info = cur.fetchone()
			if(qry_replay_info == None):
				flag = False
				sys.exit()
			turn_info = pkrply.LoadReplayInfo(qry_replay_info)

			pokemon_1.print_health_bars()
			pokemon_2.print_health_bars()

			delay_print('Es el turno de {}'.format(qry_pokemon_table[turn_info.pokemonID-1][1]))
			delay_print('Elija un ataque (o \"info <#>\" para ver la informacion del ataque)')
			
			if(qry_pokemon_table[turn_info.pokemonID-1][1] == pokemon_1.name):
				pokemon_1.show_attacks()
			else:
				pokemon_2.show_attacks()
			time.sleep(0.5)

			turn_info.pokemon_do_attack(qry_pokemon_table, qry_attack_list)


			turn +=1
			#time.sleep(0.5)

	# Opción para eliminar replays
	elif(op == '3'):

		last_replayID = pkrply.show_replay_list(cur)

		#print("[DEBUG] | last_replayID: ", last_replayID)
		
		if(last_replayID == ()):
			print("[INFO] | No hay replays para borrar. Saliendo del programa.")
			sys.exit(0)

		flag = False
		while(flag == False):

			delete_replay_opt = input("\nIngrese el número de replay que desea borrar, \"all\" para borrar todo o \"q\" para salir\n").strip()

			try:
				#print("[DEBUG] | Estoy en el try")
				delete_replay_opt = int(delete_replay_opt)
				#print("[DEBUG] | delete_replay_opt: ", delete_replay_opt)
				if(delete_replay_opt > last_replayID):
					print("\nIngreso incorrecto")
				else:
					pkrply.detele_replay(cur, conn, delete_replay_opt)
					flag = True
			except:
				if(delete_replay_opt.lower() == "all"):
					pkrply.delete_replay_all(cur, conn)
					flag = True
				elif(delete_replay_opt.lower() == "q"):
					flag =	True










	# Opción de Test de ingresar datos a los replays
	elif(op == '8'):

		pkrply.create_replay_entrance(cur, conn)

		#now = datetime.datetime.now()
		now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S').strip()
		print("[DEBUG] | now:",now)

		cur.execute('''INSERT INTO replay (time) 
  						VALUES ("{}");'''.format(now))
		conn.commit()
		print("[DEBUG] | Se agregó una entrada a replays")


	else:
		print("[ERROR] | Elección errónea. Saliendo del programa\n\n")

