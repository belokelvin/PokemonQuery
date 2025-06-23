import requests
import json
import re
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import concurrent.futures
import sys


class CampoBusca(Enum):
    """
    Enumeração dos campos de busca disponíveis para Pokémon.
    Possibilita busca por ID, nome, peso ou altura.
    """
    ID = "id"
    NOME = "name"
    PESO = "weight"
    ALTURA = "height"


@dataclass
class InfoPokemon:
    """
    Estrutura de dados para armazenar informações detalhadas de um Pokémon.

    Atributos:
        var_intId (int): ID do Pokémon na Pokédex.
        var_strNome (str): Nome do Pokémon.
        var_intAltura (int): Altura em centimetros.
        var_intPeso (int): Peso em gramas.
        var_listTipos (List[str]): Lista de tipos do Pokémon.
        var_listHabilidades (List[str]): Lista de habilidades do Pokémon.
        var_dictStatus (Dict[str, int]): Estatísticas base do Pokémon.
        var_strSprite (str): URL do sprite principal do Pokémon.
    """
    var_intId: int
    var_strNome: str
    var_intAltura: int
    var_intPeso: int
    var_listTipos: List[str]
    var_listHabilidades: List[str]
    var_dictStatus: Dict[str, int]
    var_strSprite: str


class BuscadorPokemon:
    """
    Classe principal para busca de informações de Pokémon na PokéAPI.

    Permite buscar por ID, nome, peso ou altura, retornando dados estruturados.
    Utiliza paralelização para buscas por característica.
    """
    def __init__(self):
        """
        Inicializa o buscador com configurações padrão e URL base da PokéAPI.
        """
        self.var_strUrlBase = "https://pokeapi.co/api/v2/pokemon"
        self.var_intTimeout = 10
        self.var_boolSaidaSimplificada = False #Função extra para exibição mais simples

    def _validar_entrada(self, var_mixConsulta: Union[str, int]) -> tuple[str, str]:
        """
        Valida e determina o tipo de consulta (ID ou nome).

        Args:
            var_mixConsulta (str | int): Valor de busca informado pelo usuário.
        Returns:
            tuple: (valor_processado, campo_detectado)
        """
        var_strConsulta = str(var_mixConsulta).strip().lower()
        if var_strConsulta.isdigit():
            return var_strConsulta, CampoBusca.ID.value
        return var_strConsulta, CampoBusca.NOME.value

    def _fazer_requisicao_api(self, var_strEndpoint: str) -> Optional[Dict]:
        """
        Realiza requisição HTTP GET para a PokéAPI.

        Args:
            var_strEndpoint (str): URL do endpoint a ser consultado.
        Returns:
            dict | None: Dados retornados pela API ou None em caso de erro.
        """
        try:
            var_objResposta = requests.get(
                var_strEndpoint,
                timeout=self.var_intTimeout
            )
            if var_objResposta.status_code == 200:
                return var_objResposta.json()
            elif var_objResposta.status_code == 404:
                return None
            else:
                print(f"Erro na API: Status {var_objResposta.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão com a API: {str(e)}")
            return None

    def _buscar_por_caracteristica(self, var_strCampo: str, var_mixValor: Union[str, int]) -> List[Dict]:
        """
        Busca pokémons por característica (peso ou altura) em toda a Pokédex, de forma paralelizada.

        Args:
            var_strCampo (str): Campo de busca ('weight' ou 'height').
            var_mixValor (str | int): Valor numérico a ser buscado.
        Returns:
            List[dict]: Lista de pokémons que correspondem ao critério.
        """
        var_listResultados = []
        var_intValorBusca = int(str(var_mixValor).strip())
        print(f"Realizando busca por {var_strCampo} = {var_intValorBusca}")
        print("Buscando em todos os pokémons disponíveis na PokéAPI ...")
        
        # Descobre o total de pokémons disponíveis
        var_dictDados = self._fazer_requisicao_api(f"{self.var_strUrlBase}?limit=1")
        if not var_dictDados or "count" not in var_dictDados:
            print("Não foi possível obter o total de pokémons.")
            return []
        var_intTotal = var_dictDados["count"]
        print(f"Foram encontrados {var_intTotal} resultados para {var_strCampo} = {var_intValorBusca}")
        
        # Busca todos os nomes/ids de pokémons
        var_dictTodos = self._fazer_requisicao_api(f"{self.var_strUrlBase}?limit={var_intTotal}")
        if not var_dictTodos or "results" not in var_dictTodos:
            print("Não foi possível obter a lista de pokémons.")
            return []
        var_listPokemons = var_dictTodos["results"]

        def requisitar_e_filtrar(var_dictPokemon):
            var_dictDadosPokemon = self._fazer_requisicao_api(var_dictPokemon["url"])
            if var_dictDadosPokemon:
                if var_strCampo == "weight" and var_dictDadosPokemon.get("weight") == var_intValorBusca:
                    return var_dictDadosPokemon
                elif var_strCampo == "height" and var_dictDadosPokemon.get("height") == var_intValorBusca:
                    return var_dictDadosPokemon
            return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
            resultados = list(executor.map(requisitar_e_filtrar, var_listPokemons))
        var_listResultados = [poke for poke in resultados if poke is not None]
        return var_listResultados

    def _processar_dados_pokemon(self, var_dictDadosBrutos: Dict) -> InfoPokemon:
        """
        Processa os dados brutos da API e retorna um objeto InfoPokemon estruturado.

        Args:
            var_dictDadosBrutos (dict): Dados brutos retornados pela API.
        Returns:
            InfoPokemon: Objeto estruturado com informações do Pokémon.
        """
        var_listTipos = [
            var_dictTipo["type"]["name"]
            for var_dictTipo in var_dictDadosBrutos.get("types", [])
        ]
        var_listHabilidades = [
            var_dictHab["ability"]["name"]
            for var_dictHab in var_dictDadosBrutos.get("abilities", [])
        ]
        var_dictStatus = {
            var_dictStat["stat"]["name"]: var_dictStat["base_stat"]
            for var_dictStat in var_dictDadosBrutos.get("stats", [])
        }
        var_strSprite = var_dictDadosBrutos.get("sprites", {}).get("front_default", "")
        return InfoPokemon(
            var_intId=var_dictDadosBrutos.get("id", 0),
            var_strNome=var_dictDadosBrutos.get("name", ""),
            var_intAltura=var_dictDadosBrutos.get("height", 0),
            var_intPeso=var_dictDadosBrutos.get("weight", 0),
            var_listTipos=var_listTipos,
            var_listHabilidades=var_listHabilidades,
            var_dictStatus=var_dictStatus,
            var_strSprite=var_strSprite
        )

    def _formatar_saida(self, var_objInfoPokemon: InfoPokemon, var_boolSimplificado: bool = False) -> Dict:
        """
        Formata a saída dos dados do Pokémon para dicionário pronto para exibição ou consumo externo.

        Args:
            var_objInfoPokemon (InfoPokemon): Dados estruturados do Pokémon.
            var_boolSimplificado (bool): Se True, retorna versão simplificada.
        Returns:
            dict: Dados formatados para saída.
        """
        if var_boolSimplificado:
            return {
                "id": var_objInfoPokemon.var_intId,
                "nome": var_objInfoPokemon.var_strNome.title(),
                "tipos": var_objInfoPokemon.var_listTipos,
                "altura": f"{var_objInfoPokemon.var_intAltura / 10} m",
                "peso": f"{var_objInfoPokemon.var_intPeso / 10} kg"
            }
        return {
            "id": var_objInfoPokemon.var_intId,
            "nome": var_objInfoPokemon.var_strNome.title(),
            "altura": {
                "valor": var_objInfoPokemon.var_intAltura,
                "unidade": "decímetros",
                "metros": f"{var_objInfoPokemon.var_intAltura / 10} m"
            },
            "peso": {
                "valor": var_objInfoPokemon.var_intPeso,
                "unidade": "hectogramas",
                "quilogramas": f"{var_objInfoPokemon.var_intPeso / 10} kg"
            },
            "tipos": var_objInfoPokemon.var_listTipos,
            "habilidades": var_objInfoPokemon.var_listHabilidades,
            "status": var_objInfoPokemon.var_dictStatus,
            "sprite": var_objInfoPokemon.var_strSprite
        }

    def consultar_pokemon(self, var_mixConsulta: Union[str, int], var_strCampo: str = "auto") -> Dict:
        """
        Função principal para consulta de Pokémon por ID, nome, peso ou altura.

        Args:
            var_mixConsulta (str | int): Valor de busca (ID, nome ou valor numérico).
            var_strCampo (str): Campo de busca ("auto", "id", "name", "weight", "height").
        Returns:
            dict: Informações do Pokémon ou mensagem de erro.
        """
        try:
            var_strCampoBusca = var_strCampo.strip().lower()
            if var_strCampoBusca == "auto":
                var_strConsultaProcessada, var_strTipoDetectado = self._validar_entrada(var_mixConsulta)
                var_strCampoBusca = var_strTipoDetectado
            else:
                var_strConsultaProcessada = str(var_mixConsulta).strip().lower()
            if var_strCampoBusca in ["id", "name"]:
                var_dictDadosPokemon = self._fazer_requisicao_api(
                    f"{self.var_strUrlBase}/{var_strConsultaProcessada}"
                )
                if var_dictDadosPokemon is None:
                    return {
                        "erro": True,
                        "mensagem": f"Pokémon não encontrado para: {var_mixConsulta}",
                        "consulta": var_mixConsulta,
                        "campo": var_strCampoBusca
                    }
                var_objInfoPokemon = self._processar_dados_pokemon(var_dictDadosPokemon)
                return {
                    "sucesso": True,
                    "dados": self._formatar_saida(var_objInfoPokemon, self.var_boolSaidaSimplificada),
                    "consulta": var_mixConsulta,
                    "campo": var_strCampoBusca
                }
            elif var_strCampoBusca in ["weight", "height"]:
                if not str(var_mixConsulta).strip().isdigit():
                    return {
                        "erro": True,
                        "mensagem": f"Para busca por {var_strCampoBusca}, é necessário fornecer um valor numérico",
                        "consulta": var_mixConsulta,
                        "campo": var_strCampoBusca
                    }
                var_listResultados = self._buscar_por_caracteristica(var_strCampoBusca, var_mixConsulta)
                if not var_listResultados:
                    return {
                        "erro": True,
                        "mensagem": f"Nenhum Pokémon encontrado com {var_strCampoBusca} = {var_mixConsulta}",
                        "consulta": var_mixConsulta,
                        "campo": var_strCampoBusca
                    }
                var_objInfoPokemon = self._processar_dados_pokemon(var_listResultados[0])
                var_dictResposta = {
                    "sucesso": True,
                    "dados": self._formatar_saida(var_objInfoPokemon, self.var_boolSaidaSimplificada),
                    "consulta": var_mixConsulta,
                    "campo": var_strCampoBusca,
                    "total_encontrado": len(var_listResultados)
                }
                if len(var_listResultados) > 1:
                    var_dictResposta["outros_resultados"] = [
                        {
                            "id": pokemon["id"],
                            "nome": pokemon["name"].title()
                        }
                        for pokemon in var_listResultados[1:]
                    ]
                return var_dictResposta
            else:
                return {
                    "erro": True,
                    "mensagem": f"Campo de busca inválido: {var_strCampo}. Use: auto, id, name, weight, height",
                    "consulta": var_mixConsulta,
                    "campo": var_strCampo
                }
        except Exception as e:
            return {
                "erro": True,
                "mensagem": f"Erro interno: {str(e)}",
                "consulta": var_mixConsulta,
                "campo": var_strCampo
            }


# Instância global para uso direto
var_objBuscadorPokemon = BuscadorPokemon()



def query_pokemon(var_mixConsulta: Union[str, int], field: str = "auto", traduzir: bool = False) -> Dict:
    """
    Função global para consulta de Pokémon, compatível com o padrão Gamabot.

    Args:
        var_mixConsulta (str | int): Valor de busca (ID, nome ou valor numérico).
        field (str): Campo de busca ("auto", "id", "name", "weight", "height").
        traduzir (bool): Se True, retorna a resposta formatada em português. Se False (padrão), retorna o JSON bruto da PokéAPI.
    Returns:
        dict: Informações do Pokémon ou mensagem de erro.
    Observação:
        Se chamada a partir do main.py, imprime automaticamente o resultado formatado.
    """
    if not traduzir:
        # Busca direta, sem formatação
        campo = field.strip().lower() if field != 'auto' else None
        if campo in ["id", "name", None]:
            valor = str(var_mixConsulta).strip().lower() 
            raw_data = var_objBuscadorPokemon._fazer_requisicao_api(f"{var_objBuscadorPokemon.var_strUrlBase}/{valor}")
            print(json.dumps(raw_data, indent=2, ensure_ascii=False))
            return raw_data
        elif campo in ["weight", "height"]:
            lista = var_objBuscadorPokemon._buscar_por_caracteristica(campo, var_mixConsulta)
            print(json.dumps(lista, indent=2, ensure_ascii=False))
            return lista
        else:
            resultado = var_objBuscadorPokemon.consultar_pokemon(var_mixConsulta, field)
            print(json.dumps(resultado, indent=2, ensure_ascii=False))
            return resultado
    else:
        resultado = var_objBuscadorPokemon.consultar_pokemon(var_mixConsulta, field)
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
        return resultado

def configurar_saida_simplificada(var_boolHabilitado: bool):
    """
    Configura o formato de saída dos resultados (completo ou simplificado).

    Args:
        var_boolHabilitado (bool): True para saída simplificada, False para completa.
    """
    var_objBuscadorPokemon.var_boolSaidaSimplificada = var_boolHabilitado
