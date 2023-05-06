# ASMA-TP
 

## Airport Config File

    {
        "name": <nome do aeroporto>:str,
        "max_queue" : <maximo de avioes em landing queue>:int,
        "max_planes" : <maximo de avioes iniciados ate o sistema encerrar>:int,
        "dash_board_period" : <frequencia de atualização da dashboard>:int,
        "plane_speed" : <velocidade de avião no chão>:int,
        "max_wait_in_station": <maximo de tempo de repouso na gare>:int,
        "max_wait_landing": <maximo de tempo disposto a esperar para aterrar>:int,
        "max_wait_take_off": <maximo de tempo à espera de confirmação para descolar>:int,
        "Companies":[<empresa>:str],
        "width":145,
        "height":37,
        "map":[[{"type":"Empty"}]]
    }

### Entidades do *map*

    * espaço vazio : {"type":"Empty"} 
    * gare comercial ou de bens, da empresa 1 : 
        {
        "type":"station",
        "company":"1",
        "purpose": ("comercial" | "goods")
        }

    * pista : 
        {
            "type":"airstrip"
        }
