import MySQLdb as motorDB
import math
import time
import sys
import pygame

from random import seed
from random import randint
from tabulate import tabulate
from art import tprint

NUM_ATTACKS = 2

def delay_print(s):
    # print one character at a time
    # https://stackoverflow.com/questions/9246076/how-to-print-one-character-at-a-time-on-one-line
    for c in s:
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(0.025)
    print('')


def figth_screen():
	time.sleep(1.5)
	for n in range(5):
		CLR_SCRN()
		time.sleep(0.5)
		tprint("FIGHT")
		time.sleep(0.5)

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

def load_csv(csv_route):
	datos = []
	f = open(csv_route)
	for line in f.readlines():
	    datos.append(line.split(','))

	for n in range(len(datos)):
	    for k in range(len(datos[n])):
	        datos[n][k]=datos[n][k].rstrip().lstrip()
	return datos

def CLR_SCRN(*args):
	print('\033c')
	for n in args:
		print(n)


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

	def load_pokemon_type(self, vect):
		self.tipo1 = vect[0][1]
		if (len(vect)==2):
			self.tipo2 = vect[1][1]

	def print_pokemon_info(self):

		if(self.att == []):
			print('''# Pokemon: {}\nNombre: {}\nTipo 1: {}\nTipo 2: {}\nHP: {}\nSTR: {}\nDEF: {}\nSPC: {}\nSPD:  {}\n'''.format(self.num, self.name, 
				self.tipo1, self.tipo2, self.hp, self.str, self.df, self.spc, self.spd))
		else:
			print('''# Pokemon: {}\nNombre: {}\nTipo 1: {}\nTipo 2: {}\nHP: {}\nSTR: {}\nDEF: {}\nSPC: {}\nSPD:  {}\nAtaque 1:  {}\nAtaque 2:  {}\n
				'''.format(self.num, self.name, self.tipo1, self.tipo2, self.hp, self.str, self.df, self.spc, self.spd,
					self.att[0].name, self.att[1].name))

	def print_health_bars(self):
		delay_print('----------{}----------'.format(self.name))
		delay_print('{}'.format(self.hp_bars))
		delay_print('HP:{}/{}'.format(self.curr_hp, self.hp))
		print('')

	def show_attacks(self):
		for n in range(len(self.att)):
			print('{}) {}'.format(n+1, self.att[n].name))

	# Devuelve True si el pokemon puede atacar, False eoc.
	def check_status(self):
		
		if(self.status == "ok"):
			return True

		elif(self.status == "sleep"):
			delay_print(self.name, "is fast asleep...")
			if(self.sleep_counter == 0):
				self.status = "ok"
				delay_print(self.name, "woke up!")
				return True
			self.sleep_counter -= 1
			return False

		elif(self.status == "paralyzed"):
			if(randint(1,4) == 1):
				return True
			else:
				print(self.name," is fully paralyzed.")
				return False

		elif(self.status == "confused"):
			delay_print(self.name," is confused...")
			if(self.confusion_counter == 0):
				self.status = "ok"
				print(self.name, "is no more confused!")
				return True
			self.confusion_counter -= 1
			if(randint(1,2) == 1):
				delay_print("It hurts itself in its confusion!")
				self.curr_hp -= math.floor(((((2*self.lvl/5+2)*40*(self.str/self.df))/50)+2)) 		# Se daña como si fuese atacado
				self.curr_hp = 0 if self.curr_hp < 0 else self.curr_hp								# por un ataque de PWR 40 y daño
				self.calculate_health_bars() 														# físico, sin modificadores
				return False
			return True

			## COMENTARIOS: ESTA FUNCION SOLO CHEQUEA EL ESTADO. DESPUES, ANTES DE CADA ATAQUE, SI DEVOLVIÓ FALSE TENGO QUE VER
			## LA CUASA Y HACER COSAS DISTINTAS. CUADNO EL POKEMON OBTIENE EL ESTADO, AHÍ HACER LAS COSAS QUE OCURREN UNA SOLA VEZ
			## COMO POR EJEMPLO BAJAR LA VELOCIDAD EN EL CASO DE LA PARÁLISIS

		elif(self.status == "poisoned"):
			delay_print(self.name, " is poisoned...")
			self.curr_hp -= math.floor(self.hp/16) 						# Pierde 1/16 de su vida total cada turno
			self.curr_hp = 0 if self.curr_hp < 0 else self.curr_hp
			self.calculate_health_bars()
			return True

		elif(self.status == "burned"):
			delay_print(self.name, " is burned...")
			self.curr_hp -= math.floor(self.hp/16) 						# Pierde 1/16 de su vida total cada turno
			self.curr_hp = 0 if self.curr_hp < 0 else self.curr_hp
			self.calculate_health_bars()
			return True

		elif(self.status == "frozen"):
			delay_print(self.name, " is frozen solid...")
			if(randint(1,10) == 1):
				delay_print(self.name," is no more frozen!")
				self.status = "ok"
				return True
			else:
				return False




	def do_attack(self, num, def_pk, weaknesses_table, reply_table):
		#https://bulbapedia.bulbagarden.net/wiki/Damage
		#https://bulbapedia.bulbagarden.net/wiki/Critical_hit#In_Generation_I
		
		if (self.check_status() == False):
			return

		att_index = int(num)-1						# Calculo el índice de la lista de ataques: -1 a lo que ingresó el usuario

		if(self.att[att_index].acc == 0 or self.att[att_index].acc > randint(0,99)):

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
			
			print("\n---Debugging Info---")
			print("Tipo ataque: {}	DefPok tipo1: {}	DefPok tipo2: {}".format(att_type, def_pk_type1, def_pk_type2))
			print("LVL: {}\nSpeed: {}\nPWR: {}\nA: {}\nD: {}".format(lvl,pk_base_speed,pwr,A,D))
			print("Tipo del ataque: {}	Tipo1 del pokemon: {}	Tipo2 del pokemon: {}	STAB_mod: {}".format(att_type, self.tipo1, self.tipo2, stab_mod))
			print("Random: {}	Stab: {}	Type: {}	Crit: {}	Modifier: {}".format(random_mod, stab_mod, type_mod, crit_mod, modifier))
			print('Daño: ',dmg)
			print("--------------------\n")

			if(type_mod == 0):
				delay_print("It doesn't have effect...")
			elif(crit_mod != 1):
				delay_print("It's a critical hit!")
			
			if(type_mod<1 and type_mod != 0):
				delay_print("It's not very effective...")
			elif(type_mod>1):
				delay_print("It's super effective!")

			def_pk.curr_hp -= dmg 							# Actualizo el HP del pokemon a la defensa
			if(def_pk.curr_hp < 0):
				def_pk.curr_hp = 0

			def_pk.calculate_health_bars()					# Actualizo las barras de HP del pokemon a la defensa

			if(self.att[att_index].secEffect != "None"):
				print("entre al if de secondary effect porque no es NONE")
				self.att[att_index].secEffect_methode(def_pk)
			else:
				print("no tiene efecto secundario")

		else:
			delay_print("\n{} has failed...".format(self.att[att_index].name))

	
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


	def print_info_attack(self):
		print('''\n#Ataque ID: {}\nNombre del ataque: {}\nPotencia: {}\nPP: {}\nEfectividad: {}\nTipo: {}\nDescripcion: {}\nTipo de daño: {}\nEfecto secundario: {}\nProbabilidad de efecto secundario: {}\n'''.format(self.id,
			self.name, self.pwr, self.pp, self.acc, self.tipo, self.description, self.dt, self.secEffect, self.secEffectProb))

	def load_secEffect(self, secEff, prob):
		self.secEffect = secEff
		self.secEffectProb = prob

	def secEffect_methode(self, def_pk):
		if (def_pk.status != "ok"):
			print("el pokemon a la defensa ya está en algún estado")
			return

		if(randint(0,99) < self.secEffectProb):

			if(self.secEffect == "Paralizar"):
				print("el efecto fue paralizar")
				def_pk.status = "paralyzed"
				def_pk.spd *= 0.25

			elif(self.secEffect == "Envenenamiento leve"):
				print("el efecto fue envenenar")
				def_pk.status = "poisoned"

			elif(self.secEffect == "Quemar"):
				print("El efecto secundario fue quemar")
				def_pk.status = "burned"

			elif(self.secEffect == "Congelar"):
				print("El efecto secundario fue congelar")
				def_pk.status = "frozen"

			elif(self.secEffect == "Confusión"):
				print("El efecto secundario fue confundir")
				def_pk.status = "confused"



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
	cur.execute("SELECT * FROM pokemon WHERE pokenum = {}".format(choose))
	qry_res = cur.fetchall()
	mypokemon = Pokemon(qry_res[0][1],qry_res[0][2],qry_res[0][3],qry_res[0][4],qry_res[0][5],qry_res[0][6],qry_res[0][7])

	cur.execute('''SELECT pokemon.name , type.name 
					FROM pokemon, type, pokemon_type 
					WHERE pokemon_type.pokemonID = pokemon.pokemonID 
					AND pokemon_type.typeID = type.typeID 
					AND pokemon.pokemonID = {}'''.format(choose))
	qry_res = cur.fetchall()
	mypokemon.load_pokemon_type(qry_res)
	return mypokemon

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

	# pygame.mixer.init()
	# pygame.mixer.music.load("101 - opening.mp3")
	# pygame.mixer.music.play()

	_attacks_effectiveness_table = load_csv("attacks_effectiveness.csv")
	_replay_table = []
	
	# time.sleep(1)
	# tprint("POKESIM")
	# time.sleep(3)
	
	#Hago la conexion con la base de datos y creo el cursor
	
	conn = motorDB.connect(host='localhost', user='guest', password='guest')
	conn.autocommit(True)
	cur = conn.cursor()
	cur.execute("USE myPokemonDB")


	#Tabla de ataques
	cur.execute('''SELECT * FROM attack ORDER BY attackID''')
	qry_attack_list = cur.fetchall()

	#Tabla de ataques con efectos secundarios
	cur.execute('''SELECT attack.attackID, attack.name, secEffect.name, attack_secEffect.prob 
					FROM attack, secEffect, attack_secEffect 
					WHERE attack.attackID = attack_secEffect.attackID AND attack_secEffect.secEffectID = secEffect.secEffectID;''')
	qry_attacks_with_secEffect = cur.fetchall()

	#Menu principal del juego

	print('''Ingrese el modo de uso:
		(1) Simulador de batalla P2 vs P2
		(2) Repetidor de batallas''')
	#op = input('''Ingrese el modo de uso:
		# (1) Simulador de batalla P2 vs P2
		# (2) Repetidor de batallas''')

	op='1'				# Borrar y descomentar dsp del debbug

	#Opcion Simulador de batalla
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
			mypokemon.att[i].print_info_attack()
		print("*----------INFORMACION DEL POKEMON----------*")	
		otherpokemon.print_pokemon_info()

		input("\nPresione ENTER para continuar con la batalla")

		# Comenzando la pelea
		# pygame.mixer.music.stop()
		# pygame.mixer.music.load("115 - battle.mp3")
		# pygame.mixer.music.play()
		# figth_screen()

		turn = 1
		while(mypokemon.curr_hp >0 and otherpokemon.curr_hp>0):
			
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
					if(input_attack == ''):
						delay_print("Ingreso incorrecto. Ingrese el número del ataque a utilizar o \"info <#>\" para ver la informacion de un ataque")
						continue
					elif (len(input_attack) == 2 and input_attack[0].lower() == "info"):
						mypokemon.att[int(input_attack[1])-1].print_info_attack()
						delay_print('\n\nElija un ataque (o \"info <#>\" para ver la informacion del ataque):')
						mypokemon.show_attacks()
						continue

					elif(len(input_attack) == 1 and int(input_attack[0]) >= 0 and int(input_attack[0])<=4):
						mypokemon.do_attack(input_attack[0], otherpokemon, _attacks_effectiveness_table, _replay_table)
						flag_attack_select = True
					else:
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
						if(input_attack == ''):
							delay_print("Ingreso incorrecto. Ingrese el número del ataque a utilizar o \"info <#>\" para ver la informacion de un ataque")
							continue
						elif (len(input_attack) == 2 and input_attack[0].lower() == "info"):
							otherpokemon.att[int(input_attack[1])-1].print_info_attack()
							delay_print('\n\nElija un ataque (o \"info <#>\" para ver la informacion del ataque):')
							otherpokemon.show_attacks()
							continue

						elif(len(input_attack) == 1 and int(input_attack[0]) >= 0 and int(input_attack[0])<=4):
							otherpokemon.do_attack(input_attack[0], mypokemon, _attacks_effectiveness_table, _replay_table)
							flag_attack_select = True
						else:
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
					if(input_attack == ''):
						delay_print("Ingreso incorrecto. Ingrese el número del ataque a utilizar o \"info <#>\" para ver la informacion de un ataque")
						continue
					elif (len(input_attack) == 2 and input_attack[0].lower() == "info"):
						otherpokemon.att[int(input_attack[1])-1].print_info_attack()
						delay_print('\n\nElija un ataque (o \"info <#>\" para ver la informacion del ataque):')
						otherpokemon.show_attacks()
						continue

					elif(len(input_attack) == 1 and int(input_attack[0]) >= 0 and int(input_attack[0])<=4):
						otherpokemon.do_attack(input_attack[0], mypokemon, _attacks_effectiveness_table, _replay_table)
						flag_attack_select = True
					else:
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
						if (len(input_attack) == 2 and input_attack[0].lower() == "info"):
							mypokemon.att[int(input_attack[1])-1].print_info_attack()
							delay_print('\n\nElija un ataque (o \"info <#>\" para ver la informacion del ataque):')
							mypokemon.show_attacks()
							continue

						elif(len(input_attack) == 1 and int(input_attack[0]) >= 0 and int(input_attack[0])<=4):
							mypokemon.do_attack(input_attack[0], otherpokemon, _attacks_effectiveness_table, _replay_table)
							flag_attack_select = True
						else:
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



			input()
			turn +=1

		# Anunciando al ganador
		# pygame.mixer.music.stop()
		# pygame.mixer.music.load("145 - ending.mp3")
		# pygame.mixer.music.play()
		#battle_end_screen(mypokemon, otherpokemon)


	else:
		print("[ERROR] | Elección errónea. Saliendo del programa\n\n")

