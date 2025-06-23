import requests 

class ClasseBuscaIdNome:
    def __init__(self):
        pass

    def _fun_buscar(self, var_entrada):
        """
        
        """
        try:
            var_strUrl = "https://pokeapi.co/api/v2/pokemon/"
            var_strParametro = str(var_entrada).strip().lower()
            var_strResposta = requests.get(f"{var_strUrl}{var_strParametro}")

            if var_strResposta.status_code != 200:
                return None

            return var_strResposta.json()
        
        except Exception as e:
            print(f"Erro na busca: {e}")
            return None
    
    