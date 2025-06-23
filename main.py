"""
Script interativo para consulta de Pokémon.
Digite comandos como: query_pokemon(25), query_pokemon('pikachu', traduzir=True), etc.
Para sair, digite 'exit' ou 'sair'.
"""
from Pokemon.pesquisa_poekmon import query_pokemon, configurar_saida_simplificada

def main():
    print("=== Modo Interativo do Buscador de Pokémon ===")
    print("Digite comandos como: query_pokemon(25), query_pokemon('pikachu', traduzir=True), etc.")
    print("Para sair, digite 'exit' ou 'sair'.\n")
    while True:
        try:
            entrada = input('>>> ')
            if entrada.strip().lower() in ['exit', 'sair', 'quit']:
                print("Saindo...")
                break
            if entrada.strip().startswith('query_pokemon'):
                # Executa o comando digitado
                resultado = eval(entrada, {'query_pokemon': query_pokemon, 'configurar_saida_simplificada': configurar_saida_simplificada})
            else:
                print("Comando não reconhecido. Use query_pokemon(...)")
        except Exception as e:
            print(f"Erro ao executar comando: {e}")

if __name__ == "__main__":
    main()
