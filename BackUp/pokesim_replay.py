from datetime import datetime
from tabulate import tabulate
from pokesim import delay_print



# Clase ReplayInfo: contiene toda la información necesaria para guardar una entrada de un replayInfo a la base de datos
class ReplayInfo():
	from datetime import datetime
	def __init__(self, replayID, pokemonID):
		self.replayID = replayID
		self.time = datetime.now().strftime('%Y-%m-%d %H:%M:%S').strip()
		self.pokemonID = pokemonID
		self.attackID = ''
		self.status_prev = ''
		self.status_post = ''
		self.canAttack = ''
		self.attackHit = False
		self.attackHasEffect = True
		self.attackWasCrit = False
		self.attackEffectiveness = '-'
		self.attackDmg = 0
		self.attackSecEffect = 'None'
		self.status_self_dmg = 0


# Clase para reproducir un replay. Se carga con la info de la base de datos.
class LoadReplayInfo():
	def __init__(self,*pv):
		self.replayID = pv[0][0]
		self.time = pv[0][1]
		self.pokemonID = pv[0][2]
		self.attackID = pv[0][3]
		self.status_prev = pv[0][4]
		self.status_post = pv[0][5]
		self.canAttack = pv[0][6]
		self.attackHit = pv[0][7]
		self.attackHasEffect = pv[0][8]
		self.attackWasCrit = pv[0][9]
		self.attackEffectiveness = pv[0][10]
		self.attackDmg = pv[0][11]
		self.attackSecEffect = pv[0][12]
		self.status_self_dmg = pv[0][13]

		self.pokemon_name = ''
		self.attack_name = ''


	def pokemon_do_attack(self, pk_attacking, pk_defending, qry_attack_list):
		
		self.attack_name = qry_attack_list[self.attackID-1][1]
		
		self.check_status(pk_attacking)

		# if(self.status_post != "ok" and self.status_self_dmg != 0):
		# 	if(pk_attacking._identifier == 1):
		# 		pk_attacking.print_health_bars()
		# 		pk_defending.print_health_bars()
		# 	else:
		# 		pk_defending.print_health_bars()
		# 		pk_attacking.print_health_bars()


		if(self.canAttack == True):
			if(self.attackHit == True):
				delay_print("\n{} used {}!\n".format(pk_attacking.name, self.attack_name))
				if(self.attackHasEffect == False):
					delay_print("It doesn't have effect...")
				elif(self.attackWasCrit == True):
					delay_print("It's a critical hit!")
				if(self.attackEffectiveness == "not effective"):
					delay_print("It's not very effective...")
				elif(self.attackEffectiveness == "very effective"):
					delay_print("It's super effective!")

				pk_defending.curr_hp -= self.attackDmg
				pk_defending.curr_hp = 0 if pk_defending.curr_hp < 0 else pk_defending.curr_hp

				pk_defending.calculate_health_bars()

				self.check_attack_secEffect(pk_defending)


			else:
				delay_print("\n{}'s {} has failed...\n".format(pk_attacking.name, self.attack_name))


	def check_attack_secEffect(self, pk_defending):
		if(self.attackSecEffect == "paralized"):
			delay_print("{} is now paralyzed!".format(pk_defending.name))

		elif(self.attackSecEffect == "poisoned"):
			delay_print("{} is now poisoned!".format(pk_defending.name))

		elif(self.attackSecEffect == "burned"):
			delay_print("{} is now burned!".format(pk_defending.name))

		elif(self.attackSecEffect == "frozen"):
			delay_print("{} is now frozen solid!".format(pk_defending.name))

		elif(self.attackSecEffect == "confused"):
			delay_print("{} is now confused!".format(pk_defending.name))

		elif(self.attackSecEffect == "sleep"):
			delay_print("{} fall sleep".format(pk_defending.name))


	def check_status(self, pk_attacking):

		if(self.status_prev == "ok"):
			return

		elif(self.status_prev == "sleep"):
			delay_print("\n{} is fast asleep...".format(pk_attacking.name))
			if(self.status_post != "sleep"):
				delay_print("\n{} woke up!".format(pk_attacking.name))

		elif(self.status_prev == "paralyzed" and self.canAttack == False):
			delay_print("\n{} is fully paralyzed.".format(pk_attacking.name))

		elif(self.status_prev == "confused"):
			delay_print("\n{} is confused...".format(pk_attacking.name))
			if(self.status_post != "confused"):
				delay_print("\n{} is no more confused!".format(pk_attacking.name))
			if(self.canAttack == False):
				delay_print("It hurts itself in its confusion!")
				pk_attacking.curr_hp -= self.status_self_dmg
				pk_attacking.curr_hp = 0 if pk_attacking.curr_hp < 0 else pk_attacking.curr_hp
				pk_attacking.calculate_health_bars()

		elif(self.status_prev == "poisoned"):
			delay_print("\n{} is poisoned...".format(pk_attacking.name))
			pk_attacking.curr_hp -= self.status_self_dmg
			pk_attacking.curr_hp = 0 if pk_attacking.curr_hp < 0 else pk_attacking.curr_hp
			pk_attacking.calculate_health_bars()

		elif(self.status_prev == "burned"):
			delay_print("\n{} is burned...".format(pk_attacking.name))
			pk_attacking.curr_hp -= self.status_self_dmg
			pk_attacking.curr_hp = 0 if pk_attacking.curr_hp < 0 else pk_attacking.curr_hp
			pk_attacking.calculate_health_bars()

		elif(self.status_prev == "frozen"):
			delay_print(pk_attacking.name, " is frozen solid...")
			if(self.status_post != "frozen"):
				delay_print(pk_attacking.name," is no more frozen!")


def create_replay_entrance(cursor, connection):
	cursor.execute('''INSERT INTO replay (time) 
  						VALUES (CURRENT_TIMESTAMP);''')
	connection.commit()
	#print("[DEBUG] | Se agregó una entrada a replays")


def show_replay_list(cursor):
	qry_res = []
	replay_list = []
	aux = []
	cursor.execute('''	SELECT DISTINCT replay.replayID, replay.time, pokemon.name 
						FROM replay, replayInfo 
						JOIN pokemon ON replayInfo.pokemonID = pokemon.pokemonID  
						WHERE replay.replayID = replayInfo.replayID
						ORDER BY replay.replayID DESC''')
	qry_res = cursor.fetchall();

	if(qry_res == ()):
		return qry_res

	for n in range(int(len(qry_res)/2)):
		aux = []
		aux.append(qry_res[n*2][0])
		aux.append(qry_res[n*2][1].strftime("%Y-%b-%d %H:%M:%S"))
		aux.append(qry_res[n*2][2])
		aux.append('')
		aux.append(qry_res[n*2+1][2])
		replay_list.append(aux)
	print(tabulate(replay_list, headers=['replayID', 'Datetime', 'Pokemon1','vs', 'Pokemon2'], tablefmt='fancy_grid'))		

	return qry_res[0][0]


def detele_replay(cursor, connection, rply_num):

	cursor.execute('''UPDATE hallOfFame SET replayID = NULL WHERE replayID = {}'''.format(rply_num))
	#print("[INFO] | Entradas de hallOfFame con replayID {} borradas".format(rply_num))

	cursor.execute('''DELETE FROM replayInfo WHERE replayID = {}'''.format(rply_num))
	print("[INFO] | Entradas de replayInfo con replayID {} borradas".format(rply_num))

	cursor.execute('''DELETE FROM replay WHERE replayID = {}'''.format(rply_num))
	print("[INFO] | Entradas de replay con replayID {} borradas".format(rply_num))
	connection.commit()


def delete_replay_all(cursor, connection):

	cursor.execute('''UPDATE hallOfFame SET replayID = NULL''')
	#print("[INFO] | Entradas de hallOfFame borradas")

	cursor.execute('''DELETE FROM replayInfo''')
	print("[INFO] | Entradas de replayInfo borradas")

	cursor.execute('''DELETE FROM replay''')
	print("[INFO] | Entradas de replay borradas")
	connection.commit()


def replay_pokemon_do_attack(pk_attacking, pk_defending, tur):

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
