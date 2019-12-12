select pokemon.name, attack.name, attack.attackID, attack_secEffect.prob from pokemon 
join pokemon_attack on pokemon.pokemonID = pokemon_attack.pokemonID  
join attack on pokemon_attack.attackID = attack.attackID 
join attack_secEffect on attack.attackID = attack_secEffect.attackID 
join secEffect on attack_secEffect.secEffectID = secEffect.secEffectID
where secEffect.name like "cong%";