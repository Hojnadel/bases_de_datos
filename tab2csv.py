import MySQLdb as m
import datetime
import contextlib
import csv
#if __name__ == '__main__':


#QUERIES
#select p.numero_pokedex, p.nombre, eb.ps, eb.ataque, eb.defensa, eb.especial, eb.velocidad from pokemon p, estadisticas_base eb where p.numero_pokedex = eb.numero_pokedex;
#select tipo.id_tipo,tipo.nombre, tipo_ataque.tipo   from tipo, tipo_ataque where tipo.id_tipo_ataque = tipo_ataque.id_tipo_ataque order by tipo.id_tipo;
#select * from tipo_ataque;
#select pokemon.numero_pokedex, pokemon.nombre, tipo.nombre  from pokemon, tipo, pokemon_tipo where pokemon.numero_pokedex = pokemon_tipo.numero_pokedex  and tipo.id_tipo = pokemon_tipo.id_tipo order by numero_pokedex;
#select m.nombre, m.potencia, m.precision_mov, m.pp, m.prioridad, t.nombre, m.descripcion from movimiento m, tipo t where m.id_tipo  = t.id_tipo
#select distinct pokemon.nombre , movimiento.nombre from pokemon, movimiento, pokemon_movimiento_forma where pokemon.numero_pokedex = pokemon_movimiento_forma.numero_pokedex and movimiento.id_movimiento = pokemon_movimiento_forma.id_movimiento
#select movimiento.nombre, efecto_secundario.efecto_secundario, movimiento_efecto_secundario.probabilidad from movimiento, efecto_secundario, movimiento_efecto_secundario where movimiento.id_movimiento = movimiento_efecto_secundario.id_movimiento and efecto_secundario.id_efecto_secundario  = movimiento_efecto_secundario.id_efecto_secundario;

OUTPUT_FILE_NAME = "attaks"
SQL_DB = "pokemondb"
SQL_QUERY = '''SELECT m.nombre, m.potencia, m.precision_mov, m.pp, m.prioridad, t.nombre, m.descripcion from movimiento m, tipo t where m.id_tipo  = t.id_tipo'''

conn = m.connect(host='localhost', user='guest', password='guest')
cur = conn.cursor()
cur.execute("USE {}".format(SQL_DB))

cur.execute(SQL_QUERY)
results = cur.fetchall()

output_file = '{}.csv'.format(OUTPUT_FILE_NAME)
with open(output_file, 'w', newline='') as csvfile:
    # http://stackoverflow.com/a/17725590/2958070 about lineterminator
    csv_writer = csv.writer(csvfile, lineterminator='\n')
    csv_writer.writerows(results)