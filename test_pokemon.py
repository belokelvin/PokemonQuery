from Pokemon.pesquisa_poekmon import query_pokemon

def rodar_testes():
    print("Testes Automatizados do Buscador de Pokémon\n")
    casos = [
        ("query_pokemon(132, field='id')", lambda: query_pokemon(132, field="id")),
        ("query_pokemon('132', field='id')", lambda: query_pokemon("132", field="id")),
        ("query_pokemon(133)", lambda: query_pokemon(133)),
        ("query_pokemon('squirtle')", lambda: query_pokemon("squirtle")),
        ("query_pokemon('dito')", lambda: query_pokemon("dito")),
        ("query_pokemon(40, field='weight')", lambda: query_pokemon(40, field="weight")),
        ("query_pokemon('40', field='weight')", lambda: query_pokemon("40", field="weight")),
    ]
    for nome, func in casos:
        print(f"--- {nome} ---")
        try:
            resultado = func()
            if resultado is None or (isinstance(resultado, dict) and resultado.get('erro')):
                print("[ERRO]", resultado)
            else:
                print("[SUCESSO]", resultado)
        except Exception as e:
            print(f"[EXCEPTION] {e}")
        print()

if __name__ == "__main__":
    rodar_testes() 