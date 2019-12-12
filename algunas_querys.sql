select pokemon.name, attack.name, attack.attackID, attack_secEffect.prob from pokemon 
join pokemon_attack on pokemon.pokemonID = pokemon_attack.pokemonID  
join attack on pokemon_attack.attackID = attack.attackID 
join attack_secEffect on attack.attackID = attack_secEffect.attackID 
join secEffect on attack_secEffect.secEffectID = secEffect.secEffectID
where secEffect.name like "cong%";


select hof.time, pk.name, att1.name, att2.name, hof.replayID 
from hallOfFame hof 
join pokemon pk on (hof.pokemonID = pk.pokemonID)
join attack att1 on (att1.attackID = hof.attackID1)
join attack att2 on (att2.attackID = hof.attackID2)
order by hof.time DESC;


join replay on (replay.replayID = hof.replayID)
