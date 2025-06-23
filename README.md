# Buscador de Pokémon - Consulta Inteligente via PokéAPI

Este projeto foi desenvolvido para atender a um desafio, permitindo consultar informações detalhadas de Pokémon em bases públicas, de forma simples, flexível e eficiente.

## O que eu implementei

Meu objetivo foi criar uma interface Python clara e robusta para buscar dados de Pokémon por ID, nome ou características (peso e altura), sendo facilmente escalonável. Todas as funções e estruturas foram pensadas para serem autoexplicativas, seguras e fáceis de usar, mesmo para quem não conhece a PokéAPI.

### query_pokemon

Esta é a função principal do projeto. Eu a implementei para ser o ponto de entrada universal para qualquer busca de Pokémon. Ela aceita tanto números (ID) quanto nomes, além de permitir buscas por características como peso e altura ("weight" e "height").

- **Por que existe?**
  - Para que qualquer sistema (ou pessoa) possa buscar informações de Pokémon de forma simples, sem se preocupar com detalhes técnicos da API.
- **Como funciona?**
  - Por padrão, retorna o JSON bruto da PokéAPI (em inglês), exatamente como a API responde. Isso facilita integrações e garante compatibilidade máxima com sistemas que já usam a PokéAPI.
  - Se você quiser a resposta formatada em português (com campos traduzidos e estruturados), basta passar o parâmetro `traduzir=True` (Essa é uma adição pessoal).
  - O resultado é sempre impresso no console quando chamado no main, facilitando testes e visualização.

#### Exemplos de uso:
```python
# Resposta padrão: JSON bruto da PokéAPI (em inglês)
query_pokemon(132, field="id")        # Ditto, resposta igual à API
query_pokemon("squirtle")             # Squirtle, resposta igual à API
query_pokemon(40, field="weight")     # Lista de pokémons com peso 40, resposta igual à API

# Resposta formatada em português
query_pokemon(132, field="id", traduzir=True)        # Ditto, campos em português
query_pokemon("squirtle", traduzir=True)             # Squirtle, campos em português
query_pokemon(40, field="weight", traduzir=True)     # Lista de pokémons com peso 40, campos em português
```

### configurar_saida_simplificada

Implementei esta função para dar flexibilidade na apresentação dos resultados formatados em português. Em alguns casos, você pode querer apenas as informações principais do Pokémon, sem detalhes como habilidades ou status.

- **Como funciona?**
  - Só afeta a resposta quando `traduzir=True`.
  - Basta chamar `configurar_saida_simplificada(True)` para ativar a saída simplificada.
  - Quando ativada, as buscas retornam apenas ID, nome, tipos, altura (em metros) e peso (em kg).
  - Para voltar à saída completa, basta chamar `configurar_saida_simplificada(False)`.

#### Exemplo:
```python
configurar_saida_simplificada(True)
query_pokemon("pikachu", traduzir=True)  # Retorna só o essencial em português
```

## Como funciona por dentro

- **Buscas por ID ou nome:**
  - A função detecta automaticamente se o valor é numérico (ID) ou texto (nome), faz a requisição à PokéAPI e retorna os dados estruturados.
- **Buscas por peso/altura:**
  - Eu implementei uma busca paralelizada que varre toda a Pokédex, trazendo todos os Pokémon que batem com o critério informado.
- **Tratamento de erros:**
  - Sempre retorno mensagens claras caso o Pokémon não seja encontrado ou o campo seja inválido.
- **Flexibilidade:**
  - O código aceita tanto strings quanto inteiros, e o campo de busca é opcional.

## Como rodar

### Docker (recomendado)
```bash
docker build -t buscador-pokemon .
docker run buscador-pokemon
```

### Local
```bash
pip install -r requirements.txt
python main.py  # modo interativo
python test_pokemon.py  # executa os testes obrigatórios
```

## Como usar

### Modo interativo (`main.py`)

Ao rodar `python main.py`, você entra em um modo interativo onde pode digitar comandos como:

```
query_pokemon(25)
query_pokemon('pikachu', traduzir=True)
query_pokemon(40, field='weight')
configurar_saida_simplificada(True)
```

Digite `exit` ou `sair` para encerrar.

### Testes automatizados (`test_pokemon.py`)

Ao rodar `python test_pokemon.py`, todos os casos obrigatórios do cliente são executados automaticamente, mostrando no console se cada teste teve sucesso ou erro.

## Estrutura do projeto

- `Pokemon/pesquisa_poekmon.py`: Toda a lógica de busca e formatação dos dados.
- `main.py`: Script interativo para o usuário digitar comandos.
- `test_pokemon.py`: Testes automatizados dos casos obrigatórios.
- `Dockerfile` e `requirements.txt`: Para facilitar a execução em qualquer ambiente.

## Observações finais

- Todas as funções e classes têm docstrings detalhadas, explicando o que fazem e como usar.
- O projeto foi pensado para ser facilmente expandido, podendo futuramente incluir cache, endpoints web ou integração com bancos de dados.
