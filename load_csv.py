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


if __name__ == '__main__':

	### CRGO LA TABLA INTERMEDIA pokemon_type ###
datos = load_csv2("secEffect.csv", datos);
cur.execute("SHOW COLUMNS FROM secEffect")
aux = cur.fetchall();
cols = load_cols_name(aux)
for n in datos:
	cur.execute('''INSERT INTO secEffect ({}) 
					VALUES ("{}");
				'''.format(cols[1],n[0]))
conn.commit()
