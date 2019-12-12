def load_csv(csv_route):
	f = open(csv_route)
	for line in f.readlines():
	    datos.append(line.split(','))

	for n in range(len(datos)):
	    for k in range(len(datos[n])):
	        datos[n][k]=datos[n][k].rstrip().lstrip()
	return datos

def load_csv2(csv_route, datos):
	datos=[]
	f = open(csv_route)
	for line in f.readlines():
	    datos.append(line.split(','))

	for n in range(len(datos)):
	    for k in range(len(datos[n])):
	        datos[n][k]=datos[n][k].rstrip().lstrip()
	return datos

def load_cols_name(columna):
	cols = []
	for n in range(len(columna)):
		cols.append("{}".format(columna[n][0].rstrip().lstrip()))
	return cols



if __name__ == '__main__':
	import MySQLdb as motorDB
	conn = motorDB.connect(host='localhost', user='guest', password='guest')
	conn.autocommit(True)
	cur = conn.cursor()

	cur.execute("DROP DATABASE if exists myPokemonDB")
	cur.execute("CREATE DATABASE myPokemonDB")
	print("\n[INFO] | Base de datos \"myPokemonDB\" creada")

	cur.execute("USE myPokemonDB")
	print("[INFO] | Usando base de datos myPokemonDB")

	print("[INFO] | Dropeando tablas si existen")
	cur.execute("DROP TABLE if exists pokemon")
	cur.execute("DROP TABLE if exists type")
	cur.execute("DROP TABLE if exists dmgType")
	cur.execute("DROP TABLE if exists attack")
	cur.execute("DROP TABLE if exists secEffect")
	cur.execute("DROP TABLE if exists attackEffectiveness")
	cur.execute("DROP TABLE if exists replay")
	cur.execute("DROP TABLE if exists replayInfo")
	cur.execute("DROP TABLE if exists hallOfFame")

	cur.execute("DROP TABLE if exists pokemon_type")
	cur.execute("DROP TABLE if exists pokemon_attack")
	cur.execute("DROP TABLE if exists attack_secEffect")

	#Creando tablas
	print("[INFO] | Creando tabla \"pokemon\"")
	cur.execute('''CREATE TABLE if not exists pokemon
		(	pokemonID int primary key NOT NULL AUTO_INCREMENT,
			pokenum int NOT NULL,
			name varchar(20) NOT NULL, 
			HP int NOT NULL,
			STR int NOT NULL,
			DEF int NOT NULL,
			SPC int NOT NULL,
			SPD int NOT NULL)''')
	print("[INFO] | Tabla \"pokemon\" creada")


	print("[INFO] | Creando tabla \"type\"")
	cur.execute('''CREATE TABLE if not exists type
		(	typeID	int primary key NOT NULL AUTO_INCREMENT,
			name varchar(20) NOT NULL,
			dmgTypeID int NOT NULL	)''')
	print("[INFO] | Tabla \"type\" creada")


	print("[INFO] | Creando tabla \"attack\"")
	cur.execute(''' CREATE TABLE if not exists attack
		(	attackID int primary key NOT NULL AUTO_INCREMENT,
			name varchar(20) NOT NULL,
			PWR	int NOT NULL,
			ACC int NOT NULL,
			PP int NOT NULL,
			PRIOR int NOT NULL,
			typeID int NOT NULL,
			description varchar(500))''')
	print("[INFO] | Tabla \"attack\" creada")


	print("[INFO] | Creando tabla \"dmgType\"")
	cur.execute('''CREATE TABLE if not exists dmgType
		(	dmgTypeID int primary key NOT NULL AUTO_INCREMENT,
			name varchar(10) NOT NULL	) ''')
	print("[INFO] | Tabla \"dmgType\" creada")


	print("[INFO] | Creando tabla \"secEffect\"")
	cur.execute('''CREATE TABLE if not exists secEffect
		(	secEffectID int primary key NOT NULL AUTO_INCREMENT,
			name varchar(30) NOT NULL)''')
	print("[INFO] | Tabla \"secEffect\" creada")


	print("[INFO] | Creando tabla \"pokemon_type\"")
	cur.execute('''CREATE TABLE if not exists pokemon_type
		(	pokemonID int NOT NULL,
			typeID int NOT NULL	)''')
	print("[INFO] | Tabla \"pokemon_type\" creada")


	print("[INFO] | Creando tabla \"pokemon_attack\"")
	cur.execute('''CREATE TABLE if not exists pokemon_attack
		(	pokemonID int NOT NULL,
			attackID int NOT NULL)	''')
	print("[INFO] | Tabla \"pokemon_attack\" creada")


	print("[INFO] | Creando tabla \"attack_secEffect\"")
	cur.execute('''CREATE TABLE if not exists attack_secEffect
		(	attackID int NOT NULL,
			secEffectID int NOT NULL,
			prob float NOT NULL)	''')
	print("[INFO] | Tabla \"attack_secEffect\" creada")


	print("[INFO] | Creando tabla \"attackEffectiveness\"")
	cur.execute('''CREATE TABLE if not exists attackEffectiveness
		(	attackTypeID int NOT NULL,
			pokemonTypeID int NOT NULL,
			multiplier float NOT NULL)	''')
	print("[INFO] | Tabla \"attackEffectiveness\" creada")


	print("[INFO] | Creando tabla \"replay\"")
	cur.execute('''CREATE TABLE if not exists replay
		(	replayID int primary key NOT NULL AUTO_INCREMENT,
			time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP)	''')
	print("[INFO] | Tabla \"replay\" creada")


	print("[INFO] | Creando tabla \"replayInfo\"")
	cur.execute('''CREATE TABLE if not exists replayInfo
		(	replayID int NOT NULL,
			time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
			pokemonID int NOT NULL,
			attackID int DEFAULT NULL,
			statusPrev varchar(20) DEFAULT NULL,
			statusPost varchar(20) DEFAULT NULL,
			canAttack boolean DEFAULT NULL,
			attackHit boolean DEFAULT NULL,
			attackHasEffect boolean DEFAULT NULL,
			attackWasCrit boolean DEFAULT NULL,
			attackEffectiveness varchar(20) DEFAULT NULL,
			attackDmg int DEFAULT NULL,
			attackSecEffect varchar(20) DEFAULT NULL,
			statusSelfDmg int DEFAULT NULL		)	''')
	print("[INFO] | Tabla \"replayInfo\" creada")


	print("[INFO] | Creando tabla \"hallOfFame\"")
	cur.execute('''CREATE TABLE if not exists hallOfFame
				(	time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
					pokemonID int NOT NULL,
					attackID1 int DEFAULT NULL,
					attackID2 int DEFAULT NULL,
					attackID3 int DEFAULT NULL,
					attackID4 int DEFAULT NULL,
					replayID int DEFAULT NULL)
				''')

	print("[INFO] | Tabla \"hallOfFame\" creada")




	#Estableciendo Foreign keys
	print("[INFO] | Estableciendo Foreign Keys")
	cur.execute('''ALTER TABLE type ADD CONSTRAINT FK_type_dmgType
					FOREIGN KEY (dmgTypeID) REFERENCES dmgType(dmgTypeID)
					ON DELETE NO ACTION ON UPDATE NO ACTION''')

	cur.execute('''ALTER TABLE attackEffectiveness ADD CONSTRAINT FK_attackType
					FOREIGN KEY (attackTypeID) REFERENCES type(typeID)
					ON DELETE NO ACTION ON UPDATE NO ACTION''')

	cur.execute('''ALTER TABLE attackEffectiveness ADD CONSTRAINT FK_pokemonType
					FOREIGN KEY (pokemonTypeID) REFERENCES type(typeID)
					ON DELETE NO ACTION ON UPDATE NO ACTION''')

	cur.execute('''ALTER TABLE pokemon_type ADD CONSTRAINT FK_pok_type_pokemon
					FOREIGN KEY (pokemonID) REFERENCES pokemon(pokemonID)
					ON DELETE NO ACTION ON UPDATE NO ACTION''')

	cur.execute('''ALTER TABLE pokemon_type ADD CONSTRAINT FK_pok_type_type
					FOREIGN KEY (typeID) REFERENCES type(typeID)
					ON DELETE NO ACTION ON UPDATE NO ACTION''')

	cur.execute('''ALTER TABLE pokemon_attack ADD CONSTRAINT FK_poke_att_pokemon
					FOREIGN KEY (pokemonID) REFERENCES pokemon(pokemonID)
					ON DELETE NO ACTION ON UPDATE NO ACTION''')

	cur.execute('''ALTER TABLE pokemon_attack ADD CONSTRAINT FK_poke_att_attack
					FOREIGN KEY (attackID) REFERENCES attack(attackID)
					ON DELETE NO ACTION ON UPDATE NO ACTION''')

	cur.execute('''ALTER TABLE attack ADD CONSTRAINT FK_attack_type
					FOREIGN KEY (typeID) REFERENCES type(typeID)
					ON DELETE NO ACTION ON UPDATE NO ACTION''')

	cur.execute('''ALTER TABLE attack_secEffect ADD CONSTRAINT FK_att_seff_attack
					FOREIGN KEY (attackID) REFERENCES attack(attackID)
					ON DELETE NO ACTION ON UPDATE NO ACTION''')

	cur.execute('''ALTER TABLE attack_secEffect ADD CONSTRAINT FK_att_seff_seff
					FOREIGN KEY (secEffectID) REFERENCES secEffect(secEffectID)
					ON DELETE NO ACTION ON UPDATE NO ACTION''')

	cur.execute('''ALTER TABLE replayInfo ADD CONSTRAINT FK_replayInfo_replay
					FOREIGN KEY (replayID) REFERENCES replay(replayID)
					ON DELETE NO ACTION ON UPDATE NO ACTION''')

	cur.execute('''ALTER TABLE replayInfo ADD CONSTRAINT FK_replayInfo_pokemon
					FOREIGN KEY (pokemonID) REFERENCES pokemon(pokemonID)
					ON DELETE NO ACTION ON UPDATE NO ACTION''')

	cur.execute('''ALTER TABLE replayInfo ADD CONSTRAINT FK_replayInfo_attack
					FOREIGN KEY (attackID) REFERENCES attack(attackID)
					ON DELETE NO ACTION ON UPDATE NO ACTION''')

	cur.execute('''ALTER TABLE hallOfFame ADD CONSTRAINT FK_hallOfFame_pokemonID
					FOREIGN KEY (pokemonID) REFERENCES pokemon(pokemonID)
					ON DELETE NO ACTION ON UPDATE NO ACTION	''')

	cur.execute('''ALTER TABLE hallOfFame ADD CONSTRAINT FK_hallOfFame_attackID1
					FOREIGN KEY (attackID1) REFERENCES attack(attackID)
					ON DELETE NO ACTION ON UPDATE NO ACTION	''')

	cur.execute('''ALTER TABLE hallOfFame ADD CONSTRAINT FK_hallOfFame_attackID2
					FOREIGN KEY (attackID2) REFERENCES attack(attackID)
					ON DELETE NO ACTION ON UPDATE NO ACTION	''')

	cur.execute('''ALTER TABLE hallOfFame ADD CONSTRAINT FK_hallOfFame_attackID3
					FOREIGN KEY (attackID3) REFERENCES attack(attackID)
					ON DELETE NO ACTION ON UPDATE NO ACTION	''')

	cur.execute('''ALTER TABLE hallOfFame ADD CONSTRAINT FK_hallOfFame_attackID4
					FOREIGN KEY (attackID4) REFERENCES attack(attackID)
					ON DELETE NO ACTION ON UPDATE NO ACTION	''')

	cur.execute('''ALTER TABLE hallOfFame ADD CONSTRAINT FK_hallOfFame_replayID
					FOREIGN KEY (replayID) REFERENCES replay(replayID)
					ON DELETE NO ACTION ON UPDATE NO ACTION	''')

	print("[INFO] | Relaciones (foreign keys) establecidas")

	datos = []
	aux = []

	### CARGO LOS DATOS DE LA TABLA pokemon DESDE CSV ###
	print("[INFO] | Cargando datos de la tabla \"pokemon\"")
	datos = load_csv("pokemon.csv")
	cur.execute("SHOW COLUMNS FROM pokemon")
	aux = cur.fetchall();
	cols = load_cols_name(aux)
	for n in datos:
		cur.execute('''INSERT INTO pokemon ({}, {}, {}, {}, {}, {}, {}) 
						VALUES ({}, "{}", {}, {}, {}, {}, {});
					'''.format(cols[1],cols[2],cols[3],cols[4],cols[5],cols[6],cols[7],n[0],n[1],n[2],n[3],n[4],n[5],n[6]))
	conn.commit()
	print("[INFO] | Datos de la tabla \"pokemon\" insertados")

	### CARGO LOS DATOS DE LA TABLA dmgType DESDE CSV ###
	datos = []
	aux = []
	print("[INFO] | Cargando datos de la tabla \"dmgType\"")
	datos = load_csv("dmgTypes.csv")
	cur.execute("SHOW COLUMNS FROM dmgType")
	aux = cur.fetchall();
	cols = load_cols_name(aux)
	for n in datos:
		cur.execute('''INSERT INTO dmgType ({}) 
						VALUES ("{}");
					'''.format(cols[1],n[1]))
	conn.commit()
	print("[INFO] | Datos de la tabla \"dmgType\" insertados")


	### CARGO LOS DATOS DE LA TABLA type DESDE CSV ###
	print("[INFO] | Cargando datos de la tabla \"type\"")
	datos=[];
	datos_aux=[];
	datos_aux = load_csv2("dmgTypes.csv",datos_aux);
	datos = load_csv2("types.csv",datos);
	for n in datos:
		if n[2]==datos_aux[0][1]:
			n[2] = datos_aux[0][0];
		elif n[2] == datos_aux[1][1]:
			n[2] = datos_aux[1][0];
	cur.execute("SHOW COLUMNS FROM type")
	aux = cur.fetchall();
	cols = load_cols_name(aux)
	for n in datos:
		cur.execute('''INSERT INTO type ({},{}) 
						VALUES ("{}",{});
					'''.format(cols[1],cols[2],n[1],n[2]))
	conn.commit()
	print("[INFO] | Datos de la tabla \"type\" insertados")



	### CRGO LA TABLA INTERMEDIA pokemon_type ###
	print("[INFO] | Cargando datos de la tabla \"pokemon_type\"")
	datos=[]
	pokemoninfo = []
	typeinfo = []
	cur.execute("SELECT pokemonID, name FROM pokemon")
	pokemoninfo = cur.fetchall();
	cur.execute("SELECT typeID, name FROM type")
	typeinfo = cur.fetchall();
	datos=load_csv2("pokemon_type.csv", datos);
	i=0
	for n in datos:
		for m in pokemoninfo:
			if m[1]==n[1]:
				datos[i][1]=m[0];
				break
		for m in typeinfo:
			if m[1]==n[2]:
				datos[i][2]=m[0];
				break
		i+=1;
	cur.execute("SHOW COLUMNS FROM pokemon_type")
	aux = cur.fetchall();
	cols = load_cols_name(aux)
	for n in datos:
		cur.execute('''INSERT INTO pokemon_type ({},{}) 
						VALUES ("{}",{});
					'''.format(cols[0],cols[1],n[1],n[2]))
	conn.commit()
	print("[INFO] | Datos de la tabla \"pokemon_type\" insertados")


	### CARGO LA TABLA secEffect ###
	print("[INFO] | Cargando datos de la tabla \"secEffect\"")
	datos = load_csv2("secEffect.csv", datos);
	cur.execute("SHOW COLUMNS FROM secEffect")
	aux = cur.fetchall();
	cols = load_cols_name(aux)
	for n in datos:
		cur.execute('''INSERT INTO secEffect ({}) 
						VALUES ("{}");
					'''.format(cols[1],n[0]))
	conn.commit()
	print("[INFO] | Datos de la tabla \"secEffect\" insertados")

	### CARGO LA TABLA attack ###
	print("[INFO] | Cargando datos de la tabla \"attack\"")
	cur.execute("SELECT typeID, name FROM type")
	tipo = cur.fetchall();
	datos = load_csv2("attacks.csv", datos)
	i=0;
	for ataque in datos:
		for t in tipo:
			if t[1]==ataque[5]:
				datos[i][5]=t[0]
				break
		i+=1
	cur.execute("SHOW COLUMNS FROM attack");
	aux = cur.fetchall();
	cols = load_cols_name(aux)
	for n in datos:
		cur.execute('''INSERT INTO attack ({},{},{},{},{},{},{}) 
 						VALUES ("{}",{},{},{},{},{},"{}");
 					'''.format(cols[1],cols[2],cols[3],cols[4],cols[5],cols[6],cols[7],n[0],n[1],n[2],n[3],n[4],n[5],n[6]))
	conn.commit()
	print("[INFO] | Datos de la tabla \"attack\" insertados")


	## CARGO LA TABLA pokemon_attack ###
	print("[INFO] | Cargando datos de la tabla \"pokemon_attack\"")
	pokemoninfo = []
	attackinfo = []
	cur.execute("SELECT pokemonID, name FROM pokemon")
	pokemoninfo = cur.fetchall()
	cur.execute("SELECT attackID, name FROM attack")
	attackinfo = cur.fetchall()
	datos = load_csv2("pokemon_ataques.csv",datos)
	i=0
	for pa in datos:
		for p in pokemoninfo:
			if pa[0] == p[1]:
				datos[i][0] = p[0]
				break
		for a in attackinfo:
			if pa[1] == a[1]:
				datos[i][1] = a[0];
				break
		i+=1
	cur.execute("SHOW COLUMNS FROM pokemon_attack");
	aux = cur.fetchall();
	cols = load_cols_name(aux)
	for n in datos:
		cur.execute('''INSERT INTO pokemon_attack ({},{}) 
 						VALUES ({},{});
 					'''.format(cols[0],cols[1],n[0],n[1]))
	conn.commit()
	print("[INFO] | Datos de la tabla \"pokemon_attack\" insertados")

	### CARGO LA TABLA attack_secEffect ###
	print("[INFO] | Cargando datos de la tabla \"attack_secEffect\"")
	attackinfo = []
	secEffectinfo = []
	cur.execute("SELECT attackID, name FROM attack")
	attackinfo = cur.fetchall()
	cur.execute("SELECT secEffectID, name FROM secEffect")
	secEffectinfo = cur.fetchall()
	datos = load_csv2("ataque_efecto_sec.csv",datos)
	i = 0
	for at_seceff in datos:
		for at in attackinfo:
			if at[1] == at_seceff[0]:
				datos[i][0] = at[0]
				break
		for seceff in secEffectinfo:
			if seceff[1] == at_seceff[1]:
				datos[i][1] = seceff[0]
				break
		i+=1
	cur.execute("SHOW COLUMNS FROM attack_secEffect");
	aux = cur.fetchall();
	cols = load_cols_name(aux)
	for n in datos:
		cur.execute('''INSERT INTO attack_secEffect ({},{},{}) 
 						VALUES ({},{},{});
 					'''.format(cols[0],cols[1],cols[2],n[0],n[1],n[2]))
	conn.commit()	
	print("[INFO] | Datos de la tabla \"attack_secEffect\" insertados")


	### CARGO LA TABLA attackEffectiveness ###
	print("[INFO] | Cargando datos de la tabla \"attackEffectiveness\"")
	qry = []
	cur.execute("SELECT typeID, name FROM type")
	qry = cur.fetchall()

	datos = load_csv2("attacks_effectiveness.csv", datos)
	i = 0
	for d in datos:
		for t in qry:
			if (d[0] == t[1]):
				datos[i][0] = t[0]
			if (d[1] == t[1]):
				datos[i][1] = t[0]
		datos[i][2] = float(datos[i][2])
		i+=1
	cur.execute("SHOW COLUMNS FROM attackEffectiveness");
	aux = cur.fetchall();
	cols = load_cols_name(aux)
	
	for n in datos:
		cur.execute('''INSERT INTO attackEffectiveness ({},{},{}) 
 						VALUES ({},{},{});
 					'''.format(cols[0],cols[1],cols[2],n[0],n[1],n[2]))
	conn.commit()	
	print("[INFO] | Datos de la tabla \"attackEffectiveness\" insertados")

	print("[INFO] | Database ready")






	












